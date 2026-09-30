"""RedisBus: the `Bus` protocol over Redis Streams, for the container deployment."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from pydantic import BaseModel, ValidationError

from shared.bus import Handler
from shared.secure_bus import TLSConfig, _Envelope

MAX_FRAME_BYTES = 16_000

KEY_PREFIX = "dis:"
STREAM_MAXLEN = 128
PER_STREAM = 16
MAX_PASSES = 8


class WireError(ValueError):
    """A frame that must not be delivered."""


def wire_models() -> dict[str, type[BaseModel]]:
    """Message types that may cross the wire: the joint schema file, by class name."""
    from shared import schemas

    return {
        name: obj
        for name, obj in vars(schemas).items()
        if isinstance(obj, type)
        and issubclass(obj, BaseModel)
        and obj.__module__ == schemas.__name__
    }


def encode(message: BaseModel | _Envelope) -> bytes:
    if isinstance(message, _Envelope):
        frame = {
            "type": type(message.model).__name__,
            "body": message.model.model_dump_json(),
            "sender": message.sender,
            "signature": message.signature,
        }
    else:
        frame = {"type": type(message).__name__, "body": message.model_dump_json()}
    return json.dumps(frame, separators=(",", ":")).encode()


def decode(topic: str, raw: bytes, models: dict[str, type[BaseModel]]) -> BaseModel | _Envelope:
    if len(raw) > MAX_FRAME_BYTES:
        raise WireError("oversized")
    try:
        frame = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise WireError("not_json") from exc
    if not isinstance(frame, dict) or not all(isinstance(v, str) for v in frame.values()):
        raise WireError("malformed")
    cls = models.get(frame.get("type", ""))
    if cls is None:
        raise WireError("unknown_type")
    try:
        model = cls.model_validate_json(frame.get("body", ""))
    except ValidationError as exc:
        raise WireError("invalid") from exc
    if "sender" not in frame:
        return model
    if set(frame) != {"type", "body", "sender", "signature"}:
        raise WireError("malformed")
    return _Envelope(topic=topic, model=model, sender=frame["sender"], signature=frame["signature"])


def stream_key(topic: str, publisher: str) -> str:
    return f"{KEY_PREFIX}{topic}:{publisher}"


class RedisBus:
    def __init__(
        self,
        client: Any,
        *,
        publisher: str,
        models: dict[str, type[BaseModel]] | None = None,
    ) -> None:
        self._client = client
        self.publisher = publisher
        self._subs: dict[str, list[Handler]] = defaultdict(list)
        self._models = models if models is not None else wire_models()
        self._cursor: dict[str, str] = {}
        self.discover = True
        self.published = 0
        self.delivered = 0
        self.dropped: dict[str, int] = defaultdict(int)
        self.handler_errors = 0
        self.last_handler_error: str | None = None

    @classmethod
    def connect(
        cls,
        url: str,
        *,
        publisher: str,
        username: str | None = None,
        password: str | None = None,
        tls: TLSConfig | None = None,
    ) -> RedisBus:
        import redis

        tls = tls or TLSConfig()
        tls.validate()
        kwargs: dict[str, Any] = {}
        if tls.enabled:
            kwargs.update(
                ssl_ca_certs=str(tls.ca_cert),
                ssl_certfile=str(tls.client_cert) if tls.client_cert else None,
                ssl_keyfile=str(tls.client_key) if tls.client_key else None,
                ssl_cert_reqs="required",
                ssl_check_hostname=tls.check_hostname,
            )
        client = redis.Redis.from_url(
            url, username=username, password=password, protocol=2, **kwargs
        )
        return cls(client, publisher=publisher)

    @property
    def client(self) -> Any:
        return self._client

    def publish(self, topic: str, model: BaseModel) -> None:
        self._client.xadd(
            stream_key(topic, self.publisher),
            {"f": encode(model)},
            maxlen=STREAM_MAXLEN,
            approximate=True,
        )
        self.published += 1

    def subscribe(self, topic: str, handler: Handler) -> None:
        self._subs[topic].append(handler)

    def follow(self, topic: str, publisher: str) -> None:
        self._cursor.setdefault(stream_key(topic, publisher), "0-0")

    def _discover(self) -> None:
        for topic in self._subs:
            for key in self._client.scan_iter(match=f"{KEY_PREFIX}{topic}:*", count=1000):
                key = key.decode() if isinstance(key, bytes) else key
                self._cursor.setdefault(key, "0-0")

    def pump(self, timeout: float = 0.0) -> int:
        """Deliver waiting frames on this thread, fairly across publishers."""
        if self.discover:
            self._discover()
        handled = 0
        for n in range(MAX_PASSES):
            if not self._cursor:
                break
            block = int(timeout * 1000) if n == 0 and timeout > 0 else None
            response = self._client.xread(dict(self._cursor), count=PER_STREAM, block=block)
            entries = _entries(response)
            if not entries:
                break
            for key, entry_id, fields in entries:
                self._cursor[key] = entry_id
                handled += 1
                self._deliver(key, fields)
        return handled

    def _deliver(self, key: str, fields: dict[Any, Any]) -> None:
        topic, _, publisher = key.removeprefix(KEY_PREFIX).rpartition(":")
        data = fields.get(b"f", fields.get("f"))
        if not isinstance(data, bytes):
            self.dropped["malformed"] += 1
            return
        try:
            model = decode(topic, data, self._models)
        except WireError as exc:
            self.dropped[str(exc)] += 1
            return
        if isinstance(model, _Envelope) and model.sender != publisher:
            self.dropped["sender_mismatch"] += 1
            return
        self.delivered += 1
        for handler in list(self._subs.get(topic, [])):
            try:
                handler(model)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                self.handler_errors += 1
                self.last_handler_error = f"{topic}: {type(exc).__name__}: {exc}"

    def close(self) -> None:
        self._client.close()


def _entries(response: Any) -> list[tuple[str, str, dict[Any, Any]]]:
    """XREAD's reply as (stream, id, fields), whichever protocol shape it came in."""
    if not response:
        return []
    items = response.items() if isinstance(response, dict) else response
    out = []
    for key, batches in items:
        key = key.decode() if isinstance(key, bytes) else key
        rows = batches[0] if batches and isinstance(batches[0], list) else batches
        for entry_id, fields in rows:
            entry_id = entry_id.decode() if isinstance(entry_id, bytes) else entry_id
            out.append((key, entry_id, fields))
    return out
