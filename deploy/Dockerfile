# One image for every role in docker-compose.yml; the first stage builds the Rust binder.

FROM rust:1-slim-bookworm@sha256:ff521445a372125ed4f76e1453a1f8098f2d05332d1601d30db1c1f62757e730 AS binder
RUN printf 'implementation=CPython\nversion=3.12\nshared=true\nabi3=false\npointer_width=64\n' \
        > /pyo3.cfg
ENV PYO3_CONFIG_FILE=/pyo3.cfg
WORKDIR /src
COPY m9_capability_binder/Cargo.toml m9_capability_binder/Cargo.lock ./
COPY m9_capability_binder/src src
RUN cargo build --release --locked \
    && cp target/release/libdis_m9.so "/dis_m9.cpython-312-$(uname -m)-linux-gnu.so"

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app

RUN pip install --no-cache-dir \
        numpy==2.5.2 pydantic==2.13.4 simpy==4.1.2 pyyaml==6.0.3 \
        faiss-cpu==1.15.0 langgraph==1.2.10 psutil==7.2.2 \
        redis==8.1.0 cryptography==50.0.1 mcp==2.2.0 fastapi==0.141.1

WORKDIR /app
COPY configs configs
COPY shared shared
COPY agents agents
COPY m1_monitoring m1_monitoring
COPY m4_response_engine m4_response_engine
COPY m5_immune_memory m5_immune_memory
COPY m6_trust_fusion m6_trust_fusion
COPY m7_self_healing m7_self_healing
COPY m8_eval_harness m8_eval_harness
COPY m9_capability_binder m9_capability_binder
COPY m10_persona_drift m10_persona_drift
COPY m11_memory_hardening m11_memory_hardening
COPY deploy deploy
COPY console console
COPY --from=binder /dis_m9.cpython-312-*.so /app/

RUN useradd --uid 10001 --no-create-home dis
USER dis
ENTRYPOINT ["python", "-m", "deploy.wire"]
