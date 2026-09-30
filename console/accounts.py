"""Operator accounts: who may look, who may act, who may administer."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path

ROLES = ("admin", "operator", "auditor")
SESSION_TICKS = 8 * 3600
MAX_FAILURES = 5
LOCKOUT_SECONDS = 300
_SCRYPT = {"n": 2**14, "r": 8, "p": 1, "dklen": 32}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    salt BLOB NOT NULL,
    hash BLOB NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    expires REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS failures (
    username TEXT PRIMARY KEY,
    count INTEGER NOT NULL,
    last REAL NOT NULL
);
"""


class AuthError(Exception):
    pass


@dataclass(frozen=True)
class User:
    username: str
    role: str
    active: bool = True

    def can(self, action: str) -> bool:
        return action in PERMISSIONS[self.role]


PERMISSIONS = {
    "admin": {"read", "act", "attack", "administer"},
    "operator": {"read", "act", "attack"},
    "auditor": {"read"},
}


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)


def _valid_username(name: str) -> bool:
    return 2 <= len(name) <= 32 and all(c.isalnum() or c in "._-" for c in name)


class Accounts:
    """SQLite-backed users and sessions."""

    def __init__(self, path: Path | str, *, now) -> None:  # type: ignore[no-untyped-def]
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.executescript(_SCHEMA)
        self._lock = threading.Lock()
        self._now = now

    def create(self, username: str, password: str, role: str) -> User:
        if not _valid_username(username):
            raise AuthError("usernames are 2-32 letters, digits, dots, dashes or underscores")
        if role not in ROLES:
            raise AuthError(f"role must be one of {', '.join(ROLES)}")
        if len(password) < 10:
            raise AuthError("passwords need at least 10 characters")
        salt = secrets.token_bytes(16)
        with self._lock, self._db:
            try:
                self._db.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, 1, ?)",
                    (username, role, salt, _hash(password, salt), self._now()),
                )
            except sqlite3.IntegrityError as exc:
                raise AuthError("that username is taken") from exc
        return User(username, role)

    def users(self) -> list[User]:
        rows = self._db.execute("SELECT username, role, active FROM users ORDER BY username")
        return [User(u, r, bool(a)) for u, r, a in rows]

    def count(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def update(
        self,
        username: str,
        *,
        role: str | None = None,
        active: bool | None = None,
        password: str | None = None,
    ) -> None:
        user = self._get(username)
        if user is None:
            raise AuthError("no such user")
        if role is not None and role not in ROLES:
            raise AuthError("unknown role")
        if user.role == "admin" and (role not in (None, "admin") or active is False):
            admins = [u for u in self.users() if u.role == "admin" and u.active]
            if len(admins) <= 1:
                raise AuthError("the last active administrator cannot be demoted or disabled")
        with self._lock, self._db:
            if role is not None:
                self._db.execute("UPDATE users SET role=? WHERE username=?", (role, username))
            if active is not None:
                self._db.execute(
                    "UPDATE users SET active=? WHERE username=?", (int(active), username)
                )
                if not active:
                    self._db.execute("DELETE FROM sessions WHERE username=?", (username,))
            if password is not None:
                if len(password) < 10:
                    raise AuthError("passwords need at least 10 characters")
                salt = secrets.token_bytes(16)
                self._db.execute(
                    "UPDATE users SET salt=?, hash=? WHERE username=?",
                    (salt, _hash(password, salt), username),
                )
                self._db.execute("DELETE FROM sessions WHERE username=?", (username,))

    def _get(self, username: str) -> User | None:
        row = self._db.execute(
            "SELECT username, role, active FROM users WHERE username=?", (username,)
        ).fetchone()
        return User(row[0], row[1], bool(row[2])) if row else None

    def login(self, username: str, password: str) -> tuple[User, str]:
        now = self._now()
        with self._lock:
            failure = self._db.execute(
                "SELECT count, last FROM failures WHERE username=?", (username,)
            ).fetchone()
            if failure and failure[0] >= MAX_FAILURES and now - failure[1] < LOCKOUT_SECONDS:
                raise AuthError("too many failed attempts; try again in a few minutes")
            row = self._db.execute(
                "SELECT role, salt, hash, active FROM users WHERE username=?", (username,)
            ).fetchone()
            salt = row[1] if row else b"\0" * 16
            digest = _hash(password, salt)
            ok = row is not None and hmac.compare_digest(digest, row[2])
            if not ok or not row[3]:
                with self._db:
                    count = (
                        failure[0] if failure and now - failure[1] < LOCKOUT_SECONDS else 0
                    ) + 1
                    self._db.execute(
                        "INSERT OR REPLACE INTO failures VALUES (?, ?, ?)", (username, count, now)
                    )
                raise AuthError("wrong username or password")
            token = secrets.token_urlsafe(32)
            with self._db:
                self._db.execute("DELETE FROM failures WHERE username=?", (username,))
                self._db.execute("DELETE FROM sessions WHERE expires < ?", (now,))
                self._db.execute(
                    "INSERT INTO sessions VALUES (?, ?, ?)",
                    (_token_hash(token), username, now + SESSION_TICKS),
                )
        return User(username, row[0]), token

    def open_session(self, username: str) -> str:
        """A session without a password."""
        user = self._get(username)
        if user is None or not user.active:
            raise AuthError("no such active user")
        token = secrets.token_urlsafe(32)
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO sessions VALUES (?, ?, ?)",
                (_token_hash(token), username, self._now() + SESSION_TICKS),
            )
        return token

    def session(self, token: str | None) -> User | None:
        if not token:
            return None
        row = self._db.execute(
            "SELECT u.username, u.role, u.active, s.expires FROM sessions s "
            "JOIN users u ON u.username = s.username WHERE s.token_hash=?",
            (_token_hash(token),),
        ).fetchone()
        if row is None or not row[2] or row[3] < self._now():
            return None
        return User(row[0], row[1])

    def logout(self, token: str | None) -> None:
        if token:
            with self._lock, self._db:
                self._db.execute("DELETE FROM sessions WHERE token_hash=?", (_token_hash(token),))


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
