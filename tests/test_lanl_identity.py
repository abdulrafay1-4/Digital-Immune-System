"""Identity evidence from LANL authentication: the pass, on a log small enough to read."""

from __future__ import annotations

import gzip
import hashlib

import numpy as np
import pytest

from m1_monitoring.sensors.synthetic import NoiseModel, SyntheticTelemetry
from m8_eval_harness import lanl_identity as lanl


def _unsampled(prefix: str) -> str:
    """A computer name the healthy sample does not draw."""
    n = 0
    while hashlib.sha256(f"{prefix}{n}".encode()).digest()[0] % lanl.SAMPLE_BUCKETS == 0:
        n += 1
    return f"{prefix}{n}"


def _gz(path, lines: list[str]) -> None:
    with gzip.open(path, "wt") as fh:
        fh.write("\n".join(lines) + "\n")


def test_one_pass_counts_what_the_identity_provider_sees(tmp_path, monkeypatch) -> None:
    victim, elsewhere = "C1", _unsampled("C")
    red = tmp_path / "redteam.txt.gz"
    _gz(red, ["5000,U1@DOM1,C9,C1"])
    auth = tmp_path / "auth.txt.gz"
    _gz(
        auth,
        [
            "10,U2@DOM1,U2@DOM1,C2,C1,Kerberos,Network,LogOn,Success",
            "20,U2@DOM1,U2@DOM1,C2,C1,Kerberos,Network,LogOn,Success",
            "30,U3@DOM1,U3@DOM1,C2,C1,Kerberos,Network,LogOn,Fail",
            f"40,U2@DOM1,U2@DOM1,C2,{elsewhere},Kerberos,Network,LogOn,Success",
            "4000,U2@DOM1,U2@DOM1,C2,C1,?,Network,LogOff,Success",
            "5000,U1@DOM1,U1@DOM1,C9,C1,NTLM,Network,LogOn,Success",
            f"{lanl.DAYS * 86400},U1@DOM1,U1@DOM1,C9,C1,NTLM,Network,LogOn,Success",
        ],
    )
    monkeypatch.setattr(lanl, "MIN_ACTIVE_DAYS", 1)
    summary = lanl.extract(auth, tmp_path / "features.npz", redteam=red)
    assert summary["events_read"] == 6, "the pass stops at day 30"
    assert summary["devices_active"] == 1, "a computer outside the sample is not kept"
    data = np.load(tmp_path / "features.npz")
    assert list(data["names"]) == [victim]
    hour0, hour1 = data["counts"][0][0], data["counts"][0][1]
    names = list(lanl.FEATURES)
    assert dict(zip(names, hour0, strict=True)) == {
        "logons": 3, "failed": 1, "ntlm": 0, "new_accounts": 2, "new_sources": 1,
        "new_pairs": 2, "new_ntlm_pairs": 0,
    }  # fmt: skip
    assert dict(zip(names, hour1, strict=True)) == {
        "logons": 1, "failed": 0, "ntlm": 1, "new_accounts": 1, "new_sources": 1,
        "new_pairs": 1, "new_ntlm_pairs": 1,
    }  # fmt: skip
    assert data["attack_hours"][0] == "[1]"


def test_a_replayed_identity_trace_disturbs_identity_alone() -> None:
    trace = (("node-0", (0.5, 0.5)),)
    plain = SyntheticTelemetry(7, noise_model=NoiseModel(kind="gaussian"))
    replayed = SyntheticTelemetry(
        7, noise_model=NoiseModel(kind="replay", trace=trace, trace_dimension="identity")
    )
    before, _ = plain.read(1.0, "node-0")
    after, _ = replayed.read(1.0, "node-0")
    assert after.identity == pytest.approx(max(0.0, before.identity - 0.5), abs=1e-9)
    assert (after.behavioral, after.device, after.network) == (
        before.behavioral,
        before.device,
        before.network,
    )


def test_an_unknown_dimension_is_refused() -> None:
    with pytest.raises(ValueError):
        NoiseModel(kind="replay", trace_dimension="posture")
