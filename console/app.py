"""
The operator console's HTTP API: sessions, the live fleet, operator decisions, the attack lab and
accounts.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from console import evaluation, lab
from console.accounts import ROLES, Accounts, AuthError, User
from console.runtime import ATTACKS, LiveFleet

COOKIE = "dis_session"
CSRF_HEADER = "x-dis-console"
CSP = (
    "default-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'none'"
)


class Login(BaseModel):
    username: str = Field(max_length=64)
    password: str = Field(max_length=256)


class Decision(BaseModel):
    approved: bool
    reason: str = Field(default="", max_length=500)


class Adjudication(BaseModel):
    status: Literal["confirmed", "benign"]


class Rebind(BaseModel):
    agent_id: str = Field(pattern=r"^[A-Za-z0-9._:-]{1,64}$")


class Launch(BaseModel):
    kind: str = Field(max_length=40)
    targets: list[str] | None = Field(default=None, max_length=10)
    severity: float | None = Field(default=None, gt=0, le=1)
    duration: int | None = Field(default=None, ge=1, le=200)
    dimensions: list[Literal["identity", "behavioral", "device", "network"]] | None = None
    on: int | None = Field(default=None, ge=1, le=20)
    period: int | None = Field(default=None, ge=2, le=40)


class LabRun(BaseModel):
    scenario_id: str = Field(max_length=40)
    arms: list[str] = Field(default_factory=lambda: ["full", "binary_zt"], max_length=4)
    seed: int = Field(default=20000, ge=0, lt=1_000_000)


class FleetControl(BaseModel):
    action: Literal["pause", "resume", "speed", "reset"]
    speed: float | None = Field(default=None, ge=0.25, le=8)


class NewUser(BaseModel):
    username: str = Field(max_length=32)
    password: str = Field(min_length=10, max_length=256)
    role: Literal["admin", "operator", "auditor"]


class UserPatch(BaseModel):
    role: Literal["admin", "operator", "auditor"] | None = None
    active: bool | None = None
    password: str | None = Field(default=None, min_length=10, max_length=256)


def create_app(
    accounts: Accounts,
    fleet: LiveFleet,
    *,
    static_dir: Path | None = None,
    secure_cookie: bool = False,
    kiosk_user: str | None = None,
) -> FastAPI:
    """
    Build the console's FastAPI app; `kiosk_user` opens it as that account for local requests only.
    """
    app = FastAPI(title="DIS operator console", docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def guard(request: Request, call_next: Callable) -> Response:
        if request.url.path.startswith("/api/") and request.method not in ("GET", "HEAD"):
            if request.url.path != "/api/login" and request.headers.get(CSRF_HEADER) != "1":
                return JSONResponse({"detail": "missing console header"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = CSP
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    def current(request: Request) -> User:
        user = accounts.session(request.cookies.get(COOKIE))
        if user is None:
            raise HTTPException(401, "sign in first")
        return user

    def need(permission: str) -> Callable[[User], User]:
        def check(user: User = Depends(current)) -> User:
            if not user.can(permission):
                raise HTTPException(403, f"your role ({user.role}) cannot do that")
            return user

        return check

    async def command(name: str, **payload: Any) -> Any:
        future = fleet.submit(name, **payload)
        try:
            return await asyncio.wait_for(asyncio.wrap_future(future), timeout=15)
        except (ValueError, KeyError) as exc:
            raise HTTPException(400, str(exc).strip("'")) from exc
        except TimeoutError as exc:
            raise HTTPException(503, "the fleet did not answer in time") from exc

    @app.post("/api/login")
    async def login(body: Login, response: Response) -> dict:
        try:
            user, token = await asyncio.to_thread(accounts.login, body.username, body.password)
        except AuthError as exc:
            raise HTTPException(401, str(exc)) from exc
        response.set_cookie(
            COOKIE, token, httponly=True, samesite="strict", secure=secure_cookie, max_age=8 * 3600
        )
        return _user(user)

    def _loopback(request: Request) -> bool:
        return request.client is not None and request.client.host in ("127.0.0.1", "::1")

    @app.get("/api/kiosk")
    async def kiosk_info(request: Request) -> dict:
        enabled = kiosk_user is not None and _loopback(request)
        return {"enabled": enabled, "username": kiosk_user if enabled else None}

    @app.post("/api/kiosk")
    async def kiosk(request: Request, response: Response) -> dict:
        if kiosk_user is None or not _loopback(request):
            raise HTTPException(404, "not available")
        token = accounts.open_session(kiosk_user)
        response.set_cookie(
            COOKIE, token, httponly=True, samesite="strict", secure=secure_cookie, max_age=8 * 3600
        )
        user = accounts.session(token)
        assert user is not None
        return _user(user)

    @app.post("/api/logout")
    async def logout(request: Request, response: Response) -> dict:
        accounts.logout(request.cookies.get(COOKIE))
        response.delete_cookie(COOKIE)
        return {"ok": True}

    @app.get("/api/me")
    async def me(user: User = Depends(current)) -> dict:
        return _user(user)

    @app.get("/api/state")
    async def state(user: User = Depends(need("read"))) -> dict:
        return fleet.snapshot()

    @app.get("/api/devices/{node_id}")
    async def device(node_id: str, user: User = Depends(need("read"))) -> dict:
        snap = fleet.snapshot()
        row = next((d for d in snap.get("devices", []) if d["id"] == node_id), None)
        if row is None:
            raise HTTPException(404, "no such device")
        return {"device": row, **fleet.device_detail(node_id)}

    @app.get("/api/ticks")
    async def ticks(count: int = 60, user: User = Depends(need("read"))) -> list:
        return fleet.tick_history(max(1, min(count, 300)))

    @app.post("/api/approvals/{node_id}")
    async def approve(node_id: str, body: Decision, user: User = Depends(need("act"))) -> dict:
        return await command(
            "approve",
            node_id=node_id,
            approved=body.approved,
            reason=body.reason,
            user=user.username,
        )

    @app.post("/api/devices/{node_id}/reconsider")
    async def reconsider(node_id: str, user: User = Depends(need("act"))) -> dict:
        return await command("reconsider", node_id=node_id, user=user.username)

    @app.post("/api/devices/{node_id}/grant-heal")
    async def grant_heal(node_id: str, user: User = Depends(need("act"))) -> dict:
        return await command("grant_heal", node_id=node_id, user=user.username)

    @app.post("/api/devices/{node_id}/rebind")
    async def rebind(node_id: str, body: Rebind, user: User = Depends(need("administer"))) -> dict:
        return await command("rebind", node_id=node_id, agent_id=body.agent_id, user=user.username)

    @app.post("/api/memory/{record_id}")
    async def adjudicate(
        record_id: str, body: Adjudication, user: User = Depends(need("act"))
    ) -> dict:
        return await command(
            "adjudicate", record_id=record_id, status=body.status, user=user.username
        )

    @app.post("/api/fleet")
    async def control(body: FleetControl, user: User = Depends(need("administer"))) -> dict:
        return await command("control", action=body.action, speed=body.speed, user=user.username)

    @app.get("/api/attacks/catalogue")
    async def attack_catalogue(user: User = Depends(need("read"))) -> list:
        return [{"kind": k, **{f: v for f, v in spec.items()}} for k, spec in ATTACKS.items()]

    @app.post("/api/attacks")
    async def launch(body: Launch, user: User = Depends(need("attack"))) -> dict:
        params = body.model_dump(exclude={"kind", "targets"}, exclude_none=True)
        return await command(
            "launch", kind=body.kind, targets=body.targets, user=user.username, **params
        )

    @app.post("/api/attacks/{attack_id}/stop")
    async def stop_attack(attack_id: str, user: User = Depends(need("attack"))) -> dict:
        return await command("stop_attack", attack_id=attack_id, user=user.username)

    @app.get("/api/lab/scenarios")
    async def lab_scenarios(user: User = Depends(need("read"))) -> dict:
        return {"scenarios": lab.catalogue(), "arms": list(lab.LAB_ARMS)}

    @app.post("/api/lab/run")
    async def lab_run(body: LabRun, user: User = Depends(need("attack"))) -> dict:
        try:
            return await asyncio.to_thread(lab.run, body.scenario_id, body.arms, body.seed)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get("/api/evaluation")
    async def evaluation_tables(user: User = Depends(need("read"))) -> dict:
        return await asyncio.to_thread(evaluation.summary)

    @app.get("/api/users")
    async def users(user: User = Depends(need("administer"))) -> list:
        return [_user(u) for u in accounts.users()]

    @app.post("/api/users")
    async def create_user(body: NewUser, user: User = Depends(need("administer"))) -> dict:
        try:
            created = await asyncio.to_thread(
                accounts.create, body.username, body.password, body.role
            )
        except AuthError as exc:
            raise HTTPException(400, str(exc)) from exc
        return _user(created)

    @app.patch("/api/users/{username}")
    async def update_user(
        username: str, body: UserPatch, user: User = Depends(need("administer"))
    ) -> dict:
        if username == user.username and (body.active is False or body.role not in (None, "admin")):
            raise HTTPException(400, "you cannot demote or disable your own account")
        try:
            await asyncio.to_thread(
                accounts.update,
                username,
                role=body.role,
                active=body.active,
                password=body.password,
            )
        except AuthError as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"ok": True}

    if static_dir is not None and (static_dir / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        async def spa(path: str) -> FileResponse:
            candidate = (static_dir / path).resolve()
            if path and candidate.is_file() and static_dir.resolve() in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")

    return app


def _user(user: User) -> dict[str, Any]:
    return {
        "username": user.username,
        "role": user.role,
        "active": user.active,
        "permissions": sorted(p for p in ("read", "act", "attack", "administer") if user.can(p)),
        "roles": list(ROLES),
    }
