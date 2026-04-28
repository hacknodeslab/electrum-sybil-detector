---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-04-26'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md
  - _bmad-output/planning-artifacts/prfaq-electrum-sybil-detector-distillate.md
  - _bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md
  - _bmad-output/planning-artifacts/validation-report-2026-04-26.md
  - docs/project-brief.md
  - docs/architecture.md
  - docs/tech-stack.md
  - docs/roadmap.md
  - docs/references.md
workflowType: 'architecture'
project_name: 'electrum-sybil-detector'
user_name: 'Ifuensan'
date: '2026-04-26'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (42 across 8 categories):**

The PRD organizes 42 FRs into Server Discovery (FR1–FR4), Probing & Data Collection (FR5–FR10), Storage & Schema Discipline (FR11–FR16), Analysis & Signal Computation (FR17–FR24), Dataset Publication & Archival (FR25–FR30), Output Guardrails & Disclosure (FR31–FR34), Bilingual Parity (FR35–FR38), and Operational Health & Stewardship (FR39–FR42). Each FR carries an "*owned by X module*" trace annotation, mapping cleanly to a five-module production spine: Discovery, Collection, Storage, Analysis, Publication — plus supporting CI tooling and an Output-Guardrails audit pipeline.

Architecturally, FR19 (1-D Wasserstein over fee-rate CDFs) and FR24 (multi-frontend calibration harness) are load-bearing: they fix the methodology around CDF-distance rather than equality, which the architecture must reflect across the Analysis module and the pre-launch validation harness.

**Non-Functional Requirements (17 across 7 categories):**

NFR1–NFR5 (Performance) lock timing precision (monotonic-ns clock, sub-millisecond asyncio resolution validated empirically at p99=587µs/N=100 and 1.71ms/N=200), cold-start ≤60s, CI reproducibility re-derivation ≤30 min, snowball ≤24h per sweep.

NFR6–NFR9 (Reliability) lock collection uptime ≥95% over rolling 30-day windows, exponential-backoff reconnection discipline, Tor circuit retry budgets, planned-downtime accounting.

NFR10–NFR14 (Scalability & Cost) lock 100–500 concurrent TCP/SSL sockets, native IPv6 outbound (tunnels banned for timing-precision reasons), ~6 GB/year compressed, ≤$500/year, ≤512 MB resident, SQLite→TimescaleDB by M2.

NFR15–NFR17 (Reproducibility & Determinism) lock the bit-identical contract, forward-compatible-only schema migrations, and PR-review SLAs.

NFR categories 5–7 (Compliance, Documentation/Translation, Integration Conformance) cross-reference authoritative content elsewhere in the PRD without restating, to avoid drift.

**Scale & Complexity:**

- Primary domain: **distributed measurement + scientific reproducibility + data engineering** (not web/mobile/API)
- Complexity level: **medium** with two carve-outs that raise the bar in specific axes — `rigor.statistical_methodology` and `rigor.legal_framing`
- Estimated architectural components: **5 production modules** (Discovery, Collection, Storage, Analysis, Publication) + **2 supporting components** (CI / Reproducibility self-test, Output-Guardrails audit pipeline) + **1 pre-launch validation testbed** (multi-frontend fee-histogram drift harness)

### Technical Constraints & Dependencies

**Locked decisions inherited from PRD/PRFAQ (not re-litigated):**

- **Tool as apparatus, dataset+paper as primary products.** Tool acceptance is reproducibility-driven, not UX-driven.
- **Languages.** Python (asyncio, stdlib at M0) through M3; Rust rewrite at M4. Python and Rust must produce bit-identical derived datasets at the M4 transition (or document floating-point tolerance).
- **Storage path.** SQLite (M0–M1) → TimescaleDB on PostgreSQL (M2+). Schema migration-compatible from day one.
- **Transport.** TCP/TLS at M0–M1; SOCKS5/Tor added at M2; raw JSON-RPC over wire (Electrum protocol 1.4–1.6 stable RPCs only).
- **Dual-stack IPv4+IPv6 outbound** mandatory from M0 (NFR10, LB#26); tunnels banned. Native v6 is a hard infra constraint.
- **Reuse, not reinvention.** `fork-observer` (b10c) for tip tracking; `bitcoin-data/stale-blocks` as canonical fork-race event source; `bitcoin-data` GitHub conventions for dataset publication; methodological-ancestor citations (CoinScope, TxProbe, Grundmann, Node-Probe) for related-work positioning.
- **Three-tier archival pipeline.** `bitcoin-data` GitHub + Zenodo DOI + arXiv preprint, each an independent failure domain.
- **Open-science licensing.** Code MIT, dataset CC BY 4.0, paper arXiv + peer-reviewed venue.

**Hard infra constraints:**

- ≤$500/year total cost envelope (VPS + storage + redundancy + Zenodo + arXiv)
- ≤512 MB resident at the daemon process at full-network scale
- ~6 GB/year compressed dataset volume at full-network scale
- Native IPv6 outbound (Hetzner CX22 satisfies by default; AWS requires explicit VPC/subnet/ENI/IGW config; many low-cost VPS providers omit IPv6 — disqualifying)

**Phased transition gates** locked by PRD §Implementation Considerations: M0→M1, M1→M2, M2→M3, M3 launch gate, M3→M4. The architecture must satisfy each gate in turn without rewrites.

### Cross-Cutting Concerns Identified

1. **Time discipline** (monotonic-ns + per-window NTP) cuts across Collection, Storage, Analysis. One canonical clock abstraction; wall-clock never leaks into computed-delta metrics.
2. **Schema versioning and append-only raw tier** cuts across Storage, Publication, Reproducibility, CI. Forward-compat-only migrations; deprecated raw columns retained ≥1 MAJOR dataset version.
3. **Output Guardrails phrasing-bank audit** cuts across CLI output, dataset README, paper abstract, contribution-channel docs, Spanish mirrors. Pre-publication audit is a launch gate.
4. **Bilingual parity (EN+ES)** cuts across all user-facing artifacts plus CI staleness flag (14d soft / 30d frozen-rollback).
5. **Reproducibility contract** (bit-identical re-derivation from raw inputs + code hash) cuts across Tool, Dataset, CI. Self-test ships with every release.
6. **Five-module production spine** with stable module boundaries: Discovery, Collection, Storage, Analysis, Publication. Module isolation is deliberate to enable independent module-level testing and the Python→Rust M4 transition.
7. **Transport abstraction** must accept clearnet now and Tor SOCKS5 at M2 without re-architecting.
8. **Three-tier archival pipeline** (idempotent `bitcoin-data` PR + Zenodo DOI mint + arXiv upload) cuts across Publication module + CI + manual launch gates.
9. **Python→Rust M4 transition** as a forward-looking constraint on derived-tier determinism, floating-point ordering, hash iteration, BLAS choice.
10. **Solo-researcher operational SPOF** with pre-identified Path 2 handoff (b10c orbit / academic measurement group) at 12-month post-launch threshold. Architectural defense: documentation-first, bilingual, idempotent flows, anyone-can-re-run-the-self-test posture.

## Starter Template Evaluation

### Primary Technology Domain

**Long-running scientific data-collection daemon + offline analysis pipeline + idempotent dataset-publication pipeline + reproducibility self-test.**

This is a `research_project` archetype (per PRD classification), not a web/mobile/API/CLI-tool archetype. Standard starter templates targeting application archetypes (Next.js, T3, NestJS, Expo, oclif) are evaluated and rejected as inappropriate to this project's acceptance criteria (reproducibility-driven, not UX-driven) and to the M0 stdlib-only constraint locked in PRD §Roadmap.

### Starter Options Considered

| Option | Considered for | Rejection rationale |
|---|---|---|
| `cookiecutter-pypackage` (audreyfeldroy) | Generic Python project skeleton | Pulls in opinionated tool choices (tox, sphinx, click, travis) that conflict with M0 stdlib-only constraint and add dev-tooling churn before it's earned |
| `cookiecutter-data-science` (drivendata) | Data-pipeline projects | Optimized for ML / Jupyter workflows; assumes a single dataset and a notebook-driven exploration loop, neither of which matches a long-running collection daemon + reproducibility-gated derived tier |
| `python-poetry` starter | Modern Python packaging | `poetry`'s dependency resolver is overkill at M0 (zero deps); locks the project into one packaging tool before the dev-tooling decision is made in step-04 |
| `oclif` (CLI framework, Node) | Tool / CLI archetype | Wrong language; the daemon is Python, and CLI ergonomics are explicitly out-of-scope per PRD §Project-Type Overview L363 |
| `Next.js` / `Vite` / `T3` / `Expo` / `NestJS` | Web / mobile / API archetypes | Project is none of those; would inject framework decisions inappropriate to a measurement daemon |

### Selected Starter: **None — bespoke project skeleton**

**Rationale for Selection:**

Three constraints specific to this PRD make a starter template a net-negative relative to a bespoke skeleton:

1. **M0 stdlib-only constraint.** PRD §Roadmap M0 explicitly locks the M0 daemon at *"single Python script, stdlib only (no pip deps), SQLite storage."* Any starter would inject dependencies before they're earned.
2. **`fork-observer` reuse posture (LB#8).** The Discovery + Collection modules are designed to consume or share code paths with b10c's existing tool. A starter's opinionated scaffold would compete with that integration.
3. **Reproducibility-driven acceptance.** Tool acceptance is judged by deterministic dataset regeneration (NFR15, FR27, LB#25), not by developer experience or packaging polish. A starter optimizes for the wrong axis.

**Initialization Command:**

No third-party scaffold. The "first implementation story" is to scaffold the M0 stdlib-only daemon directly per PRD §Roadmap M0:

```bash
mkdir -p src/electrum_sybil_detector tests
touch src/electrum_sybil_detector/__init__.py
touch src/electrum_sybil_detector/electrum_monitor.py  # M0 single-file daemon, stdlib-only
touch pyproject.toml                                    # PEP-621 metadata only at M0
touch README.md README.es.md                            # bilingual EN + ES (FR35)
touch LICENSE                                           # MIT
touch .gitignore
git init
```

**Architectural Decisions Provided by Starter:**

(Equivalent: decisions deferred to step-04 with established Python ecosystem conventions as the default candidate set, web-verified before commitment.)

**Language & Runtime:**
- Python ≥ 3.10 (asyncio TaskGroup, `time.monotonic_ns`); Rust at M4. Specific minor-version floor decided in step-04.

**Styling Solution:**
- N/A (no UI). Output Guardrails phrasing-bank audit (FR31) is the closest analogue and is decided in step-04.

**Build Tooling:**
- M0: `pyproject.toml` PEP-621 metadata only; no build backend exercised (script-only).
- M1+: build backend (setuptools / hatch) decided in step-04.

**Testing Framework:**
- `pytest` + `pytest-asyncio` (proposed; ratified in step-04). M0 ships with at minimum a reproducibility self-test invocable from `python -m`, satisfying NFR15 / FR27 / LB#25.

**Code Organization:**
- `src/`-layout. Five-module production spine: `discovery/`, `collection/`, `storage/`, `analysis/`, `publication/` + supporting `audit/` (output guardrails) and `selftest/` (reproducibility CI gate). Module structure ratified in step-04.

**Development Experience:**
- `ruff` (lint + format), `mypy --strict` (type-check), `pre-commit`, bilingual issue/PR templates (EN+ES per FR36). Versions and hook composition decided in step-04.

**Note:** Project initialization (the bespoke M0 skeleton above) should be the first implementation story. Subsequent dev-tooling adoption (ruff / mypy / pytest / pre-commit) is the second story, gated on M0 daemon being runnable end-to-end against ≥1 seed server.

## Core Architectural Decisions

_Decisions ratified collaboratively in step-04. Versions web-verified 2026-04-26._

### Decision Priority Analysis

**Already locked by PRD/PRFAQ (not re-litigated here):** daemon language M0–M3 = Python · M4 = Rust · storage path = SQLite (M0–M1) → TimescaleDB (M2+) · transport = TCP/TLS now, SOCKS5/Tor at M2 · dual-stack v4+v6 from M0 · code MIT, dataset CC BY 4.0 · `fork-observer` reuse posture · three-tier archival.

**Critical (block implementation):** Cat 1 (Language & Runtime), Cat 2 (Data Architecture & Storage), Cat 3 (Connection & Transport), Cat 4 (Module Boundaries), Cat 5 (Analysis Pipeline), Cat 6 (Infrastructure & Deployment), Cat 7 (Dev Tooling).

**Deferred:** M4 Rust pin → M4 entry · multi-process collection → M4 if asyncio profiling shows GIL bottleneck · `fork-observer` code-sharing → M4 Rust transition · Sphinx docs → M4 if surface grows · Monitoring at M0–M1 → M2 if log-line metrics insufficient.

### Cat 1 — Language & Runtime

| ID | Decision | Rationale |
|---|---|---|
| D1.1 | **Python ≥ 3.11** as project floor | `asyncio.TaskGroup` (3.11+) structural for D3.1; pandas 3.0 requires 3.11+; 3.10 is security-only and risks dropping out before M3. |
| D1.2 | CI matrix = **3.11, 3.12, 3.13, 3.14** | Floor + leading-edge coverage; supports Path-2-handoff reproducers on Debian/Ubuntu LTS; 3.14 catches forward-incompat early. |
| D1.3 | Async idiom = **structured concurrency** (TaskGroup, no bare `gather`) on production paths | TaskGroup propagates ExceptionGroup; methodology integrity depends on never silently dropping a probe. |
| D1.4 | Type discipline = **`mypy 1.20+` `--strict`** in CI; `# type: ignore` requires inline reason | Reproducibility-driven acceptance demands type-checked module boundaries. |
| D1.5 | M0 dependency posture = **stdlib only** (PRD §Roadmap M0 lock); analytical deps (numpy/scipy/sklearn/pandas/pyarrow) enter at M1+ | Earned-dependency principle. |
| D1.6 | M4 Rust language pin = **deferred to M4 entry** | Rust ecosystem moves; pinning now over-commits. |

### Cat 2 — Data Architecture & Storage

| ID | Decision | Rationale |
|---|---|---|
| D2.1 | **Two-tier schema** — append-only raw tier + churnable derived tier | FR11/FR14/NFR16; reproducibility contract requires re-derivability. |
| D2.2 | M0–M1 = **SQLite 3 with WAL mode**, one file per collection window | stdlib `sqlite3`; WAL enables concurrent readers (analysis) while collector writes; window-bounded files simplify rotation and Parquet snapshotting. |
| D2.3 | M2+ = **TimescaleDB 2.26+ on PostgreSQL 18** | PG 18 latest GA; avoids one upgrade cycle before M3. PG 15 disqualified (EOL June 2026). |
| D2.4 | Snapshot format = **Parquet via pyarrow 24.x with Zstandard compression** | Matches `bitcoin-data` repo conventions (LB#11); Zstd hits ~6 GB/year target (NFR11). |
| D2.5 | Schema versioning = **`schema_version INTEGER NOT NULL`** column on every raw row + **dataset semver** at release level | FR14 forward-compat-only; per-row tag survives migrations. |
| D2.6 | Server identifier = **BLAKE2b-256 hash** of canonical `(host, port, transport)` triple, 32-byte hex | FR16 opaque-id; BLAKE2b is stdlib (`hashlib`), no extra dep at M0; mapping hostname→hash unpublished by default per Output Guardrails. |
| D2.7 | Time storage = **`monotonic_ns BIGINT` + `wall_clock_ns BIGINT`** (always two columns, never one) | NFR1 lock; physical separation prevents accidental substitution in computed-delta metrics. |
| D2.8 | Migrations at M0 = **stdlib `sqlite3` + numbered idempotent forward-only DDL scripts**; M2+ = **`psycopg` 3.2+ + plain SQL migrations**, **no Alembic at M0–M2** | Alembic adds dep + magic; PRD's forward-compat-only constraint is simple enough for plain SQL. |
| D2.9 | Retention = **raw events indefinitely** for block notifications + connection events + metadata; **90-day raw retention then downsample** for fee histograms and pings | Per `docs/architecture.md` §3; preserves load-bearing fork-race signal indefinitely while bounding fee-histogram bloat. |

### Cat 3 — Connection & Transport Architecture

| ID | Decision | Rationale |
|---|---|---|
| D3.1 | Connection manager = **asyncio.TaskGroup-based pool**, one task per server | Structured concurrency for failure propagation; 100–500 connections (NFR10) within asyncio's empirically-validated regime (NFR2). |
| D3.2 | Transport plugin = **`Transport` Protocol class** with `clearnet_tcp`, `clearnet_ssl` impls at M0; `tor_socks5` impl drops in at M2 without re-architecting | M2 transition becomes "add new impl," not "rewrite collection module." |
| D3.3 | TLS verification = **opportunistic TLS** at M0; record SHA-256 cert fingerprint at connect-time (FR8) | Self-signed certs are common in Electrum ecosystem (TR §5); pinning would block valid honest servers. |
| D3.4 | Reconnection policy = **exponential backoff with jitter**; base=2s, cap=300s, jitter=±25% | NFR7 requires documented base/cap/jitter; jitter prevents thundering-herd reconnection. |
| D3.5 | Rate-limit = **per-server token bucket**, default ≤1 active probe/sec; subscriptions are passive listeners (no rate cost) | FR10 + measurement-ethics LB#22. |
| D3.6 | Tor circuit handling = **3 retries / 300s budget per probe**, then probe-failed (NFR8); circuit fingerprint logged where exposed | Distinguishes Tor failure semantics from clearnet's persistent-connectivity assumption. |
| D3.7 | IPv6 stance = **dual-stack outbound, `happy-eyeballs` disabled** (always try v6 first when AAAA exists; record both attempt outcomes) | Phase-1 V3 evidence shows ~28% of network is IPv6-only; happy-eyeballs would mask that signal. NB: user's local box has broken IPv6 routing — confirms VPS deploy host must differ from local dev. |

### Cat 4 — Module Boundaries & Internal Dataflow

| ID | Decision | Rationale |
|---|---|---|
| D4.1 | **Five production modules + three supporting**: `discovery/`, `collection/`, `storage/`, `analysis/`, `publication/` + `audit/` (FR31), `selftest/` (NFR15/FR27), `harness/` (FR24) | Aligns with PRD §Tool Specification > Module structure; supports M4 Rust port one module at a time. |
| D4.2 | **In-process execution at M0–M3**; multi-process only at M4 if profiling shows GIL bottleneck | Asyncio empirically adequate (NFR2); avoids IPC overhead and determinism concerns. |
| D4.3 | Inter-module surface = **Python `Protocol` classes** (PEP 544 structural typing); no DI framework, no message bus | YAGNI for 5-module system; structural typing supports M4 Rust transition. |
| D4.4 | Discovery → Storage = `connection_event` rows + `servers` registry table (UPSERT on opaque-id) | Discovery is write-only producer; Collection reads `servers` for connection targets. |
| D4.5 | Collection → Storage = **append-only raw-tier inserts**; never UPDATE on raw rows | FR11; UPDATEs would break reproducibility. |
| D4.6 | Storage → Analysis = **read-only views on raw + derived**; Analysis writes only to derived tables tagged with `derived_run_id` + `code_hash` | Lets multiple Analysis runs (re-derivations) coexist; supports NFR15 self-test. |
| D4.7 | Analysis → Publication = **Parquet snapshot from derived tier + `manifest.json`** containing `code_hash`, `raw_input_fingerprint`, `ntp_stratum`, `window_boundaries`, `dataset_version`, `release_timestamp`, `zenodo_doi` | FR26 lock. |
| D4.8 | `fork-observer` integration = **read-only consumption of fork-observer's HTTP/JSON output** at M0–M3; code-sharing reconsidered only at M4 | LB#8 verifies the data-surface; minimizes coupling. |
| D4.9 | Module isolation discipline = each module has own `tests/<module>/` subdir, fixture-based, runnable in isolation | Supports reproducibility self-test + M4 port-one-at-a-time. |

### Cat 5 — Analysis Pipeline Architecture

| ID | Decision | Rationale |
|---|---|---|
| D5.1 | Wasserstein computation = **`scipy.stats.wasserstein_distance` (1-D)** over fee-rate CDFs (FR19) | Canonical implementation; the canonical metric must be the canonical library, not a re-implementation. |
| D5.2 | Fork-race timing variance = **numpy + pandas**; per-pair delta in monotonic-ns; window bounded by `bitcoin-data/stale-blocks` event timestamps (FR17, FR18) | numpy is the right vector primitive. |
| D5.3 | Synchronized-downtime = **interval-overlap algorithm** over `connection_event` rows (FR20) | Stdlib + numpy; no graph-theory framework needed at M3 scale. |
| D5.4 | Multi-signal threshold evaluation = **rule engine**, thresholds in `selftest/thresholds.yaml`, **frozen pre-M3** to prevent post-hoc tuning (FR21) | Pre-commit-as-discipline is innovation IQ4; loaded by reproducibility self-test. |
| D5.5 | Baseline noise-floor = **bootstrap from declared independent-server set** + **permutation test** for null distribution (FR22) | Frequentist, well-understood, reviewer-friendly at FC/PETS/IMC. |
| D5.6 | Clustering = **DBSCAN as primary**; **Ward hierarchical as secondary** for sensitivity analysis (FR23). Both via `scikit-learn` 1.6+ | DBSCAN matches methodology (clusters dense in similarity space, noise = below-threshold candidates); Ward provides sanity check. |
| D5.7 | Statistical rigor = **Benjamini–Hochberg FDR** correction; **bootstrap CIs** on every cluster claim; **power analysis** disclosed for M3 dataset window | BH-FDR has more power than Bonferroni at same FDR; ratified explicitly by user. |
| D5.8 | Determinism contract = pinned random seeds (`numpy.random.default_rng(seed=0)`); deterministic dict iteration; sorted-key serialization for hashes; numpy FP determinism caveats documented per column tolerance (NFR15) | Bit-identical or per-column tolerance — both paths sealed. |
| D5.9 | Computation language = **pure Python at M3** (numpy/scipy/sklearn/pandas/pyarrow); no Cython, no Numba | Reproducibility > raw speed at M3 dataset window scale; harness fits NFR4 30-min CI budget. |
| D5.10 | Calibration harness (FR24) = `python -m electrum_sybil_detector.harness.fee_histogram_drift`, runs both **one-shot pre-launch** (against the 5-frontend matrix: ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs vs. 1 Bitcoin Core) **and as a recurring CI check** | Same code path for both modes; CI mode catches methodology drift between releases. |

### Cat 6 — Infrastructure & Deployment

| ID | Decision | Rationale |
|---|---|---|
| D6.1 | Cloud = **AWS** (user has credits to consume); compute = **EC2 t4g.small** (ARM Graviton, 2 vCPU, 2 GB); region = **us-east-1**; networking = **VPC with explicit IPv6 CIDR + subnet IPv6 CIDR + egress-only IGW + standard IGW**; storage = **gp3 EBS 50 GB**; OS AMI = **Debian 13 ARM64** | EC2 chosen over Lightsail/Fargate for direct kernel access for `chrony` NTP (D6.4) and monotonic-ns timing (NFR1). t4g.small fits NFR13 ≤512 MB resident with headroom; ~$147/year on-demand, well inside NFR12 ≤$500/year. **AWS does not give native v6 by default** like Hetzner does — VPC IPv6 config is mandatory per NFR10. **No IPv6 tunnels** (banned by NFR10). Cost-envelope audit: t4g.small + gp3 stays ≤$500/year on standard pricing with or without credits. |
| D6.2 | OS = **Debian 13 (trixie) ARM64** | Apt-packaged TimescaleDB at M2; long support; matches `bitcoin-data` ecosystem conventions. |
| D6.3 | Process supervision = **systemd** unit with `Restart=on-failure`, **structured-JSON logs to journal**; **no Docker at M0–M1** | Deploy host stays direct-install for accuracy of NTP/timing measurement (Docker adds isolation layer that complicates monotonic-ns guarantees). LB#5 covers user-facing Docker docs path. |
| D6.4 | NTP = **`chrony`** with declared canonical source per collection window logged in dataset manifest (FR13, NFR1) | chrony has better accuracy reporting than ntpd. |
| D6.5 | Monitoring at M2+ = **Grafana + Prometheus + node_exporter**; M0–M1 = structured-JSON log lines parsed via `journalctl --output=json` | `tech-stack.md` names Grafana; deferring its setup until M2 is consistent with earned-dependency principle. |
| D6.6 | CI = **GitHub Actions** (free for OSS, matches `bitcoin-data` ecosystem); reproducibility self-test as CI job within NFR4 ≤30-min budget; matrix = Python 3.11/3.12/3.13/3.14 | Native to OSS ecosystem the project targets. |
| D6.7 | Three-tier archival pipeline = **idempotent helper scripts** invoked from CI on tag push: (a) `bitcoin-data` PR via `gh` CLI, (b) Zenodo DOI mint via Zenodo REST API, (c) arXiv upload manual at M3 (no API for academic preprints) | Idempotency prevents partial-failure poisoning. |
| D6.8 | Bilingual CI staleness = **GitHub Action** diffing `*.md` vs `*.es.md` mtimes; >14d warning, >30d release-blocking gate (FR37/FR38) | Locks bilingual SLA into CI rather than human discipline. |
| D6.9 | Output Guardrails phrasing-bank audit = **CI job** running regex rule-engine across CLI strings, dataset README, paper abstract, Spanish mirrors; release-blocking gate (FR31) | Audit becomes deterministic, not subjective; rules versioned alongside phrasing bank. |

### Cat 7 — Dev Tooling

| ID | Decision | Rationale |
|---|---|---|
| D7.1 | Build backend at M1+ = **`hatchling`** (PEP-621 native, no `setup.py`) | Modern, simple, PyPA-aligned. Rejected: setuptools (legacy ergonomics), poetry (heavier). |
| D7.2 | Dependency manager = **`uv`** (Astral) for venv + lockfile + Python version mgmt | uv.lock pins entire tree byte-by-byte (reproducibility-contract aligned); 10–100× faster than pip; built-in CPython install removes pyenv from CI matrix. Conservative-expert alternative `hatch` was considered and declined. |
| D7.3 | Lint + format = **`ruff` 0.15.12+** with strict ruleset (E, F, W, I, N, UP, B, A, C4, SIM, ARG, PL) | Single tool replaces black/isort/flake8/pylint, ~100× faster, identical formatting to black. |
| D7.4 | Type check = **`mypy` 1.20+ `--strict`** in CI | Strict mode enforces no-untyped-functions; aligned with D1.4. |
| D7.5 | Tests = **`pytest` 8.4+** + **`pytest-asyncio` 1.3.x** (avoid 1.4.0a1 prerelease); coverage via `coverage.py` | Stable, broadly compatible; pre-release rejected for reproducibility. |
| D7.6 | Pre-commit hooks = **`pre-commit` 4.x** with ruff (lint+format), mypy, EOF-fixer, trailing-whitespace, conventional-commits message lint | Catches issues before CI; conventional-commits supports automated CHANGELOG per PRD §Versioning contract. |
| D7.7 | Docs at M0–M3 = bilingual `README.md` + `README.es.md`; schema docs as machine-readable JSON Schema with EN+ES sidecars; **no Sphinx at M0–M3** | Sphinx overkill for research-tool README + first-run guide; revisit at M4 if surface grows. |

### Cross-Component Dependencies (Cascading Implications)

1. **D1.1 (Python ≥ 3.11) → D5.1, D5.6, D5.9**: pandas 3.0 / pyarrow 24 / scipy / sklearn baselines all assume 3.11+, locking the analytical stack.
2. **D2.6 (BLAKE2b stdlib hash) → D1.5**: keeps M0 stdlib-only constraint intact, no `cryptography` dep.
3. **D3.2 (Transport Protocol class) → D4.3 (Protocol-based interfaces)**: same idiom across modules; Tor SOCKS5 at M2 becomes plug-in not rewrite.
4. **D5.4 (frozen thresholds in `selftest/`) → D6.6 (CI gate)**: thresholds-file change after M3 launch is itself a release event requiring new dataset version.
5. **D6.3 (no Docker at M0–M1) → LB#5**: first-run-guide Docker path is *user-facing convenience*, not deploy reality.
6. **D7.2 (uv) → D6.6 (CI)**: GitHub Actions matrix uses `uv` for env setup; pin lockfile in repo.
7. **D6.1 (AWS) → NFR10**: explicit VPC IPv6 CIDR + subnet IPv6 CIDR + egress-only IGW + ENI assignment must be Terraform-codified or documented step-by-step (no ClickOps).

### Implementation Sequence

1. **Story 1**: M0 skeleton — `pyproject.toml` (D7.1 metadata), Python ≥3.11 floor declared, MIT LICENSE, bilingual README placeholders.
2. **Story 2**: M0 daemon — single-script collection (D3.1, D3.2 clearnet impls, D2.7 time discipline, D2.2 SQLite WAL, D2.5 schema_version) against ≥3 hardcoded seeds.
3. **Story 3**: Reproducibility self-test scaffold (D5.8, D6.6 CI matrix, NFR4 budget).
4. **Story 4**: AWS deploy environment (D6.1 EC2 + VPC + IPv6 config, Terraform-codified); LB#26 dual-stack gate verified.
5. **Story 5**: Discovery snowball (M1 entry — D6.6 CI matrix passes against ≥150 servers).
6. **Story 6**: Analysis pipeline scaffolding (D5.1, D5.2, D5.6, D5.7) operating on M0/M1 SQLite snapshots.
7. **Story 7**: Tor SOCKS5 transport plugin (M2 entry — D3.2 third impl, D3.6 retry budget).
8. **Story 8**: TimescaleDB migration (M2 — D2.3, D2.8 psycopg flow).
9. **Story 9**: Three-tier archival pipeline (M3 — D6.7 idempotent scripts, D6.8/D6.9 audit gates).
10. **Story 10**: Calibration harness pre-launch run (M3 LB#2 — D5.10 against 5-frontend matrix).
11. **Story 11**: M3 launch (all 5 forced PRD sections green + reproducibility self-test green + 3-tier archival operational).

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical conflict points identified:** 17 areas where AI agents could make divergent choices that would silently break methodology, force manual rework, or leak defamation exposure. Patterns below pin each one.

### Naming Patterns

**Python code naming** (defer to ruff/PEP 8 enforcement; pinned for emphasis):
- Modules / packages / directories: `snake_case` (e.g., `electrum_sybil_detector/discovery/`)
- Classes / Protocols / TypedDicts: `PascalCase` (e.g., `Transport`, `ConnectionEvent`)
- Functions / methods / variables: `snake_case`
- Module-level constants: `SCREAMING_SNAKE_CASE`
- Private symbols: leading underscore (`_internal_helper`)
- Test files: mirror source path, prefix with `test_` (e.g., `tests/discovery/test_snowball.py` mirrors `src/electrum_sybil_detector/discovery/snowball.py`)

**Database / schema naming** (load-bearing — agents diverge here often):
- Tables: plural snake_case (`servers`, `block_notifications`, `connection_events`, `fee_histograms`)
- Columns: snake_case
- **Time columns** end in `_ns` or `_ts`:
  - `_ns` = BIGINT nanoseconds (monotonic OR wall-clock; never mix)
  - Always two columns paired: `monotonic_ns` and `wall_clock_ns` (D2.7)
  - Never store seconds; never store ISO strings in raw tier
- **Hash columns** end in `_hash`: stored as 64-char hex TEXT (grep-able)
- **Identifier columns** end in `_id` (foreign keys keep the same name as the referenced primary key, no `fk_` prefix)
- **Schema-version column** present on every raw-tier row: `schema_version INTEGER NOT NULL` (D2.5)
- Indexes: `idx_<table>_<columns>` (e.g., `idx_block_notifications_server_id_monotonic_ns`)
- Migrations: `migrations/<seq>_<short_description>.sql` where `<seq>` is zero-padded 4 digits (e.g., `0001_initial_schema.sql`); strictly forward-only (D2.8)

**Configuration files**:
- Pre-committed thresholds: `selftest/thresholds.yaml` (single canonical location, frozen pre-M3 — D5.4)
- Calibration-harness fixtures: `harness/fixtures/<scenario>/`
- Phrasing bank: `audit/phrasing_bank/{en,es}.yaml`
- No environment variables for thresholds or methodology parameters (post-hoc tuning vector — disallowed)

**CLI flags**:
- Long form: `--kebab-case` (e.g., `--collection-window`)
- Short form: single-char only when unambiguous (`-h`, `-v`)
- Boolean flags: `--enable-tor` / `--no-enable-tor` pair (argparse `BooleanOptionalAction`)
- Bilingual `--help` text follows phrasing-bank rules (no originated intent attribution)

### Structure Patterns

**Project layout** (PEP 621 + src-layout):

```
electrum-sybil-detector/
├── src/electrum_sybil_detector/
│   ├── __init__.py
│   ├── discovery/         # Module 1 (D4.1)
│   ├── collection/        # Module 2
│   ├── storage/           # Module 3
│   ├── analysis/          # Module 4
│   ├── publication/       # Module 5
│   ├── audit/             # Supporting: phrasing-bank audit (FR31)
│   ├── selftest/          # Supporting: reproducibility self-test (NFR15)
│   └── harness/           # Supporting: fee-histogram drift testbed (FR24)
├── tests/
│   ├── discovery/         # Mirrors src tree (D4.9)
│   ├── collection/
│   ├── storage/
│   ├── analysis/
│   ├── publication/
│   ├── audit/
│   ├── selftest/
│   ├── harness/
│   └── fixtures/          # Shared test fixtures
├── migrations/
│   ├── sqlite/0001_initial.sql
│   └── timescaledb/0001_initial.sql
├── docs/
│   ├── README.md          # English (authoritative)
│   ├── README.es.md       # Spanish (mirror)
│   └── schema/
│       ├── schema.json    # JSON Schema (machine-readable, language-neutral)
│       ├── schema.en.md
│       └── schema.es.md
├── ci/                    # GitHub Actions workflows
├── infra/                 # Terraform for AWS deploy (D6.1)
├── pyproject.toml
├── uv.lock
├── LICENSE                # MIT
└── .pre-commit-config.yaml
```

**Test organization**: one `test_*.py` per source module, mirror directory tree under `tests/`. Fixtures go in `tests/fixtures/` for cross-module fixtures, `tests/<module>/conftest.py` for module-local. Integration tests that require multiple modules go in `tests/integration/`.

**Where shared utilities go**: there is no `utils/` package. If a helper is used by ≥2 modules, it lives in `src/electrum_sybil_detector/<lowest-common-ancestor-module>/` or graduates to a top-level package (`time_discipline.py`, `hashing.py`). The `utils/` anti-pattern accumulates global state and breaks the M4 port-one-module-at-a-time discipline (D4.9).

### Format Patterns

**Time format** (load-bearing — every probe row has this pair):
- `monotonic_ns`: BIGINT, value from `time.monotonic_ns()` at probe receipt
- `wall_clock_ns`: BIGINT, value from `time.time_ns()` at probe receipt
- Display-only formatting (logs, reports) uses ISO 8601 with `Z` suffix for UTC: `2026-04-26T14:32:11.123456789Z`
- **Never** use Python `datetime` objects in computed-delta metrics; the only legal arithmetic on time columns is `BIGINT - BIGINT` on the monotonic_ns column

**JSON / data exchange format**:
- Field naming: `snake_case` (not camelCase) — matches database column naming and Python convention
- Booleans: `true` / `false` (never `1` / `0`)
- Null handling: explicit `null` for missing optional values; never use sentinel strings like `"N/A"` or empty string
- Timestamps in JSON: BIGINT nanoseconds (matches schema), never ISO strings in machine-readable surfaces
- Hash values: hex strings, lowercase, no `0x` prefix, no separators

**Manifest format** (FR26 — every dataset release):

```json
{
  "manifest_version": 1,
  "dataset_version": "0.3.0",
  "code_hash": "blake2b-256:abc123...",
  "raw_input_fingerprint": "blake2b-256:def456...",
  "ntp_stratum": 2,
  "ntp_canonical_source": "pool.ntp.org",
  "window_boundaries": {
    "start_monotonic_ns": 12345,
    "end_monotonic_ns": 67890,
    "start_wall_clock_ns": 1714137131000000000,
    "end_wall_clock_ns": 1716729131000000000
  },
  "release_timestamp_ns": 1716729131000000000,
  "zenodo_doi": "10.5281/zenodo.XXXXXXX",
  "schema_version": 1,
  "compression": "zstd:level=19"
}
```

**Logging format** (D6.3 — structured JSON to journal):
- One JSON object per line (JSONL)
- Required keys (lowercase snake_case): `monotonic_ns`, `wall_clock_ns`, `level`, `module`, `event`, `server_id` (when applicable)
- `level`: one of `debug`, `info`, `warning`, `error`, `critical`
- `event`: snake_case verb_object (e.g., `probe_sent`, `connection_lost`, `cluster_classified`)
- Free-form context goes under `context` key as a nested object
- No PII in logs (Output Guardrails — server `server_id` is the opaque hash, never the hostname unless explicitly debug-mode + non-published)

**CLI output format**:
- Default: human-readable text following phrasing-bank
- `--json` flag: emits the same structured-JSON shape as logs (one object per line)
- All emitted strings audited by `audit/phrasing_bank` CI gate (D6.9)

### Communication Patterns

**Inter-module communication** (D4.3 — Protocol classes only):
- Modules expose Protocol classes (PEP 544 structural typing) at their package root (e.g., `discovery/__init__.py` exports `class Discoverer(Protocol):`)
- Concrete implementations live in submodules (e.g., `discovery/snowball.py`)
- **No DI framework, no message bus, no event emitter pattern.** A module consumes another module by importing its Protocol and calling methods.
- The Storage module is the only module that owns mutating database operations; other modules call Storage methods, never raw SQL.

**Storage write discipline** (load-bearing):
- Raw tier: only `INSERT`. Never `UPDATE`, never `DELETE`. (D4.5)
- Derived tier: `INSERT` with `derived_run_id` + `code_hash`; old rows from prior runs are not deleted, just superseded by SELECT filters on `derived_run_id`. (D4.6)
- All writes batched within a single transaction per atomic event (e.g., one block notification = one `block_notifications` row + zero or more `connection_events` rows in one transaction).

**Connection-event invariant**: every connect, disconnect, reconnect, and probe-failure produces a `connection_events` row before any dependent probe row is written. Discovery and Collection modules both write to `connection_events`; the Storage module enforces that no `block_notifications` / `fee_histograms` row references a `connection_id` that has no prior `connection_events` row. (FR8)

**`derived_run_id` discipline**:
- Generated as `BLAKE2b-256(code_hash || raw_input_fingerprint || run_timestamp_ns)`
- Stamped on every derived-tier row in that run
- Carries through to the manifest.json (`code_hash` + `derived_run_id` form the reproducibility fingerprint)
- Multiple coexisting derived-runs are allowed; querying without filtering by `derived_run_id` is a code-review violation

### Process Patterns

**Error handling**:
- Use exceptions, not Result types (Pythonic, ruff-friendly)
- Define a project-wide exception hierarchy under `src/electrum_sybil_detector/exceptions.py`:
  - `ElectrumSybilError` (base)
    - `DiscoveryError`
    - `CollectionError`
      - `ProbeError` (recoverable)
      - `ConnectionError` (recoverable)
    - `StorageError` (load-bearing — never swallow)
    - `AnalysisError`
    - `PublicationError`
    - `AuditError`
- **Never `except Exception:`** without re-raising or logging at `error` level with full context
- **Never `except: pass`** (lint rule enforces)
- Recoverable errors (Probe, Connection) get logged at `warning` and feed the reconnection-backoff state machine (D3.4); they do NOT propagate to the TaskGroup root
- Unrecoverable errors propagate to the TaskGroup root, which logs at `critical` and exits non-zero

**Async cancellation handling**:
- All async functions must be cancellation-safe (use `try/finally` for resource cleanup; never swallow `CancelledError`)
- Cancellation is triggered only by:
  - SIGTERM / SIGINT from systemd or operator (D6.3)
  - TaskGroup-root unrecoverable error
  - Per-probe timeout (rate-limit + measurement-ethics combined)

**Reconnection backoff** (D3.4 — pinned for agent consistency):

```python
def backoff_delay(attempt: int) -> float:
    base = 2.0  # seconds
    cap = 300.0  # seconds
    jitter_pct = 0.25
    raw = min(cap, base * (2 ** attempt))
    jitter = raw * jitter_pct * (random.random() * 2 - 1)
    return raw + jitter
```

**Determinism pattern** (D5.8 — load-bearing for NFR15):
- All `random.Random` and `numpy.random.default_rng` instances created with explicit `seed=0` for repeatability tests; explicit per-run seeds for production runs, logged in manifest
- All `dict` iteration is insertion-ordered (Python 3.7+ guaranteed); never depend on this for serialization
- All hashes computed over sorted-key JSON: `json.dumps(obj, sort_keys=True, separators=(",", ":"))`
- All `set` and `frozenset` operations on collections that feed hashes or derived rows must `sorted()` first
- numpy floating-point operations: documented per-column tolerance in schema docs; bit-identical re-derivation is the goal, but per-column tolerance is the documented fallback

**Migration application discipline**:
- Migrations applied in numeric order (`0001_*.sql` before `0002_*.sql`)
- Each migration is idempotent (use `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`, etc.)
- A `schema_migrations` table tracks applied migration filenames
- **Never modify an applied migration**; corrections go in a new numbered migration
- Forward-compat-only: deprecated columns kept until at least the next MAJOR dataset version (D2.8, NFR16)

**Bilingual document update workflow** (FR37/FR38 + D6.8):
- English `*.md` is authoritative; Spanish `*.es.md` is the mirror
- When the English file is updated, a CI bot opens an issue tagging `translation-pending`
- 14-day soft SLA: warning in CI
- 30-day hard SLA: CI gate blocks releases until the Spanish mirror is updated OR the English change is rolled back to the prior synchronized version
- Translation PRs accepted in English or Spanish (FR36)

**Output Guardrails enforcement** (FR31 — load-bearing for legal framing):
- All public-facing strings (CLI output, dataset README, paper abstract, contribution-channel docs, Spanish mirrors) audited by the `audit/` CI job before release
- Phrasing bank rules:
  - **Approved**: "shared infrastructure clusters", "infrastructure-shared cluster", "backend-shared frontend group"
  - **Prohibited**: "operator X runs servers Y", "Chainalysis runs", "surveillance operator", any phrase that originates intent attribution
  - **Cited-only**: intent-attribution language is permitted only when citing published third-party material (b10c issue #11; CoinDesk 2021); the citation must be inline-visible in the same sentence
- Audit gate is release-blocking; release blocked until phrasing-bank audit passes

**Reproducibility self-test workflow** (NFR15, FR27, LB#25):
- Self-test invoked via `python -m electrum_sybil_detector.selftest`
- Runs full re-derivation pipeline on a frozen raw-input fixture
- Compares output to expected `manifest.json` + per-column tolerance bounds
- Exits 0 on bit-identical match or within-tolerance match; exits 1 otherwise
- CI runs self-test on every push; release pipeline blocks on self-test failure (NFR4: ≤30 min runtime budget)

### Enforcement Guidelines

**All AI Agents MUST:**

1. Use the time pair (`monotonic_ns` + `wall_clock_ns`) on every probe row; never substitute one for the other in computed-delta metrics.
2. Never write UPDATE or DELETE against raw-tier tables.
3. Stamp every derived-tier row with `derived_run_id` + `code_hash`.
4. Use Python `Protocol` classes for inter-module surfaces; no DI framework, no message bus.
5. Use the project exception hierarchy (`ElectrumSybilError` and subclasses); never `except Exception: pass`.
6. Use seeded randomness (`seed=0` for repeatability tests; explicit per-run seeds for production runs, logged in manifest).
7. Apply phrasing-bank discipline to every public-facing string.
8. Update Spanish mirror within 14 days of any English `*.md` change, or roll back the English change.
9. Apply migrations in numeric order; never modify an applied migration; never break forward-compat on raw tier.
10. Pass ruff (lint + format), mypy --strict, and the reproducibility self-test before merge.

**Pattern enforcement mechanisms:**
- **Compile-time**: `mypy --strict` with the project Protocol classes catches DI-framework imports and type-incompatible Storage calls
- **Lint-time**: `ruff` rules enforce naming, import order, exception handling, no-bare-except
- **Pre-commit**: hooks reject commits that fail ruff, mypy, or EOF-fixer
- **CI-time**: phrasing-bank audit, bilingual staleness check, reproducibility self-test, schema-migration order check
- **Code-review**: humans verify Protocol-class usage, derived_run_id discipline, and `connection_events`-precedence invariant

**Pattern updates**: any pattern change requires a PR titled `pattern: <change>` and a CHANGELOG entry under `docs/architecture-patterns-changelog.md`. Pre-M3 lock: pattern changes that affect the methodology (time discipline, append-only raw, determinism contract, phrasing bank) require explicit user ratification, not just code review.

### Pattern Examples

**Good — Storage write (Collection module)**:

```python
class SqliteStorage:
    async def record_block_notification(
        self,
        connection_id: int,
        block_height: int,
        block_hash: str,
        monotonic_ns: int,
        wall_clock_ns: int,
        schema_version: int = CURRENT_SCHEMA_VERSION,
    ) -> None:
        async with self._conn.transaction():
            await self._conn.execute(
                "INSERT INTO block_notifications "
                "(connection_id, block_height, block_hash, monotonic_ns, "
                " wall_clock_ns, schema_version) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (connection_id, block_height, block_hash,
                 monotonic_ns, wall_clock_ns, schema_version),
            )
```

**Anti-pattern — UPDATE on raw row, mixing time semantics**:

```python
# BAD: UPDATE on raw tier (D4.5 violation)
await self._conn.execute(
    "UPDATE block_notifications SET block_hash = ? WHERE id = ?",
    (corrected_hash, row_id),
)

# BAD: storing only one time column (D2.7 violation)
await self._conn.execute(
    "INSERT INTO block_notifications (block_height, timestamp) "
    "VALUES (?, ?)",
    (height, datetime.now()),  # Which clock? Wall? Monotonic? Both lost.
)
```

**Good — phrasing-bank-compliant CLI output**:

```
Detected 3 shared-infrastructure clusters in the M3 dataset window.
Cluster 1: 4 servers, multi-signal threshold passed
  (fork-race timing variance: 0.012; fee-histogram Wasserstein: 0.003;
   ASN: AS24940).
See docs/phrasing-bank for the full guide on interpreting these findings.
```

**Anti-pattern — originates intent attribution**:

```
DETECTED: Chainalysis is running 4 surveillance servers (Cluster 1).
Operator AS24940 is conducting wallet-user de-anonymization.
```

(The first form is a measurement claim; the second originates intent attribution and is defamation-exposed.)

## Project Structure & Boundaries

### Complete Project Directory Structure

Files marked with milestone tags indicate when they enter the codebase: **[M0]** = M0 launch, **[M1]** = added at M1 entry, **[M2]** = added at M2 entry, **[M3]** = added pre-M3 launch, **[M4]** = post-M3 (future).

```
electrum-sybil-detector/
├── README.md                              [M0] English authoritative
├── README.es.md                           [M0] Spanish mirror (FR35)
├── LICENSE                                [M0] MIT
├── pyproject.toml                         [M0] PEP-621 metadata + tool config
├── uv.lock                                [M0] Pinned deps (NFR15)
├── .gitignore                             [M0]
├── .pre-commit-config.yaml                [M0] D7.6 hooks
├── CHANGELOG.md                           [M0] Conventional-commits
├── CONTRIBUTING.md                        [M0] EN
├── CONTRIBUTING.es.md                     [M0] ES (FR35)
├── CODE_OF_CONDUCT.md                     [M0]
├── docs/
│   ├── architecture.md                    [M0] This document
│   ├── architecture-patterns-changelog.md [M0] Pattern updates log
│   ├── first-run-guide.md                 [M0] EN (LB#5)
│   ├── first-run-guide.es.md              [M0] ES (FR35)
│   ├── deploy-aws.md                      [M0] AWS EC2 setup (D6.1)
│   ├── deploy-aws.es.md                   [M0]
│   ├── methodology.md                     [M3] Paper draft scaffold
│   ├── threat-model.md                    [M3] LB#23
│   ├── measurement-ethics.md              [M3] LB#22
│   ├── known-evasion-paths.md             [M3]
│   ├── what-flagged-cluster-does-not-mean.md     [M3] FR32 EN
│   ├── what-flagged-cluster-does-not-mean.es.md  [M3]
│   ├── reproducibility-statement.md       [M3] FR27 link
│   ├── schema/
│   │   ├── schema.json                    [M0] JSON Schema (machine-readable)
│   │   ├── schema.en.md                   [M0] EN docs
│   │   └── schema.es.md                   [M0] ES docs (FR35)
│   ├── papers/                            [M0+] References (existing)
│   └── bmad-binnacle/                     [M0+] Process logs (existing)
├── src/electrum_sybil_detector/
│   ├── __init__.py                        [M0] Package version
│   ├── __main__.py                        [M0] Entry: python -m electrum_sybil_detector
│   ├── exceptions.py                      [M0] Project exception hierarchy
│   ├── time_discipline.py                 [M0] monotonic_ns + wall_clock_ns pair (D2.7, NFR1)
│   ├── hashing.py                         [M0] BLAKE2b-256 helpers (D2.6)
│   ├── config.py                          [M0] CLI + config-file loading
│   ├── logging_setup.py                   [M0] Structured-JSON logging (D6.3)
│   ├── version.py                         [M0] Single source for code_hash + dataset_version
│   ├── discovery/                         # Module 1 (D4.1, FR1–FR4)
│   │   ├── __init__.py                    [M0] Discoverer Protocol class
│   │   ├── seeds.py                       [M0] Seed-list ingestion (FR1)
│   │   ├── snowball.py                    [M1] server.peers.subscribe expansion (FR2)
│   │   ├── tor.py                         [M2] Tor SOCKS5 onion discovery (FR3)
│   │   ├── provenance.py                  [M0] Discovery-source recording (FR4)
│   │   └── asn.py                         [M1] ASN diversity handling
│   ├── collection/                        # Module 2 (D4.1, FR5–FR10)
│   │   ├── __init__.py                    [M0] Collector Protocol class
│   │   ├── connection_manager.py          [M0] asyncio.TaskGroup pool (D3.1, FR5)
│   │   ├── transport/                     # D3.2 transport plugins
│   │   │   ├── __init__.py                [M0] Transport Protocol class
│   │   │   ├── tcp.py                     [M0] Plain TCP (clearnet)
│   │   │   ├── ssl.py                     [M0] TLS (clearnet, opportunistic, D3.3)
│   │   │   └── tor_socks5.py              [M2] Tor SOCKS5 (D3.6)
│   │   ├── electrum_protocol.py           [M0] JSON-RPC over Electrum (FR7)
│   │   ├── headers_subscribe.py           [M0] blockchain.headers.subscribe (FR6)
│   │   ├── periodic_probes.py             [M0] Polling loop (FR7)
│   │   ├── connection_lifecycle.py        [M0] Connect/disconnect/uptime events (FR8, FR9)
│   │   ├── rate_limit.py                  [M0] Per-server token bucket (D3.5, FR10)
│   │   └── reconnect.py                   [M0] Exponential backoff (D3.4, NFR7)
│   ├── storage/                           # Module 3 (D4.1, FR11–FR16)
│   │   ├── __init__.py                    [M0] Storage Protocol class (canonical surface)
│   │   ├── sqlite_backend.py              [M0] SQLite WAL impl (D2.2)
│   │   ├── timescaledb_backend.py         [M2] TimescaleDB on PG18 impl (D2.3)
│   │   ├── schema.py                      [M0] Schema versioning + opaque-id (D2.5, FR16)
│   │   ├── migrations.py                  [M0] Forward-only migration runner (D2.8, FR14)
│   │   ├── models.py                      [M0] TypedDicts for raw + derived rows
│   │   └── retention.py                   [M2] 90-day downsampling (D2.9)
│   ├── analysis/                          # Module 4 (D4.1, FR17–FR24)
│   │   ├── __init__.py                    [M3] Analyzer Protocol class
│   │   ├── fork_race_events.py            [M3] bitcoin-data/stale-blocks ingest (FR17)
│   │   ├── pairwise_delta.py              [M3] Per-pair monotonic-ns variance (FR18)
│   │   ├── wasserstein.py                 [M3] scipy.stats.wasserstein_distance (D5.1, FR19)
│   │   ├── synchronized_downtime.py       [M3] Interval-overlap (D5.3, FR20)
│   │   ├── multi_signal_threshold.py      [M3] Rule engine (D5.4, FR21)
│   │   ├── baseline_distribution.py       [M3] Bootstrap + permutation (D5.5, FR22)
│   │   ├── clustering.py                  [M3] DBSCAN + Ward (D5.6, FR23)
│   │   ├── statistical_rigor.py           [M3] BH-FDR + bootstrap CIs (D5.7)
│   │   └── derived_run.py                 [M3] derived_run_id stamping (D4.6)
│   ├── publication/                       # Module 5 (D4.1, FR25–FR30)
│   │   ├── __init__.py                    [M3] Publisher Protocol class
│   │   ├── parquet_snapshot.py            [M1] pyarrow Parquet + Zstd (D2.4, FR25)
│   │   ├── manifest.py                    [M3] manifest.json builder (FR26)
│   │   ├── self_test_gate.py              [M3] Reproducibility self-test invocation (FR27)
│   │   ├── bitcoin_data_pr.py             [M3] gh CLI flow (D6.7a, FR28)
│   │   ├── zenodo_doi.py                  [M3] Zenodo REST API (D6.7b, FR29)
│   │   └── arxiv_upload.py                [M3] Manual upload helper (D6.7c, FR30)
│   ├── audit/                             # Supporting (FR31, D6.9)
│   │   ├── __init__.py                    [M0] PhrasingBank Protocol class
│   │   ├── phrasing_bank/
│   │   │   ├── en.yaml                    [M0] EN approved/prohibited/cited
│   │   │   └── es.yaml                    [M0] ES mirror
│   │   ├── audit_runner.py                [M0] Regex rule engine
│   │   ├── disclosure_template.md         [M3] FR33 EN issue template
│   │   ├── disclosure_template.es.md      [M3] ES
│   │   └── flagged_operator_workflow.py   [M3] FR33–FR34 disclosure flow
│   ├── selftest/                          # Supporting (NFR15, FR27, LB#25)
│   │   ├── __init__.py                    [M0]
│   │   ├── thresholds.yaml                [M3] Pre-committed thresholds (D5.4, frozen pre-M3)
│   │   ├── fixtures/
│   │   │   └── m3_dataset_window/         [M3] Frozen raw-input fixture
│   │   ├── reproducibility.py             [M0] Self-test runner (NFR4 ≤30 min)
│   │   ├── tolerance.py                   [M3] Per-column FP tolerance
│   │   └── manifest_checker.py            [M3] manifest.json comparison
│   └── harness/                           # Supporting (FR24, LB#2)
│       ├── __init__.py                    [M0]
│       ├── fee_histogram_drift.py         [M3] FR24 calibration harness
│       ├── multi_frontend_matrix.py       [M3] 5-frontend orchestration
│       └── fixtures/
│           ├── electrumx_a/               [M3] One ElectrumX instance config
│           ├── electrumx_b/               [M3] Second ElectrumX instance
│           ├── fulcrum/                   [M3]
│           ├── mempool_electrs/           [M3]
│           └── blockstream_electrs/       [M3]
├── tests/
│   ├── __init__.py                        [M0]
│   ├── conftest.py                        [M0] Cross-module fixtures
│   ├── fixtures/                          [M0] Shared raw-data fixtures
│   ├── discovery/
│   │   ├── conftest.py                    [M0]
│   │   ├── test_seeds.py                  [M0]
│   │   ├── test_snowball.py               [M1]
│   │   └── test_tor.py                    [M2]
│   ├── collection/
│   │   ├── conftest.py                    [M0]
│   │   ├── test_connection_manager.py     [M0]
│   │   ├── test_transport_tcp.py          [M0]
│   │   ├── test_transport_ssl.py          [M0]
│   │   ├── test_transport_tor.py          [M2]
│   │   ├── test_electrum_protocol.py      [M0]
│   │   ├── test_rate_limit.py             [M0]
│   │   └── test_reconnect.py              [M0]
│   ├── storage/
│   │   ├── conftest.py                    [M0]
│   │   ├── test_sqlite_backend.py         [M0]
│   │   ├── test_timescaledb_backend.py    [M2]
│   │   ├── test_schema.py                 [M0]
│   │   ├── test_migrations.py             [M0]
│   │   └── test_retention.py              [M2]
│   ├── analysis/
│   │   ├── conftest.py                    [M3]
│   │   ├── test_pairwise_delta.py         [M3]
│   │   ├── test_wasserstein.py            [M3]
│   │   ├── test_clustering.py             [M3]
│   │   ├── test_multi_signal_threshold.py [M3]
│   │   ├── test_baseline_distribution.py  [M3]
│   │   └── test_statistical_rigor.py      [M3]
│   ├── publication/
│   │   ├── conftest.py                    [M3]
│   │   ├── test_parquet_snapshot.py       [M1]
│   │   ├── test_manifest.py               [M3]
│   │   ├── test_self_test_gate.py         [M3]
│   │   ├── test_bitcoin_data_pr.py        [M3]
│   │   └── test_zenodo_doi.py             [M3]
│   ├── audit/
│   │   ├── conftest.py                    [M0]
│   │   ├── test_phrasing_bank.py          [M0]
│   │   └── test_audit_runner.py           [M0]
│   ├── selftest/
│   │   ├── conftest.py                    [M0]
│   │   └── test_reproducibility.py        [M0]
│   ├── harness/
│   │   ├── conftest.py                    [M3]
│   │   └── test_fee_histogram_drift.py    [M3]
│   └── integration/
│       ├── test_m0_end_to_end.py          [M0] Discovery+Collection+Storage round-trip
│       ├── test_snowball_to_storage.py    [M1]
│       ├── test_analysis_pipeline.py      [M3]
│       └── test_publication_pipeline.py   [M3]
├── migrations/
│   ├── sqlite/
│   │   ├── 0001_initial_schema.sql        [M0] servers, connection_events, block_notifications
│   │   ├── 0002_periodic_probes.sql       [M0] server_metadata, fee_estimates, relay_fees, fee_histograms, availability
│   │   ├── 0003_add_donation_address.sql  [M0]
│   │   ├── 0004_add_provenance.sql        [M1] Discovery provenance (FR4)
│   │   ├── 0005_add_features.sql          [M1] server.features columns
│   │   └── 0006_derived_runs.sql          [M3] derived_run_id table + indices
│   └── timescaledb/
│       ├── 0001_initial_schema.sql        [M2] Hypertables
│       └── 0002_compression_policy.sql    [M2] Compression for 90-day downsampling
├── ci/
│   ├── github-actions/
│   │   ├── ci.yml                         [M0] Python 3.11/3.12/3.13/3.14 matrix; ruff + mypy + pytest
│   │   ├── selftest.yml                   [M0] Reproducibility self-test job
│   │   ├── audit.yml                      [M0] Phrasing-bank audit job (FR31)
│   │   ├── bilingual-staleness.yml        [M0] EN/ES mirror staleness check (D6.8)
│   │   └── release.yml                    [M3] Three-tier archival pipeline
│   └── scripts/
│       ├── verify_dual_stack.sh           [M0] LB#26 IPv6 outbound gate
│       └── run_selftest.sh                [M0] Self-test invocation wrapper
├── infra/
│   ├── terraform/
│   │   ├── main.tf                        [M0] AWS EC2 t4g.small (D6.1)
│   │   ├── network.tf                     [M0] VPC + IPv6 CIDR + IGW + egress-only IGW (NFR10)
│   │   ├── compute.tf                     [M0] EC2 instance + EBS gp3 50 GB
│   │   ├── security.tf                    [M0] Security groups
│   │   └── outputs.tf                     [M0]
│   └── systemd/
│       ├── electrum-monitor.service       [M0] D6.3 unit file
│       └── chrony.conf.d/                 [M0] D6.4 NTP discipline
├── scripts/
│   ├── verify_dataset.py                  [M3] Reviewer-runnable bit-identical check
│   ├── run_calibration_harness.sh         [M3] Pre-launch FR24 invocation
│   └── publish_release.sh                 [M3] Three-tier archival driver
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report_en.md               [M0]
    │   ├── bug_report_es.md               [M0] FR36
    │   ├── flagged_operator_en.md         [M3] FR33
    │   └── flagged_operator_es.md         [M3]
    ├── PULL_REQUEST_TEMPLATE.md           [M0] EN
    ├── PULL_REQUEST_TEMPLATE.es.md        [M0] ES
    └── workflows -> ../ci/github-actions/ [M0] Symlink convention
```

### Architectural Boundaries

**Module surfaces (D4.3)** — each module's public Protocol class lives at the package root and is the only legal way other modules consume it. Concrete implementations live in submodules and are not imported across module boundaries.

| Module | Public Protocol class | Where exported |
|---|---|---|
| Discovery | `Discoverer` | `src/electrum_sybil_detector/discovery/__init__.py` |
| Collection | `Collector` | `src/electrum_sybil_detector/collection/__init__.py` |
| Storage | `Storage` | `src/electrum_sybil_detector/storage/__init__.py` |
| Analysis | `Analyzer` | `src/electrum_sybil_detector/analysis/__init__.py` |
| Publication | `Publisher` | `src/electrum_sybil_detector/publication/__init__.py` |
| Audit (supporting) | `PhrasingBankAuditor` | `src/electrum_sybil_detector/audit/__init__.py` |

**Storage as the single integration point** — the Storage module is the only module that owns mutating database operations. Discovery, Collection, and Analysis all consume the `Storage` Protocol; none of them import from `storage/sqlite_backend.py` or `storage/timescaledb_backend.py` directly. This invariant is what makes the SQLite → TimescaleDB migration (D2.3) a backend-swap, not a project-wide rewrite.

**Transport plugin boundary (D3.2)** — the `Transport` Protocol class in `collection/transport/__init__.py` is consumed by `connection_manager.py`. New transports (Tor at M2) drop in as new files implementing the Protocol; the connection manager itself does not change.

**External integration boundaries:**

| External | Interface | Owned by |
|---|---|---|
| Electrum servers (clearnet + Tor) | JSON-RPC over TCP/TLS/SOCKS5 | `collection/transport/`, `collection/electrum_protocol.py` |
| `bitcoin-data/stale-blocks` | Read-only HTTP/JSON consumption | `analysis/fork_race_events.py` |
| `fork-observer` (b10c) | Read-only HTTP/JSON consumption (D4.8) | `analysis/fork_race_events.py` (M3) |
| `bitcoin-data` GitHub repo | `gh` CLI (D6.7a) | `publication/bitcoin_data_pr.py` |
| Zenodo | REST API (D6.7b) | `publication/zenodo_doi.py` |
| arXiv | Manual upload (D6.7c) | `publication/arxiv_upload.py` (helper, not full automation) |
| AWS EC2 + EBS | Terraform-codified infra (D6.1, NFR10) | `infra/terraform/` |
| systemd | Unit files (D6.3) | `infra/systemd/` |
| chrony | Config (D6.4) | `infra/systemd/chrony.conf.d/` |

**Data tier boundaries:**

- **Raw tier** — `block_notifications`, `connection_events`, `server_metadata`, `fee_estimates`, `relay_fees`, `fee_histograms`, `availability`. INSERT-only (D4.5).
- **Derived tier** — `clusters`, `pair_similarity_scores`, `signal_breakdowns`, `derived_runs` (the run-tracking table itself). All rows tagged with `derived_run_id` + `code_hash` (D4.6).
- **Schema-meta tier** — `schema_migrations` (which migrations are applied), `manifest_history` (released manifest.jsons).

### Requirements to Structure Mapping

**Functional Requirements (42 FRs → file/module mapping):**

| FR | Description (abbrev) | Location |
|---|---|---|
| FR1 | Seed-list ingestion | `discovery/seeds.py` |
| FR2 | Snowball expansion | `discovery/snowball.py` |
| FR3 | Tor SOCKS5 .onion discovery | `discovery/tor.py` |
| FR4 | Discovery provenance | `discovery/provenance.py` |
| FR5 | Persistent asyncio connections | `collection/connection_manager.py` |
| FR6 | `headers.subscribe` capture | `collection/headers_subscribe.py` |
| FR7 | Stable RPC periodic polling | `collection/periodic_probes.py` + `collection/electrum_protocol.py` |
| FR8 | Connection-event metadata at connect-time | `collection/connection_lifecycle.py` |
| FR9 | Per-server uptime/downtime events | `collection/connection_lifecycle.py` |
| FR10 | Rate-limit conformance | `collection/rate_limit.py` |
| FR11 | Append-only raw-tier rows | `storage/sqlite_backend.py`, `storage/timescaledb_backend.py` (Storage Protocol enforces no UPDATE/DELETE) |
| FR12 | Two time columns separately persisted | `storage/schema.py` + `time_discipline.py` |
| FR13 | NTP manifest per window | `publication/manifest.py` + `infra/systemd/chrony.conf.d/` |
| FR14 | Forward-compat-only migrations | `migrations/sqlite/` + `migrations/timescaledb/` + `storage/migrations.py` |
| FR15 | SQLite → TimescaleDB migration | `storage/timescaledb_backend.py` + `migrations/timescaledb/` |
| FR16 | Opaque server identifiers | `hashing.py` + `storage/schema.py` |
| FR17 | Fork-race event ingestion | `analysis/fork_race_events.py` |
| FR18 | Pairwise-delta variance | `analysis/pairwise_delta.py` |
| FR19 | 1-D Wasserstein over fee CDFs | `analysis/wasserstein.py` |
| FR20 | Synchronized-downtime signal | `analysis/synchronized_downtime.py` |
| FR21 | Multi-signal threshold evaluation | `analysis/multi_signal_threshold.py` + `selftest/thresholds.yaml` |
| FR22 | Known-independent baseline | `analysis/baseline_distribution.py` |
| FR23 | DBSCAN/Ward clustering | `analysis/clustering.py` |
| FR24 | Fee-histogram drift harness | `harness/fee_histogram_drift.py` + `harness/multi_frontend_matrix.py` |
| FR25 | Parquet snapshot generation | `publication/parquet_snapshot.py` |
| FR26 | manifest.json per release | `publication/manifest.py` |
| FR27 | Bit-identical re-derivation self-test | `selftest/reproducibility.py` |
| FR28 | `bitcoin-data` PR flow | `publication/bitcoin_data_pr.py` |
| FR29 | Zenodo DOI mint | `publication/zenodo_doi.py` |
| FR30 | arXiv upload | `publication/arxiv_upload.py` |
| FR31 | Phrasing-bank audit pass | `audit/audit_runner.py` + `audit/phrasing_bank/` |
| FR32 | "What flagged cluster does NOT mean" text | `docs/what-flagged-cluster-does-not-mean.{md,es.md}` |
| FR33 | Disclosure issue + 48h ack | `audit/disclosure_template.md` + `audit/flagged_operator_workflow.py` |
| FR34 | Operator contextual note ingestion | `audit/flagged_operator_workflow.py` |
| FR35 | EN+ES synchronized parity | All `*.md` + `*.es.md` mirrors |
| FR36 | Spanish issues/PRs accepted, same SLA | `.github/ISSUE_TEMPLATE/` + `.github/PULL_REQUEST_TEMPLATE.es.md` |
| FR37 | Translation-pending CI flag | `ci/github-actions/bilingual-staleness.yml` |
| FR38 | Stale-translation rollback | `ci/github-actions/bilingual-staleness.yml` (release-blocking gate) |
| FR39 | 30-day-rolling uptime monitoring | `collection/connection_lifecycle.py` + Grafana (M2+) |
| FR40 | Collection-gap enumeration | `storage/schema.py` (gap views) |
| FR41 | PR-review SLA tracking | `.github/` automation (out of code scope; doc'd in CONTRIBUTING) |
| FR42 | Launch-blocker checklist tracking | `docs/launch-blockers.md` (M3 tracking artifact) |

**Non-Functional Requirements (17 NFRs → enforcement mechanism):**

| NFR | Description (abbrev) | Enforcement |
|---|---|---|
| NFR1 | Monotonic-ns + NTP discipline | `time_discipline.py` + `infra/systemd/chrony.conf.d/` + manifest |
| NFR2 | Asyncio sub-ms resolution | `collection/connection_manager.py` (asyncio.TaskGroup); empirically validated |
| NFR3 | ≤60s cold-start | `__main__.py` startup path; integration test gates |
| NFR4 | ≤30 min self-test | `selftest/reproducibility.py` + `ci/github-actions/selftest.yml` timeout |
| NFR5 | ≤24h snowball convergence | `discovery/snowball.py` (max-rounds termination) |
| NFR6 | ≥95% uptime / 30-day rolling | `collection/connection_lifecycle.py` + Grafana (M2+) |
| NFR7 | Reconnection backoff with documented params | `collection/reconnect.py` |
| NFR8 | Tor 3-retry / 300s budget | `collection/transport/tor_socks5.py` |
| NFR9 | Planned-downtime accounting | `collection/connection_lifecycle.py` |
| NFR10 | 100–500 concurrent sockets, native v6, no tunnels | `collection/connection_manager.py` + `infra/terraform/network.tf` + `ci/scripts/verify_dual_stack.sh` |
| NFR11 | ~6 GB/year compressed | `publication/parquet_snapshot.py` (Zstd config) |
| NFR12 | ≤$500/year cost | `infra/terraform/` (t4g.small + gp3) |
| NFR13 | ≤512 MB resident | `collection/connection_manager.py` (memory profiling test) |
| NFR14 | SQLite M0–M1 → TimescaleDB by M2 | `storage/sqlite_backend.py` → `storage/timescaledb_backend.py` |
| NFR15 | Bit-identical contract | `selftest/reproducibility.py` + `selftest/tolerance.py` |
| NFR16 | Forward-compat-only schema | `migrations/` + `storage/migrations.py` |
| NFR17 | PR-review SLA | `CONTRIBUTING.md` (process; not enforced in code) |

**Cross-Cutting Concerns (10 from §Project Context Analysis):**

| Concern | Where it lives | Enforcement mechanism |
|---|---|---|
| Time discipline | `time_discipline.py` | mypy + Pattern §Time format |
| Append-only raw tier | Storage Protocol class shape | mypy + Pattern §Storage write discipline |
| Phrasing-bank audit | `audit/` + CI gate | `ci/github-actions/audit.yml` release-blocker |
| Bilingual parity | All `*.md`/`*.es.md` pairs + CI gate | `ci/github-actions/bilingual-staleness.yml` |
| Reproducibility contract | `selftest/` | `ci/github-actions/selftest.yml` release-blocker |
| Five-module spine | `src/electrum_sybil_detector/` layout | mypy Protocol-class types |
| Transport abstraction | `collection/transport/` | Pattern §Inter-module communication |
| Three-tier archival | `publication/` + `ci/github-actions/release.yml` | Idempotent helper scripts |
| Python→Rust M4 transition | Module isolation discipline (D4.9) | `tests/<module>/` runs in isolation |
| Solo-researcher SPOF | `docs/`, `selftest/`, `CONTRIBUTING.md` bilingual | Path-2 handoff: anyone can re-run self-test |

### Integration Points

**Internal communication (data flow within the daemon):**

```
                    ┌──────────────────────────────────────────────┐
                    │          External Inputs                     │
                    │  (Electrum servers, fork-observer,           │
                    │   bitcoin-data/stale-blocks)                 │
                    └──────────────────────────────────────────────┘
                                       ↓
       ┌──────────────────┐        ┌──────────────────┐
       │  Discovery       │ ─────→ │  Collection      │
       │  (FR1–FR4)       │        │  (FR5–FR10)      │
       └──────────────────┘        └──────────────────┘
                ↓                            ↓
                └────────────┬───────────────┘
                             ↓
                    ┌──────────────────┐
                    │  Storage         │  ← single canonical write surface
                    │  (FR11–FR16)     │     (raw tier, append-only)
                    └──────────────────┘
                             ↓
                    ┌──────────────────┐
                    │  Analysis        │  ← reads raw, writes derived
                    │  (FR17–FR24)     │     (with derived_run_id + code_hash)
                    └──────────────────┘
                             ↓
                    ┌──────────────────┐
                    │  Publication     │  ← reads derived,
                    │  (FR25–FR30)     │     emits Parquet + manifest.json
                    └──────────────────┘
                             ↓
       ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
       │  bitcoin-data    │  │  Zenodo          │  │  arXiv           │
       │  GitHub PR       │  │  DOI mint        │  │  preprint upload │
       └──────────────────┘  └──────────────────┘  └──────────────────┘
                             ↑
                    ┌──────────────────┐
                    │  Audit           │  ← gates all 3 archival tiers
                    │  (FR31–FR34)     │     (phrasing-bank + bilingual)
                    └──────────────────┘
                             ↑
                    ┌──────────────────┐
                    │  Selftest        │  ← gates Publication
                    │  (NFR15, FR27)   │     (bit-identical re-derivation)
                    └──────────────────┘
```

**Data flow invariants:**

1. Every write to a raw-tier table is preceded by a `connection_events` row for that connection (Pattern §Connection-event invariant).
2. Every read by Analysis goes through a `derived_run_id` filter (Pattern §`derived_run_id` discipline).
3. Every Parquet snapshot is accompanied by a `manifest.json` (FR26).
4. Every release of a snapshot+manifest is gated by:
   (a) self-test green (NFR15),
   (b) phrasing-bank audit green (FR31),
   (c) bilingual staleness check green (FR37/FR38).

### File Organization Patterns

**Configuration files** — co-located with the code that consumes them:
- Methodology thresholds → `src/electrum_sybil_detector/selftest/thresholds.yaml`
- Phrasing bank → `src/electrum_sybil_detector/audit/phrasing_bank/{en,es}.yaml`
- Calibration fixtures → `src/electrum_sybil_detector/harness/fixtures/<frontend>/`
- Tool config (ruff, mypy, pytest) → `pyproject.toml`
- Pre-commit → `.pre-commit-config.yaml`
- CI workflows → `ci/github-actions/`
- Infra → `infra/terraform/`

**Source organization** — one module per top-level concern (D4.1); one file per substantive concept; one Protocol class per module boundary. Submodules import from the parent module's `__init__.py` (which exports only the Protocol class), never from sibling submodules' implementation files.

**Test organization** — tests mirror the source tree (`tests/<module>/` mirrors `src/electrum_sybil_detector/<module>/`). Each source file has exactly one corresponding `test_*.py`. Cross-module integration tests go in `tests/integration/`.

**Asset organization** — schema documentation in `docs/schema/` (JSON Schema as language-neutral source of truth; EN/ES `.md` files as human-facing mirrors). No binary assets at M0–M3.

### Development Workflow Integration

**Development environment** — `uv sync` reads `pyproject.toml` + `uv.lock` and provisions a venv with all deps. `uv run python -m electrum_sybil_detector` runs the daemon. CI uses the same `uv` flow on each Python version in the matrix (D7.2).

**Build process** — `hatchling` builds source + wheel distributions from `pyproject.toml` PEP-621 metadata (D7.1). At M0 there is no distribution build; the daemon runs from source. M1+ builds wheels for GitHub Actions CI cache and Path-2 reproducer convenience.

**Deployment** — `infra/terraform/` provisions AWS EC2 t4g.small + VPC IPv6 + EBS gp3 (D6.1, NFR10). `infra/systemd/` deploys the daemon as a systemd unit on the instance (D6.3). Deploy is `terraform apply && scp src/ → ec2 && systemctl restart electrum-monitor.service`. No container layer at M0–M2 (D6.3).

## Architecture Validation Results

### Coherence Validation

**Decision compatibility audit:**

| Check | Result | Notes |
|---|---|---|
| Python 3.11 floor compatible with all chosen libs | ✓ Pass | pandas 3.0 needs ≥3.11; pyarrow 24, scipy, sklearn all support 3.11+ |
| `uv` (D7.2) compatible with `hatchling` (D7.1) | ✓ Pass | uv supports any PEP-517 build backend |
| TimescaleDB 2.26 supports PostgreSQL 18 | ✓ Pass | `postgresql-18-timescaledb` 2.26.3+dfsg-1 in Debian sid; ARM64 builds available via Tiger's packagecloud apt repo |
| `asyncio.TaskGroup` (D1.3) composes with connection-pool design (D3.1) | ✓ Pass | TaskGroup is the canonical structured-concurrency primitive for one-task-per-server |
| SQLite WAL (D2.2) works with stdlib `sqlite3` | ✓ Pass | `PRAGMA journal_mode=WAL` |
| BLAKE2b (D2.6) is stdlib-available at M0 | ✓ Pass | `hashlib.blake2b()` in stdlib since Python 3.6 |
| No-Docker (D6.3) composes with AWS EC2 + Debian 13 ARM64 (D6.1) | ✓ Pass | Direct install on Debian AMI; systemd unit |
| `chrony` works against AWS Time Sync Service | ✓ Pass | AWS exposes stratum-1 time at `169.254.169.123`; recommended pattern |
| AWS native IPv6 outbound (NFR10) supported on t4g.small | ✓ Pass | All current-gen instance types support IPv6; constraint is VPC + subnet config (already captured in D6.1) |
| Storage Protocol prevents UPDATE/DELETE on raw tier | ✓ Pass | Protocol surface only exposes INSERT-style methods; mypy enforces |
| Python→Rust M4 transition supported by module isolation (D4.9) | ✓ Pass | Each `tests/<module>/` runs in isolation; modules port one-at-a-time |

**Pattern consistency audit:**

| Check | Result | Notes |
|---|---|---|
| `monotonic_ns` + `wall_clock_ns` paired everywhere a time is stored | ✓ Pass | Pattern §Time format + D2.7 + Storage Protocol shape all enforce |
| All raw-tier writes go through Storage Protocol | ✓ Pass | D4.3 + Pattern §Inter-module communication |
| `derived_run_id` + `code_hash` stamped on every derived row | ✓ Pass | D4.6 + Pattern §`derived_run_id` discipline |
| Phrasing-bank applied to all public-facing strings | ✓ Pass | FR31 + D6.9 + Pattern §Output Guardrails enforcement |
| Bilingual EN+ES synchronization enforced | ✓ Pass | D6.8 + FR37/FR38 + Pattern §Bilingual document update workflow |
| Forward-compat-only schema migrations | ✓ Pass | D2.8 + NFR16 + Pattern §Migration application discipline |

**Structure alignment audit:**

| Check | Result | Notes |
|---|---|---|
| Five-module spine matches PRD §Tool Specification > Module structure | ✓ Pass | Discovery, Collection, Storage, Analysis, Publication — exactly mirrored |
| Three supporting modules cover FR31/FR24/NFR15 | ✓ Pass | audit/, harness/, selftest/ |
| Tests mirror src tree (D4.9) | ✓ Pass | `tests/<module>/` = `src/electrum_sybil_detector/<module>/` 1:1 |
| Migration directory split SQLite + TimescaleDB | ✓ Pass | `migrations/sqlite/` + `migrations/timescaledb/` |
| Infra split Terraform + systemd | ✓ Pass | `infra/terraform/` + `infra/systemd/` |

**Coherence verdict:** ✓ All decisions compose without contradictions; patterns support decisions; structure supports patterns.

### Requirements Coverage Validation

**Functional Requirements (42/42 covered):** Cross-reference complete in §Project Structure & Boundaries > Requirements to Structure Mapping. Every FR has a designated file/module.

**Non-Functional Requirements (17/17 covered):** Cross-reference complete in same section. Every NFR has a designated enforcement mechanism. Note: NFR17 (PR-review SLA) is process-only, not code-enforced — documented in `CONTRIBUTING.md`.

**Forced top-level PRD sections (5/5 covered):**

| Section | Coverage |
|---|---|
| `dataset_requirements` | D2.1–D2.9, FR11–FR16, FR25–FR30, `storage/`, `publication/parquet_snapshot.py` |
| `publication_requirements` | FR25–FR30, D6.7, `publication/`, `docs/methodology.md` [M3], `docs/threat-model.md` [M3] |
| `measurement_validity` | D2.7 time discipline, D5.5 baseline, NFR1, `time_discipline.py`, `selftest/`, manifest |
| `output_guardrails` | D6.9, FR31–FR34, `audit/`, phrasing-bank CI gate |
| `bilingual_parity` | D6.8, FR35–FR38, all `*.es.md` mirrors, bilingual-staleness CI gate |

**M0 architectural guardrails (4/4 enforced):**

| Guardrail | Mechanism |
|---|---|
| `timestamp_precision_monotonic_ns` | `time_discipline.py` + D2.7 + NFR1 |
| `raw_event_schema_append_only` | Storage Protocol shape + D4.5 + FR11 |
| `connection_metadata_captured_at_connect` | `collection/connection_lifecycle.py` + D3.3 + FR8 |
| `one_canonical_ntp_time_source_per_window` | `infra/systemd/chrony.conf.d/` + manifest + D6.4 + FR13 |

**Launch-blockers (26/26 have homes in the structure):** All 26 LBs map to either a code location, a process step (`docs/launch-blockers.md` tracking artifact), or a CI gate. Critical-path cluster (LB#11, #2, #8, #1, #9) all addressed.

**Cross-cutting concerns (10/10 covered):** Cross-reference complete in §Project Structure & Boundaries > Cross-Cutting Concerns table.

**Coverage verdict:** ✓ Complete coverage. No FR, NFR, forced section, M0 guardrail, or launch-blocker is unaddressed.

### Implementation Readiness Validation

**Decision completeness:**

- ✓ All 7 decision categories have ratified decisions (D1.1–D7.7)
- ✓ All technology versions web-verified 2026-04-26
- ✓ All deferred decisions have explicit "when to revisit" triggers
- ✓ Cross-component cascading implications enumerated

**Pattern completeness:**

- ✓ Naming, structure, format, communication, process patterns all defined
- ✓ 10 mandatory patterns enumerated under "All AI Agents MUST"
- ✓ Pattern enforcement mechanisms specified (compile / lint / pre-commit / CI / code-review)
- ✓ Concrete examples provided for load-bearing patterns (Storage write, time discipline, phrasing-bank)
- ✓ Anti-pattern examples provided

**Structure completeness:**

- ✓ Complete project tree with milestone tags ([M0]/[M1]/[M2]/[M3]/[M4])
- ✓ Every FR mapped to a specific file
- ✓ Every NFR mapped to an enforcement mechanism
- ✓ External integration points enumerated with ownership
- ✓ Data-flow diagram with invariants documented

**Implementation-readiness verdict:** ✓ Ready. AI agents can implement consistently from this document.

### Gap Analysis

I'm flagging the following honestly. None block M0 implementation; all are forward-looking verification tasks or known-unknowns that surface in later milestones.

**Critical gaps:** 0 (none block M0 implementation start).

**Important gaps (require follow-up before specific milestones):**

| ID | Gap | Required by | Resolution path |
|---|---|---|---|
| G1 | M0 self-test fixture is not the [M3] frozen `m3_dataset_window/` fixture | M0 implementation start | Add `selftest/fixtures/m0_smoke/` — synthetic SQLite rows for module-level determinism testing. Self-test at M0 verifies hash stability and append-only invariant, not full pipeline. |
| G2 | t4g.small (2 GB RAM) may not fit daemon (≤512 MB, NFR13) **plus** TimescaleDB+PG18 at M2+ | M2 entry | Plan: at M2 entry, profile resident memory of TimescaleDB workload; if >1.4 GB, upgrade to **t4g.medium (4 GB)** at ~$30/month — still ≤$500/year envelope. Document in `infra/terraform/compute.tf` as a TODO with budget evaluation. |
| G3 | Python's `socket.getaddrinfo` default may not honor "v6 first, record both attempts" (D3.7) | M0 implementation of `collection/connection_manager.py` | Implementation note: explicitly call `getaddrinfo` with `family=AF_INET6` and `family=AF_INET` separately; record both attempt outcomes in `connection_events`. Don't rely on happy-eyeballs default behavior. |
| G4 | `fork-observer` (b10c) Electrum-data HTTP/JSON surface unverified | M3 (LB#8) | LB#8 already tracks this. If surface doesn't exist, fall back to direct `bitcoin-data/stale-blocks` consumption (already implemented in `analysis/fork_race_events.py`); fork-observer integration becomes nice-to-have, not load-bearing. |
| G5 | Manifest format includes `code_hash` but how it's computed isn't pinned (file content hash? git commit hash? git-archive hash?) | M3 (manifest.py) | Pin in step-08 or first-implementation-story refinement. Recommend: `git archive HEAD \| sha256sum` for reproducibility (deterministic, doesn't depend on dirty working tree). |
| G6 | Bilingual `docs/deploy-aws.md` + `docs/deploy-aws.es.md` are M0 but require AWS-specific Spanish technical translation expertise | M0 | Process gap, not architecture gap. Track in `CONTRIBUTING.md` as "translation-pending" if user can't write the Spanish version directly at M0. |
| G7 | TimescaleDB 2.26 ARM64 packages on Debian 13 require Tiger Data's apt repo, not stock Debian stable | M2 entry | `infra/systemd/` deploy step adds Tiger Data's apt repo before installing PG18. Document in `docs/deploy-aws.md`. |

**Nice-to-have gaps (refinements that would help but don't gate any milestone):**

| ID | Gap | Suggestion |
|---|---|---|
| N1 | No formal ADR (Architecture Decision Record) directory | Could add `docs/adrs/` with one ADR per major decision; the Step-04 decision tables already capture this content but ADRs are the conventional format |
| N2 | No testbed orchestration definition for FR24 5-frontend matrix | `harness/multi_frontend_matrix.py` mentioned but the orchestration approach (docker-compose? bare metal? cloud-init?) is unspecified; revisit at M3 implementation story |
| N3 | M3 paper draft scaffold (`docs/methodology.md` etc.) doesn't have a content template | LaTeX vs Markdown vs Asciidoc choice deferred; recommend Markdown at first then Pandoc-convert to LaTeX for FC submission |
| N4 | Migration files for Storage have rollback strategy unspecified | Forward-only is the policy (D2.8, NFR16); rollback is not supported by design. Worth making this explicit in `migrations/README.md` |

### Validation Issues Addressed

**Resolved during validation:**

- TimescaleDB 2.26 ARM64 PG18 availability — verified via packagecloud + Debian sid (G7 documents the apt-repo step)
- M0 self-test fixture ambiguity — G1 documents the M0-smoke fixture path
- Memory budget at M2 — G2 documents the t4g.medium upgrade path
- happy-eyeballs concern — G3 documents the explicit-getaddrinfo pattern

**Deferred to first implementation stories or follow-up milestones:**

- G4 fork-observer surface (LB#8 milestone-bound)
- G5 code_hash computation method (M3 manifest implementation)
- G6 Spanish AWS deploy guide (M0 process)
- N1–N4 (refinements)

### Architecture Completeness Checklist

**✓ Requirements Analysis** (Step 2)
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed (medium with carve-outs)
- [x] Technical constraints identified (10 cross-cutting concerns)
- [x] All locked PRD/PRFAQ decisions enumerated

**✓ Starter Template Evaluation** (Step 3)
- [x] Primary technology domain identified (research_project / measurement-daemon)
- [x] 5 starter options evaluated and rejected with rationale
- [x] Bespoke skeleton chosen with M0 stdlib-only justification

**✓ Architectural Decisions** (Step 4)
- [x] 7 decision categories fully covered
- [x] All technology versions web-verified (Python, ruff, mypy, pytest, pyarrow, pandas, TimescaleDB)
- [x] Cascading implications enumerated
- [x] Implementation sequence defined (11 stories M0→M3)
- [x] Deferred decisions have explicit triggers

**✓ Implementation Patterns** (Step 5)
- [x] Naming conventions (Python + DB schema + CLI flags + config files)
- [x] Structure patterns (project layout + test organization + helpers policy)
- [x] Format patterns (time, JSON, manifest, logging, CLI output)
- [x] Communication patterns (Protocol classes, Storage discipline, derived_run_id, connection-event invariant)
- [x] Process patterns (error handling, async cancellation, reconnection backoff, determinism, migrations, bilingual workflow, Output Guardrails)
- [x] 10 mandatory rules + enforcement mechanisms
- [x] Good and anti-pattern examples

**✓ Project Structure** (Step 6)
- [x] Complete directory tree with milestone tags
- [x] Module surfaces and Protocol-class contracts
- [x] External integration points
- [x] FR-to-file mapping (42/42)
- [x] NFR-to-mechanism mapping (17/17)
- [x] Cross-cutting concerns mapping
- [x] Data-flow diagram with invariants

**✓ Validation** (Step 7 — this section)
- [x] Coherence audit: 11/11 checks pass
- [x] Coverage audit: 42 FRs + 17 NFRs + 5 forced sections + 4 M0 guardrails + 26 LBs + 10 cross-cutting concerns
- [x] Implementation readiness: decisions, patterns, structure all complete
- [x] Gap analysis: 0 critical, 7 important (all with resolution paths), 4 nice-to-have

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** HIGH

The architecture is grounded in:
- A 5/5-validated PRD with 42 FRs, 17 NFRs, and 26 launch-blockers
- A research-rigorous methodology spine (fork-race timing variance + Wasserstein) that's already empirically de-risked at Phase-1 closeout
- Web-verified 2026 technology versions with explicit floors and matrix
- Module isolation discipline that supports the M4 Python→Rust transition
- Reproducibility-contract gating release pipeline (NFR15)
- Output-Guardrails CI gate that automates the legal-framing carve-out

**Key strengths:**

1. **Methodology-first design.** The architecture is shaped by the discriminator (fork-race timing variance + Wasserstein over fee-rate CDFs), not retrofitted. Time discipline (D2.7), append-only raw tier (D4.5), and pre-committed thresholds (D5.4) are load-bearing for the science.
2. **Protocol-class boundaries.** The five-module spine + Storage-as-single-write-surface lets the SQLite→TimescaleDB migration (D2.3) and Python→Rust M4 transition happen as backend-swaps, not project rewrites.
3. **CI-gated release pipeline.** Self-test + phrasing-bank audit + bilingual-staleness check are all release-blocking. Reproducibility, legal framing, and bilingual parity become deterministic gates, not human discipline.
4. **Cost discipline.** Sub-$500/year envelope (NFR12) achievable on AWS t4g.small at M0–M1 and t4g.medium at M2+; no architectural decision violates this.
5. **Path-2 handoff posture.** Bilingual docs + idempotent flows + reproducibility self-test make the project anyone-can-re-run from day one.

**Areas for future enhancement** (G1–G7 + N1–N4 above; none gate M0).

### Implementation Handoff

**AI Agent Guidelines:**

- Follow the 10 mandatory rules under §Implementation Patterns > Enforcement Guidelines exactly.
- Storage is the single canonical write surface — never write SQL outside `storage/`.
- Time pair (`monotonic_ns` + `wall_clock_ns`) is non-negotiable on every probe row.
- `derived_run_id` + `code_hash` stamped on every derived-tier row.
- Phrasing-bank discipline applies to every public-facing string.
- Forward-compat-only migrations; never modify an applied migration.
- Pass ruff + mypy --strict + reproducibility self-test before merge.
- Update Spanish mirror within 14 days of any English `*.md` change.

**First Implementation Priority (Story 1):**

```bash
mkdir -p src/electrum_sybil_detector tests
touch src/electrum_sybil_detector/__init__.py
touch src/electrum_sybil_detector/__main__.py
touch src/electrum_sybil_detector/electrum_monitor.py  # M0 daemon stub
touch pyproject.toml                                   # PEP-621 metadata, Python ≥3.11
touch README.md README.es.md                           # bilingual EN + ES
touch LICENSE                                          # MIT
touch .gitignore .pre-commit-config.yaml CHANGELOG.md CONTRIBUTING.md CONTRIBUTING.es.md
git init
```

Then Story 2 (M0 daemon end-to-end against ≥3 hardcoded seeds) and Story 3 (reproducibility self-test scaffold).
