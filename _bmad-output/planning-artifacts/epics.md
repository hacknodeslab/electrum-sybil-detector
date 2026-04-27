---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
status: 'complete'
completedAt: '2026-04-27'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
workflowType: 'epics-and-stories'
project_name: 'electrum-sybil-detector'
user_name: 'Ifuensan'
date: '2026-04-26'
---

# electrum-sybil-detector - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for `electrum-sybil-detector`, decomposing the requirements from the PRD and the Architecture decisions into implementable stories. There is no UX document because this is a research-daemon archetype with no UI surface (architecture.md L141: "N/A (no UI). Output Guardrails phrasing-bank audit is the closest analogue").

The breakdown respects the locked PRD/Architecture sequencing: M0 → M1 → M2 → M3 launch → M4 (post-M3 Rust rewrite, out of scope here). Stories are organized by user value and milestone-gated capability arrival, not by horizontal layer.

## Requirements Inventory

### Functional Requirements

**Server Discovery (FR1–FR4)**

- **FR1:** The system can ingest seed-list server endpoints from configured sources (1209k.com / bitcoin-eye and Electrum wallet hardcoded defaults). *(Discovery module)*
- **FR2:** The system can expand the discovered server population via `server.peers.subscribe` snowball traversal until convergence. *(Discovery module)*
- **FR3:** The system can connect to `.onion` Electrum servers via SOCKS5 to a Tor circuit. *(Discovery module)*
- **FR4:** The system can record per-server discovery provenance (source, discovery timestamp, observed ASN, advertised `server.features` protocol-version range) so vantage diversity can be declared in the dataset manifest. *(Discovery module)*

**Probing & Data Collection (FR5–FR10)**

- **FR5:** The system can maintain persistent asyncio TCP/SSL connections to all discovered servers concurrently, with reconnection via exponential backoff on disconnect. *(Collection module)*
- **FR6:** The system can subscribe to `blockchain.headers.subscribe` on every connected server and capture each header notification with monotonic-ns and wall-clock timestamps. *(Collection module)*
- **FR7:** The system can periodically poll the stable Electrum RPC suite (`server.version`, `server.features`, `server.banner`, `server.donation_address`, `server.ping`, `blockchain.estimatefee(n)`, `blockchain.relayfee`, `mempool.get_fee_histogram`) at a configurable per-server cadence. *(Collection module)*
- **FR8:** The system can capture connection-event metadata (banner, TLS fingerprint, resolved IP, Tor circuit ID where applicable) at connect-time and never re-derive it later. *(Collection module)*
- **FR9:** The system can emit per-server uptime / downtime events with monotonic-ns timestamps so synchronized-downtime can be computed downstream. *(Collection module)*
- **FR10:** The system can throttle probe rates per server in conformance with the documented measurement-ethics rate-limiting policy. *(Collection module)*

**Storage & Schema Discipline (FR11–FR16)**

- **FR11:** The system can store all probe results as append-only raw-event rows with a `schema_version` tag; existing rows are immutable. *(Storage module)*
- **FR12:** The system can persist monotonic-ns and wall-clock timestamps per event in separate columns, never substituting one for the other in computed-delta metrics. *(Storage module)*
- **FR13:** The system can persist a per-collection-window NTP-discipline manifest (declared canonical NTP source, stratum, drift bound). *(Storage module)*
- **FR14:** The system can apply forward-compatible-only schema migrations: deprecated raw-tier columns are retained until at least the next MAJOR dataset version. *(Storage module)*
- **FR15:** The system can migrate raw + derived storage from SQLite (M0–M1) to TimescaleDB (M2+) without loss or schema divergence. *(Storage module)*
- **FR16:** The system can emit opaque server identifiers (BLAKE2b-256 hash of public-protocol fingerprints) in all published artifacts; the public-hostname mapping is not exported by default. *(Storage module)*

**Analysis & Signal Computation (FR17–FR24)**

- **FR17:** The system can ingest fork-race events from `bitcoin-data/stale-blocks` and identify the windowed time interval surrounding each event. *(Analysis module)*
- **FR18:** The system can compute per-pair pairwise-delta variance for `blockchain.headers.subscribe` notifications across all observed servers within a fork-race window. *(Analysis module)*
- **FR19:** The system can compute the 1-D Wasserstein distance (Earth Mover's Distance, `∫ |F_A(x) − F_B(x)| dx` over fee-rate CDFs) between `mempool.get_fee_histogram` outputs across all server pairs over a configurable window. The Wasserstein metric is canonical because cross-instance bit-identity is false by construction. *(Analysis module)*
- **FR20:** The system can detect synchronized downtime across server pairs and emit a synchronized-downtime signal. *(Analysis module)*
- **FR21:** The system can evaluate the pre-committed multi-signal threshold (≥2 backend-state signals + ≥1 frontend-config signal) per cluster candidate and classify each as *finding*, *candidate-for-reproduction*, or *below-threshold*. *(Analysis module)*
- **FR22:** The system can compute the known-independent baseline similarity distribution from a declared independent-server set, producing a noise-floor reference distribution. *(Analysis module)*
- **FR23:** The system can produce cluster assignments via DBSCAN (primary) or Ward hierarchical clustering (secondary, sensitivity analysis) on the weighted similarity matrix, with confidence intervals and multiple-testing correction (Benjamini–Hochberg FDR) applied. *(Analysis module)*
- **FR24:** The system can run the fee-histogram drift-magnitude calibration harness against a multi-frontend matrix sharing one Bitcoin Core (ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs) — measuring the Wasserstein-distance distribution under same-backend conditions to fix the cluster-membership threshold. Used both as one-time pre-launch calibration and as a recurring CI check monitoring methodology drift between releases. *(Analysis module / CI tooling)*

**Dataset Publication & Archival (FR25–FR30)**

- **FR25:** The system can generate a Parquet snapshot (pyarrow + Zstandard) of raw + derived tiers at a configurable cadence (default monthly) conformant with `bitcoin-data` repository conventions (directory layout, CHANGELOG, README). *(Publication module)*
- **FR26:** The system can produce a `manifest.json` per release declaring code hash, raw-input fingerprint, NTP stratum, collection-window boundaries, dataset version, release timestamp, and Zenodo DOI. *(Publication module)*
- **FR27:** The system can re-derive the derived tier from raw inputs + code hash and self-test for bit-identical reproduction (or per-column floating-point tolerance), failing the release on mismatch. *(Publication module)*
- **FR28:** A maintainer can open a `bitcoin-data` PR for a dataset release using the project's idempotent submission flow, including the upstream-mandated CHANGELOG entry and directory-layout conformance.
- **FR29:** A maintainer can mint a Zenodo DOI for a dataset release using the project's idempotent submission flow, with version cross-references preserved across releases.
- **FR30:** A maintainer can upload an arXiv preprint citing the Zenodo DOI in its abstract, with the LaTeX source archived alongside the submission.

**Output Guardrails & Disclosure (FR31–FR34)**

- **FR31:** A maintainer can run a phrasing-bank audit pass over CLI output, dataset README, paper abstract, contribution-channel documentation, and Spanish translations, with the audit functioning as a release gate (release blocked on audit completion).
- **FR32:** A flagged operator can locate a "What a flagged cluster does NOT mean" explanatory text within both the dataset README and the methodology paper, with explicit enumeration of plausible benign explanations.
- **FR33:** A flagged operator can open a disclosure issue via a dedicated template and receive maintainer acknowledgment within 48 hours; if classification is empirically wrong, the dataset is corrected in the next release with the correction documented in the CHANGELOG.
- **FR34:** A maintainer can append a flagged operator's contextual note (with operator consent) to the dataset's qualitative literature when the operator confirms the classification stands but provides benign-deployment context.

**Bilingual Parity (FR35–FR38)**

- **FR35:** A Spanish-speaking contributor can read README, first-run guide, dataset schema documentation, dataset README, contribution guide, and CLI `--help` text in Spanish at synchronized parity with English (no content present in one language and absent in the other).
- **FR36:** A Spanish-speaking contributor can open issues and pull requests in Spanish, and receive acknowledgment within the same 48-hour SLA and substantive review within the same 7-day SLA as English-language submissions.
- **FR37:** The system can flag bilingual documents updated in only one language for >14 days as "translation pending" via a CI check, visible publicly. *(CI tooling)*
- **FR38:** A maintainer can roll back a stale-translation document (>30 days divergent) to the prior synchronized version rather than ship divergent content.

**Operational Health & Stewardship (FR39–FR42)**

- **FR39:** A researcher operating the daemon can monitor collection uptime over rolling 30-day windows and is alerted when uptime falls below the 95% threshold. *(Collection module / operational tooling)*
- **FR40:** The system can enumerate collection gaps (intervals exceeding the per-window-declared N seconds without successful probes for a given server) so analyses spanning gap boundaries can declare the gap structure explicitly. *(Storage module)*
- **FR41:** A maintainer can track PR-review SLA conformance (48-hour acknowledgment, 7-day substantive review) and publicly tag PRs as `review-queued` during peak load; data-integrity PRs are exempt from triage and reviewed same-day.
- **FR42:** A maintainer can track launch-blocker checklist completion (the 26 items enumerated in §Project Scoping & Phased Development) and surface per-blocker status (cleared / pending / blocked).

### NonFunctional Requirements

**Performance (NFR1–NFR5)**

- **NFR1 — Timing precision at capture.** Monotonic-ns clock at probe receipt; wall-clock recorded separately and never used in computed-delta metrics. NTP-disciplined host with declared stratum per collection window.
- **NFR2 — Asyncio event-loop resolution.** Adequate for sub-millisecond event handling at full-network scale (~150–500 concurrent connections). Empirically validated 2026-04-25: p99 fanout-broadcast spread = 587 µs at N=100, 1.71 ms at N=200. Methodology signal floor (hundreds of ms inter-server in fork races) dominates collector jitter by orders of magnitude.
- **NFR3 — Cold-start time-to-first-probe.** ≤ 60 seconds from daemon launch to first successful `blockchain.headers.subscribe` notification ingestion at full-network scale.
- **NFR4 — CI reproducibility self-test runtime.** ≤ 30 minutes for the bit-identical re-derivation pass on the M3 dataset window. If exceeded, sample-based verification with documented sampling parameters is the fallback.
- **NFR5 — Snowball convergence bound.** ≤ 24 hours per discovery sweep, after which discovery is suspended and resumed in the next scheduled sweep. Prevents unbounded recursive expansion.

**Reliability (NFR6–NFR9)**

- **NFR6 — Collection uptime.** ≥ 95% over any rolling 30-day window, measured both per server and at fleet aggregate. Uptime < 95% for 30 days triggers the IQ5 triage protocol.
- **NFR7 — Reconnection discipline.** Per-server reconnection on disconnect via exponential backoff with documented base / cap / jitter parameters (base=2s, cap=300s, jitter=±25% per D3.4); reconnection events captured as connection-event rows.
- **NFR8 — Tor circuit-failure retry budget.** ≤ 3 retries per probe over ≤ 300 seconds, then mark probe-failed and continue collection without poisoning the longitudinal record.
- **NFR9 — Planned-downtime accounting.** Planned downtime ≤ 24 h cumulative per rolling 30-day period is excluded from the NFR6 uptime calculation; planned downtime > 24 h cumulative counts against uptime.

**Scalability & Cost (NFR10–NFR14)**

- **NFR10 — Concurrent-connection scale.** 100–500 heterogeneous TCP / SSL sockets sustained at full-network scale. **Native IPv6 outbound required** (Hetzner default; AWS requires explicit VPC + subnet IPv6 CIDR + ENI assignment + egress route via IGW or egress-only IGW). IPv6 tunnels (Hurricane Electric, ZeroTier-routed exits) **not acceptable** for the timing methodology.
- **NFR11 — Dataset-volume budget.** ~ 6 GB / year compressed at full-network scale. Compression algorithm and ratio documented per release manifest.
- **NFR12 — Operational cost envelope.** ≤ $500 / year total (VPS + storage + redundancy + Zenodo deposit + arXiv hosting).
- **NFR13 — Memory footprint envelope.** ≤ 512 MB resident at the daemon process at full-network scale.
- **NFR14 — Storage migration timeline.** SQLite at M0–M1; TimescaleDB by M2, OR explicit demonstration that SQLite snapshot is sufficient for the M3 dataset window.

**Reproducibility & Determinism (NFR15–NFR17)**

- **NFR15 — Bit-identical contract.** Code hash + raw-input fingerprint → bit-identical derived dataset, OR documented per-column floating-point tolerance with bounds. Self-test ships with every dataset release; reviewers can re-run independently.
- **NFR16 — Schema discipline.** Forward-compatible-only migrations on the raw tier; deprecated columns retained until at least the next MAJOR dataset version.
- **NFR17 — PR-review SLA.** 48-hour acknowledgment, 7-day substantive review for non-data-integrity PRs; same-day review for data-integrity PRs.

### Additional Requirements

These are technical / infrastructure / process requirements derived from the Architecture decisions (D1–D7), the project structure, and the M0 architectural guardrails. They are not FRs/NFRs but they materially affect epic and story design.

**Starter Template — bespoke skeleton (CRITICAL — Epic 1 Story 1 implication)**

- **AR1 — No third-party starter template.** Architecture explicitly rejects all considered scaffolds (cookiecutter-pypackage, cookiecutter-data-science, poetry, oclif, Next.js, etc.) due to (a) M0 stdlib-only constraint, (b) `fork-observer` reuse posture, (c) reproducibility-driven acceptance criteria. The first implementation story scaffolds the M0 stdlib-only daemon directly per the bespoke layout specified in architecture.md L120–L131.

**Language, Runtime & Dependency Posture (D1.x, D7.x)**

- **AR2 — Python ≥ 3.11 floor** (TaskGroup, `time.monotonic_ns`, pandas 3.0 / pyarrow 24 / scipy / sklearn baselines all assume 3.11+); CI matrix = 3.11, 3.12, 3.13, 3.14.
- **AR3 — Structured concurrency only** on production paths (asyncio.TaskGroup; no bare `gather`); methodology integrity depends on never silently dropping a probe.
- **AR4 — `mypy 1.20+ --strict`** in CI; `# type: ignore` requires inline reason.
- **AR5 — M0 stdlib-only** (no pip deps); analytical deps (numpy/scipy/sklearn/pandas/pyarrow) enter at M1+ (earned-dependency principle).
- **AR6 — Dev tooling stack:** `uv` (Astral) for venv + lockfile + Python version mgmt; `ruff 0.15.12+` (lint+format with E,F,W,I,N,UP,B,A,C4,SIM,ARG,PL); `pytest 8.4+` + `pytest-asyncio 1.3.x` (avoid 1.4.0a1 prerelease); `pre-commit 4.x` with hooks for ruff, mypy, EOF-fixer, conventional-commits; `hatchling` build backend at M1+.

**Module Boundaries & Inter-Module Surfaces (D4.x)**

- **AR7 — Five-module production spine + three supporting modules:** `discovery/`, `collection/`, `storage/`, `analysis/`, `publication/` + supporting `audit/` (Output Guardrails), `selftest/` (reproducibility CI gate), `harness/` (fee-histogram drift testbed).
- **AR8 — Inter-module surface = Python `Protocol` classes** (PEP 544 structural typing) at each module's package root; no DI framework, no message bus, no event emitter.
- **AR9 — Storage as the single integration point** — only Storage module owns mutating database operations. Backend swap (SQLite → TimescaleDB) must not require changes outside `storage/`.
- **AR10 — Transport plugin boundary** — `Transport` Protocol class in `collection/transport/__init__.py`; new transports (Tor at M2) drop in as new files implementing the Protocol; `connection_manager.py` does not change.
- **AR11 — Project exception hierarchy** rooted at `ElectrumSybilError` in `src/electrum_sybil_detector/exceptions.py`. Never `except Exception:` without re-raise/log; never `except: pass`.

**Time, Hashing & Determinism Discipline**

- **AR12 — Time pair invariant.** Every probe row carries `monotonic_ns` (BIGINT, from `time.monotonic_ns()`) AND `wall_clock_ns` (BIGINT, from `time.time_ns()`); the only legal arithmetic on time columns is `BIGINT - BIGINT` on `monotonic_ns`.
- **AR13 — BLAKE2b-256 stdlib hashing** for opaque server identifiers, code-hash, raw-input fingerprint, derived_run_id (keeps M0 stdlib-only intact).
- **AR14 — Determinism contract** — pinned random seeds (`numpy.random.default_rng(seed=0)` for repeatability tests; explicit per-run seeds for production logged in manifest); sorted-key JSON serialization for hashes; sorted iteration over sets/dicts that feed hashes.
- **AR15 — `derived_run_id` discipline** — generated as `BLAKE2b-256(code_hash || raw_input_fingerprint || run_timestamp_ns)`; stamped on every derived-tier row; querying derived tier without filtering on `derived_run_id` is a code-review violation.

**Storage Backend Specifics (D2.x)**

- **AR16 — SQLite 3 with WAL mode** at M0–M1; one file per collection window; numbered idempotent forward-only DDL scripts in `migrations/sqlite/`.
- **AR17 — TimescaleDB 2.26+ on PostgreSQL 18** at M2+; `psycopg 3.2+` + plain SQL migrations (no Alembic).
- **AR18 — Parquet via pyarrow 24.x with Zstandard compression** for snapshot format (matches `bitcoin-data` conventions, hits ~6 GB/year NFR11 target).
- **AR19 — Retention policy** — raw events indefinitely for block notifications + connection events + metadata; **90-day raw retention then downsample** for fee histograms and pings.

**Connection Layer Specifics (D3.x)**

- **AR20 — Opportunistic TLS** at M0; record SHA-256 cert fingerprint at connect-time (self-signed certs common in Electrum ecosystem; pinning would block valid honest servers).
- **AR21 — Per-server token bucket rate limit**, default ≤1 active probe/sec; subscriptions are passive listeners (no rate cost).
- **AR22 — IPv6 stance: dual-stack outbound, `happy-eyeballs` disabled** — always try v6 first when AAAA exists; record both attempt outcomes. (Phase-1 V3 evidence: ~28% of network is IPv6-only.)

**Analysis Pipeline Specifics (D5.x)**

- **AR23 — Wasserstein computation = `scipy.stats.wasserstein_distance` (1-D)** — canonical metric must be the canonical library, not a re-implementation.
- **AR24 — Multi-signal threshold engine** — thresholds in `selftest/thresholds.yaml`, **frozen pre-M3** to prevent post-hoc tuning. No environment variables for thresholds.
- **AR25 — Statistical rigor stack** — Benjamini–Hochberg FDR correction; bootstrap CIs on every cluster claim; power analysis disclosed for the M3 dataset window.
- **AR26 — Pure Python analysis at M3** (numpy/scipy/sklearn/pandas/pyarrow); no Cython, no Numba (reproducibility > raw speed at M3 scale; harness fits NFR4 30-min CI budget).
- **AR27 — `fork-observer` integration via read-only consumption of HTTP/JSON output** at M0–M3; code-sharing reconsidered only at M4.

**Infrastructure & Deployment (D6.x)**

- **AR28 — AWS deploy environment:** EC2 t4g.small (ARM Graviton, 2 vCPU, 2 GB) in us-east-1; gp3 EBS 50 GB; Debian 13 ARM64; chosen for direct kernel access for `chrony` NTP and monotonic-ns timing.
- **AR29 — VPC with explicit IPv6 CIDR + subnet IPv6 CIDR + egress-only IGW + standard IGW**, Terraform-codified (no ClickOps). Verified via collector reaching ≥3 IPv6-only Electrum servers (LB#26).
- **AR30 — `chrony` NTP** with declared canonical source per collection window logged in dataset manifest (better accuracy reporting than ntpd).
- **AR31 — systemd unit + structured-JSON logs to journal**; **no Docker at M0–M1** (Docker adds isolation layer that complicates monotonic-ns guarantees; Docker exists for user-facing first-run convenience only at LB#5).
- **AR32 — GitHub Actions CI** matrix Python 3.11/3.12/3.13/3.14; reproducibility self-test as CI job within NFR4 ≤30-min budget.
- **AR33 — Three-tier archival pipeline = idempotent helper scripts** invoked from CI on tag push: (a) `bitcoin-data` PR via `gh` CLI, (b) Zenodo DOI mint via Zenodo REST API, (c) arXiv upload manual at M3 (no API for academic preprints).
- **AR34 — Bilingual CI staleness as GitHub Action** diffing `*.md` vs `*.es.md` mtimes; >14d warning, >30d release-blocking gate.
- **AR35 — Output Guardrails phrasing-bank audit as CI job** running regex rule-engine across CLI strings, dataset README, paper abstract, Spanish mirrors; release-blocking gate.
- **AR36 — Monitoring at M2+** = Grafana + Prometheus + node_exporter; M0–M1 = structured-JSON log lines parsed via `journalctl --output=json`.

**Pre-Launch Calibration & Validation Harness (D5.10, LB#2)**

- **AR37 — Fee-histogram drift calibration harness** runs both as **one-shot pre-launch** (against the 5-frontend matrix: ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs vs. 1 Bitcoin Core) **and as a recurring CI check** on the same code path, fixing the cluster-membership Wasserstein threshold and monitoring methodology drift between releases.

**Bilingual Parity Operationalization**

- **AR38 — Bilingual mirror discipline** — English `*.md` is authoritative; Spanish `*.es.md` is the mirror. CI bot opens a `translation-pending` issue when EN is updated; 14d soft SLA (warning); 30d hard SLA (release-blocking) until ES updated OR EN rolled back.
- **AR39 — Bilingual issue/PR templates** in `.github/ISSUE_TEMPLATE/` (EN + ES variants for bug reports, flagged-operator disclosure); both languages accepted on identical SLAs.

**Phased Milestone Gating**

- **AR40 — M0 → M1 gate.** Asyncio collection running 24/7 against 10–20 seed servers; SQLite schema covering all data points; M0 architectural guardrails enforced; reproducibility self-test green.
- **AR41 — M1 → M2 gate.** Snowball expansion complete; clearnet ~150–500 servers reached (Phase-1 lower bound: 344 dual-stack-reachable mainnet servers); IPv6 reachability verified end-to-end; SQLite scale stress-tested; SQLite → TimescaleDB migration plan in place.
- **AR42 — M2 → M3 gate.** Tor coverage operational; TimescaleDB migration complete (or SQLite snapshot demonstrably sufficient); 26-item launch-blocker checklist actively cleared; pre-launch empirical premise tests (LB#1, LB#2) green.
- **AR43 — M3 launch gate.** All five forced PRD sections satisfied and audited; tool + dataset + paper bit-identical-reproducible; three-tier archival operational (`bitcoin-data` PR accepted; Zenodo DOI cited in paper abstract; arXiv preprint timestamped).

**Launch-Blocker Checklist (operational tracking)**

- **AR44 — 26-item launch-blocker checklist** tracked in repo (status: cleared / pending / blocked), with priority-1 cluster #11 (b10c socialization) → #2 (fee-histogram) → #8 (fork-observer) → #1 (stale-blocks cadence) → #9 (methodology-ancestor citations).

### UX Design Requirements

_Not applicable._ This is a research-daemon project with no UI surface (architecture.md L141: "N/A (no UI). Output Guardrails phrasing-bank audit is the closest analogue and is decided in step-04"). CLI ergonomics are explicitly secondary per PRD §Tool Specification (L450–L452): "CLI ergonomics, polished `--help` text, packaging quality, onboarding flow, and runtime efficiency are explicitly secondary." Phrasing-bank discipline (FR31) and bilingual `--help` (FR35) are the closest user-experience analogues and are captured under Functional Requirements above.

### FR Coverage Map

Every FR maps to exactly one epic. 42 / 42 FRs covered, no duplicates, no orphans.

| FR | Epic | Capability |
|---|---|---|
| FR1 | Epic 1 | Seed-list ingestion (M0) |
| FR2 | Epic 2 | Snowball expansion (M1) |
| FR3 | Epic 2 | Tor SOCKS5 onion connectivity (M2) |
| FR4 | Epic 2 | Per-server discovery provenance |
| FR5 | Epic 1 | Persistent asyncio TCP/SSL pool |
| FR6 | Epic 1 | `headers.subscribe` capture with monotonic-ns |
| FR7 | Epic 2 | Periodic stable-RPC polling at full scale |
| FR8 | Epic 1 | Connection-event metadata at connect-time |
| FR9 | Epic 1 | Uptime/downtime event emission |
| FR10 | Epic 1 | Per-server probe rate throttling |
| FR11 | Epic 1 | Append-only raw rows + schema_version |
| FR12 | Epic 1 | Time-pair invariant (monotonic_ns + wall_clock_ns) |
| FR13 | Epic 1 | Per-window NTP-discipline manifest |
| FR14 | Epic 1 | Forward-compat-only schema migrations |
| FR15 | Epic 2 | SQLite → TimescaleDB migration |
| FR16 | Epic 1 | BLAKE2b-256 opaque server identifiers |
| FR17 | Epic 3 | `bitcoin-data/stale-blocks` fork-race ingest |
| FR18 | Epic 3 | Per-pair pairwise-delta variance |
| FR19 | Epic 3 | 1-D Wasserstein over fee-rate CDFs |
| FR20 | Epic 3 | Synchronized-downtime detection |
| FR21 | Epic 3 | Multi-signal threshold engine |
| FR22 | Epic 3 | Baseline noise-floor distribution |
| FR23 | Epic 3 | DBSCAN + Ward clustering with FDR + CIs |
| FR24 | Epic 3 | Fee-histogram 5-frontend calibration harness |
| FR25 | Epic 4 | Parquet+Zstd snapshot per `bitcoin-data` conventions |
| FR26 | Epic 4 | `manifest.json` per release |
| FR27 | Epic 4 | Bit-identical re-derivation ship gate |
| FR28 | Epic 4 | Idempotent `bitcoin-data` PR flow |
| FR29 | Epic 4 | Idempotent Zenodo DOI minting |
| FR30 | Epic 4 | arXiv preprint upload citing DOI |
| FR31 | Epic 5 | Phrasing-bank audit as release gate |
| FR32 | Epic 5 | "What a flagged cluster does NOT mean" text |
| FR33 | Epic 5 | Flagged-operator disclosure issue + 48h SLA |
| FR34 | Epic 5 | Operator contextual note appended with consent |
| FR35 | Epic 6 | Bilingual README/guide/schema/CLI parity |
| FR36 | Epic 6 | Spanish-language issues/PRs at same SLA |
| FR37 | Epic 6 | Bilingual staleness CI flag (>14 days) |
| FR38 | Epic 6 | Stale-translation rollback (>30 days) |
| FR39 | Epic 7 | Rolling 30-day uptime monitoring + alerting |
| FR40 | Epic 2 | Collection-gap enumeration |
| FR41 | Epic 7 | PR-review SLA tracking + `review-queued` tagging |
| FR42 | Epic 7 | 26-item launch-blocker checklist tracking |

## Epic List

### Epic 1: Reproducible Measurement Foundation on Production Host (M0)

Ifuensan can run a stdlib-only Electrum collection daemon 24/7 against 10–20 seed servers on a production AWS EC2 t4g.small host with dual-stack IPv6 outbound, `chrony` NTP, systemd supervision, monotonic-ns timestamping, append-only SQLite storage, and a green reproducibility self-test in GitHub Actions CI. The bespoke project skeleton (no third-party starter — AR1), exception hierarchy, structured-JSON logging, bilingual README placeholders, MIT LICENSE, and dev-tooling stack (uv + ruff + mypy --strict + pytest + pre-commit) all ship with this epic. M0 architectural guardrails are enforced; the project is ready to expand to snowball discovery (M0→M1 gate green).

**FRs covered:** FR1, FR5, FR6, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR16
**Key NFRs:** NFR1, NFR7, NFR10 (deploy IPv6), NFR12, NFR13, NFR15 (self-test scaffold), NFR16
**Milestone arrival:** M0 entry → M0→M1 gate
**Standalone value:** Yes — produces collected data, has working reproducibility self-test, runs on production host. Useful as a small-fleet collector even without snowball expansion.

### Epic 2: Full-Network Discovery & Sustained Collection (M1 → M2)

The daemon discovers the full clearnet Electrum population (≥150–500 servers; Phase-1 V3 lower bound 344) via snowball expansion from seeds + `server.peers.subscribe`, sustains ≥95% uptime across all of them with per-server rate limiting, ASN-diverse provenance, gap enumeration, and the full periodic-probe RPC suite. Tor `.onion` coverage joins via SOCKS5 transport plug-in at M2; storage migrates SQLite → TimescaleDB at production scale.

**FRs covered:** FR2, FR3, FR4, FR7, FR15, FR40
**Key NFRs:** NFR2, NFR3, NFR5, NFR6, NFR8, NFR10 (full scale), NFR11, NFR14
**Milestone arrival:** M1 entry → M2→M3 gate
**Standalone value:** Yes — provides full-network longitudinal coverage. Doesn't require Analysis (Epic 3) to function as a data collector.

### Epic 3: Methodology Signal Computation & Cluster Findings (M3 entry)

Lukas can run the analysis pipeline against an M0/M1/M2 dataset snapshot and produce statistically-rigorous cluster findings: fee-histogram drift calibration via the 5-frontend harness (LB#2 priority-1) → fork-race pairwise-delta variance → 1-D Wasserstein over fee-rate CDFs → synchronized-downtime overlap → pre-committed multi-signal threshold evaluation → DBSCAN/Ward clustering with Benjamini–Hochberg FDR + bootstrap CIs. Output: cluster assignments classified as finding / candidate-for-reproduction / below-threshold.

**FRs covered:** FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24
**Key NFRs:** NFR4 (CI ≤30 min budget), NFR15 (determinism contract honored across analysis)
**Milestone arrival:** M2→M3 gate → M3 launch
**Standalone value:** Yes — produces analyzable findings even if Publication (Epic 4) hasn't shipped yet. Calibration harness (FR24) is the first story because it sets the FR21 threshold.

### Epic 4: Citable Dataset Bundle Publication (M3 launch)

Lukas / Sarah can cite the dataset by Zenodo DOI from the arXiv preprint; the `bitcoin-data` PR is accepted; the M3 release ships as a Parquet snapshot + `manifest.json` + LaTeX source + bit-identical re-derivation self-test that any reviewer can re-run independently. Three-tier archival operational; release pipeline gated on reproducibility self-test + phrasing-bank audit + bilingual mirror parity.

**FRs covered:** FR25, FR26, FR27, FR28, FR29, FR30
**Key NFRs:** NFR4, NFR11 (volume budget), NFR12 (cost), NFR15 (bit-identical contract as ship gate), NFR16
**Milestone arrival:** M3 entry → M3 launch
**Standalone value:** Yes — citable bundle is an end-product. Doesn't require subsequent epics to function.

### Epic 5: Output Guardrails & Flagged-Operator Disclosure (M0 audit gate → M3 disclosure flow)

Camila (ElectrumX maintainer) sees only phrasing-bank-compliant strings across CLI output, dataset README, paper abstract, contribution-channel docs, and Spanish mirrors — the audit is a release-blocking CI gate from M0. Diego (flagged operator) can find a "What a flagged cluster does NOT mean" text in dataset README + paper, open a disclosure issue via a dedicated bilingual template, get acknowledgment within 48h, and have his contextual note appended to the dataset's qualitative literature with consent.

**FRs covered:** FR31, FR32, FR33, FR34
**Milestone arrival:** M0 (audit CI scaffold) → M3 (disclosure flow live)
**Standalone value:** Yes — phrasing-bank audit ships at M0 and protects every release thereafter; the disclosure flow lands at M3. Independent of Analysis/Publication mechanics.

### Epic 6: Bilingual EN+ES Parity (M0 scaffold → ongoing SLA)

Óscar (Spanish-speaking university researcher) can read README, first-run guide, dataset schema documentation, dataset README, contribution guide, CLI `--help` text in Spanish at synchronized parity with English; he can open issues and PRs in Spanish with the same 48h/7d SLA; bilingual documents drifting >14 days are publicly flagged in CI as "translation pending"; documents drifting >30 days block releases or roll back to the prior synchronized version.

**FRs covered:** FR35, FR36, FR37, FR38
**Milestone arrival:** M0 (scaffold) → ongoing
**Standalone value:** Yes — bilingual scaffold (templates, mirror discipline, staleness CI) is M0-foundational and protects every release. Independent of analysis/publication content.

### Epic 7: Operational Stewardship — Uptime, SLAs, Launch-Blocker Tracking

Ifuensan can monitor collection uptime over rolling 30-day windows (alerted when < 95% or > 24h cumulative planned downtime); a maintainer can track PR-review SLA conformance (48h ack / 7d substantive / same-day for data-integrity) and tag PRs as `review-queued` during peak load; a maintainer can track per-launch-blocker status across the 26-item checklist (cleared / pending / blocked) with priority-1 cluster surfaced.

**FRs covered:** FR39, FR41, FR42
**Key NFRs:** NFR6, NFR9, NFR17
**Milestone arrival:** M0 (journalctl-parsed metrics) → ongoing (Grafana + Prometheus at M2+)
**Standalone value:** Yes — operational tooling supports every epic without depending on any of them.

---

## Epic 1: Reproducible Measurement Foundation on Production Host (M0)

Ifuensan can run a stdlib-only Electrum collection daemon 24/7 against 10–20 seed servers on a production AWS EC2 t4g.small host with dual-stack IPv6 outbound, `chrony` NTP, systemd supervision, monotonic-ns timestamping, append-only SQLite storage, and a green reproducibility self-test in GitHub Actions CI. Bespoke skeleton (no third-party starter — AR1) ships with the dev tooling stack, exception hierarchy, structured-JSON logging, and bilingual README placeholders. The M0→M1 gate is green at the end of the epic.

### Story 1.1: Bespoke M0 project skeleton

As **Ifuensan (the maintainer)**,
I want **a minimal `pyproject.toml` + `src/`-layout skeleton with MIT license and bilingual README placeholders**,
So that **the project has a working PEP-621 package, install path, and bilingual surface from commit #1, with no third-party starter pulling in unwanted dependencies**.

**Acceptance Criteria:**

**Given** an empty git-initialized directory
**When** Story 1.1 completes
**Then** `pyproject.toml` exists with PEP-621 metadata declaring `requires-python = ">=3.11"`, project name `electrum-sybil-detector`, MIT license classifier, and no third-party runtime dependencies
**And** the directory structure matches architecture.md L613–L829 at the M0 subset: `src/electrum_sybil_detector/{__init__,__main__,version}.py`, `LICENSE` (MIT verbatim), `README.md` + `README.es.md` (bilingual placeholders with project name + one-line summary in each language), `CHANGELOG.md`, `CONTRIBUTING.md` + `CONTRIBUTING.es.md`, `CODE_OF_CONDUCT.md`, `.gitignore`
**And** `src/electrum_sybil_detector/__init__.py` exposes `__version__` resolved from `pyproject.toml`
**And** `python -m electrum_sybil_detector --version` prints the version string and exits 0
**And** no `setup.py`, no `requirements.txt`, no `Pipfile`, no `poetry.lock` are present (AR1 — bespoke, no starter)

### Story 1.2: Dev tooling stack — uv + ruff + mypy --strict + pytest + pre-commit

As **Ifuensan (the maintainer)**,
I want **a deterministic local dev environment via `uv` + a strict lint/type/test toolchain enforced by pre-commit hooks**,
So that **every contributor (including future Path 2 reproducers) gets identical environments, byte-by-byte locked dependencies, and lint/type errors caught before commit**.

**Acceptance Criteria:**

**Given** the M0 skeleton from Story 1.1
**When** a contributor runs `uv sync` in a clean clone
**Then** `uv` creates a `.venv/` with the pinned Python version (3.11+) and installs all dev dependencies from `uv.lock`
**And** `uv.lock` is committed and pins the entire dependency tree byte-for-byte (NFR15 reproducibility-aligned)
**And** `pyproject.toml` declares `[tool.ruff]` with the ruleset `E, F, W, I, N, UP, B, A, C4, SIM, ARG, PL`, format-on, line length 100
**And** `pyproject.toml` declares `[tool.mypy]` with `strict = true`, `disallow_untyped_defs = true`, `warn_unused_ignores = true`
**And** `pyproject.toml` declares `[tool.pytest.ini_options]` with `pytest-asyncio` plugin pinned to `1.3.x` (NOT `1.4.0a1`), `asyncio_mode = "auto"`, `testpaths = ["tests"]`
**And** `.pre-commit-config.yaml` configures hooks for ruff (lint+format), mypy --strict, EOF-fixer, trailing-whitespace, and conventional-commits message lint
**Given** a contributor stages a file with a lint or type error
**When** they attempt to `git commit`
**Then** the pre-commit hook rejects the commit with the offending rule cited
**And** `hatchling` is declared as the build backend in `pyproject.toml [build-system]` (D7.1)

### Story 1.3: GitHub Actions CI baseline matrix

As **Ifuensan (the maintainer)**,
I want **a GitHub Actions CI matrix that runs ruff, mypy --strict, and pytest across Python 3.11 / 3.12 / 3.13 / 3.14 on every push and PR**,
So that **forward-incompatibilities are caught early and Path 2 reproducers on Debian/Ubuntu LTS can pick any of the four versions with confidence**.

**Acceptance Criteria:**

**Given** the dev tooling stack from Story 1.2
**When** a PR is opened or a commit is pushed to the main branch
**Then** `ci/github-actions/ci.yml` runs three sequential jobs in a matrix across Python 3.11, 3.12, 3.13, 3.14: (1) `uv sync` env setup, (2) `uv run ruff check --output-format=github . && uv run ruff format --check .`, (3) `uv run mypy --strict src/`, (4) `uv run pytest`
**And** the workflow uses the `astral-sh/setup-uv` action with the lockfile cached
**And** `ci/github-actions/` is symlinked to `.github/workflows/` per the convention in architecture.md L828
**And** any matrix cell failure marks the PR as failing CI
**Given** the symlink convention is alien to GitHub Actions defaults
**When** the workflow file is committed
**Then** `.github/workflows/ci.yml` resolves to `ci/github-actions/ci.yml` and triggers correctly on push/PR events

### Story 1.4: Core utilities — time discipline, hashing, exceptions, structured logging

As **a future story author or contributor**,
I want **shared utilities for monotonic-ns time pairing, BLAKE2b-256 hashing, the project exception hierarchy, and structured-JSON logging**,
So that **every probe, every storage row, every log line, and every error in subsequent stories uses the same timing semantics, the same hash function, the same exception types, and the same log shape — with no module reinventing them**.

**Acceptance Criteria:**

**Given** the M0 skeleton + dev tooling stack
**When** Story 1.4 completes
**Then** `src/electrum_sybil_detector/time_discipline.py` exports `now_ns_pair() -> tuple[int, int]` returning `(time.monotonic_ns(), time.time_ns())` and a `Timestamp` TypedDict with two fields `monotonic_ns: int` and `wall_clock_ns: int` (AR12)
**And** `src/electrum_sybil_detector/hashing.py` exports `blake2b_256(data: bytes) -> str` returning lowercase 64-char hex (no `0x` prefix), and `opaque_server_id(host: str, port: int, transport: str) -> str` returning the BLAKE2b-256 hash of the canonical `(host, port, transport)` triple (AR13, FR16)
**And** `src/electrum_sybil_detector/exceptions.py` defines the hierarchy `ElectrumSybilError → {DiscoveryError, CollectionError → {ProbeError, ConnectionError}, StorageError, AnalysisError, PublicationError, AuditError}` (AR11)
**And** `src/electrum_sybil_detector/logging_setup.py` configures Python `logging` to emit one JSON object per line with required keys `monotonic_ns`, `wall_clock_ns`, `level`, `module`, `event` and an optional nested `context` object; `level` is one of `debug/info/warning/error/critical`; `event` is snake_case verb_object (AR31)
**And** unit tests in `tests/test_time_discipline.py`, `tests/test_hashing.py`, `tests/test_exceptions.py`, `tests/test_logging_setup.py` cover happy path + edge cases (e.g., hashing with empty bytes; logging with and without context)
**Given** a developer attempts to compute a delta from `wall_clock_ns`
**When** they import `time_discipline`
**Then** the module documentation explicitly states `wall_clock_ns` MUST NOT be used in computed-delta metrics — the only legal arithmetic is `BIGINT - BIGINT` on `monotonic_ns`

### Story 1.5: SQLite WAL storage backend + initial schema + forward-only migration runner

As **the Collection module (and any future module that records data)**,
I want **a Storage Protocol exposing append-only inserts to versioned raw-tier tables backed by SQLite in WAL mode, with a forward-only migration runner**,
So that **every probe row carries `monotonic_ns + wall_clock_ns + schema_version`, raw rows are immutable, and the SQLite → TimescaleDB swap at Epic 2 only requires a backend swap (not a project-wide rewrite)**.

**Acceptance Criteria:**

**Given** the core utilities from Story 1.4
**When** Story 1.5 completes
**Then** `src/electrum_sybil_detector/storage/__init__.py` exports a `Storage` Protocol class (PEP 544) with async methods `record_connection_event(...)`, `record_block_notification(...)`, `record_server_metadata(...)`, `record_ntp_window_manifest(...)`, `upsert_server(...)`, `apply_migrations(directory: Path) -> None` (AR8, AR9)
**And** `src/electrum_sybil_detector/storage/sqlite_backend.py` implements `Storage` against `sqlite3` in WAL journal mode, opening one DB file per collection window, exposing transactional batched writes (AR16)
**And** `src/electrum_sybil_detector/storage/schema.py` defines `CURRENT_SCHEMA_VERSION = 1` and the `schema_migrations` tracking table
**And** `src/electrum_sybil_detector/storage/migrations.py` runs files matching `migrations/sqlite/[0-9]{4}_*.sql` in numeric order, idempotently (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`), recording each applied filename in `schema_migrations`
**And** `migrations/sqlite/0001_initial_schema.sql` creates `servers (server_id TEXT PRIMARY KEY, host TEXT, port INTEGER, transport TEXT, first_seen_monotonic_ns BIGINT, first_seen_wall_clock_ns BIGINT, schema_version INTEGER NOT NULL)`, `connection_events (connection_id INTEGER PRIMARY KEY, server_id TEXT, event_type TEXT, banner TEXT, tls_cert_sha256 TEXT, resolved_ip TEXT, source TEXT, monotonic_ns BIGINT, wall_clock_ns BIGINT, schema_version INTEGER NOT NULL)`, and `block_notifications (id INTEGER PRIMARY KEY, connection_id INTEGER, block_height INTEGER, block_hash TEXT, monotonic_ns BIGINT, wall_clock_ns BIGINT, schema_version INTEGER NOT NULL)` with indexes `idx_connection_events_server_id_monotonic_ns` and `idx_block_notifications_connection_id_monotonic_ns` (FR8, FR11, FR12, FR16)
**And** `migrations/sqlite/0002_periodic_probes.sql` creates `server_metadata`, `fee_estimates`, `relay_fees`, `fee_histograms`, `availability` tables with the same `monotonic_ns` + `wall_clock_ns` + `schema_version` invariant (FR12, FR14)
**And** `migrations/sqlite/0003_add_donation_address.sql` adds `donation_address TEXT` column to `server_metadata` via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
**And** `migrations/sqlite/0004_ntp_window_manifest.sql` creates `ntp_window_manifest (window_id INTEGER PRIMARY KEY, canonical_source TEXT, stratum INTEGER, drift_bound_ns BIGINT, window_start_monotonic_ns BIGINT, window_start_wall_clock_ns BIGINT, schema_version INTEGER NOT NULL)` (FR13)
**Given** a probe row already inserted into a raw-tier table
**When** any code attempts an `UPDATE` or `DELETE` against a raw-tier row in `tests/storage/test_sqlite_backend.py`
**Then** the test asserts that the storage backend's public Protocol surface exposes no UPDATE / DELETE methods on raw tier (FR11) — UPDATE/DELETE are physically possible at the SQLite level but not reachable through the `Storage` Protocol
**And** `tests/storage/test_migrations.py` verifies migrations 0001–0004 apply in order on a fresh DB, are idempotent on re-run, and that `schema_migrations` records each filename exactly once

### Story 1.6: Seed-list ingestion (Discovery M0)

As **Ifuensan (the maintainer)**,
I want **a Discoverer that ingests a versioned snapshot of the 1209k.com/bitcoin-eye seed list + the Electrum wallet hardcoded-defaults seed list, upserts them into the `servers` registry, and records a `connection_events` row tagged with the seed source**,
So that **the M0 daemon has a starter population of 10–20 known-good Electrum servers to connect to without requiring snowball expansion (deferred to Epic 2)**.

**Acceptance Criteria:**

**Given** the Storage backend from Story 1.5
**When** Story 1.6 completes
**Then** `src/electrum_sybil_detector/discovery/__init__.py` exports a `Discoverer` Protocol class with methods `discover_from_seeds() -> list[ServerEndpoint]` and `record_provenance(server_id: str, source: str) -> None` (AR8)
**And** `src/electrum_sybil_detector/discovery/seeds.py` implements `Discoverer` reading from versioned local fixtures `src/electrum_sybil_detector/discovery/fixtures/{1209k_snapshot.json, electrum_hardcoded_defaults.json}` (snapshot date stamped in filename or fixture metadata)
**And** each fixture contains a documented snapshot date and source URL in a top-level `_meta` field
**And** `discover_from_seeds()` returns a deduplicated list of ≥10 `ServerEndpoint` records, each with `host`, `port`, `transport ∈ {"tcp", "ssl"}`
**And** for each discovered endpoint, the Discoverer upserts a row into `servers` (using `opaque_server_id(host, port, transport)` from Story 1.4) and writes a `connection_events` row with `event_type = "discovered"` and `source ∈ {"1209k_snapshot", "electrum_hardcoded_defaults"}` (FR1)
**And** `tests/discovery/test_seeds.py` verifies (a) the fixture files load, (b) deduplication across fixtures works, (c) the Storage round-trip records the expected `servers` + `connection_events` rows
**Given** a future story (Epic 2) needs to add snowball-discovered servers
**When** that story runs
**Then** the same `Discoverer` Protocol surface accepts both seed and snowball sources without a Discovery-module rewrite (AR8)

### Story 1.7: Connect to one Electrum server end-to-end

As **Ifuensan (the maintainer)**,
I want **a Transport plug-in surface (TCP + opportunistic-TLS implementations), a JSON-RPC over Electrum protocol layer, and a `headers.subscribe` capture that records one block-header notification with monotonic-ns and wall-clock timestamps**,
So that **the daemon can prove end-to-end that one Electrum server connection produces one valid raw-tier `block_notifications` row, before scaling to many connections in Story 1.8**.

**Acceptance Criteria:**

**Given** the Discovery + Storage modules from Stories 1.5 and 1.6
**When** Story 1.7 completes
**Then** `src/electrum_sybil_detector/collection/transport/__init__.py` exports a `Transport` Protocol class with async methods `connect() -> ConnectionHandle`, `send(payload: bytes) -> None`, `recv() -> bytes`, `close() -> None`, and a property `cert_sha256: str | None` (AR10)
**And** `src/electrum_sybil_detector/collection/transport/tcp.py` implements `Transport` for plain TCP (port 50001 typical)
**And** `src/electrum_sybil_detector/collection/transport/ssl.py` implements `Transport` for opportunistic TLS (port 50002 typical), capturing the SHA-256 cert fingerprint at connect-time and exposing it via `cert_sha256` (AR20, FR8)
**And** `src/electrum_sybil_detector/collection/electrum_protocol.py` implements newline-terminated JSON-RPC framing per Electrum protocol 1.4–1.6, with a `call(method: str, params: list) -> Any` async method and a `subscribe(method: str, on_notification: Callable) -> None` async method
**And** `src/electrum_sybil_detector/collection/headers_subscribe.py` opens a `blockchain.headers.subscribe` subscription, records `(monotonic_ns, wall_clock_ns)` at the moment the notification is received from `recv()`, and writes a `block_notifications` row via the `Storage` Protocol (FR6, NFR1)
**And** at connect-time the module writes a `connection_events` row with `event_type = "connected"`, `banner` from `server.banner`, `tls_cert_sha256` from the Transport (or NULL for TCP), `resolved_ip` from socket peer, captured monotonic-ns and wall-clock-ns (FR8)
**And** `tests/collection/test_transport_tcp.py` + `test_transport_ssl.py` verify round-trip against a mock Electrum server fixture
**And** `tests/collection/test_electrum_protocol.py` verifies JSON-RPC framing handles partial reads, multi-line responses, and malformed payloads (raises `ProbeError`)
**And** `tests/integration/test_single_server_round_trip.py` runs the full chain Discovery seed → Transport TCP → headers.subscribe → Storage round-trip against a mock Electrum server, asserting one `block_notifications` row is persisted with non-zero monotonic_ns
**Given** an Electrum server presents a self-signed TLS certificate
**When** the SSL transport connects
**Then** the connection succeeds (opportunistic TLS, no pinning) and the cert fingerprint is recorded in `connection_events.tls_cert_sha256` (AR20)

### Story 1.8: Persistent multi-server connection pool with reconnect, rate limit, lifecycle events

As **Ifuensan (the maintainer)**,
I want **an asyncio TaskGroup-based connection pool that maintains persistent subscriptions to all 10–20 seed servers concurrently, with per-server token-bucket rate limiting, exponential-backoff reconnection on disconnect, and connect/disconnect/uptime/downtime lifecycle events**,
So that **the M0 daemon runs unattended against the seed population, surviving individual server outages without manual intervention and emitting the lifecycle signal Epic 3's synchronized-downtime analyzer (FR20) will later consume**.

**Acceptance Criteria:**

**Given** the single-server connection from Story 1.7
**When** Story 1.8 completes
**Then** `src/electrum_sybil_detector/collection/connection_manager.py` opens an `asyncio.TaskGroup` with one task per discovered server, each task running the headers.subscribe loop indefinitely until cancelled (AR3, FR5)
**And** the manager handles ≥10 concurrent server connections in the integration test
**And** `src/electrum_sybil_detector/collection/reconnect.py` implements `backoff_delay(attempt: int) -> float` matching architecture.md L476–L483 exactly: `base=2.0`, `cap=300.0`, `jitter_pct=0.25`, raw delay `min(cap, base * 2**attempt)`, jitter `raw * 0.25 * (random() * 2 - 1)` (NFR7, AR-specific D3.4)
**And** on disconnect, the per-server task writes a `connection_events` row with `event_type = "disconnected"`, captures monotonic-ns + wall-clock-ns, sleeps `backoff_delay(attempt)`, increments `attempt`, and reconnects; on successful reconnect, attempt resets to 0 and a `connection_events` row with `event_type = "reconnected"` is written (FR9, NFR7)
**And** `src/electrum_sybil_detector/collection/rate_limit.py` implements a per-server token bucket with default capacity 1, refill 1 token/sec, blocking `acquire()` API; subscriptions (passive listeners) bypass the bucket; explicit RPC calls via `electrum_protocol.call(...)` go through `acquire()` (FR10, AR21)
**And** `src/electrum_sybil_detector/collection/connection_lifecycle.py` exposes a periodic per-server `ping_loop()` invoking `server.ping` at 60-second cadence to detect zombie connections; failed pings trigger the disconnect+reconnect path
**And** `tests/collection/test_connection_manager.py` simulates ≥10 mock servers, randomly disconnecting some and verifying the pool reconnects each within the expected backoff window
**And** `tests/collection/test_rate_limit.py` verifies the token bucket blocks the second probe within 1 second and releases after 1 second
**And** `tests/collection/test_reconnect.py` verifies `backoff_delay` matches the architecture's exact formula at attempts 0 through 8
**And** `tests/integration/test_m0_end_to_end.py` runs the full Discovery → ConnectionManager → Storage chain against ≥10 mock servers for 60 seconds and asserts (a) all 10 produce ≥1 block_notification row each, (b) at least one disconnect+reconnect cycle is recorded for the simulated-flaky server
**Given** an unrecoverable error inside one per-server task
**When** the error propagates
**Then** the TaskGroup catches it, logs at `critical`, cancels sibling tasks, and exits non-zero — never silently swallowed (per AR11 invariant)

### Story 1.9: Reproducibility self-test scaffold + CI gate

As **Ifuensan (the maintainer) and any future Path 2 reproducer**,
I want **a self-test that re-runs a deterministic minimal pipeline against a frozen raw-input fixture and asserts bit-identical output (or a documented per-column floating-point tolerance), invocable as `python -m electrum_sybil_detector.selftest` and gated in CI within the ≤30-min budget**,
So that **the bit-identical contract scaffold (NFR15) is in place from M0 — protecting every release thereafter — even though the full M3 dataset re-derivation gate lights up later in Epic 4**.

**Acceptance Criteria:**

**Given** the M0 daemon from Story 1.8
**When** Story 1.9 completes
**Then** `src/electrum_sybil_detector/selftest/__init__.py` and `src/electrum_sybil_detector/selftest/reproducibility.py` are present
**And** `python -m electrum_sybil_detector.selftest` runs a frozen-fixture pipeline: load `tests/fixtures/m0_selftest_input.json` (≥3 mock-server connection events + ≥30 mock block notifications) → write to a temp SQLite file → re-export as JSONL → BLAKE2b-256 hash the export → compare to expected hash `tests/fixtures/m0_selftest_expected.txt` (NFR15 scaffold)
**And** the self-test exits 0 on hash match, exits 1 on hash mismatch with diagnostic showing observed vs. expected hash and the differing JSONL line(s)
**And** the self-test runtime stays ≤ 30 seconds at M0 fixture size (well under NFR4's ≤ 30 min budget that lights up at M3 dataset scale)
**And** `ci/github-actions/selftest.yml` runs `uv run python -m electrum_sybil_detector.selftest` on every push and PR, blocking merge on failure
**And** `ci/scripts/run_selftest.sh` is a thin wrapper (`#!/bin/bash`, `set -euo pipefail`, `exec uv run python -m electrum_sybil_detector.selftest "$@"`) reusable from local runs and from the AWS deploy host
**And** `tests/integration/test_m0_end_to_end.py` (extended from Story 1.8) now also invokes the self-test on the integration-test SQLite snapshot and asserts the bit-identical contract holds
**Given** a developer changes a default value in storage row insertion (e.g., reordering columns)
**When** the self-test runs
**Then** the hash mismatches and CI blocks the merge until either the change is reverted or the expected hash is regenerated with a `pattern:` PR titled per architecture.md L543

### Story 1.10: AWS production deploy via Terraform + chrony + systemd + IPv6 dual-stack gate

As **Ifuensan (the maintainer)**,
I want **a Terraform-codified AWS EC2 t4g.small deploy with VPC-explicit IPv6 outbound, `chrony` NTP discipline, systemd supervision of the daemon, and a `verify_dual_stack.sh` gate proving the collector reaches ≥3 IPv6-only Electrum servers**,
So that **the daemon runs on a cost-bounded production host (≤ $500/year per NFR12, ≤ 512 MB resident per NFR13) with native IPv6 verified end-to-end (closing LB#26) and an Infrastructure-as-Code substrate the user's local broken-IPv6-routing constraint cannot pollute**.

**Acceptance Criteria:**

**Given** the M0 daemon from Story 1.8 + the self-test gate from Story 1.9
**When** Story 1.10 completes
**Then** `infra/terraform/main.tf` declares the AWS provider in region `us-east-1` and required Terraform version ≥ 1.6
**And** `infra/terraform/network.tf` provisions a VPC with explicit IPv4 + IPv6 CIDR blocks, one public subnet with both v4 and v6 CIDR, an Internet Gateway, an egress-only Internet Gateway for v6, and explicit route-table entries for v4 (`0.0.0.0/0` → IGW) and v6 (`::/0` → egress-only IGW) — NO IPv6 tunnels (NFR10, AR29)
**And** `infra/terraform/compute.tf` provisions one EC2 `t4g.small` instance (ARM Graviton, 2 vCPU, 2 GB) with Debian 13 ARM64 AMI, gp3 EBS root volume sized 50 GB, IPv6 ENI assignment from the subnet's IPv6 CIDR (AR28)
**And** `infra/terraform/security.tf` defines a security group permitting outbound to ports 50001/50002 (Electrum clearnet) and inbound only to port 22 (SSH) restricted to the maintainer's IP range
**And** `infra/terraform/outputs.tf` exposes the EC2 public DNS, public IPv4, and public IPv6 addresses
**And** `infra/systemd/electrum-monitor.service` declares the daemon as a systemd unit with `Restart=on-failure`, `MemoryMax=512M` (NFR13), `StandardOutput=journal`, `StandardError=journal`, running as a non-root user
**And** `infra/systemd/chrony.conf.d/electrum-monitor.conf` declares one canonical NTP source (e.g., `pool.ntp.org` with iburst and per-collection-window stratum logging) and disables alternate sources to satisfy "one canonical NTP-disciplined time source per collection window" (FR13, AR30)
**And** `ci/scripts/verify_dual_stack.sh` runs from the deploy host, picks ≥3 IPv6-only Electrum servers from a curated fixture, attempts `server.features` + `server.peers.subscribe` against each via the production daemon binary, exits 0 if all ≥3 succeed and exits 1 otherwise (LB#26 gate)
**And** `docs/deploy-aws.md` (English) provides a step-by-step deploy runbook from `terraform apply` to `verify_dual_stack.sh` exit 0 to first `block_notifications` row in SQLite
**And** `docs/deploy-aws.es.md` (Spanish mirror) is a same-day translation of `deploy-aws.md` (bilingual scaffold per AR38, full bilingual ops machinery is Epic 6)
**And** monthly cost projection from the Terraform outputs ≤ $20/mo (≤ $240/year) leaving comfortable headroom under NFR12's $500/year envelope
**Given** the deploy is applied via `terraform apply` and `electrum-monitor.service` is enabled
**When** an operator runs `verify_dual_stack.sh` from the EC2 host
**Then** the script exits 0 within 30 seconds and prints the IPv6-only servers reached (LB#26 cleared)

### Story 1.11: M0→M1 gate verification + per-window NTP manifest persistence

As **Ifuensan (the maintainer)**,
I want **the daemon to persist a per-collection-window NTP manifest at window-start (sourced from `chronyc tracking`) and to demonstrably sustain 7 days of ≥95% uptime against 10–20 seed servers on the AWS deploy host with a green self-test at the end**,
So that **the M0 architectural guardrails (monotonic-ns, append-only raw, connection metadata at connect-time, one canonical NTP source per window) are proven in production — the M0→M1 gate (AR40) is closed and Epic 2's snowball expansion can begin**.

**Acceptance Criteria:**

**Given** the AWS deploy from Story 1.10 + the daemon from Story 1.8 + the self-test from Story 1.9
**When** Story 1.11 completes
**Then** `src/electrum_sybil_detector/collection/connection_manager.py` invokes a `record_ntp_window_manifest(...)` call once per collection window at window-start, sourcing `canonical_source`, `stratum`, `drift_bound_ns` from `chronyc tracking` parsed output, persisting via the Storage Protocol into the `ntp_window_manifest` table (FR13)
**And** a "collection window" boundary is defined and documented (proposed: 24-hour rotation aligned to UTC midnight; window IDs monotonic) in `docs/architecture-patterns-changelog.md`
**And** a 7-day soak test on the AWS deploy host is run against ≥10 seed servers
**And** at the end of the soak, fleet aggregate uptime ≥ 95% per `connection_events` analysis (NFR6 prerequisite — full rolling-30d monitoring lives in Epic 7)
**And** at the end of the soak, `python -m electrum_sybil_detector.selftest` exits 0 against a freshly-snapshotted SQLite window file
**And** at the end of the soak, the `ntp_window_manifest` table contains ≥7 rows (one per window) with non-NULL `canonical_source`, `stratum`, `drift_bound_ns` (FR13)
**And** at the end of the soak, every `block_notifications` and `connection_events` row has non-zero `monotonic_ns` and `wall_clock_ns` (FR12 invariant verified in production)
**And** at the end of the soak, no raw-tier row has been UPDATEd or DELETEd (FR11 invariant verified via SQLite audit query)
**And** soak results (uptime %, NTP drift bounds observed, self-test runtime, SQLite size) are captured in `docs/bmad-binnacle/04_m0_soak_test.md` for the M0→M1 gate evidence trail
**Given** the soak passes
**When** the maintainer reviews the M0→M1 gate
**Then** the gate is recorded as cleared in the launch-blocker tracker (Epic 7 Story 7.3 will surface this) and Epic 2 work can begin

---

## Epic 2: Full-Network Discovery & Sustained Collection (M1 → M2)

The daemon discovers the full clearnet Electrum population (≥150–500 servers; Phase-1 V3 lower bound 344) via snowball expansion from seeds + `server.peers.subscribe`, sustains ≥95% uptime across all of them with per-server rate limiting, ASN-diverse provenance, gap enumeration, and the full periodic-probe RPC suite. Tor `.onion` coverage joins via SOCKS5 transport plug-in at M2; storage migrates SQLite → TimescaleDB at production scale. M1→M2 and M2→M3 gates are green at the end of the epic.

### Story 2.1: Snowball discovery via `server.peers.subscribe`

As **Ifuensan (the maintainer)**,
I want **iterative `server.peers.subscribe` traversal from the M0 seed population until convergence, persisting each newly discovered server with `source = "snowball"` provenance and bounded by NFR5's ≤24 h per-sweep budget**,
So that **the daemon discovers the full clearnet Electrum population (Phase-1 V3 lower bound 344 dual-stack-reachable mainnet servers) without manual seed list curation, while respecting the post-2019 ElectrumX subnet-dedup hardening so the snowball is not silently filtered**.

**Acceptance Criteria:**

**Given** the M0 daemon from Epic 1 with 10–20 seed servers connected
**When** Story 2.1 completes
**Then** `src/electrum_sybil_detector/discovery/snowball.py` implements `Discoverer.discover_via_snowball()` that, for each currently-connected server, calls `server.peers.subscribe` and parses the response into a list of `(host, port, transport_hint)` tuples (FR2)
**And** the snowball runs in iterations: each iteration queries newly-connected servers; convergence is reached when an iteration discovers zero new endpoints OR when the per-sweep wall-clock budget reaches 24 h (NFR5)
**And** at convergence-or-budget-exhaustion the sweep terminates and is suspended until the next scheduled sweep (NFR5)
**And** for each newly-discovered endpoint, the Discoverer (a) computes `opaque_server_id` via `hashing.opaque_server_id(host, port, transport)` from Story 1.4, (b) upserts into `servers` (idempotent), (c) writes a `connection_events` row with `event_type = "discovered"` and `source = "snowball"` and `discovered_via_server_id = <parent_server_id>`
**And** subnet-dedup awareness is documented: a comment in `snowball.py` notes that ElectrumX's post-2019 `add_peer` hardening filters /24 dups in `server.peers.subscribe` responses, so the snowball will under-report when seed servers run hardened ElectrumX — this is acknowledged as a methodology limitation, NOT papered over with a workaround (per AR (no shortcuts to bypass safety checks))
**And** `migrations/sqlite/0005_snowball_provenance.sql` adds the `discovered_via_server_id TEXT` column to `connection_events` via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (FR14 forward-compat)
**And** `tests/discovery/test_snowball.py` verifies (a) one iteration of snowball against ≥3 mock servers each advertising 2 distinct peers produces 6 new server rows, (b) re-running the snowball is idempotent (no duplicate `servers` rows), (c) the 24 h budget terminates an in-progress sweep
**Given** a sweep terminates by hitting the 24 h budget (not convergence)
**When** the sweep state is queried
**Then** the partial sweep result is durable (servers discovered so far are in the registry) and the next sweep resumes from the most recent connected population — not from the original seed list

### Story 2.2: Discovery provenance enrichment — ASN + protocol-version range

As **Ifuensan (the maintainer) and downstream Lukas (analyst)**,
I want **each discovered server's provenance row enriched with the ASN of its resolved IP and the advertised `server.features` protocol-version range captured at connect-time**,
So that **vantage-diversity declarations in the dataset manifest (FR26 hook) and ASN-stratified analyses (Epic 3 baseline-distribution FR22) have the per-server attributes they need without re-deriving from raw bytes**.

**Acceptance Criteria:**

**Given** the snowball from Story 2.1 + the connection lifecycle from Story 1.8
**When** Story 2.2 completes
**Then** `src/electrum_sybil_detector/discovery/asn.py` implements `lookup_asn(ip: str) -> int | None` using `pyasn` (added to `pyproject.toml` as the M1-entry first runtime dependency per AR5) against an offline RIB snapshot bundled in `src/electrum_sybil_detector/discovery/fixtures/asn_rib_<YYYYMMDD>.dat`
**And** the bundled RIB snapshot has a documented refresh procedure in `docs/architecture-patterns-changelog.md` (e.g., quarterly refresh from Routeviews; pin SHA-256 in lockfile); the snapshot date is also captured in any `manifest.json` consumer (Epic 4 hook)
**And** `migrations/sqlite/0006_provenance_enrichment.sql` adds `resolved_ip_asn INTEGER`, `protocol_version_min TEXT`, `protocol_version_max TEXT` columns to `connection_events` and `server_metadata` as appropriate, via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (FR14)
**And** at connect-time, the Collection module (extending Story 1.7's connect-time metadata path) (a) calls `server.features` once, (b) parses the `protocol_min` and `protocol_max` fields from the response, (c) calls `asn.lookup_asn(resolved_ip)`, (d) persists the enriched row (FR4)
**And** `tests/discovery/test_asn.py` verifies ASN lookup for known IPs (e.g., AS24940 / Hetzner from architecture LB#14) and returns `None` for non-resolvable IPs (e.g., RFC1918 ranges)
**And** `tests/integration/test_provenance_enrichment.py` runs the full Snowball → connect → enrich chain against ≥3 mock servers and asserts the `connection_events` rows carry non-NULL ASN + `protocol_version_min/max` for each
**Given** a server's `server.features` response is malformed or missing the `protocol_min`/`protocol_max` keys
**When** enrichment runs
**Then** the missing fields are persisted as NULL (not faked), a `warning`-level log line is emitted with the offending server_id, and the connection proceeds (probe failure is non-fatal per Epic 1 Story 1.8's recoverable-error pattern)

### Story 2.3: Periodic stable-RPC polling suite at full network scale

As **Ifuensan (the maintainer) and downstream Lukas (analyst)**,
I want **per-server periodic polling of the full stable Electrum RPC suite (`server.{version,features,banner,donation_address,ping}`, `blockchain.{estimatefee(n),relayfee}`, `mempool.get_fee_histogram`) at configurable cadences, persisting each polled value into its target table from the Story 1.5 migrations**,
So that **the longitudinal raw tier captures every signal Epic 3's analysis pipeline needs (fork-race deltas via headers.subscribe from Epic 1 + fee-histogram CDFs + frontend-config drift over time + uptime via ping) at full network scale, while honoring the per-server token-bucket rate limit from Story 1.8**.

**Acceptance Criteria:**

**Given** the Snowball + Provenance from Stories 2.1, 2.2 + Connection pool from Story 1.8
**When** Story 2.3 completes
**Then** `src/electrum_sybil_detector/collection/periodic_probes.py` implements per-server polling tasks for: `server.version` (cadence default 6 h), `server.features` (6 h), `server.banner` (6 h), `server.donation_address` (6 h), `server.ping` (60 s), `blockchain.estimatefee(n)` for `n ∈ {2, 6, 25, 144}` (5 min), `blockchain.relayfee` (5 min), `mempool.get_fee_histogram` (5 min) (FR7)
**And** all cadences are configurable via `config.py` from a single `[collection.cadences]` TOML section in the project config file (no per-RPC env vars per AR rule "no environment variables for thresholds or methodology parameters" — methodology parameters live in the config file under version control)
**And** each periodic task runs as a child of the per-server `asyncio.TaskGroup` from Story 1.8, sharing the same per-server `rate_limit.acquire()` token bucket (probes count against the bucket; subscriptions remain passive)
**And** each polled value is persisted into the corresponding table (`server_metadata`, `fee_estimates`, `relay_fees`, `fee_histograms`, `availability`) created by `migrations/sqlite/0002_periodic_probes.sql` from Story 1.5; row carries `server_id`, `connection_id`, `monotonic_ns`, `wall_clock_ns`, `schema_version`
**And** for `mempool.get_fee_histogram`, the response (a list of `[fee_rate, vsize]` pairs) is persisted as a single JSONB-encoded TEXT blob in `fee_histograms.histogram_json`, plus a derived `bin_count INTEGER` column for quick summary queries
**And** `migrations/sqlite/0007_fee_histogram_bin_count.sql` adds the `bin_count INTEGER` column via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (FR14)
**And** for `server.ping`, the round-trip-time delta in monotonic-ns is computed (`recv_monotonic_ns − send_monotonic_ns`) and persisted in `availability.rtt_ns` (NFR1 — never use wall-clock for delta)
**And** `tests/collection/test_periodic_probes.py` verifies (a) all 8 RPC types fire at their configured cadences against ≥3 mock servers over a 10-minute simulated window, (b) every persisted row has non-zero monotonic_ns + wall_clock_ns, (c) malformed RPC responses raise `ProbeError` (recoverable per Epic 1 Story 1.7 pattern) without crashing the per-server task
**Given** a probe rate exceeds the per-server token-bucket capacity
**When** the rate-limited task attempts a call
**Then** the call blocks on `rate_limit.acquire()` until a token is available — no rate-limit bypass, no concurrent probes per server (FR10 invariant verified)

### Story 2.4: Collection gap enumeration

As **a downstream analyst (Lukas) and the dataset manifest builder (Epic 4)**,
I want **gaps in per-server collection enumerated as explicit rows derivable from `connection_events` + probe rows, with the gap threshold configurable per collection window and surfaced in the manifest**,
So that **Epic 3 analyses spanning gap boundaries can declare the gap structure explicitly (per PRD §Measurement Validity > Longitudinal continuity) rather than silently smoothing — and the dataset is honest about its temporal coverage**.

**Acceptance Criteria:**

**Given** the periodic-probe data from Story 2.3 + connection lifecycle events from Story 1.8
**When** Story 2.4 completes
**Then** `src/electrum_sybil_detector/storage/gaps.py` implements `enumerate_gaps(window_id: int, gap_threshold_seconds: int = 600) -> list[Gap]` returning one `Gap` per `(server_id, gap_start_monotonic_ns, gap_end_monotonic_ns, gap_duration_ns, preceding_event_type, following_event_type)` (FR40)
**And** a gap is defined as: any interval `> gap_threshold_seconds` between two consecutive successful probes (any of the periodic RPCs OR a `block_notifications` row) for a given server, OR the interval between a `disconnected` event and the next `reconnected` event for the same server when that interval exceeds the threshold
**And** `migrations/sqlite/0008_gaps.sql` creates `gaps (gap_id INTEGER PRIMARY KEY, server_id TEXT, window_id INTEGER, gap_start_monotonic_ns BIGINT, gap_end_monotonic_ns BIGINT, gap_duration_ns BIGINT, gap_threshold_seconds INTEGER, preceding_event_type TEXT, following_event_type TEXT, schema_version INTEGER NOT NULL)` plus `idx_gaps_server_id_window_id`
**And** `enumerate_gaps()` is idempotent: re-running for the same `(window_id, gap_threshold_seconds)` deletes the previous gap rows for that key and re-inserts (this is a derived-tier table, not raw — FR11 invariant preserved)
**And** the per-window `gap_threshold_seconds` value used is recorded in `ntp_window_manifest` via a new column added by `migrations/sqlite/0009_window_gap_threshold.sql` (forward-compat, FR14)
**And** `tests/storage/test_gaps.py` verifies (a) zero-gap baseline (continuous probes), (b) one explicit 1-hour gap is enumerated correctly, (c) the disconnect→reconnect-after-1-hour case is enumerated as a gap, (d) idempotency on re-run
**Given** the dataset manifest builder (Epic 4) needs to declare gap structure for a published window
**When** it queries `gaps` for that window
**Then** all gaps are present and the threshold is recoverable from the window manifest

### Story 2.5: M1→M2 gate verification — full-network reach + IPv6-only end-to-end + 14-day soak

As **Ifuensan (the maintainer)**,
I want **empirical verification that the snowball converges within 24 h, that ≥150 servers are reached (target ≥344 per Phase-1 V3 lower bound), that ≥3 IPv6-only Electrum servers are reached end-to-end via the production daemon, and that a 14-day soak across the full population sustains ≥95% uptime under SQLite-WAL load**,
So that **the M1→M2 gate (AR41) is empirically closed — Tor SOCKS5 (Story 2.6) and TimescaleDB (Story 2.7) work can begin with confidence that the underlying collector can carry the load**.

**Acceptance Criteria:**

**Given** the snowball + provenance + periodic probes + gaps from Stories 2.1–2.4 deployed to the AWS host from Story 1.10
**When** Story 2.5 completes
**Then** at least one full snowball sweep has been observed converging in ≤ 24 h on the production host (NFR5)
**And** the converged population is ≥150 servers (target ≥344 per Phase-1 V3 lower bound; under-shoot is acknowledged not papered over — `docs/bmad-binnacle/05_m1_soak_test.md` explains any delta vs. Phase-1 V3 baseline 344)
**And** an extended `ci/scripts/verify_dual_stack.sh` (from Story 1.10) now selects ≥3 IPv6-only servers from the *snowball-discovered* population (not from a hand-curated fixture) and verifies all 3 produce ≥1 `block_notifications` row each (LB#26 closed at full network scale)
**And** a 14-day soak test is run against the converged population on the AWS host
**And** at the end of the soak, fleet aggregate uptime ≥ 95% per `connection_events` + `availability` analysis (NFR6 prerequisite)
**And** at the end of the soak, the AWS host's daemon process resident memory is ≤ 512 MB at the 99th-percentile sample (NFR13)
**And** at the end of the soak, the SQLite window file size is ≤ 500 MB (extrapolation: ~6 GB/year compressed at full scale per NFR11; uncompressed monthly size therefore ≤ ~500 MB)
**And** at the end of the soak, asyncio cold-start time-to-first-`headers.subscribe` notification is ≤ 60 s on daemon restart (NFR3)
**And** at the end of the soak, the reproducibility self-test (Story 1.9) still exits 0 on a freshly-snapshotted SQLite window file
**And** soak metrics (server count, uptime %, memory peaks, file sizes, IPv6 reach, NFR2 asyncio resolution at full scale) are captured in `docs/bmad-binnacle/05_m1_soak_test.md` for the M1→M2 gate evidence trail
**Given** any soak metric falls below threshold
**When** the gate review is conducted
**Then** the gate is recorded as NOT cleared and triage actions are documented (drop discretionary work and fix per IQ5 protocol) before M2 entry

### Story 2.6: Tor SOCKS5 transport plug-in + `.onion` reach

As **Ifuensan (the maintainer)**,
I want **a new `transport/tor_socks5.py` implementation of the Story 1.7 Transport Protocol that connects via SOCKS5 to a local Tor daemon, logs Tor circuit IDs in `connection_events`, and respects a 3-retry / 300-second budget per probe (NFR8)**,
So that **`.onion` Electrum servers (already discovered by the snowball from Story 2.1 when seed servers expose `.onion` peers) become connectable, broadening vantage diversity at M2 and providing the Tor coverage the M2→M3 gate (AR42) requires**.

**Acceptance Criteria:**

**Given** the Transport Protocol from Story 1.7 + the connection manager from Story 1.8
**When** Story 2.6 completes
**Then** `src/electrum_sybil_detector/collection/transport/tor_socks5.py` implements the `Transport` Protocol via SOCKS5 to `127.0.0.1:9050` (default; configurable in `[collection.tor]` TOML section) using stdlib `socket` + manual SOCKS5 handshake (no third-party SOCKS lib required at this layer; Tor itself is a system dep installed in `infra/systemd/`)
**And** `connection_manager.py` from Story 1.8 selects the appropriate Transport impl based on the server's `transport_hint` field: `tcp.py` for `.com/.net/.org/IP`, `ssl.py` when port 50002 or `s` suffix, `tor_socks5.py` when host ends in `.onion` — this dispatch is the only change to `connection_manager.py`; the TaskGroup pool, reconnect, rate-limit modules are untouched (AR10 invariant verified)
**And** at connect-time over Tor, the `tor_socks5.py` Transport queries the local Tor controller (port 9051 with cookie auth) for the current circuit ID associated with the connection and exposes it via a `tor_circuit_id: str | None` Transport property
**And** `migrations/sqlite/0010_tor_circuit_id.sql` adds the `tor_circuit_id TEXT` column to `connection_events` via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (FR14)
**And** the connect-time `connection_events` row writer (Story 1.7) populates `tor_circuit_id` from the Transport when present, NULL for clearnet (FR3)
**And** `src/electrum_sybil_detector/collection/reconnect.py` from Story 1.8 honors a Tor-specific retry budget for probes through `tor_socks5.py`: ≤ 3 retries per probe over ≤ 300 seconds, then mark probe-failed and emit a `connection_events` row with `event_type = "probe_failed_tor_budget_exhausted"` (NFR8)
**And** `infra/systemd/tor.service` (or distribution-packaged equivalent) is installed on the AWS deploy host with a documented Tor `torrc` snippet enabling the SOCKS5 + control ports
**And** `tests/collection/test_transport_tor.py` verifies SOCKS5 handshake against a mock SOCKS5 server fixture, retry-budget enforcement, and circuit-ID parsing
**And** `tests/integration/test_onion_reach.py` (skipped in CI absent a Tor daemon; documented as a manual integration check) verifies one real `.onion` Electrum server produces ≥1 `block_notifications` row when run against a deploy-host Tor instance
**Given** the local Tor daemon is unreachable at startup
**When** the daemon attempts to connect to a `.onion` server
**Then** the per-server task logs `error`-level "tor unreachable, skipping onion server <id>", emits a `connection_events` row with `event_type = "skipped_tor_unavailable"`, and proceeds with clearnet connections — Tor unavailability does not crash the daemon

### Story 2.7: TimescaleDB backend + storage backend swap

As **Ifuensan (the maintainer)**,
I want **a `storage/timescaledb_backend.py` implementation of the Story 1.5 `Storage` Protocol against TimescaleDB 2.26+ on PostgreSQL 18 via `psycopg 3.2+`, plus a one-time data migration utility that copies SQLite window files into TimescaleDB hypertables**,
So that **the M2 storage scale (full snowball population × periodic-probe cadences × indefinite raw retention) is supported without changing any module other than `storage/`, validating the AR9 invariant — and the bit-identical reproducibility self-test (Story 1.9) continues to pass against the new backend**.

**Acceptance Criteria:**

**Given** the Storage Protocol from Story 1.5 + the M1 dataset accumulated by Stories 2.1–2.5
**When** Story 2.7 completes
**Then** `src/electrum_sybil_detector/storage/timescaledb_backend.py` implements the `Storage` Protocol exactly as `sqlite_backend.py` does (same async method signatures from Story 1.5), backed by TimescaleDB 2.26+ on PostgreSQL 18 via `psycopg 3.2+` (added to `pyproject.toml` runtime deps; AR17, FR15)
**And** `migrations/timescaledb/0001_initial_schema.sql` mirrors `migrations/sqlite/0001_*` plus subsequent SQLite migrations, but creates the time-series tables (`block_notifications`, `availability`, `fee_histograms`, `fee_estimates`, `relay_fees`, `connection_events`) as TimescaleDB **hypertables** partitioned on `monotonic_ns` (D2.3)
**And** the migration runner from Story 1.5 (`storage/migrations.py`) is extended to dispatch by backend: SQLite migrations from `migrations/sqlite/`, TimescaleDB migrations from `migrations/timescaledb/`; both subdirectories use the same forward-only numeric-prefix convention (D2.8, FR14)
**And** `src/electrum_sybil_detector/storage/__init__.py` exposes a `get_storage(backend: Literal["sqlite", "timescaledb"], **config) -> Storage` factory; backend selection driven by `[storage.backend]` in the project config file (not env var)
**And** `scripts/migrate_sqlite_to_timescaledb.py` reads SQLite window files from a directory, opens a TimescaleDB connection, and idempotently copies all rows into the TimescaleDB hypertables preserving `(server_id, monotonic_ns, wall_clock_ns, schema_version)` byte-for-byte; copy is resumable on interruption via a `migration_state` tracking table; copy completes in ≤ 4 hours for the M1 soak's accumulated data on the production host (FR15)
**And** post-migration, `tests/storage/test_storage_protocol_parity.py` runs the same Protocol-surface test suite against both backends and asserts they return the same rows for the same queries (raw bytes parity for hex hashes, exact int equality for monotonic_ns, JSON canonical-form equality for histogram_json blobs)
**And** post-migration, `python -m electrum_sybil_detector.selftest` against the TimescaleDB backend with the M1 raw inputs produces a bit-identical hash to the SQLite-backend output (NFR15 invariant)
**And** no module outside `src/electrum_sybil_detector/storage/` is modified to enable the TimescaleDB backend (AR9 invariant verified by `git diff --stat HEAD~ -- src/electrum_sybil_detector/ | grep -v '^ src/electrum_sybil_detector/storage/'` should be empty for this story)
**Given** the data migration utility is interrupted partway through
**When** it is restarted
**Then** it resumes from the last successfully-copied window without duplicating rows (idempotent — verified by `tests/scripts/test_migrate_sqlite_to_timescaledb.py`)

### Story 2.8: 90-day downsampling retention policy

As **Ifuensan (the maintainer)**,
I want **a retention policy that keeps raw `block_notifications`, `connection_events`, `server_metadata`, `gaps`, and `ntp_window_manifest` rows indefinitely, but downsamples `fee_histograms` and `availability` rows older than 90 days using TimescaleDB native compression**,
So that **the dataset stays under NFR11's ~6 GB/year compressed envelope without sacrificing the load-bearing fork-race signal (block_notifications) — fee-histogram drift signal at full per-5-min cadence is only needed in recent windows; older windows retain a downsampled summary**.

**Acceptance Criteria:**

**Given** the TimescaleDB backend from Story 2.7
**When** Story 2.8 completes
**Then** `src/electrum_sybil_detector/storage/retention.py` implements `apply_retention_policy(now_ns: int) -> RetentionReport` which returns counts of (rows compressed, rows kept indefinitely, downsample bins created) per table (AR19)
**And** `block_notifications`, `connection_events`, `server_metadata`, `gaps`, `ntp_window_manifest` are explicitly listed as "indefinite-retention" tables; the function MUST NOT compress or delete them (AR19 — load-bearing fork-race signal preserved)
**And** `fee_histograms` and `availability` rows older than 90 days are downsampled into 1-hour bins per server, persisted into new derived tables `fee_histograms_hourly` and `availability_hourly`, then the original raw rows in those windows are TimescaleDB-compressed (not deleted; queryable via decompression but stored at low byte cost) (AR19, NFR11)
**And** `migrations/timescaledb/0002_compression_policy.sql` (a) creates `fee_histograms_hourly` and `availability_hourly` derived tables with their own `derived_run_id` + `code_hash` columns per AR15, (b) configures TimescaleDB native compression on `fee_histograms` and `availability` for chunks older than 90 days
**And** the retention policy runs as a systemd timer on the AWS deploy host: `infra/systemd/electrum-monitor-retention.timer` invokes `python -m electrum_sybil_detector.storage.retention` daily at 03:00 UTC
**And** `tests/storage/test_retention.py` verifies (a) indefinite-retention tables are untouched, (b) 90-day-old `fee_histograms` rows are downsampled into the hourly table with correct bin counts, (c) re-running retention is idempotent (no duplicate hourly bins), (d) the operation completes within an SLA of 30 minutes for a year's accumulated data
**And** post-retention, the TimescaleDB cluster size projection ≤ 6 GB/year (NFR11) is verified with extrapolation captured in `docs/bmad-binnacle/06_retention_projection.md`
**Given** a compressed `fee_histograms` row needs to be queried for an analytical re-derivation (Epic 3)
**When** the analysis layer queries the table
**Then** TimescaleDB transparently decompresses the chunk and returns the row — compressed storage is read-transparent (verified in `tests/storage/test_retention.py`)

### Story 2.9: M2→M3 gate verification — Tor coverage + storage migration + LB readiness

As **Ifuensan (the maintainer)**,
I want **empirical verification that Tor coverage is operational (≥1 `.onion` server producing block_notifications), that the SQLite → TimescaleDB migration is complete (or that the SQLite-snapshot-sufficient AR42 alternative path is documented), and that a 14-day soak across the full population including Tor sustains ≥95% uptime, plus a re-evaluation of LB#1 (stale-blocks cadence) and LB#2 (fee-histogram harness fixtures) to confirm Epic 3 work is unblocked**,
So that **the M2→M3 gate (AR42) is empirically closed, the M3 launch-blocker checklist (AR44) is on track, and Epic 3 (Methodology Signal Computation) can begin against a stable production substrate**.

**Acceptance Criteria:**

**Given** Tor coverage from Story 2.6 + TimescaleDB backend from Story 2.7 + retention from Story 2.8 deployed to the AWS host
**When** Story 2.9 completes
**Then** ≥1 `.onion` Electrum server has produced ≥1 `block_notifications` row over the soak window (FR3 production verification)
**And** EITHER (a) the `[storage.backend]` config on the AWS deploy host is set to `timescaledb`, the data migration from Story 2.7 has completed, all writes go to TimescaleDB; OR (b) `[storage.backend]` remains `sqlite` and `docs/bmad-binnacle/07_m2_storage_choice.md` documents the explicit demonstration that SQLite snapshot is sufficient for the M3 dataset window (AR42 alternative — not a default; requires sign-off)
**And** a 14-day soak is run across the full population including Tor servers
**And** at the end of the soak, fleet aggregate uptime ≥ 95% (NFR6)
**And** at the end of the soak, the daemon resident memory is ≤ 512 MB at p99 (NFR13) — including Tor SOCKS5 connection overhead
**And** LB#1 (stale-blocks cadence): a re-check of `bitcoin-data/stale-blocks` confirms the 3–8/month cadence claim still holds in the most recent 6 months; result captured in `docs/bmad-binnacle/08_lb1_recheck.md`
**And** LB#2 (fee-histogram harness): the 5-frontend matrix (ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs) is provisioned in `harness/fixtures/` with a documented `docker-compose.yaml` or equivalent local-bringup script, ready for Epic 3 Story 3.1 to invoke
**And** the 26-item launch-blocker checklist is reviewed and per-item status (cleared / pending / blocked) is recorded; priority-1 cluster (#11 b10c socialization → #2 fee-histogram → #8 fork-observer → #1 stale-blocks → #9 methodology-ancestor citations) status is explicit
**And** the M2→M3 gate evidence (Tor reach, storage migration choice, soak metrics, LB statuses) is captured in `docs/bmad-binnacle/09_m2_m3_gate.md` for hand-off to Epic 3 work
**Given** any gate criterion fails
**When** the gate review is conducted
**Then** the gate is recorded as NOT cleared, blockers are itemized, and Epic 3 work does not begin until the gate clears

---

## Epic 3: Methodology Signal Computation & Cluster Findings (M3 entry)

Lukas can run the analysis pipeline against an M0/M1/M2 dataset snapshot and produce statistically-rigorous cluster findings: fee-histogram drift calibration via the 5-frontend harness (LB#2 priority-1) → fork-race pairwise-delta variance → 1-D Wasserstein over fee-rate CDFs → synchronized-downtime overlap → pre-committed multi-signal threshold evaluation → DBSCAN/Ward clustering with Benjamini–Hochberg FDR + bootstrap CIs. Every Epic 3 story writes only to derived-tier tables stamped with `derived_run_id + code_hash` — preserving FR11's append-only raw invariant.

### Story 3.1: Fee-histogram drift calibration harness — 5-frontend matrix (LB#2)

As **Ifuensan (the maintainer) and downstream Lukas (analyst)**,
I want **a calibration harness orchestrating ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs against one Bitcoin Core, measuring the 1-D Wasserstein-distance distribution between every frontend pair under known-same-backend conditions**,
So that **the cluster-membership Wasserstein threshold (consumed by Story 3.8's multi-signal engine) is empirically calibrated rather than guessed — closing LB#2 (priority-1 launch-blocker) and providing a code-path that doubles as a recurring CI drift-detection check**.

**Acceptance Criteria:**

**Given** a workstation (not the production AWS host) with Docker Engine ≥ 24 installed
**When** Story 3.1 completes
**Then** `harness/fixtures/{electrumx_a,electrumx_b,fulcrum,mempool_electrs,blockstream_electrs,bitcoin_core}/` each contain a frozen-version `Dockerfile` (or pinned image tag) and minimal config for a regtest-or-mainnet-readonly Bitcoin Core + each Electrum-class frontend, plus a top-level `harness/docker-compose.yaml` orchestrating all six containers on a private Docker network (FR24, AR37, LB#2)
**And** `src/electrum_sybil_detector/harness/multi_frontend_matrix.py` exposes `bringup() -> MatrixHandle`, `teardown(handle) -> None`, and `query_fee_histogram(handle, frontend: str) -> list[tuple[float, int]]` — connecting to each frontend over the Docker network and pulling its `mempool.get_fee_histogram` response
**And** `src/electrum_sybil_detector/harness/fee_histogram_drift.py` exposes a `calibrate(samples: int = 1000, refresh_interval_s: int = 30) -> CalibrationReport` function that, over `samples` time-steps, queries `mempool.get_fee_histogram` from all 5 frontends and computes pairwise 1-D Wasserstein distance via `scipy.stats.wasserstein_distance` (D5.1, AR23) — producing the per-pair distance distribution plus per-pair summary statistics (median, p95, p99, max)
**And** the calibration output writes to `selftest/thresholds.yaml` under key `fee_histogram_wasserstein_threshold` the configurable percentile (default p95) of the pooled distribution; each threshold row carries calibration metadata (sample count, harness version, frontend versions, Bitcoin Core version, calibration timestamp, `derived_run_id`)
**And** the same code path supports a `--mode=ci` invocation that runs against a smaller fixture (e.g., 60 samples) and compares the observed Wasserstein distribution to the calibrated baseline — exits 0 if within tolerance (default: pooled p95 within ±20% of calibrated baseline), exits 1 with diagnostic on drift (recurring CI drift-detection per AR37)
**And** `harness/docker-compose.yaml` is documented in `docs/methodology.md` Appendix as the canonical pre-launch calibration procedure; the run is reproducible by any Path 2 reproducer with Docker access
**And** `tests/harness/test_fee_histogram_drift.py` verifies (a) `calibrate` produces a non-empty `CalibrationReport` against a mocked matrix fixture, (b) `--mode=ci` exits 0 when within tolerance and exits 1 with diagnostic on simulated drift, (c) the output `thresholds.yaml` row schema validates
**Given** the 5-frontend matrix produces bit-identical fee-histogram outputs for two replicated ElectrumX instances
**When** the harness measures their pairwise Wasserstein distance
**Then** the distance is exactly 0 — and the calibration documentation in `docs/bmad-binnacle/03_phase1-validations.md` is updated to reflect that bit-identity is achievable for replicated frontends, while the broader cross-implementation drift bound is the calibrated value (sealing the binary question vs. drift-magnitude question per Phase-1 closeout)

### Story 3.2: Derived-tier scaffolding — `derived_run_id`, frozen `thresholds.yaml`, statistical-rigor utilities

As **every subsequent Epic 3 analysis story (3.3–3.9)**,
I want **the `Analyzer` Protocol surface, the `derived_run_id` stamping discipline, the BH-FDR / bootstrap-CI / power-analysis utility module, and the `selftest/thresholds.yaml` schema (frozen pre-M3 by Story 3.10)**,
So that **every derived-tier write in Epic 3 is reproducibility-stamped, every cluster claim has the statistical-rigor primitives available, and the methodology parameter file (thresholds) lives under git version control rather than as environment-variable post-hoc tuning vectors**.

**Acceptance Criteria:**

**Given** the Storage Protocol from Story 1.5 + the M2 dataset substrate from Epic 2
**When** Story 3.2 completes
**Then** `src/electrum_sybil_detector/analysis/__init__.py` exports an `Analyzer` Protocol class with async methods `compute(window_id: int, derived_run_id: str) -> AnalysisReport` and `register_derived_table(name: str, schema: dict) -> None` (AR8)
**And** `src/electrum_sybil_detector/analysis/derived_run.py` exports `make_derived_run_id(code_hash: str, raw_input_fingerprint: str, run_timestamp_ns: int) -> str` returning `BLAKE2b-256(code_hash || raw_input_fingerprint || run_timestamp_ns)` as 64-char hex (AR15)
**And** `src/electrum_sybil_detector/analysis/statistical_rigor.py` exports: `benjamini_hochberg_fdr(p_values: ArrayLike, alpha: float = 0.05) -> ArrayLike`, `bootstrap_ci(samples: ArrayLike, statistic: Callable, n_resamples: int = 10_000, ci: float = 0.95, seed: int) -> tuple[float, float]`, `power_analysis(effect_size: float, n: int, alpha: float = 0.05) -> float` — all using `numpy.random.default_rng(seed=seed)` for reproducibility (AR25, D5.7, D5.8)
**And** `selftest/thresholds.yaml` schema is declared with top-level keys: `fee_histogram_wasserstein_threshold` (Story 3.1 source), `pairwise_delta_variance_threshold` (Story 3.7 source), `pairwise_wasserstein_threshold` (Story 3.7 source), `pairwise_sync_downtime_threshold` (Story 3.7 source), each with sub-keys `value`, `calibration_source`, `calibration_run_id`, `calibrated_at_ns`, `frozen` (bool, set true by Story 3.10 git-tag)
**And** `migrations/timescaledb/0003_derived_runs.sql` (and matching `migrations/sqlite/0011_derived_runs.sql`) creates `derived_runs (derived_run_id TEXT PRIMARY KEY, code_hash TEXT NOT NULL, raw_input_fingerprint TEXT NOT NULL, run_timestamp_ns BIGINT NOT NULL, analyzer_version TEXT NOT NULL, schema_version INTEGER NOT NULL)` and per-signal derived tables `pairwise_delta_variance`, `pairwise_wasserstein`, `pairwise_sync_downtime`, `cluster_candidates`, `cluster_assignments`, `baseline_distributions`, `fork_race_windows` — each carrying `derived_run_id TEXT NOT NULL`, `code_hash TEXT NOT NULL`, plus signal-specific columns (FR14)
**And** all derived tables have an index on `derived_run_id` for query filtering; querying any derived table without filtering by `derived_run_id` is a code-review violation (AR15)
**And** `tests/analysis/test_derived_run.py` verifies (a) `make_derived_run_id` is deterministic and BLAKE2b-256 length, (b) two runs with the same inputs but different timestamps produce different IDs, (c) the same inputs produce the same hash byte-for-byte
**And** `tests/analysis/test_statistical_rigor.py` verifies BH-FDR matches `scipy.stats.false_discovery_control(method='bh')` reference output, bootstrap-CI is reproducible across runs with the same seed, power-analysis matches `statsmodels` reference output to 3 decimal places
**Given** any derived-tier write attempts to bypass the `derived_run_id` stamp
**When** the row is inserted
**Then** the Storage Protocol surface rejects the insert (NOT NULL constraint at the SQL level enforces; tested in `tests/storage/test_derived_run_id_required.py`)

### Story 3.3: Fork-race event ingestion from `bitcoin-data/stale-blocks` + `fork-observer` cross-check

As **the pairwise-delta variance story (3.4)**,
I want **fork-race events ingested from a pinned version of `bitcoin-data/stale-blocks` with a configurable per-event time window, optionally cross-checked against `fork-observer` HTTP/JSON output**,
So that **Story 3.4 has a derived `fork_race_windows` table with `window_start_monotonic_ns / window_end_monotonic_ns / event_metadata` to scope its variance computation, and LB#1 (stale-blocks cadence verification) is closed at production scale**.

**Acceptance Criteria:**

**Given** the derived-tier scaffolding from Story 3.2
**When** Story 3.3 completes
**Then** `src/electrum_sybil_detector/analysis/fork_race_events.py` exports `ingest_stale_blocks(version: str, window_seconds: int = 60) -> int` returning the number of fork-race windows persisted (FR17)
**And** `bitcoin-data/stale-blocks` is pinned to a specific dataset version in `pyproject.toml [tool.electrum_sybil_detector.datasets]` table (e.g., `stale_blocks = "v2026.04"`); the version pin is documented in `docs/methodology.md` and surfaces in the `manifest.json` (Epic 4 hook)
**And** `ingest_stale_blocks` (a) downloads the pinned dataset version (or reads a vendored copy in `src/electrum_sybil_detector/analysis/fixtures/stale_blocks_<version>.csv` if offline-mode is configured), (b) filters events to those within the M3 dataset collection window, (c) for each event computes `(window_start_monotonic_ns, window_end_monotonic_ns)` as `(event_wall_clock_ns - window_seconds*1e9, event_wall_clock_ns + window_seconds*1e9)` mapped through the per-window NTP manifest (Story 1.11) into monotonic-ns space, (d) persists each window to `fork_race_windows` derived table stamped with `derived_run_id + code_hash`
**And** the wall-clock → monotonic-ns mapping discipline is documented: events from `stale-blocks` are wall-clock-stamped (external dataset); the mapping uses the per-collection-window NTP manifest to convert; the mapping introduces a known wall-clock-drift uncertainty of `drift_bound_ns` from the manifest, which is preserved as a `mapping_uncertainty_ns BIGINT` column on `fork_race_windows` (NFR1 invariant — wall-clock used only when no monotonic source exists, with explicit uncertainty)
**And** an optional `--cross-check-fork-observer URL` flag queries `fork-observer`'s HTTP/JSON tip-tracking endpoint for the same time range and warns (does not fail) on event-set mismatches between the two sources (AR27 — read-only consumption of fork-observer)
**And** `tests/analysis/test_fork_race_events.py` verifies (a) ingestion of a 3-event mock stale-blocks fixture produces 3 `fork_race_windows` rows, (b) re-running with the same `derived_run_id` is idempotent (no duplicates), (c) the cross-check flag emits a warning on simulated mismatch without raising
**And** LB#1 (stale-blocks cadence) is re-verified at this story's completion: the 3–8/month cadence claim is checked against the most recent 6 months of the pinned dataset version; result captured in `docs/bmad-binnacle/10_lb1_production_recheck.md`
**Given** the pinned `bitcoin-data/stale-blocks` version is updated upstream
**When** the project bumps the version pin
**Then** the new pin is treated as a methodology-affecting change and triggers a `pattern:` PR per architecture.md L543 (pre-M3 lock)

### Story 3.4: Per-pair pairwise-delta variance over fork-race windows

As **the multi-signal threshold engine (Story 3.8)**,
I want **per-server-pair monotonic-ns-delta variance computed across all fork-race windows from Story 3.3, derived from each pair's first `headers.subscribe` notification of the new tip within each window**,
So that **the load-bearing fork-race timing-variance backend-state signal (the methodological spine per PRD §Innovation) is materialized as a derived-tier feature ready for Story 3.7 to noise-floor-baseline and Story 3.8 to threshold-classify**.

**Acceptance Criteria:**

**Given** the derived-tier scaffolding from Story 3.2 + fork-race windows from Story 3.3 + `block_notifications` raw rows from Epic 1 Story 1.7
**When** Story 3.4 completes
**Then** `src/electrum_sybil_detector/analysis/pairwise_delta.py` exports `compute_pairwise_delta_variance(derived_run_id: str, fork_race_window_id: int) -> int` returning the number of pair-rows persisted (FR18, D5.2)
**And** for each `fork_race_window`, the function (a) selects the FIRST `block_notifications` row per server within the window (matching the new tip's `block_hash`), (b) for every server pair `(A, B)` computes `delta_ns = monotonic_ns_A - monotonic_ns_B`, (c) accumulates per-pair deltas across ALL fork-race windows, (d) computes per-pair variance via `numpy.var(deltas, ddof=1)` (sample variance), (e) persists one row per pair to `pairwise_delta_variance(derived_run_id TEXT, code_hash TEXT, server_a_id TEXT, server_b_id TEXT, n_events INTEGER, mean_delta_ns REAL, variance_ns2 REAL, sample_std_ns REAL)` ordered by `(server_a_id, server_b_id)` with `server_a_id < server_b_id` (canonical pair ordering)
**And** monotonic_ns computation discipline is enforced: only `monotonic_ns` columns participate in delta arithmetic; `wall_clock_ns` is never read by this module (NFR1, AR12 invariant verified by `mypy --strict` ban on `wall_clock_ns` imports in `pairwise_delta.py` plus a unit test asserting the function does not read wall_clock_ns)
**And** server pairs with `n_events < min_events_per_pair` (default 5; configurable per derived run) are persisted with `variance_ns2 = NULL` and a `low_event_count` flag — they are NOT silently dropped
**And** the function uses pandas DataFrames internally for groupby + variance computation (D5.2); output uses canonical ordering and sorted-key dict iteration (D5.8 determinism)
**And** `tests/analysis/test_pairwise_delta.py` verifies (a) two synthetic same-backend pairs (delta variance ≈ 0) vs. two synthetic independent-backend pairs (delta variance >> 0) are correctly distinguished, (b) the `n_events < threshold` low-event-count path is honored, (c) re-running with the same `derived_run_id` produces bit-identical numeric output (NFR15 invariant verified at the per-story level)
**Given** a future per-column floating-point tolerance is needed for `variance_ns2`
**When** Story 3.10 documents tolerances
**Then** the tolerance bound is recorded in `selftest/tolerance.yaml` keyed `pairwise_delta_variance.variance_ns2`

### Story 3.5: 1-D Wasserstein distance over fee-rate CDFs

As **the multi-signal threshold engine (Story 3.8)**,
I want **per-server-pair 1-D Wasserstein distance computed over their `mempool.get_fee_histogram` outputs across a configurable time window, using the canonical `scipy.stats.wasserstein_distance` implementation (no re-implementation)**,
So that **the second backend-state signal (fee-histogram correlation, downgraded from "bit-identity" to "Wasserstein-distance" per Phase-1 closeout) is materialized as a derived-tier feature with the canonical metric — and Story 3.7 can baseline-noise-floor it, Story 3.8 can threshold-classify it against the calibrated value from Story 3.1**.

**Acceptance Criteria:**

**Given** the derived-tier scaffolding from Story 3.2 + `fee_histograms` raw rows from Epic 2 Story 2.3 + the calibrated threshold from Story 3.1's `selftest/thresholds.yaml`
**When** Story 3.5 completes
**Then** `src/electrum_sybil_detector/analysis/wasserstein.py` exports `compute_pairwise_wasserstein(derived_run_id: str, window_start_monotonic_ns: int, window_end_monotonic_ns: int, sampling_interval_seconds: int = 300) -> int` returning the number of pair-rows persisted (FR19, AR23, D5.1)
**And** for each `(server_a, server_b)` pair, the function (a) selects all `fee_histograms` rows from both servers within the window at the configured sampling interval (default every 5 min, matching Epic 2 Story 2.3's polling cadence), (b) for each time-aligned snapshot pair, computes `scipy.stats.wasserstein_distance(u_values, u_weights, v_values, v_weights)` where `u_values, v_values` are the fee-rate bins parsed from `histogram_json` and `u_weights, v_weights` are the corresponding vsize weights, (c) summarizes per-pair distances with `mean_wasserstein` and `p95_wasserstein` and `n_snapshot_pairs`, (d) persists to `pairwise_wasserstein(derived_run_id TEXT, code_hash TEXT, server_a_id TEXT, server_b_id TEXT, n_snapshot_pairs INTEGER, mean_wasserstein REAL, p95_wasserstein REAL)` with canonical pair ordering
**And** the function uses ONLY `scipy.stats.wasserstein_distance` for the metric (D5.1, AR23 — no re-implementation); a unit test asserts the function does not import any other Wasserstein/EMD library
**And** snapshot pairs where one or both histograms are empty (NULL `histogram_json` or zero bins) are persisted with `mean_wasserstein = NULL` and a `null_histogram` flag — they are NOT silently substituted with 0 or imputed
**And** `tests/analysis/test_wasserstein.py` verifies (a) two identical histograms produce distance 0, (b) a known toy example (e.g., uniform vs. point-mass) produces the closed-form distance to 6 decimal places, (c) re-running with the same `derived_run_id` produces bit-identical numeric output (FP tolerance for Wasserstein on real data documented in Story 3.10's `tolerance.yaml`)
**And** the output schema is documented in `docs/schema/schema.en.md` and mirrored in `docs/schema/schema.es.md` (bilingual scaffold per Epic 6)

### Story 3.6: Synchronized-downtime detection via interval-overlap

As **the multi-signal threshold engine (Story 3.8)**,
I want **per-server-pair synchronized-downtime overlap computed via interval-overlap algorithm over each pair's downtime intervals (derived from `connection_events` `disconnected → reconnected` pairs from Epic 1 Story 1.8 plus gaps from Epic 2 Story 2.4)**,
So that **the third backend-state signal (synchronized downtime as a same-fleet indicator) is materialized as a derived-tier feature without requiring a graph-theory framework at M3 scale (D5.3)**.

**Acceptance Criteria:**

**Given** the derived-tier scaffolding from Story 3.2 + `connection_events` raw rows from Epic 1 + `gaps` derived rows from Epic 2 Story 2.4
**When** Story 3.6 completes
**Then** `src/electrum_sybil_detector/analysis/synchronized_downtime.py` exports `compute_pairwise_sync_downtime(derived_run_id: str, window_start_monotonic_ns: int, window_end_monotonic_ns: int) -> int` returning the number of pair-rows persisted (FR20, D5.3)
**And** for each server, the function (a) constructs a list of downtime `Interval(start_ns, end_ns)` objects from `connection_events` `disconnected → reconnected` consecutive pairs and from `gaps` rows whose `gap_duration_ns > sync_downtime_min_gap_ns` (default 60s, configurable), (b) sorts intervals by `start_ns`, (c) for each pair `(server_a, server_b)` computes total overlap duration via a linear interval-overlap sweep, (d) computes overlap fraction as `total_overlap_ns / max(server_a_total_downtime_ns, server_b_total_downtime_ns)`, (e) persists to `pairwise_sync_downtime(derived_run_id TEXT, code_hash TEXT, server_a_id TEXT, server_b_id TEXT, n_intervals_a INTEGER, n_intervals_b INTEGER, total_overlap_ns BIGINT, overlap_fraction REAL)` with canonical pair ordering
**And** the implementation uses stdlib + numpy only — no `networkx`, no `intervaltree` library (D5.3 — graph-theory framework not needed at M3 scale; documented in module docstring)
**And** server pairs where either side has zero downtime intervals in the window are persisted with `overlap_fraction = NULL` and a `no_downtime_data` flag — NOT silently set to 0 or excluded
**And** `tests/analysis/test_synchronized_downtime.py` verifies (a) two pairs with identical downtime intervals produce overlap_fraction = 1.0, (b) two pairs with disjoint downtime intervals produce overlap_fraction = 0.0, (c) a pair with partial overlap matches the closed-form expected fraction to 6 decimal places, (d) re-running with the same `derived_run_id` is bit-identical
**And** the algorithm runtime is `O((n_a + n_b) log(n_a + n_b))` per pair (interval sort dominates), keeping Story 3.10's NFR4 ≤30 min CI budget headroom

### Story 3.7: Baseline noise-floor distribution from declared independent-server set

As **the multi-signal threshold engine (Story 3.8)**,
I want **per-signal noise-floor reference distributions bootstrapped from a curated set of known-independent server pairs, with permutation tests producing the null distribution and threshold percentiles written to `selftest/thresholds.yaml`**,
So that **Story 3.8 has empirical thresholds rooted in observed noise rather than guessed cutoffs — and the per-signal threshold values are auditable against the `independent_servers.yaml` curation source (AR — pre-commit-as-discipline)**.

**Acceptance Criteria:**

**Given** the per-signal derived tables `pairwise_delta_variance`, `pairwise_wasserstein`, `pairwise_sync_downtime` populated by Stories 3.4–3.6
**When** Story 3.7 completes
**Then** `src/electrum_sybil_detector/analysis/independent_servers.yaml` is created with a manually-curated declaration of known-independent server pairs, each entry carrying `(server_a_host, server_b_host, evidence: str, declared_by: str, declared_at: str)` — the evidence field documents WHY the pair is treated as independent (e.g., "different operators per public Twitter, different ASNs per Story 2.2 enrichment, different jurisdictions"); bilingual review note in `docs/methodology.md` directs Path 2 reproducers to maintain their own list (FR22)
**And** `src/electrum_sybil_detector/analysis/baseline_distribution.py` exports `compute_baseline_distributions(derived_run_id: str, n_bootstrap: int = 10_000, percentile: float = 95.0, seed: int) -> BaselineReport` returning per-signal threshold values
**And** for each backend-state signal (delta variance, Wasserstein, sync-downtime), the function (a) selects pair-rows from the corresponding derived table where both servers appear in `independent_servers.yaml`, (b) bootstraps `n_bootstrap` resamples of the signal value distribution via `numpy.random.default_rng(seed)`, (c) computes the configured `percentile` (default 95th) of the pooled bootstrap distribution as the per-signal noise-floor threshold, (d) runs a permutation test producing the null-hypothesis p-value distribution, (e) persists per-signal `baseline_distributions(derived_run_id TEXT, code_hash TEXT, signal_name TEXT, percentile REAL, threshold_value REAL, n_bootstrap INTEGER, n_independent_pairs INTEGER, permutation_test_p_value REAL, seed INTEGER)` rows
**And** the threshold values are written to `selftest/thresholds.yaml` under their corresponding keys (`pairwise_delta_variance_threshold`, `pairwise_wasserstein_threshold`, `pairwise_sync_downtime_threshold`) with `calibration_source = "story_3_7_baseline_distribution"`, `calibration_run_id = <derived_run_id>`, `calibrated_at_ns = <now>`, `frozen = false` (frozen flips to true in Story 3.10)
**And** the `seed` parameter is an explicit per-run argument (not `seed=0` default for production) and is logged in the resulting `derived_runs` row's analyzer config — production calibration runs use a per-run seed captured in the manifest (D5.8)
**And** `tests/analysis/test_baseline_distribution.py` verifies (a) bootstrap resampling is reproducible with the same seed, (b) two known-independent pair fixtures produce a tight noise-floor distribution while a synthetic same-backend pair would lie far above the 95th percentile, (c) the permutation-test p-value is in [0, 1] and matches a `scipy.stats.permutation_test` reference for a small fixture
**Given** a future Path 2 reproducer extends `independent_servers.yaml` with additional pairs from a different vantage
**When** they re-run baseline computation
**Then** the additional pairs strengthen the noise floor (more independent samples) without invalidating prior calibration runs (multi-vantage-additive property per PRD §Innovation)

### Story 3.8: Multi-signal threshold engine — frozen rule classification

As **the clustering story (3.9) and downstream Lukas (analyst)**,
I want **a rule engine that classifies each candidate cluster as `finding` / `candidate-for-reproduction` / `below-threshold` based on the pre-committed multi-signal threshold (≥2 backend-state signals + ≥1 frontend-config signal), with thresholds loaded from frozen `selftest/thresholds.yaml`**,
So that **Story 3.9's clustering operates on threshold-classified candidates rather than raw similarity scores — preserving the pre-commit-as-discipline innovation (PRD §Innovation IQ4) and preventing post-hoc threshold tuning that would weaken the methodology paper's evidentiary claims**.

**Acceptance Criteria:**

**Given** per-signal derived tables `pairwise_delta_variance` (Story 3.4), `pairwise_wasserstein` (Story 3.5), `pairwise_sync_downtime` (Story 3.6) + thresholds in `selftest/thresholds.yaml` from Stories 3.1 + 3.7 + frontend-config signals (banner, version, ASN, donation_address) in raw-tier rows from Epic 2 Stories 2.2 + 2.3
**When** Story 3.8 completes
**Then** `src/electrum_sybil_detector/analysis/multi_signal_threshold.py` exports `classify_cluster_candidates(derived_run_id: str) -> ClassificationReport` returning counts per classification bucket (FR21, AR24, D5.4)
**And** for every server pair from the per-signal derived tables, the function (a) loads thresholds from `selftest/thresholds.yaml` and ASSERTS that `frozen = true` for the M3 launch run (raises `AnalysisError` otherwise, allowing pre-launch dry-runs but blocking publishable runs against unfrozen thresholds), (b) checks each backend-state signal: delta_variance pair PASSES threshold IF `variance_ns2 ≤ threshold_value`; Wasserstein pair PASSES IF `mean_wasserstein ≤ threshold_value`; sync-downtime pair PASSES IF `overlap_fraction ≥ threshold_value`, (c) checks frontend-config signals: banner-match (string equality on `connection_events.banner` over window), version-match (`server_metadata.protocol_version_min/max` equality), ASN-match (`connection_events.resolved_ip_asn` equality), donation-address-match (`server_metadata.donation_address` equality), (d) classifies the pair: `finding` if ≥2 backend-state PASS AND ≥1 frontend-config matches; `candidate-for-reproduction` if exactly 1 backend-state PASSES (regardless of frontend) or if all backend-state PASS but no frontend-config matches; `below-threshold` otherwise, (e) persists to `cluster_candidates(derived_run_id TEXT, code_hash TEXT, server_a_id TEXT, server_b_id TEXT, classification TEXT, backend_state_pass_count INTEGER, frontend_config_match_count INTEGER, backend_state_signals_passed JSON, frontend_config_signals_matched JSON)` with canonical pair ordering
**And** the threshold-loading code asserts `frozen` and the source-of-truth thresholds file path is `selftest/thresholds.yaml` (not env vars per AR rule "no environment variables for thresholds or methodology parameters")
**And** the rule logic is documented in `docs/methodology.md` §Multi-Signal Threshold with a worked example for each of the three classifications
**And** `tests/analysis/test_multi_signal_threshold.py` verifies (a) a synthetic pair with 2 backend-state passes + 1 frontend-config match → `finding`, (b) a synthetic pair with 1 backend-state pass + N frontend-config matches → `candidate-for-reproduction`, (c) a synthetic pair with 0 backend-state passes → `below-threshold`, (d) attempting to run against unfrozen thresholds raises `AnalysisError`, (e) re-running with the same `derived_run_id` is bit-identical
**Given** Lukas wants to re-run the engine with different thresholds for sensitivity analysis
**When** he forks `selftest/thresholds.yaml` to a non-default path and runs in `--dry-run --thresholds-file=<path>` mode
**Then** the engine runs with the alternative thresholds, classifications are written to a separate `derived_run_id`, and the run is explicitly marked as `dry_run = true` in the `derived_runs` row (NOT publishable; the M3 launch run requires the frozen canonical thresholds)

### Story 3.9: DBSCAN + Ward clustering with BH-FDR + bootstrap CIs + power analysis

As **downstream Lukas (analyst) and Sarah (citation reader)**,
I want **DBSCAN clustering (primary) and Ward hierarchical clustering (secondary, for sensitivity analysis) on the weighted similarity matrix from Stories 3.4–3.6, with Benjamini–Hochberg FDR correction across all cluster claims and bootstrap CIs on every claim, plus power analysis disclosed for the M3 dataset window**,
So that **the methodology output is a set of statistically-rigorous cluster assignments (per FR23 + PRD §Compliance > rigor.statistical_methodology carve-out) ready for Story 3.10's ship-readiness gate and Epic 4's publication bundle**.

**Acceptance Criteria:**

**Given** `cluster_candidates` from Story 3.8 + statistical-rigor utilities from Story 3.2
**When** Story 3.9 completes
**Then** `src/electrum_sybil_detector/analysis/clustering.py` exports `cluster(derived_run_id: str, primary_algorithm: Literal["dbscan"] = "dbscan", sensitivity_algorithm: Literal["ward"] = "ward", fdr_alpha: float = 0.05, bootstrap_ci_resamples: int = 10_000, seed: int) -> ClusteringReport` returning the number of clusters per algorithm + power-analysis output (FR23, AR25, D5.6)
**And** the function (a) constructs a weighted similarity matrix `S` over all server pairs where `S[a, b]` is a configurable composite of delta_variance + Wasserstein + sync-downtime values from Stories 3.4–3.6 (composite weights documented in `selftest/thresholds.yaml` and frozen pre-M3), restricted to pairs classified as `finding` OR `candidate-for-reproduction` from Story 3.8, (b) runs `sklearn.cluster.DBSCAN` (eps and min_samples loaded from `selftest/thresholds.yaml`) producing primary cluster labels, (c) runs `sklearn.cluster.AgglomerativeClustering(linkage='ward')` producing secondary cluster labels for sensitivity analysis, (d) for each primary cluster, computes p-value via permutation test against the noise-floor distribution from Story 3.7's `baseline_distributions`, (e) applies `benjamini_hochberg_fdr` from Story 3.2 across all per-cluster p-values with `alpha = fdr_alpha`, (f) computes bootstrap CIs on each cluster's mean composite-similarity-score with `bootstrap_ci_resamples` and the explicit `seed`, (g) persists to `cluster_assignments(derived_run_id TEXT, code_hash TEXT, server_id TEXT, primary_cluster_id INTEGER, secondary_cluster_id INTEGER, cluster_p_value REAL, cluster_p_value_fdr_corrected REAL, cluster_mean_similarity REAL, cluster_ci_low REAL, cluster_ci_high REAL, cluster_n_servers INTEGER, fdr_significant BOOLEAN)`
**And** dependencies in `pyproject.toml`: `scikit-learn>=1.6,<2.0`, `numpy`, `scipy`, `pandas`, `pyarrow` — explicitly NOT `cython`, NOT `numba` (D5.9, AR26 — pure Python at M3; verified by `tests/test_pure_python_dependency_audit.py` running `pip-licenses` or `uv tree` and asserting no native-code analytical deps in the runtime closure)
**And** primary vs. secondary cluster agreement (Adjusted Rand Index) is computed and disclosed in the report — divergence > 0.2 is flagged as a sensitivity-analysis caveat in `docs/methodology.md`
**And** power analysis is computed for the M3 dataset window: `power_analysis(effect_size, n_servers, fdr_alpha)` from Story 3.2 — output disclosed in `docs/methodology.md` §Statistical Validity AND in the dataset `manifest.json` (Epic 4 hook), per PRD §Statistical Validity carve-out
**And** `tests/analysis/test_clustering.py` verifies (a) a synthetic same-backend cluster (3 servers with low pairwise variances) produces a primary cluster labeled `0` with bootstrap-CI containing the synthetic similarity, (b) DBSCAN noise points (no cluster) get `primary_cluster_id = -1` per scikit-learn convention, (c) re-running with the same `seed` and `derived_run_id` produces bit-identical labels and bit-identical bootstrap CIs (FP tolerance documented per column in Story 3.10's `tolerance.yaml`)
**Given** the primary DBSCAN result diverges from the secondary Ward result by ARI < 0.8 (low agreement)
**When** the report is generated
**Then** the divergence is flagged as a `LOW_PRIMARY_SECONDARY_AGREEMENT` warning in the report and surfaces in `docs/methodology.md` for reviewer transparency

### Story 3.10: M3 analysis-pipeline ship-readiness gate

As **Ifuensan (the maintainer) and Epic 4 (Publication)**,
I want **the analysis pipeline run end-to-end against the M2 production dataset snapshot, `selftest/thresholds.yaml` git-tagged frozen-pre-M3 with calibration sources documented per signal, the reproducibility self-test (Story 1.9) extended to cover analysis, per-column FP tolerance documented, pure-Python verified, and the priority-1 launch-blocker cluster re-evaluated**,
So that **the M3 ship-readiness gate (AR26 + AR42 + AR44 priority-1) is empirically closed and Epic 4 can begin packaging the citable bundle on a stable methodology substrate**.

**Acceptance Criteria:**

**Given** Stories 3.1–3.9 complete + the M2 production dataset snapshot from Epic 2 Story 2.9
**When** Story 3.10 completes
**Then** the full analysis pipeline (Stories 3.3 → 3.4 → 3.5 → 3.6 → 3.7 → 3.8 → 3.9, with calibration values from Story 3.1) runs end-to-end against the M2 dataset snapshot on a workstation, producing one `cluster_assignments` derived-tier output per `derived_run_id`
**And** the pipeline runtime stays ≤ 30 minutes (NFR4) on the workstation; if exceeded, sample-based verification with documented sampling parameters is the documented fallback per NFR4
**And** `selftest/thresholds.yaml` has `frozen = true` set on every threshold key, with `calibration_source` populated per signal: `fee_histogram_wasserstein_threshold` ← `story_3_1_calibration_harness`; `pairwise_delta_variance_threshold`, `pairwise_wasserstein_threshold`, `pairwise_sync_downtime_threshold` ← `story_3_7_baseline_distribution`; the file is git-tagged `thresholds-frozen-pre-m3-<YYYYMMDD>` and the tag is documented in `docs/methodology.md`
**And** the reproducibility self-test from Story 1.9 (`python -m electrum_sybil_detector.selftest`) is extended to invoke the analysis pipeline against a frozen analysis fixture (`tests/fixtures/m3_analysis_input/`) and assert bit-identical output (or per-column FP tolerance), exiting 0 on success (NFR15 invariant extended to analysis)
**And** `selftest/tolerance.yaml` documents per-column FP tolerance for analysis derived columns where bit-identical reproduction is not achievable: `pairwise_delta_variance.variance_ns2`, `pairwise_wasserstein.{mean,p95}_wasserstein`, `pairwise_sync_downtime.overlap_fraction`, `cluster_assignments.{cluster_p_value, cluster_ci_low, cluster_ci_high, cluster_mean_similarity}` — each with documented bound (e.g., relative tolerance 1e-9) and rationale (e.g., "numpy/scipy floating-point summation order"); the tolerance bounds are tested in `tests/selftest/test_tolerance_bounds.py`
**And** pure-Python compliance (AR26) is verified: `tests/test_pure_python_dependency_audit.py` runs `uv tree` (or equivalent) and asserts no `cython`, `numba`, or compiled-from-source dependencies appear in the runtime closure; result captured in `docs/bmad-binnacle/11_m3_pure_python_audit.md`
**And** the priority-1 launch-blocker cluster (#11 b10c socialization → #2 fee-histogram → #8 fork-observer → #1 stale-blocks → #9 methodology-ancestor citations) is re-evaluated: each item's status (cleared / pending / blocked) is recorded in the launch-blocker tracker (Epic 7 Story 7.3 surface); LB#2 is explicitly cleared by Story 3.1 + this gate; LB#1 is explicitly cleared by Story 3.3
**And** the M3 ship-readiness package is captured in `docs/bmad-binnacle/12_m3_ship_readiness.md` documenting: pipeline runtime, per-cluster `derived_run_id`, frozen thresholds tag, tolerance bounds, pure-Python audit result, LB statuses; this document is the hand-off artifact to Epic 4
**Given** any gate criterion fails (e.g., self-test fails on analysis fixture; tolerance bound violated; pure-Python audit shows native dep)
**When** the ship-readiness review is conducted
**Then** the gate is recorded as NOT cleared, blockers are itemized in `docs/bmad-binnacle/12_m3_ship_readiness.md`, and Epic 4 work does not begin until the gate clears

---

## Epic 4: Citable Dataset Bundle Publication (M3 launch)

Lukas / Sarah can cite the dataset by Zenodo DOI from the arXiv preprint; the `bitcoin-data` PR is accepted; the M3 release ships as a Parquet snapshot + `manifest.json` + LaTeX source + bit-identical re-derivation self-test that any reviewer can re-run independently. Three-tier archival operational; release pipeline gated on reproducibility self-test (Story 4.3) + phrasing-bank audit (Epic 5) + bilingual mirror parity (Epic 6). M3 launch gate (AR43) is cleared at the end of the epic.

### Story 4.1: Parquet snapshot generator (Tier 1: `bitcoin-data` GitHub conventions)

As **Ifuensan (the maintainer) and downstream Lukas (analyst)**,
I want **a Parquet snapshot generator that exports raw + derived tiers via `pyarrow 24.x` with Zstandard compression, with per-table file naming + directory layout matching `bitcoin-data` repository conventions (mirroring residents like `stale-blocks`, `mining-pools`, `block-arrival-times`)**,
So that **the dataset is publishable in the canonical format the target research community already consumes — closing the format-conformance prerequisite for Story 4.4's `bitcoin-data` PR — and the ~6 GB/year compressed envelope (NFR11) is realized in practice**.

**Acceptance Criteria:**

**Given** the M3 derived-tier output from Epic 3 Story 3.9 + the M2 raw-tier substrate from Epic 2
**When** Story 4.1 completes
**Then** `src/electrum_sybil_detector/publication/parquet_snapshot.py` exports `generate_snapshot(window_id: int, output_dir: Path, dataset_version: str, derived_run_id: str) -> SnapshotReport` returning the per-table file paths and per-file byte sizes (FR25, AR18)
**And** for each raw-tier table (`servers`, `connection_events`, `block_notifications`, `server_metadata`, `fee_estimates`, `relay_fees`, `fee_histograms`, `availability`, `gaps`, `ntp_window_manifest`) and each derived-tier table (`fork_race_windows`, `pairwise_delta_variance`, `pairwise_wasserstein`, `pairwise_sync_downtime`, `cluster_candidates`, `cluster_assignments`, `baseline_distributions`, `derived_runs`), the function exports one Parquet file per table per window
**And** Parquet files use `pyarrow 24.x` with `compression='zstd'`, `compression_level=19` (matches manifest schema from Story 3.2 + AR18); column types preserve `BIGINT` for `*_ns` columns (Parquet INT64) and `TEXT` for opaque hashes (Parquet UTF8)
**And** the output directory layout matches `bitcoin-data` conventions: `<output_dir>/<dataset_version>/<table_name>.parquet` with a top-level `<output_dir>/<dataset_version>/README.md` (English) + `README.es.md` (Spanish mirror per Epic 6) + `<output_dir>/<dataset_version>/CHANGELOG.md` (conventional-commits-style entry for this version)
**And** the README scaffold cites the `bitcoin-data` repository conventions, declares the CC BY 4.0 license, and links to the methodology paper + Zenodo DOI placeholder (filled in by Story 4.5)
**And** the CHANGELOG entry is appended (not overwritten) on each new dataset version, recording: dataset version, code hash, raw-input fingerprint, NTP stratum, window boundaries, summary row counts per table, schema-version deltas vs. prior release (FR14 forward-compat narrative)
**And** total compressed snapshot size for the M3 dataset window is ≤ 500 MB (extrapolation: ~6 GB/year ÷ 12 = ~500 MB/month per NFR11 — verified empirically on the M2 dataset substrate)
**And** `tests/publication/test_parquet_snapshot.py` verifies (a) every table from Stories 1.5, 2.4, 2.7, 2.8, 3.2 is exported, (b) round-trip read via `pyarrow.parquet.read_table` recovers exact row content (no precision loss for `monotonic_ns`/`wall_clock_ns` BIGINT, no encoding drift for hex hash strings), (c) the directory layout matches the `bitcoin-data` reference layout fixture in `tests/fixtures/bitcoin_data_layout/`, (d) re-running with the same `derived_run_id` is byte-identical (NFR15 prerequisite for Story 4.3's full bit-identical gate)
**Given** a future `bitcoin-data` upstream convention change (e.g., new directory rule)
**When** the project bumps its conformance to the new convention
**Then** the layout test fixture is updated and a `pattern:` PR is opened per architecture.md L543 (forward-compat narrative captured in CHANGELOG)

### Story 4.2: `manifest.json` builder

As **the bit-identical re-derivation ship gate (Story 4.3) and downstream reviewers**,
I want **a `manifest.json` per release declaring `code_hash`, `raw_input_fingerprint`, `ntp_stratum`, `window_boundaries`, `dataset_version`, `release_timestamp_ns`, `zenodo_doi` (placeholder until Story 4.5), `schema_version`, `compression`, and `manifest_version: 1`**,
So that **every dataset release carries the reproducibility fingerprint Story 4.3 verifies against, the Zenodo DOI Story 4.5 cross-references, and the human-readable release context any third-party reviewer needs to re-run the self-test independently**.

**Acceptance Criteria:**

**Given** the Parquet snapshot from Story 4.1 + `derived_run_id` discipline from Epic 3 Story 3.2
**When** Story 4.2 completes
**Then** `src/electrum_sybil_detector/publication/manifest.py` exports `build_manifest(snapshot_dir: Path, derived_run_id: str, dataset_version: str, zenodo_doi: str | None = None) -> dict` returning the manifest dictionary, and `write_manifest(manifest: dict, snapshot_dir: Path) -> Path` writing it to `<snapshot_dir>/manifest.json` (FR26)
**And** the manifest matches the schema defined in architecture.md L390–L410 exactly, with top-level keys: `manifest_version` (int, set to 1 for M3), `dataset_version` (semver string), `code_hash` (BLAKE2b-256 of the project source tree at release tag, format `blake2b-256:<hex>`), `raw_input_fingerprint` (BLAKE2b-256 of the sorted raw-tier file digests, same format), `ntp_stratum` (int, sourced from `ntp_window_manifest`), `ntp_canonical_source` (string), `window_boundaries` (object with `start_monotonic_ns`, `end_monotonic_ns`, `start_wall_clock_ns`, `end_wall_clock_ns` BIGINTs), `release_timestamp_ns` (BIGINT, from `time.time_ns()` at manifest build), `zenodo_doi` (string or null until Story 4.5 fills it in), `schema_version` (int, current schema version from `storage/schema.py`), `compression` (string, e.g., `"zstd:level=19"`)
**And** the manifest is JSON-serialized with `sort_keys=True, separators=(",", ":")` (sorted-key canonical form per AR14 / D5.8 — required for the `code_hash`/`raw_input_fingerprint` to be deterministic across re-runs)
**And** `code_hash` is computed via `find <project_root>/src -type f -name "*.py" | sort | xargs sha256sum | sha256sum`-equivalent in Python: walk `src/electrum_sybil_detector/` deterministically, BLAKE2b-256 each `.py` file, concatenate sorted-by-path digests, BLAKE2b-256 the concatenation; the algorithm is documented in `docs/methodology.md` §Reproducibility so any reviewer can recompute
**And** `raw_input_fingerprint` is computed analogously over the raw-tier Parquet file digests (sorted by table name) from Story 4.1's snapshot
**And** the manifest is itself part of the published dataset (per PRD §Reproducibility manifest per release) and citable; its file path appears in the dataset README from Story 4.1
**And** `tests/publication/test_manifest.py` verifies (a) the manifest schema matches the architecture-defined schema, (b) JSON serialization is sorted-key canonical, (c) `code_hash` is deterministic across re-runs given the same source tree, (d) `code_hash` changes when any `.py` file changes (verified by mutating one file and recomputing), (e) the `zenodo_doi` field accepts both `null` (pre-Story-4.5) and a valid DOI string (`10.5281/zenodo.XXXXXXX` format)
**Given** Story 4.5 mints a Zenodo DOI for this release
**When** the manifest is regenerated
**Then** the manifest's `zenodo_doi` field is populated and the manifest is re-emitted; the `code_hash` and `raw_input_fingerprint` are NOT recomputed (the manifest update is metadata-only and does not break the bit-identical contract — verified by Story 4.3's self-test treating `zenodo_doi` as an excluded-from-hash field documented in `selftest/manifest_excluded_fields.yaml`)

### Story 4.3: Bit-identical re-derivation ship gate (full NFR15 contract at M3 dataset scale)

As **Ifuensan (the maintainer), Lukas (peer reviewer), and the M3 release pipeline**,
I want **a self-test that re-derives the derived tier from the published raw tier + the published `code_hash`, compares to the manifest-recorded hashes, PASSES on bit-identical match (or within `selftest/tolerance.yaml` bounds from Story 3.10), FAILS the release on mismatch, with CI ≤30 min budget and sample-based fallback documented**,
So that **the NFR15 bit-identical contract is enforced at full M3 dataset scale (extending Story 1.9's M0 scaffold and Story 3.10's analysis-pipeline-only extension), closing LB#25 and giving every reviewer the ability to independently verify the dataset by re-running one command**.

**Acceptance Criteria:**

**Given** the Parquet snapshot from Story 4.1 + the manifest from Story 4.2 + the analysis pipeline + tolerance documentation from Epic 3 Story 3.10
**When** Story 4.3 completes
**Then** `src/electrum_sybil_detector/publication/self_test_gate.py` exports `verify_release(snapshot_dir: Path) -> VerificationReport` (FR27, NFR15)
**And** the function (a) reads `manifest.json` and extracts `code_hash`, `raw_input_fingerprint`, `dataset_version`, `derived_run_id`, (b) recomputes `code_hash` over the current source tree via the same algorithm as Story 4.2 and asserts byte-equality (raises `PublicationError` on mismatch — meaning the source tree at verification time does not match the source at snapshot time), (c) recomputes `raw_input_fingerprint` over the raw-tier Parquet files and asserts byte-equality (raises `PublicationError` on mismatch — raw inputs corrupted), (d) re-runs the full analysis pipeline (Stories 3.3 → 3.4 → 3.5 → 3.6 → 3.7 → 3.8 → 3.9) against the raw-tier Parquet files producing a fresh derived tier, (e) compares the fresh derived tier against the published derived-tier Parquet files using the per-column tolerance bounds from `selftest/tolerance.yaml` (Story 3.10), (f) returns `VerificationReport(status: "PASS"|"FAIL", per_table_diffs: list[TableDiff], runtime_seconds: float)`
**And** `verify_release` exits 0 when status == "PASS", exits 1 with diagnostic output (per-table-per-column diff summary) when status == "FAIL"
**And** `python -m electrum_sybil_detector.publication.self_test_gate <snapshot_dir>` is the canonical reviewer-runnable invocation; documented in the dataset README scaffold from Story 4.1 and reproduced in `scripts/verify_dataset.py` (per architecture.md L817)
**And** runtime stays ≤ 30 minutes on the AWS deploy host (NFR4); if exceeded, the function automatically falls back to sample-based verification (random-sample 10% of windows, parameter `sample_fraction` exposed) with the sampling parameters and seed logged in the `VerificationReport` (NFR4 fallback per AR)
**And** the self-test is wired into the M3 release CI workflow `ci/github-actions/release.yml`: triggered on git tag push matching `v*`, runs against the about-to-be-published snapshot, blocks the three-tier archival pipeline (Stories 4.4–4.6) on FAIL
**And** `tests/publication/test_self_test_gate.py` verifies (a) PASS path on a frozen reference snapshot in `tests/fixtures/m3_release_reference/`, (b) FAIL path triggered by mutating one derived-tier value beyond its tolerance bound, (c) FAIL path triggered by `code_hash` mismatch, (d) FAIL path triggered by `raw_input_fingerprint` mismatch, (e) sample-based fallback produces a deterministic subset given the same seed
**Given** a release attempts to publish without first running the self-test gate
**When** the CI workflow `release.yml` evaluates the release pipeline
**Then** Stories 4.4 / 4.5 / 4.6 jobs are conditional on `needs.self_test_gate.outputs.status == 'PASS'` and DO NOT run when the gate fails — the release halts at this story (LB#25 enforcement)

### Story 4.4: Tier 2 archival — `bitcoin-data` GitHub PR via `gh` CLI (idempotent)

As **Ifuensan (the maintainer)**,
I want **an idempotent helper script that packages the M3 snapshot per the `bitcoin-data` upstream layout, opens a PR via `gh` CLI with the mandatory CHANGELOG entry and dataset README, and skips on retry if a PR for this dataset version already exists**,
So that **the canonical community-archival tier (`bitcoin-data` GitHub repository, b10c-maintained) is populated automatically at release without re-PR pollution on retries — closing LB#11 (b10c socialization completed) at PR submission**.

**Acceptance Criteria:**

**Given** the snapshot from Story 4.1 + the manifest from Story 4.2 + the self-test gate green from Story 4.3 + LB#11 (b10c socialization) cleared (Story 7.3 tracker)
**When** Story 4.4 completes
**Then** `src/electrum_sybil_detector/publication/bitcoin_data_pr.py` exports `submit_pr(snapshot_dir: Path, fork_url: str, upstream_repo: str = "b10c/bitcoin-data", dry_run: bool = False) -> PRSubmissionReport` (FR28, AR33a)
**And** the function (a) clones / pulls the maintainer's fork of `bitcoin-data`, (b) creates a branch `electrum-sybil-detector-<dataset_version>`, (c) copies the Story 4.1 snapshot into the layout `electrum-sybil-detector/<dataset_version>/` matching upstream conventions (verified against `tests/fixtures/bitcoin_data_layout/` from Story 4.1), (d) appends a CHANGELOG entry per upstream convention, (e) commits with a conventional-commits message including dataset version + window boundaries + Zenodo DOI from the manifest, (f) pushes to the fork, (g) opens a PR against `upstream_repo` via `gh pr create` with title `Add electrum-sybil-detector dataset v<dataset_version>` and a body templated from `src/electrum_sybil_detector/publication/templates/bitcoin_data_pr_body.md` linking to the methodology paper + Zenodo DOI + reproducibility self-test invocation
**And** idempotency: before doing any work, the function queries `gh pr list --repo <upstream_repo> --head <fork_branch>` and skips if a PR exists at this dataset version (returns `status: "skipped_already_open"`); on retry after an interrupted upload, the local branch state is reconciled (rebase on upstream main; force-push only the fork branch with explicit confirmation flag, never the upstream main)
**And** LB#11 (b10c socialization) verification: `submit_pr` reads `docs/bmad-binnacle/13_lb11_b10c_socialization.md` and asserts the file declares `status: cleared`; if not, raises `PublicationError` instructing the maintainer to complete socialization first (4–6 weeks pre-launch per architecture)
**And** `dry_run=True` mode runs the full sequence except `gh pr create`; outputs the proposed PR title + body for review
**And** `tests/publication/test_bitcoin_data_pr.py` verifies (a) the fork directory structure matches the upstream-layout fixture, (b) `gh pr create` is invoked exactly once on first run, (c) re-running returns `skipped_already_open` without invoking `gh pr create`, (d) LB#11 unchecked status raises `PublicationError`, (e) `dry_run` produces the expected PR body without side effects (`gh` mocked)
**Given** the upstream `bitcoin-data` repo rejects the PR (formatting issue, naming convention drift)
**When** the maintainer addresses feedback
**Then** the script supports `submit_pr(snapshot_dir, ..., update_existing_pr=True)` to amend the open PR's branch (not open a new one) — preserving the PR review thread

### Story 4.5: Tier 2 archival — Zenodo DOI minting via REST API (idempotent)

As **Ifuensan (the maintainer), Sarah (citation reader), and Lukas (peer reviewer)**,
I want **an idempotent helper script that creates a Zenodo deposit, uploads the Parquet snapshot + manifest + checksums, mints a DOI, cross-references prior dataset versions, and writes the DOI back into the manifest**,
So that **the canonical persistent identifier (DOI hosted by CERN, independent of any GitHub account) exists at launch — citable from the arXiv preprint abstract (Story 4.6) and resolvable from the methodology paper — closing LB#12**.

**Acceptance Criteria:**

**Given** the snapshot from Story 4.1 + the manifest from Story 4.2 (with `zenodo_doi: null` placeholder) + the self-test gate green from Story 4.3 + a Zenodo personal-access token in `ZENODO_API_TOKEN` env var
**When** Story 4.5 completes
**Then** `src/electrum_sybil_detector/publication/zenodo_doi.py` exports `mint_doi(snapshot_dir: Path, prior_concept_doi: str | None = None, sandbox: bool = False) -> ZenodoMintReport` returning the minted DOI + Zenodo deposit URL + checksum manifest (FR29, AR33b)
**And** the function (a) reads `manifest.json` and asserts `zenodo_doi == null` (idempotency precondition: skip if already minted at this dataset version), (b) computes BLAKE2b-256 + SHA-256 + MD5 checksums of every snapshot file (Parquet + README + CHANGELOG + manifest itself excluding the doi field), (c) writes a `<snapshot_dir>/CHECKSUMS.txt` file listing all hashes, (d) creates a new Zenodo deposit via the Zenodo REST API (sandbox endpoint when `sandbox=True`), (e) uploads each snapshot file via the Zenodo Files API, (f) sets the deposit metadata (title, authors, description from `docs/methodology.md` abstract, license CC BY 4.0, version from manifest, related_identifiers including `prior_concept_doi` for cross-version chaining), (g) publishes the deposit and captures the minted DOI, (h) updates `manifest.json`'s `zenodo_doi` field via Story 4.2's `write_manifest` and re-uploads the updated manifest to the deposit (atomic version bump if needed)
**And** idempotency on retry: if Zenodo API responds with "deposit at this version already exists" (queried by title + version match), the function returns `status: "skipped_already_published"` with the existing DOI from the API rather than minting a new one (prevents duplicate DOIs on transient network failure)
**And** cross-versioning: if `prior_concept_doi` is provided, the new deposit is created as a NEW VERSION of the prior concept DOI (Zenodo's versioning model — concept DOI stays stable, version DOI is per-release); the manifest records BOTH `zenodo_doi` (this version) and `zenodo_concept_doi` (stable cross-version handle) — adds field to manifest schema with a `manifest_version` bump from 1 → 2 captured in `migrations/manifest_schema/0002_add_concept_doi.json`
**And** when `sandbox=True`, the function uses Zenodo Sandbox (sandbox.zenodo.org) to validate the full submission flow before production minting — documented in the dataset README and in the M3 launch runbook
**And** `tests/publication/test_zenodo_doi.py` verifies (a) successful first-mint flow against a mocked Zenodo API fixture, (b) idempotent skip on re-run when deposit exists, (c) cross-version chaining via `prior_concept_doi`, (d) checksum file generation matches a frozen reference, (e) manifest update preserves all other fields and only mutates `zenodo_doi`
**Given** the Zenodo API rate-limits or returns transient errors mid-upload
**When** the function retries
**Then** it uses exponential backoff (matching architecture.md `backoff_delay` formula from Story 1.8 with base=5s, cap=600s) and resumes file upload from the last successfully-uploaded chunk; transient failures do not produce a partial deposit (Zenodo deposits are draft-state until explicit publish, so partial uploads are safe to retry)

### Story 4.6: Tier 3 archival — arXiv preprint upload helper + LaTeX source bundle

As **Ifuensan (the maintainer) and downstream Sarah (citation reader)**,
I want **a preflight + upload runbook helper that bundles the LaTeX source, verifies the abstract cites the Story 4.5 Zenodo DOI, packages figures + data references, and produces an arXiv-ready upload tarball + manual upload runbook (no academic-preprint API at M3 per AR33c)**,
So that **the timestamps-priority preprint upload (LB#13) lands at or before launch with the Zenodo DOI in the abstract — establishing canonical-reference position before any competing measurement parallel-publishes**.

**Acceptance Criteria:**

**Given** the LaTeX paper source in `docs/papers/` + the Zenodo DOI minted by Story 4.5 (now populated in the manifest)
**When** Story 4.6 completes
**Then** `src/electrum_sybil_detector/publication/arxiv_upload.py` exports `package_arxiv_submission(paper_dir: Path, manifest: dict, output_path: Path) -> ArxivPackageReport` returning the path to the upload tarball + a preflight report (FR30, AR33c)
**And** the function (a) reads the manifest to extract `zenodo_doi`, (b) parses `<paper_dir>/main.tex` (or configured entry-point file) and verifies the abstract block contains the literal `zenodo_doi` string from the manifest — raises `PublicationError` if absent (LB#13 contract: arXiv abstract MUST cite the DOI), (c) verifies all `\includegraphics` references resolve to files present in `<paper_dir>/figures/`, (d) verifies any `\input{}` / `\include{}` references resolve, (e) bundles the entire `<paper_dir>` minus build artifacts (`.aux`, `.log`, `.out`, `.toc`, `.bbl`, `.blg`) into a gzipped tarball at `output_path` per arXiv submission requirements (single-tarball upload), (f) writes a sibling `<output_path>.preflight.json` with bundle size, file count, abstract DOI string, paper title, author list parsed from LaTeX
**And** the function ships with a manual upload runbook at `docs/papers/arxiv_upload_runbook.md` covering: (1) arxiv.org account login, (2) "New Submission" → upload `<output_path>` tarball, (3) verify auto-extracted preview shows abstract DOI, (4) verify figure rendering, (5) select primary subject class (`cs.CR` Cryptography and Security; secondary `cs.NI` Networking and Internet Architecture), (6) submit with creation timestamp captured for the launch coordinator (Story 4.7)
**And** the runbook is bilingual: `docs/papers/arxiv_upload_runbook.md` (EN) + `docs/papers/arxiv_upload_runbook.es.md` (ES mirror per Epic 6)
**And** the package script does NOT auto-upload: arXiv has no academic-preprint API surface (per architecture D6.7c, AR33c). The script's deliverable ends at the validated tarball + runbook; the upload itself is a documented manual step.
**And** `tests/publication/test_arxiv_upload.py` verifies (a) abstract-DOI verification PASSES when the manifest DOI appears in the abstract block, (b) abstract-DOI verification FAILS (raises `PublicationError`) when missing, (c) figure-resolution verification catches a missing `\includegraphics` target, (d) the tarball contains the expected file set (no build artifacts), (e) preflight JSON matches a frozen reference for a fixture paper
**Given** the maintainer uploads the tarball to arXiv
**When** arXiv returns the preprint identifier (e.g., `arXiv:2604.01234`)
**Then** the maintainer records the identifier + creation timestamp in `docs/bmad-binnacle/14_lb13_arxiv_upload.md` as evidence for Story 4.7's M3 launch gate

### Story 4.7: M3 launch ship gate — 26-item LB checklist final pass + three-tier archival operational + cross-epic readiness

As **Ifuensan (the maintainer), Sarah (grant reviewer), Lukas (peer researcher), Camila (ElectrumX maintainer), Óscar (Spanish-speaking reproducer), and Diego (flagged operator)**,
I want **the M3 launch coordinator that verifies the bit-identical self-test green (Story 4.3), `bitcoin-data` PR accepted upstream (Story 4.4), Zenodo DOI minted and resolves (Story 4.5), arXiv preprint timestamped citing DOI (Story 4.6), Output Guardrails audit green (Epic 5), bilingual mirror parity green (Epic 6), 26-item launch-blocker checklist 100% cleared (Epic 7 tracker), and required paper sections present (PRD §Publication Requirements §a–§j)**,
So that **the M3 launch ships as one coordinated event — tool + dataset + paper bit-identical-reproducible AND archival operational AND launch-blocker checklist cleared — closing the AR43 launch gate**.

**Acceptance Criteria:**

**Given** Stories 4.1–4.6 complete + Epic 5 phrasing-bank audit (Story 5.1 CI gate) + Epic 6 bilingual staleness CI (Story 6.3) + Epic 7 launch-blocker tracker (Story 7.3)
**When** Story 4.7 completes
**Then** `scripts/publish_release.sh` (per architecture.md L819) is the canonical M3 launch entry-point: it invokes Story 4.3 self-test gate, then conditionally Stories 4.4 / 4.5 / 4.6 in parallel, then Story 4.7 verification (AR43)
**And** the launch coordinator verifies all of the following are true; if any fails, the launch is aborted and the failure is captured in `docs/bmad-binnacle/15_m3_launch_attempt_<YYYYMMDD>.md`:
**And** verification 1 — Story 4.3 self-test green: `verify_release(<snapshot_dir>)` exits 0 within NFR4 budget
**And** verification 2 — Story 4.4 `bitcoin-data` PR accepted upstream: `gh pr view <pr_url> --json state,mergedAt` returns `state: "MERGED"` (not "OPEN" or "CLOSED")
**And** verification 3 — Story 4.5 Zenodo DOI resolves: HTTP GET on `https://doi.org/<zenodo_doi>` returns 200 OR redirects to the Zenodo deposit landing page; the manifest in the live deposit matches the manifest in the snapshot (idempotency check)
**And** verification 4 — Story 4.6 arXiv preprint timestamped: `docs/bmad-binnacle/14_lb13_arxiv_upload.md` declares `status: timestamped` with non-empty `arxiv_id` field; HTTP GET on `https://arxiv.org/abs/<arxiv_id>` returns 200 and the abstract contains the Zenodo DOI string
**And** verification 5 — Epic 5 phrasing-bank audit: the most recent CI run of `audit.yml` workflow returns success across CLI strings, dataset README, paper abstract, and Spanish mirrors (FR31)
**And** verification 6 — Epic 6 bilingual mirror parity: the most recent CI run of `bilingual-staleness.yml` workflow returns success (no `*.md` / `*.es.md` mtime drift > 30 days; FR37 / FR38)
**And** verification 7 — Epic 7 launch-blocker tracker: 26 / 26 items in `docs/launch_blockers.yaml` (Story 7.3 tracker) declare `status: cleared` with the cleared-by reference (story ID or external evidence binnacle file); priority-1 cluster (#11 → #2 → #8 → #1 → #9) explicitly cleared
**And** verification 8 — Required paper sections present: a documentation lint runs against `docs/papers/main.tex` asserting the presence of sections matching the PRD §Publication Requirements §a–§j checklist: `\begin{abstract}` containing the Zenodo DOI, `\section{Threat Model}`, `\section{Measurement Ethics}`, `\section{Related Work}` containing references to CoinScope/TxProbe/Grundmann/NodeProbe/Electrohunt2019, `\section{Methodology}`, `\section{Results}`, `\section{Known Evasion Paths}`, `\section{Limitations}` covering single-vantage + M3 scale + Wasserstein tolerance, `\section{Reproducibility}` linking to the dataset DOI + self-test invocation
**And** verification 9 — three-tier archival are independent failure domains: Stories 4.4 / 4.5 / 4.6 are confirmed each independently functional (loss of any single tier does not invalidate the contribution per PRD §Archival Strategy)
**And** the launch coordinator emits a `docs/bmad-binnacle/16_m3_launch_success_<YYYYMMDD>.md` on full success documenting: launch timestamp, Zenodo DOI, arXiv ID, `bitcoin-data` PR URL, dataset version, code hash, bit-identical self-test runtime, all 9 verification outcomes
**And** `tests/publication/test_launch_coordinator.py` verifies (a) all 9 verification gates run in the correct order, (b) any one failing aborts the launch with the failure captured, (c) success path produces the success binnacle entry, (d) the verifications use mocked `gh`, `requests`, and CI-API fixtures
**Given** the launch coordinator successfully completes all 9 verifications
**When** the M3 launch is recorded
**Then** the project transitions from M3 entry to M3+X follow-up posture (per PRD §Two-Papers Plan); Epic 7 Story 7.3 marks AR43 cleared; the IQ9 anti-success-trigger window (6/12 months post-launch) begins

---

## Epic 5: Output Guardrails & Flagged-Operator Disclosure (M0 audit gate → M3 disclosure flow)

Camila (ElectrumX maintainer) sees only phrasing-bank-compliant strings across CLI output, dataset README, paper abstract, contribution-channel docs, and Spanish mirrors — the audit is a release-blocking CI gate from M0. Diego (flagged operator) can find a "What a flagged cluster does NOT mean" text in dataset README + paper, open a disclosure issue via a dedicated bilingual template, get acknowledgment within 48h, and have his contextual note appended to the dataset's qualitative literature with consent. Carve-out `rigor.legal_framing` is honored across every artifact.

### Story 5.1: Phrasing-bank YAML schema + regex rule engine + audit runner

As **every contributor (and Camila as observer)**,
I want **a phrasing-bank declaration in YAML, a regex rule engine that classifies any phrase as `approved` / `prohibited` / `cited-only`, and a CLI invocable as `python -m electrum_sybil_detector.audit <paths>` that scans target files and exits non-zero on prohibited matches outside cited-only contexts**,
So that **the canonical phrasing bank (PRD §Output Guardrails) becomes a deterministic, version-controlled, lint-style enforcement mechanism — not a subjective human review burden — usable from pre-commit, local runs, and CI alike**.

**Acceptance Criteria:**

**Given** the M0 skeleton from Epic 1 + the bilingual scaffold (Epic 6 Story 6.1)
**When** Story 5.1 completes
**Then** `src/electrum_sybil_detector/audit/__init__.py` exports a `PhrasingBankAuditor` Protocol class with methods `audit_file(path: Path) -> list[Finding]`, `audit_string(content: str, lang: Literal["en", "es"]) -> list[Finding]`, `load_phrasing_bank(lang: Literal["en", "es"]) -> PhrasingBank` (FR31, AR8)
**And** `src/electrum_sybil_detector/audit/phrasing_bank/en.yaml` declares three top-level keys: `approved` (list of approved phrase patterns: `"shared infrastructure clusters"`, `"infrastructure-shared cluster"`, `"backend-shared frontend group"`, `"cluster of common-backend Electrum servers"`), `prohibited` (list of prohibited regex patterns: `r"\boperator\s+\w+\s+runs\s+(servers|electrum)"`, `r"\bChainalysis\s+runs\b"`, `r"\bsurveillance\s+operator\b"`, plus broader patterns matching originated intent attribution), `cited_only` (list of patterns permitted only when accompanied by an inline citation to specific sources: `b10c issue #11`, `CoinDesk 2021`, with the citation regex required in the same paragraph)
**And** `src/electrum_sybil_detector/audit/phrasing_bank/es.yaml` mirrors the structure with Spanish translations of the approved phrases (e.g., `"clústeres de infraestructura compartida"`) and the same prohibited patterns translated; bilingual parity per Epic 6 (the Spanish file is the mirror of the English authoritative file)
**And** `src/electrum_sybil_detector/audit/audit_runner.py` implements the regex rule engine: (a) loads both EN + ES phrasing banks (file lang detected by `.es.md` suffix; default EN otherwise), (b) for each `prohibited` pattern, scans the file for matches and emits a `Finding(file, line, column, matched_text, rule_id, severity="error", suggested_alternative)` per match, (c) for each `cited_only` pattern, emits a `Finding(severity="error")` ONLY if the citation regex is absent in the surrounding paragraph (defined as text bounded by blank lines), (d) approved phrases produce no findings (positive control)
**And** `python -m electrum_sybil_detector.audit <paths>` is the canonical CLI invocation: accepts one or more file paths or directories, recursively scans `.md` / `.es.md` / `.tex` / `.py` (Python docstrings + string literals via AST walk), exits 0 if no findings, exits 1 with diagnostic listing per-finding `file:line:column: error: <rule_id>: <matched_text> — suggested: <alternative>`
**And** `tests/audit/test_phrasing_bank.py` verifies (a) the EN + ES YAML files load and parse, (b) bilingual parity: every key present in `en.yaml` is present in `es.yaml`, (c) phrase patterns compile as valid regex
**And** `tests/audit/test_audit_runner.py` verifies (a) approved phrase produces zero findings, (b) prohibited phrase produces one error finding with line/column, (c) cited-only phrase WITH citation produces zero findings, (d) cited-only phrase WITHOUT citation produces one error finding, (e) Python file scan extracts string literals via AST and applies rules to docstrings + literal strings only (not variable names or comments — those are out of scope), (f) directory recursion correctly walks nested folders skipping `.git/`, `node_modules/`, `__pycache__/`
**Given** the phrasing bank evolves (e.g., a new prohibited pattern is identified)
**When** the EN YAML is updated
**Then** the ES YAML must be updated within 14 days (per Epic 6 bilingual SLA) and the audit fixture tests must be updated to cover the new rule; the change requires a `pattern:` PR per architecture.md L543 (legal-framing pattern change requires explicit user ratification per architecture pre-M3 lock)

### Story 5.2: Audit CI gate — release-blocking enforcement across CLI strings + dataset README + paper abstract + Spanish mirrors

As **the M3 launch coordinator (Story 4.7) and Camila (downstream observer)**,
I want **the Story 5.1 audit runner wired as a CI job that runs on every push and PR against the documented file set (CLI string literals, dataset README, paper abstract, all Spanish mirrors), with the release pipeline gated on green status — closing LB#24**,
So that **the phrasing-bank discipline is mechanically enforced (no human reviewer can accidentally merge a defamation-exposed string), the carve-out `rigor.legal_framing` is honored, and the M3 launch gate (Story 4.7 verification 5) has a deterministic CI signal to consume**.

**Acceptance Criteria:**

**Given** the audit runner from Story 5.1 + the M0 GitHub Actions setup from Epic 1 Story 1.3
**When** Story 5.2 completes
**Then** `ci/github-actions/audit.yml` is a GitHub Actions workflow triggered on `push` and `pull_request` to `main`, running on `ubuntu-latest` (audit is platform-independent, no need for the Python matrix from Story 1.3)
**And** the workflow's audit job (a) runs `uv sync` to install the project, (b) invokes `uv run python -m electrum_sybil_detector.audit` against the documented file set: `docs/**/*.md`, `docs/**/*.es.md`, `docs/papers/**/*.tex`, `src/**/*.py`, `.github/ISSUE_TEMPLATE/**`, `.github/PULL_REQUEST_TEMPLATE*.md`, `README.md`, `README.es.md`, `CONTRIBUTING.md`, `CONTRIBUTING.es.md`, `CHANGELOG.md`, the dataset snapshot's README + CHANGELOG (FR31, AR35, LB#24)
**And** any prohibited match (or missing citation for cited-only patterns) fails the CI job; the failure surfaces in the PR review with the per-finding `file:line:column` annotation via `--output-format=github` (matching ruff's GitHub Actions integration pattern from Story 1.3)
**And** Story 4.7's M3 launch coordinator checks the most-recent successful `audit.yml` workflow run on `main` as Verification 5 — if the most recent run is failed or stale (>24h old), the launch is blocked
**And** the audit CI is also wired as a release-blocking gate in `ci/github-actions/release.yml` (Story 4.3 release pipeline): the release job depends on `audit` job success
**And** documentation: `docs/output_guardrails.md` (EN) + `docs/output_guardrails.es.md` (ES) explain the phrasing-bank discipline, the canonical phrasing bank, the cited-only sources (b10c issue #11; CoinDesk 2021), and the audit CI workflow — referenced from `CONTRIBUTING.md` so contributors understand the constraint upfront
**And** `tests/audit/test_audit_ci_target_set.py` verifies the documented file set in `audit.yml` matches the file set declared in `docs/output_guardrails.md` (single source of truth for what gets audited; preventing drift)
**Given** a contributor submits a PR introducing a prohibited phrase
**When** the audit CI runs on the PR
**Then** the PR fails CI, the per-finding annotation surfaces inline in the GitHub PR review UI, and merge is blocked until the offending phrase is replaced with an approved alternative or supplemented with the required citation
**Given** the maintainer needs to merge a legitimate cited-only phrase (e.g., a quoted excerpt from CoinDesk 2021)
**When** the inline citation is present in the same paragraph as the cited-only phrase
**Then** the audit passes and the PR can merge — the cited-only mechanism is the explicit escape hatch for legitimate third-party-attributed quotation per AR (cited-only intent attribution rule)

### Story 5.3: "What a flagged cluster does NOT mean" explanatory text — dataset README + paper sections

As **Diego (flagged operator) and any third-party reading the dataset or paper**,
I want **a "What a flagged cluster does NOT mean" explanatory text that explicitly enumerates plausible benign explanations (cost-sharing across personal nodes; one operator running multiple frontends for redundancy; community-sovereignty-kit shared deployments), present in both the dataset README and the methodology paper, in EN + ES**,
So that **the cluster classification is contextualized for any reader (especially Diego the flagged operator) — the methodological claim "shared backend infrastructure" is explicitly distinguished from "operator surveillance," upholding the legal-framing discipline at the documentation surface (not just at the phrasing-bank string level)**.

**Acceptance Criteria:**

**Given** the dataset README scaffold from Epic 4 Story 4.1 + the paper structure from Epic 4 Story 4.7 verification 8 + the bilingual scaffold from Epic 6
**When** Story 5.3 completes
**Then** `docs/what-flagged-cluster-does-not-mean.md` (EN, authoritative) is created with the following structural elements: (a) one-paragraph framing of the methodological scope (we measure shared backend infrastructure; we do NOT originate intent attribution), (b) explicit numbered enumeration of ≥4 plausible benign explanations for shared backend infrastructure: (1) cost-sharing across personal nodes (e.g., one operator running multiple frontends behind a single Bitcoin Core for cost reasons), (2) operator-internal redundancy (e.g., one operator running multiple frontends for high-availability), (3) community-sovereignty-kit shared deployments (e.g., a community of users sharing infrastructure operated by a trusted member), (4) shared hosting provider with no operator coordination (e.g., multiple independent operators co-located on the same VPS provider's network), (c) explicit instruction to flagged operators directing them to Story 5.4's disclosure issue template, (d) inline citations to b10c issue #11 + CoinDesk 2021 for any intent-attribution language (cited-only per phrasing-bank discipline) (FR32)
**And** `docs/what-flagged-cluster-does-not-mean.es.md` is the Spanish mirror at synchronized parity (Epic 6 Story 6.1 ScrutinyB; bilingual SLA enforced by Epic 6 Story 6.3)
**And** the text passes the audit CI from Story 5.2 (no prohibited phrases; cited-only attributions properly cited)
**And** the explanatory text is included verbatim in the dataset README scaffold from Story 4.1 (Story 4.1's README template is updated to `\include{}` or markdown-include the file content) — verified by `tests/publication/test_dataset_readme_includes_flagged_cluster_explanation.py`
**And** the explanatory text is included as a paper section per PRD §Publication Requirements §i (Limitations) AND surfaced in the abstract via a one-line cross-reference; the Story 4.7 verification 8 documentation-lint includes `docs/what-flagged-cluster-does-not-mean.md`-content presence as a required check
**And** the text is also linked from Story 5.4's disclosure issue template — Diego sees "Before opening a disclosure issue, please read [What a flagged cluster does NOT mean] (link)" as the first instruction in the issue template
**And** `tests/audit/test_what_flagged_cluster_text.py` verifies (a) the EN + ES files exist, (b) both pass the Story 5.2 audit, (c) both contain the required ≥4 enumerated benign explanations (regex match on numbered list items), (d) both contain the cross-reference to Story 5.4's disclosure issue template, (e) the EN + ES bilingual mtime drift is < 14 days (Epic 6 staleness CI integration)
**Given** the methodology evolves (e.g., a new benign explanation is identified post-launch)
**When** the maintainer updates the EN file
**Then** the ES mirror is updated within 14 days per Epic 6 SLA, the audit CI re-runs, the dataset README and paper section pick up the change at the next release; pattern change requires a `pattern:` PR per architecture.md L543

### Story 5.4: Flagged-operator disclosure issue template + 48h SLA acknowledgment workflow

As **Diego (flagged operator)**,
I want **a dedicated bilingual issue template I can use to disclose that I am the operator of a flagged cluster, receive maintainer acknowledgment within 48 hours, and trigger a dataset correction in the next release if the classification is empirically wrong (with the correction documented in the CHANGELOG)**,
So that **the disclosure response channel (PRD §Output Guardrails > Disclosure / response channel) is operationalized — flagged operators have a clear, low-friction path to engage, the 48h SLA is publicly committed, and the dataset's data-integrity contract is preserved through corrections rather than silent re-publication**.

**Acceptance Criteria:**

**Given** the M3 published dataset from Epic 4 + the explanatory text from Story 5.3 + the bilingual scaffold from Epic 6
**When** Story 5.4 completes
**Then** `.github/ISSUE_TEMPLATE/flagged_operator_en.md` is a GitHub issue template (with frontmatter `name: "Flagged Operator Disclosure"`, `labels: ["flagged-operator-disclosure"]`, `assignees: [<maintainer>]`) prompting Diego for: (a) link to the published cluster in the dataset (Zenodo DOI + cluster ID), (b) statement of which servers in the cluster he operates, (c) declaration that he has read `what-flagged-cluster-does-not-mean.md` (link inline), (d) optional benign-deployment context, (e) optional consent to publication of the contextual note (links to Story 5.5 workflow), (f) preferred contact channel (FR33, AR39)
**And** `.github/ISSUE_TEMPLATE/flagged_operator_es.md` is the Spanish mirror at synchronized parity (Epic 6 enforced)
**And** both templates include opening text: "First, please read [What a flagged cluster does NOT mean] (link to docs/what-flagged-cluster-does-not-mean.md). Most flagged clusters represent benign infrastructure-sharing patterns, not surveillance; this template helps us distinguish empirically-correct classifications from misclassifications."
**And** `src/electrum_sybil_detector/audit/flagged_operator_workflow.py` exports `track_disclosure_sla(repo: str = "<owner>/electrum-sybil-detector") -> SLAReport` returning a list of open disclosure issues with their age and SLA status (within 48h ack window / SLA breached / acknowledged / resolved)
**And** the 48h SLA is operationalized: a CI cron job `ci/github-actions/disclosure-sla.yml` runs every 6 hours, queries open issues labeled `flagged-operator-disclosure` via `gh api`, and emits a maintainer notification if any issue is >40 hours old without a maintainer comment (early warning before the 48h deadline)
**And** dataset correction flow: when the maintainer determines (via issue thread) that a classification is empirically wrong (e.g., Diego provides verifiable evidence the servers are independently operated), the maintainer (a) records the correction decision in the issue, (b) the next dataset release excludes / re-classifies the affected pair, (c) the dataset CHANGELOG entry from Story 4.1 includes a `## Corrections` section listing each corrected cluster with a reference to the disclosure issue (without naming Diego unless he consents per Story 5.5)
**And** documentation: `docs/disclosure_workflow.md` (EN) + `docs/disclosure_workflow.es.md` (ES) explain the end-to-end flow for both flagged operators (how to open an issue, what to expect) and maintainers (48h SLA, correction flow, consent capture for Story 5.5)
**And** `tests/audit/test_flagged_operator_workflow.py` verifies (a) the EN + ES issue templates exist with the correct frontmatter, (b) `track_disclosure_sla` correctly classifies fixture issues into within-window / breached / acknowledged buckets, (c) the disclosure workflow doc exists in both EN + ES and passes the Story 5.2 audit
**Given** Diego opens a disclosure issue at 2026-04-27 10:00 UTC
**When** the maintainer comments on the issue at 2026-04-29 09:30 UTC (within 48h)
**Then** `track_disclosure_sla` reports the SLA as `acknowledged_within_window`, the disclosure-sla CI job does not emit a breach alert, and the issue progresses through normal triage
**Given** Diego opens a disclosure issue and 48 hours pass with no maintainer comment
**When** `track_disclosure_sla` runs
**Then** it reports `sla_breached`, the disclosure-sla CI cron emits a critical maintainer notification, and the breach is logged in `docs/bmad-binnacle/sla_breaches.md` for retrospective review (per PRD §Operational Health & Stewardship)

### Story 5.5: Operator contextual-note appending workflow with consent capture

As **Diego (flagged operator who consents to publication of his benign-deployment context)**,
I want **a workflow where, after I confirm the classification stands but provides benign-deployment context, the maintainer can append my contextual note to the dataset's qualitative literature with my explicit consent recorded in a verifiable form**,
So that **the dataset's qualitative literature (PRD §Output Guardrails > Disclosure flow) accumulates real-world context from flagged operators — and the publication of my note is legally defensible by an explicit, signed consent record (never published-by-default; never silently)**.

**Acceptance Criteria:**

**Given** the disclosure issue template from Story 5.4 + the dataset README from Epic 4 Story 4.1 + the legal-framing carve-out from PRD §Compliance
**When** Story 5.5 completes
**Then** `src/electrum_sybil_detector/audit/flagged_operator_workflow.py` is extended with `append_contextual_note(disclosure_issue_id: int, derived_run_id: str, server_opaque_id: str, note_content_md: str, consent_record: ConsentRecord) -> Path` returning the path to the appended note file (FR34)
**And** the function (a) verifies `consent_record` is one of two valid forms: (1) `git_commit` consent — Diego's GPG-signed commit appending the note himself to the qualitative-notes directory via PR (most defensible, preferred); (2) `disclosure_issue_consent` — a maintainer-attested consent statement quoting Diego's verbatim consent text from the disclosure issue thread, with the issue URL + timestamp + SHA-256 of the consent comment recorded, (b) creates the file `docs/dataset_qualitative_notes/<derived_run_id>/<server_opaque_id>.md` with frontmatter declaring `consent_form: <git_commit|disclosure_issue_consent>`, `consent_evidence: <commit_sha|issue_url+comment_sha>`, `appended_by: <maintainer>`, `appended_at_ns: <timestamp>`, and the verbatim note content below, (c) commits the file via the standard PR flow (no direct main-branch writes — every appended note goes through PR review for audit trail)
**And** `ConsentRecord` is a TypedDict with required fields: `form: Literal["git_commit", "disclosure_issue_consent"]`, `evidence: str`, `consent_text_verbatim: str`, `consent_timestamp_ns: int`
**And** the consent capture mechanism is documented in `docs/legal/consent_workflow.md` (EN) + `docs/legal/consent_workflow.es.md` (ES) — explaining for both flagged operators (how to consent: either submit a signed PR yourself, or post explicit consent text in your disclosure issue thread that the maintainer can quote) and maintainers (how to record consent: the function rejects appends without a valid `ConsentRecord`)
**And** the dataset's qualitative literature directory `docs/dataset_qualitative_notes/` is referenced from the dataset README (Story 4.1) with a brief introduction: "These notes are operator-contributed contextual additions, published with explicit consent. See <consent_workflow.md> for the consent process."
**And** the appended notes pass the Story 5.2 phrasing-bank audit (operator-contributed text is not exempt; if Diego's note contains prohibited phrases the maintainer requests a revision before appending)
**And** `tests/audit/test_consent_workflow.py` verifies (a) `append_contextual_note` succeeds with `git_commit` consent form, (b) succeeds with `disclosure_issue_consent` form when all evidence fields populated, (c) raises `AuditError` when consent_form is missing or invalid, (d) the appended note file passes the audit_runner from Story 5.1, (e) the resulting file frontmatter records all consent metadata
**Given** Diego provides benign-deployment context but does NOT consent to publication
**When** the maintainer attempts to append the note
**Then** the function raises `AuditError("consent not provided")` and the note is NOT appended; the disclosure issue is resolved with a maintainer comment thanking Diego for the context with no public publication of the note (consent-by-default-OFF — the most legally defensible posture)
**Given** a published note's underlying consent is later withdrawn by Diego
**When** the maintainer receives the withdrawal request
**Then** the note file is removed via PR (preserving git history of the removal), a CHANGELOG entry documents the redaction, and the next dataset release does not include the note (per FR33 dataset-correction flow extended to cover qualitative-literature withdrawals)

---

## Epic 6: Bilingual EN+ES Parity (M0 scaffold → ongoing SLA)

Óscar (Spanish-speaking university researcher) can read README, first-run guide, dataset schema documentation, dataset README, contribution guide, CLI `--help` text in Spanish at synchronized parity with English; he can open issues and pull requests in Spanish, and receive acknowledgment within the same 48h SLA and substantive review within the same 7-day SLA as English-language submissions; bilingual documents drifting >14 days are publicly flagged in CI as "translation pending"; documents drifting >30 days block releases or roll back to the prior synchronized version. Sustained by HackNodes Lab / Librería de Satoshi for the dataset lifetime per PRD §Bilingual Parity > Sustainability commitment.

### Story 6.1: Bilingual scaffold — README, first-run guide, schema docs, contribution guide, CLI `--help` in EN+ES at parity

As **Óscar (Spanish-speaking reproducer)**,
I want **all user-facing documentation (README, first-run guide, dataset schema docs, contribution guide) and the CLI `--help` text available in Spanish at synchronized parity with the English authoritative versions, with the first-run guide getting me to a working collection daemon in ≤1 hour (LB#5)**,
So that **I can engage with the project end-to-end in Spanish — Librería de Satoshi's bilingual mission lands in practice — without falling back to English at any user-touch point**.

**Acceptance Criteria:**

**Given** the M0 skeleton from Epic 1 Story 1.1 (which shipped bilingual README placeholders) + the deploy doc from Epic 1 Story 1.10
**When** Story 6.1 completes
**Then** `README.md` (EN, authoritative) and `README.es.md` (ES mirror) are populated with synchronized content covering: project name + one-paragraph mission summary, link to first-run guide, link to methodology paper (Zenodo DOI placeholder until Epic 4 Story 4.5), license declarations (MIT for code, CC BY 4.0 for dataset), bilingual contribution invitation pointing at `CONTRIBUTING.md` / `.es.md` (FR35, AR38)
**And** `docs/first-run-guide.md` (EN) + `docs/first-run-guide.es.md` (ES) provide step-by-step instructions from `git clone` to first `block_notifications` row in SQLite within ≤1 hour for a competent developer following the guide; closes LB#5
**And** the first-run guide bilingual parity is empirically tested: a fresh-eyed Spanish-fluent reader walks the ES guide and reaches `block_notifications` row #1 in ≤1 hour; result captured in `docs/bmad-binnacle/17_lb5_first_run_es_walkthrough.md`
**And** `docs/schema/schema.json` is the language-neutral machine-readable JSON Schema declaration; `docs/schema/schema.en.md` + `docs/schema/schema.es.md` are sidecars providing prose column-by-column documentation; both sidecars reference the same authoritative `schema.json` per AR (PRD §Dataset Requirements > Bilingual schema documentation)
**And** `CONTRIBUTING.md` + `CONTRIBUTING.es.md` document: (a) dev environment setup (link to Story 1.2 dev tooling), (b) PR workflow + 48h ack / 7d substantive review SLA from Story 6.2, (c) bilingual SLA from Story 6.3 (>14d warn, >30d block-or-rollback), (d) phrasing-bank audit constraint from Epic 5 Story 5.2, (e) link to flagged-operator disclosure path from Epic 5 Story 5.4
**And** CLI `--help` text is bilingual via stdlib `gettext`: `locale/en/LC_MESSAGES/electrum_sybil_detector.po` + `locale/es/LC_MESSAGES/electrum_sybil_detector.po` translation catalogs; build step in `pyproject.toml [tool.hatch.build]` compiles `.po` → `.mo` at install time; runtime selection via `LANG=es python -m electrum_sybil_detector --help` produces the Spanish help text
**And** `docs/deploy-aws.md` + `docs/deploy-aws.es.md` from Epic 1 Story 1.10 are part of the bilingual scaffold inventory tracked by Story 6.3
**And** the bilingual file inventory is centralized in `docs/bilingual_inventory.yaml` listing every `(en_path, es_path)` pair tracked under the bilingual SLA — single source of truth for Story 6.3's CI staleness check
**And** all bilingual content passes the Story 5.2 phrasing-bank audit (no prohibited language; cited-only language properly cited) in both languages
**And** `tests/test_bilingual_inventory.py` verifies (a) every entry in `bilingual_inventory.yaml` resolves to two existing files, (b) the EN file is the authoritative side (no parallel `*.en.md` / `*.es.md` sibling structure where one is missing), (c) the schema JSON Schema validates against a meta-schema for self-consistency
**And** `tests/test_first_run_guide_completeness.py` verifies the EN + ES first-run guides each contain the required sections: prerequisites, installation, configuration, first-run, verification (block_notifications row check), troubleshooting
**Given** any bilingual file is added to or removed from the project
**When** the inventory is updated
**Then** `docs/bilingual_inventory.yaml` is updated in the same PR (verified by Story 6.3's CI which fails if a `*.es.md` exists without a corresponding inventory entry, or vice versa)

### Story 6.2: Bilingual issue + PR templates with same-SLA acknowledgment workflow

As **Óscar (Spanish-speaking contributor)**,
I want **dedicated bilingual issue templates and a PR-template mirror, plus a documented commitment that Spanish-language issues and PRs receive acknowledgment within 48 hours and substantive review within 7 days at the same SLA as English-language submissions**,
So that **I can engage the project in Spanish without quality-of-service degradation — the bilingual sustainability commitment (PRD §Bilingual Parity > Sustainability commitment) is operationalized at the GitHub-surface level**.

**Acceptance Criteria:**

**Given** the M0 GitHub repository setup from Epic 1
**When** Story 6.2 completes
**Then** `.github/ISSUE_TEMPLATE/bug_report_en.md` is a bilingual-tagged issue template (frontmatter `name: "Bug Report (English)"`, `labels: ["bug", "lang:en"]`) prompting the contributor for: (a) project version (from `python -m electrum_sybil_detector --version`), (b) deploy environment (workstation / AWS / other), (c) reproduction steps, (d) expected vs. observed behavior, (e) relevant log lines from journalctl (FR36, AR39)
**And** `.github/ISSUE_TEMPLATE/bug_report_es.md` is the Spanish mirror (frontmatter `name: "Reporte de Error (Español)"`, `labels: ["bug", "lang:es"]`) prompting the same fields in Spanish; both templates appear in GitHub's "New Issue" picker
**And** additional issue templates from Epic 5 (`flagged_operator_en.md` + `flagged_operator_es.md` from Story 5.4) and a generic `feature_request_en.md` + `feature_request_es.md` complete the bilingual issue template set; all templates inventoried in `docs/bilingual_inventory.yaml` from Story 6.1
**And** `.github/PULL_REQUEST_TEMPLATE.md` (EN, authoritative) + `.github/PULL_REQUEST_TEMPLATE.es.md` (ES mirror) prompt the contributor for: (a) summary, (b) related issue / FR / story reference, (c) test coverage, (d) phrasing-bank audit status (per Epic 5 Story 5.2), (e) bilingual scope flag (does this PR touch bilingual files? if yes: ES mirror updated in same PR, or `translation-pending` issue opened); GitHub auto-selects EN by default with documented `?template=PULL_REQUEST_TEMPLATE.es.md` URL parameter for ES (GitHub's template picker for PRs is less ergonomic than for issues; documented in `CONTRIBUTING.es.md`)
**And** `docs/contributor_sla.md` (EN) + `docs/contributor_sla.es.md` (ES) explicitly declare: (a) issue acknowledgment SLA: 48 hours from submission for both EN + ES (NFR17), (b) PR substantive review SLA: 7 days for both EN + ES (NFR17), (c) data-integrity PR same-day review SLA, (d) `review-queued` tagging during peak load with public visibility, (e) escalation path if SLA is breached
**And** maintainer routing: `docs/maintainer_routing.md` (internal contributor doc) explains which maintainer owns ES-tagged-issue routing — the architectural SPOF (solo-researcher) is acknowledged with the Path 2 handoff candidate (b10c orbit / academic measurement group) named as the bilingual-sustainability backstop per PRD §Risk Mitigations
**And** SLA conformance is measured by Epic 7 Story 7.2 (PR-review SLA tracker) which extends to ES-tagged issues + PRs — the same SLA, the same tracker, the same `review-queued` tag, the same exemption for data-integrity PRs
**And** `tests/test_bilingual_templates.py` verifies (a) all issue templates exist with valid frontmatter, (b) EN + ES PR templates exist with parallel field structures, (c) the contributor SLA docs exist in both languages, (d) maintainer-routing doc exists
**Given** Óscar opens an issue using `bug_report_es.md`
**When** the issue is created
**Then** the issue is auto-labeled `lang:es`, the maintainer-routing process surfaces it in the Spanish-language queue, and Epic 7 Story 7.2's tracker treats it identically to an EN-tagged issue for SLA computation
**Given** an EN-only contributor opens a PR touching a bilingual file but the ES mirror is not updated in the same PR
**When** the PR is opened
**Then** the PR template's bilingual-scope flag prompts the contributor to either (a) include the ES update in the same PR, or (b) explicitly open a `translation-pending` issue (which Story 6.3's CI will track) — the choice is documented in the PR description for review-time visibility

### Story 6.3: Bilingual staleness CI — >14d warn, >30d release-blocking gate

As **Ifuensan (the maintainer) and the M3 launch coordinator (Story 4.7)**,
I want **a CI workflow that, on every push and daily on a schedule, walks the EN/ES file pairs from `docs/bilingual_inventory.yaml`, computes git-mtime drift between each pair, emits a public `translation-pending` issue at >14 days, and sets a release-blocking commit status at >30 days**,
So that **the bilingual SLA (PRD §Bilingual Parity > Staleness SLA) is mechanically enforced — never a human-discipline burden — and the M3 launch (Story 4.7) has a deterministic CI signal to consume for Verification 6**.

**Acceptance Criteria:**

**Given** the bilingual inventory from Story 6.1 + the M0 GitHub Actions setup from Epic 1
**When** Story 6.3 completes
**Then** `ci/github-actions/bilingual-staleness.yml` is a GitHub Actions workflow triggered by (a) `push` to `main`, (b) `pull_request` to `main`, (c) `schedule` cron daily at 06:00 UTC (FR37, AR34)
**And** the workflow's job (a) reads `docs/bilingual_inventory.yaml` for the EN/ES file pair list, (b) for each pair, queries `git log -1 --format=%ct -- <en_path>` and `git log -1 --format=%ct -- <es_path>` to get the last-modification commit timestamp from git history (NOT filesystem mtime — stable across clones per AR), (c) computes `drift_seconds = en_commit_ts - es_commit_ts` (positive = EN newer than ES), (d) classifies drift: `synchronized` if abs(drift) ≤ 14d, `warn` if 14d < drift_when_en_newer ≤ 30d, `block` if drift_when_en_newer > 30d; ES-newer-than-EN drifts are tracked separately as `es_ahead` (informational, not blocking — ES contributors fixing typos ahead of EN are encouraged)
**And** for each `warn` or `block` file pair, the workflow emits a `translation-pending` GitHub issue (or updates the existing one) with: (a) issue title `Translation pending: <es_path>`, (b) labels `translation-pending`, `lang:es`, (c) body listing the EN commit SHA + timestamp, the ES commit SHA + timestamp, the drift duration, and a one-click `?template=...` link to a translation-PR draft, (d) auto-close when the next workflow run detects the pair returned to `synchronized`
**And** for each `block` file pair, the workflow sets a GitHub commit status `bilingual-staleness/blocking` with state `failure` on the head commit; the M3 launch coordinator (Story 4.7 Verification 6) reads this commit status and refuses to launch when state is `failure`
**And** the workflow surfaces a summary report in the workflow logs: total pairs, synchronized count, warn count, block count, plus per-block-pair drift duration; Story 7.1 (uptime monitoring) extends to surface bilingual-staleness state in the operator dashboard
**And** documentation: `docs/bilingual_sla.md` + `.es.md` explain the 14d / 30d thresholds, the rollback escape hatch (Story 6.4), the public visibility commitment ("translation-pending issues are public; the project's bilingual posture is auditable")
**And** `tests/audit/test_bilingual_staleness.py` (a) provides a fixture git repo with file pairs at synchronized / warn / block ages, (b) verifies the classification function correctly buckets each pair, (c) verifies issue creation idempotency (no duplicate issues for the same drifted pair on re-runs), (d) verifies the commit status is set correctly for block-state pairs
**Given** a contributor updates `README.md` without updating `README.es.md`
**When** the bilingual-staleness CI runs the next day
**Then** if the drift is ≤ 14d the run reports `warn` (informational), at >14d a `translation-pending` issue is opened, at >30d the commit status `bilingual-staleness/blocking` blocks the next release
**Given** the maintainer needs to verify launch readiness ahead of Story 4.7
**When** they query the latest `bilingual-staleness.yml` workflow result on `main`
**Then** the result is either green (all pairs synchronized) OR explicitly enumerates which file pairs are blocking (with their drift durations) — Story 4.7 Verification 6 succeeds only on green

### Story 6.4: Stale-translation rollback workflow (>30d hard SLA enforcement)

As **Ifuensan (the maintainer)**,
I want **a CLI tool that, when an EN file has drifted >30 days from its ES mirror without an ES update landing, can revert the EN file to its last synchronized commit (preserving git history with an explicit revert commit) — with a documented `--accept-divergence` escape hatch that requires a mandatory binnacle entry rationale**,
So that **the AR38 hard-enforcement principle ("never ship divergent content silently") is operationalized — either ES catches up, or EN reverts, or the maintainer explicitly accepts divergence for a documented reason (e.g., security disclosure where translation cannot wait)**.

**Acceptance Criteria:**

**Given** the bilingual staleness CI from Story 6.3 has flagged a file pair at `block` state (>30d drift)
**When** Story 6.4 completes
**Then** `src/electrum_sybil_detector/audit/bilingual_rollback.py` exports `rollback_en_to_synchronized(en_path: Path, dry_run: bool = False) -> RollbackReport` returning the revert commit SHA + the previously-synchronized commit SHA + the rollback diff summary (FR38, AR38)
**And** the function (a) looks up the last commit where the EN file's git mtime equaled the ES mirror's git mtime (i.e., last synchronized commit) via `git log` analysis of both files, (b) computes the diff from current EN HEAD back to that synchronized commit, (c) creates a revert commit `revert: bilingual_sla: <en_path> reverted to last synchronized state at <prior_sha>` on a new branch, (d) opens a PR with the revert commit + body explaining the SLA enforcement (links to `docs/bilingual_sla.md`, links to the original EN-update PR, links to the `translation-pending` issue from Story 6.3); maintainer reviews and merges the revert
**And** `python -m electrum_sybil_detector.audit.bilingual_rollback <en_path>` is the canonical CLI invocation; `dry_run=True` mode prints the revert plan without creating the branch / PR
**And** `--accept-divergence` flag is the explicit escape hatch: when set, the function does NOT revert; instead, it (a) requires `--rationale-binnacle <path>` pointing at a `docs/bmad-binnacle/<NN>_bilingual_divergence_<YYYYMMDD>.md` file that the maintainer authors with: rationale (e.g., "critical security disclosure published in EN; ES translator unavailable; staleness accepted for 14 additional days"), expected resolution date, mitigation (e.g., "machine-translation summary added to ES file as interim placeholder marked `translation-quality:machine`"), (b) verifies the binnacle file exists and contains the required frontmatter fields (`accepted_at_ns`, `accepted_by`, `expected_resolution_date`, `rationale`, `mitigation`), (c) sets a git tag `bilingual-divergence-accepted-<YYYYMMDD>-<en_path_slug>` on the head commit, (d) updates `docs/bilingual_inventory.yaml` to mark the file pair `divergence_accepted: true` with the binnacle reference (causing Story 6.3 to report the pair as `accepted_divergence` rather than `block` — does NOT auto-block releases, but is publicly visible in the staleness report)
**And** documentation: `docs/bilingual_sla.md` from Story 6.3 is extended to document the rollback workflow + the escape hatch; `docs/bmad-binnacle/template_bilingual_divergence.md` provides a fill-in-the-blanks template for the rationale binnacle
**And** the escape hatch is governance-bound: a recurring quarterly review of `docs/bilingual_inventory.yaml` `divergence_accepted` entries verifies each `expected_resolution_date` has been honored; long-overdue entries (>90 days past expected resolution) escalate to the maintainer SPOF / Path 2 candidate per PRD §Sustainability commitment
**And** `tests/audit/test_bilingual_rollback.py` (a) provides a fixture git repo with a file pair at >30d drift, (b) verifies dry-run rollback produces the expected revert plan without side effects, (c) verifies actual rollback creates the revert commit + branch, (d) verifies `--accept-divergence` requires `--rationale-binnacle` with the binnacle file existing and containing required frontmatter, (e) verifies the inventory update marks `divergence_accepted: true`
**Given** a critical security disclosure is published in EN that cannot wait for ES translation
**When** the maintainer invokes `bilingual_rollback --accept-divergence --rationale-binnacle docs/bmad-binnacle/18_bilingual_divergence_2026MMDD.md <en_path>`
**Then** the rollback is suppressed, the binnacle entry is verified, the git tag + inventory update are applied, the file pair is publicly visible as `accepted_divergence` in Story 6.3's staleness report, and the M3 launch (Story 4.7) is NOT blocked by this specific pair (other unaccepted-divergence pairs still block per Story 6.3's standard logic)
**Given** an `accepted_divergence` entry passes its `expected_resolution_date` by >90 days without ES catching up
**When** the quarterly review runs
**Then** the entry is escalated for governance review (per PRD §Sustainability commitment); options are: (a) extend the acceptance with an updated binnacle entry, (b) execute the rollback now, (c) trigger Path 2 handoff sustainability review

---

## Epic 7: Operational Stewardship — Uptime, SLAs, Launch-Blocker Tracking

Ifuensan can monitor collection uptime over rolling 30-day windows (alerted when < 95% or > 24h cumulative planned downtime); a maintainer can track PR-review SLA conformance (48h ack / 7d substantive / same-day for data-integrity) and tag PRs as `review-queued` during peak load; a maintainer can track per-launch-blocker status across the 26-item checklist (cleared / pending / blocked) with priority-1 cluster surfaced. Operational tooling supports every other epic without depending on any of them. Lightweight at M0–M1 (journalctl-parsed metrics); upgrades to Grafana + Prometheus at M2+.

### Story 7.1: Rolling 30-day uptime monitoring + 95% threshold alerting + planned-downtime accounting

As **Ifuensan (the maintainer / operator)**,
I want **rolling 30-day uptime computed per server and at fleet aggregate from the `availability` table + `connection_events` rows, alerted when uptime < 95% (NFR6) or when cumulative planned downtime > 24h per rolling 30-day period (NFR9), with M0–M1 implementation parsing structured-JSON journalctl lines and an M2+ migration to Grafana + Prometheus + node_exporter (AR36)**,
So that **the IQ5 triage protocol (drop discretionary work and fix collection) has a deterministic trigger — and the M3 launch coordinator (Story 4.7 Verification 5 / 7) can consume a uptime-health signal as part of ship-readiness**.

**Acceptance Criteria:**

**Given** the AWS deploy from Epic 1 Story 1.10 + the connection lifecycle events from Epic 1 Story 1.8 + the periodic `server.ping` from Epic 2 Story 2.3
**When** Story 7.1 completes (M0–M1 phase)
**Then** `src/electrum_sybil_detector/audit/uptime_monitor.py` exports `compute_uptime_30d(now_ns: int, scope: Literal["per_server", "fleet_aggregate"]) -> UptimeReport` returning a list of `(server_id, uptime_fraction, planned_downtime_ns, unplanned_downtime_ns, sla_status)` per server (or one row for `fleet_aggregate`) (FR39, NFR6)
**And** the function (a) computes per-server downtime intervals from `connection_events` `disconnected → reconnected` pairs + `gaps` rows (Epic 2 Story 2.4) within the 30-day rolling window ending at `now_ns`, (b) classifies each downtime interval as `planned` if it falls within an explicit `planned_downtime_windows` table (created by `migrations/sqlite/0012_planned_downtime.sql` + matching TimescaleDB migration) OR `unplanned` otherwise, (c) computes `uptime_fraction = (window_duration_ns - unplanned_downtime_ns) / window_duration_ns` (excluding planned downtime per NFR9), (d) classifies `sla_status` as `green` if uptime ≥ 95% AND planned_downtime ≤ 24h cumulative, `warn` if 90% ≤ uptime < 95% OR planned_downtime > 24h, `red` (IQ5 trigger) if uptime < 90%
**And** `python -m electrum_sybil_detector.audit.uptime_monitor` is the canonical CLI invocation; supports `--scope=per_server`, `--scope=fleet_aggregate`, `--alert-on=red,warn` flags; exits 0 on green, exits 1 with diagnostic on alert
**And** `infra/systemd/electrum-monitor-uptime.timer` invokes the monitor every 1 hour on the AWS deploy host; alerts route via maintainer email (configured in `[monitoring.alerting.email]` section of project config) — at M0–M1 this is sendmail / mailx via systemd; at M2+ this becomes Prometheus Alertmanager
**And** the M0–M1 implementation parses structured-JSON log lines from `journalctl --output=json` via `journalctl --since "30 days ago" --output=json | python -m electrum_sybil_detector.audit.uptime_monitor --from-stdin` as a documented operator alternative when database queries are infeasible (e.g., during a TimescaleDB migration window)
**Given** the M2+ migration from Epic 2 Story 2.7 is complete
**When** Story 7.1 advances to M2+ phase
**Then** `infra/grafana/dashboards/uptime.json` is provisioned via Terraform (extending Epic 1 Story 1.10's `infra/terraform/`), defining a Grafana dashboard with panels for per-server uptime, fleet aggregate uptime, planned-downtime timeline, IQ5 trigger history; data source is Prometheus scraping a `node_exporter` running on the deploy host plus a custom `electrum_monitor_exporter` exposing the metrics computed by `uptime_monitor.py` over Prometheus's HTTP exposition format
**And** `infra/prometheus/alerting_rules.yml` defines two PromQL rules: `ElectrumUptimeBelow95Pct30d` (for=10m) and `ElectrumPlannedDowntimeExceeded24hCumulative` (for=10m); both fire to Alertmanager which routes to the maintainer's email + (optionally) a Matrix room operated by Librería de Satoshi for community visibility
**And** the M2+ Grafana dashboard is publicly viewable (read-only) — operator-transparency is a project value (PRD §Operational Health & Stewardship)
**And** Story 4.7 Verification 5 (uptime health) reads `uptime_monitor.py`'s output as a launch readiness signal: launch is blocked if `sla_status != "green"` for the most recent 30-day window
**And** `tests/audit/test_uptime_monitor.py` verifies (a) per-server uptime computation against fixture `availability` + `connection_events` rows with known downtime intervals, (b) `planned_downtime_windows` table correctly excludes planned intervals from unplanned-downtime accounting, (c) SLA classification matches the documented thresholds, (d) M0–M1 stdin-mode parses journalctl JSON correctly, (e) the M2+ Grafana dashboard JSON validates against Grafana's dashboard schema
**Given** uptime drops below 95% over a rolling 30-day window
**When** the next hourly monitor invocation runs
**Then** `sla_status = "red"`, an alert email is sent to the maintainer, the IQ5 triage protocol is invoked (operator drops discretionary work), and the breach is logged to `docs/bmad-binnacle/sla_breaches.md` with timestamp + per-server downtime breakdown
**Given** the maintainer schedules planned downtime (e.g., for storage migration)
**When** they insert a row into `planned_downtime_windows` ahead of the maintenance window
**Then** the downtime is excluded from the unplanned-downtime computation; the planned-downtime cumulative counter increments toward the 24h NFR9 limit; if the planned window exceeds 24h cumulative for the rolling 30d, the monitor fires a `warn` alert (planned downtime exhausting the NFR9 envelope)

### Story 7.2: PR-review SLA tracker + `review-queued` tagging during peak load

As **Ifuensan (the maintainer), Lukas / Óscar (contributors awaiting review)**,
I want **a tracker that classifies every open issue + PR by its SLA bucket (within-window / approaching / breached / acknowledged / merged) using the 48h ack / 7d substantive / same-day data-integrity SLAs from PRD §Operational Health, auto-tags `review-queued` during peak load, and treats ES-tagged issues at identical SLAs (Epic 6 Story 6.2 integration)**,
So that **the PR-stewardship metric (PRD §Success Criteria > Technical / Measurement Success) is observable to both maintainers and contributors — peak-load `review-queued` tagging is publicly visible (no silent backlog), data-integrity exemption is honored, and SLA breaches are systematically captured for retrospective**.

**Acceptance Criteria:**

**Given** the M0 GitHub repository setup + the bilingual templates from Epic 6 Story 6.2 + the disclosure issue template from Epic 5 Story 5.4
**When** Story 7.2 completes
**Then** `src/electrum_sybil_detector/audit/pr_sla_tracker.py` exports `compute_sla_status(repo: str = "<owner>/electrum-sybil-detector") -> SLAReport` returning a list of `SLAEntry(item_type: Literal["issue", "pr"], item_number: int, title: str, opened_at_ns: int, last_maintainer_response_at_ns: int | None, age_hours: float, sla_bucket: Literal["within_window", "approaching", "breached", "acknowledged", "merged_or_closed"], lang_label: Literal["en", "es"], data_integrity_flag: bool)` (FR41, NFR17)
**And** the function (a) queries GitHub via `gh api repos/<owner>/<repo>/issues?state=open` + `repos/<owner>/<repo>/pulls?state=open`, (b) for each item, parses the labels for `lang:en` / `lang:es` (Epic 6 Story 6.2) and `data-integrity` (used by maintainer to mark data-integrity PRs), (c) for each item, finds the first maintainer comment timestamp via `gh api repos/<owner>/<repo>/issues/<n>/comments` (filtered by author == maintainer username), (d) classifies by SLA: `acknowledged` if the first maintainer comment exists; `within_window` if no comment yet AND age < 36h (data-integrity: < 12h); `approaching` if 36h ≤ age < 48h (data-integrity: 12h ≤ age < 24h); `breached` if age ≥ 48h with no comment (data-integrity: ≥ 24h); `merged_or_closed` for closed items (final state)
**And** `python -m electrum_sybil_detector.audit.pr_sla_tracker` is the canonical CLI invocation; supports `--lang=es` to filter ES-tagged items only, `--bucket=breached` to filter breaches only, `--auto-tag-review-queued` to emit `gh issue edit --add-label review-queued` calls for items past the peak-load threshold (default: when ≥5 unreviewed PRs are open)
**And** `--auto-tag-review-queued` mode (a) counts open PRs with no maintainer comment, (b) if count ≥ peak-load threshold, applies `review-queued` label to all unreviewed PRs (idempotent — does not re-apply), (c) when the count drops back below threshold, removes the label from unreviewed PRs (also idempotent); the label is publicly visible in the GitHub PR list per PRD's "publicly tag PRs as `review-queued` during peak load" requirement
**And** SLA breaches are logged: each newly-breached item appends a row to `docs/bmad-binnacle/sla_breaches.md` with timestamp + item URL + lang label + maintainer-response state at breach moment + recovery time (filled in when item exits `breached` state)
**And** `infra/systemd/electrum-monitor-pr-sla.timer` invokes the tracker every 6 hours on the AWS deploy host (or a separate maintainer workstation if AWS isn't desired for SLA monitoring); alerts (`breached` count > 0) route via maintainer email
**And** ES-tagged items: the tracker treats `lang:es`-labeled items at IDENTICAL SLA thresholds as `lang:en`-labeled items (no second-class treatment for Spanish contributors per PRD §Bilingual Parity); the report's per-bucket counts include a per-language breakdown for transparency
**And** `tests/audit/test_pr_sla_tracker.py` verifies (a) SLA bucket classification against fixture issues at known ages with / without maintainer comments, (b) data-integrity exemption applies the tighter same-day SLA, (c) ES-tagged items are classified at identical thresholds, (d) `--auto-tag-review-queued` is idempotent (no duplicate labels), (e) breach logging appends to `sla_breaches.md` correctly, (f) recovery times are filled in when an item exits `breached`
**Given** Óscar opens an ES-tagged bug-report issue
**When** the SLA tracker runs 50 hours later with no maintainer comment
**Then** the issue is classified as `breached`, the breach is logged to `sla_breaches.md` tagged `lang:es`, the alert email cites the SLA breach, and the issue retains a `review-queued` label until the maintainer responds (closing the breach window) — Spanish-language contributor SLA is enforced at parity per Epic 6 Story 6.2
**Given** the maintainer marks a PR as data-integrity-related via the `data-integrity` label
**When** the SLA tracker classifies the PR
**Then** the same-day SLA (12h within / 24h approaching / 24h+ breached) applies — preserving the "Data-integrity PRs are exempt from triage and reviewed same-day" requirement from PRD §Operational Health

### Story 7.3: 26-item launch-blocker checklist tracker — `docs/launch_blockers.yaml` + priority-1 cluster surfacing

As **Ifuensan (the maintainer), Sarah (grant reviewer auditing project discipline), and the M3 launch coordinator (Story 4.7)**,
I want **a single source of truth for the 26-item launch-blocker checklist (PRD §Launch-Blocker Checklist L501–L532) declared in `docs/launch_blockers.yaml`, where each item carries `id`, `title`, `status`, `priority`, `cleared_by`, `cleared_at`, `priority_1_cluster_member` — surfaced via a CLI status report that highlights the priority-1 cluster (#11 → #2 → #8 → #1 → #9) first**,
So that **launch readiness is auditable in version control (no spreadsheet, no project board), Story 4.7 Verification 7 has a deterministic file to read for the M3 ship gate, and the PRD's pre-commitment-as-discipline innovation (PRD §Innovation IQ4) is operationalized as a tracking artifact**.

**Acceptance Criteria:**

**Given** the 26-item launch-blocker checklist enumerated in PRD §Launch-Blocker Checklist L501–L532
**When** Story 7.3 completes
**Then** `docs/launch_blockers.yaml` is created with one entry per item (1–26) carrying: `id` (int 1–26), `title` (string verbatim from PRD), `prfaq_origin` (string: PRFAQ Stage 3 / Stage 4 / promoted-from-PRD-body / added-2026-04-26), `status` (enum: `cleared` / `pending` / `blocked` / `superseded`), `priority` (enum: `priority_1` / `priority_2` / `priority_3`), `priority_1_cluster_member` (bool), `cleared_by` (string: story ID like `1.5` OR external evidence binnacle reference like `docs/bmad-binnacle/03_phase1-validations.md` OR null), `cleared_at` (ISO 8601 date OR null), `notes` (multiline string for context, e.g., LB#15 cleared 2026-04-25 with empirical numbers) (FR42, AR44)
**And** the `priority_1_cluster_member: true` items are LB#11 (b10c socialization), LB#2 (fee-histogram empirical verification), LB#8 (fork-observer Electrum-support), LB#1 (stale-blocks cadence), LB#9 (methodology-ancestor citations) — matching the PRD's priority-1 cluster ordering
**And** the initial `launch_blockers.yaml` reflects the actual current state per PRD lastEdited 2026-04-26: LB#15 (asyncio timing) `status: cleared`, `cleared_by: docs/bmad-binnacle/03_phase1-validations.md`, `cleared_at: 2026-04-25`; LB#26 (VPS dual-stack) `status: pending`, `priority_1_cluster_member: false`; LB#16 (1209k uptime cross-validation) `status: pending` with `notes` documenting the deferral to M1; all others initialized at `pending` until corresponding stories close them
**And** `src/electrum_sybil_detector/audit/launch_blocker_status.py` exports `report_status() -> LBStatusReport` returning a structured report grouped by `priority_1_cluster` (5 items, ordered #11 → #2 → #8 → #1 → #9) + `priority_2` + `priority_3`, with per-bucket cleared / pending / blocked counts
**And** `python -m electrum_sybil_detector.audit.launch_blocker_status` is the canonical CLI invocation; supports `--format={text,json,markdown}`, `--filter=pending`, `--priority-1-only`; the markdown format produces a checklist suitable for inclusion in a launch-readiness dashboard or a grant-application appendix
**And** the report enforces a consistency check: `cleared_by` MUST be non-null when `status: cleared`; `cleared_at` MUST be non-null when `status: cleared`; raises `AuditError` on inconsistency (validates the YAML on every run)
**And** `tests/audit/test_launch_blocker_status.py` verifies (a) all 26 items exist in `launch_blockers.yaml`, (b) the priority-1 cluster matches the canonical 5-item ordering, (c) consistency check raises on inconsistent rows, (d) the `cleared_by` field for cleared items resolves to either an existing story ID (cross-checked against `epics.md`) OR an existing binnacle file path
**And** Story 4.7 Verification 7 (launch-blocker checklist 100% cleared) reads `docs/launch_blockers.yaml` directly: launch is blocked if any item has `status != "cleared"` (priority-1 cluster blocked is a hard fail; priority-2/3 blocked emits a warning that requires explicit maintainer override flag `--accept-priority-2-pending` with binnacle rationale per Story 6.4-style governance)
**And** the `launch_blockers.yaml` is a documented bilingual artifact (per Epic 6 inventory): the YAML field VALUES are EN-only (machine-readable), but a sibling `docs/launch_blockers.es.md` provides a Spanish-language human-readable summary auto-generated from the YAML on each push to `main` via a CI step in `bilingual-staleness.yml` (so the YAML stays the single source of truth and Spanish-speaking auditors get the readable summary)
**Given** Story 1.5 closes (Storage backend ships) which clears LB# (none directly listed in the priority-1 cluster but example: a hypothetical LB about schema definition)
**When** the maintainer updates `launch_blockers.yaml` setting `cleared_by: 1.5`, `cleared_at: <date>`, `status: cleared`
**Then** the next CI run validates the consistency, the priority-1 cluster status report updates, and the M3 launch readiness dashboard reflects the cleared item
**Given** all 26 items achieve `status: cleared` ahead of M3 launch
**When** Story 4.7 Verification 7 runs
**Then** the verification passes; the launch coordinator proceeds to verifications 8–9; on full success, the M3 launch is recorded and `launch_blockers.yaml` is git-tagged `launch-blockers-cleared-<launch_date>` for archival auditability (matching Story 3.10's `thresholds-frozen-pre-m3-<YYYYMMDD>` pattern)
**Given** an item must be marked `superseded` (e.g., a future PRD edit removes it)
**When** the maintainer transitions it from `pending` → `superseded` with a `notes` rationale
**Then** the consistency check accepts `superseded` as a valid terminal state (treated as "not blocking launch"); Story 4.7 Verification 7 treats `cleared` and `superseded` as both pass-states; the supersession is itself a `pattern:` PR per architecture.md L543

---

## Coverage Verification

### Story → FR Coverage Matrix

All 42 FRs are covered by at least one story across the 7 epics. Total story count: **49 stories** (Epic 1: 11 + Epic 2: 9 + Epic 3: 10 + Epic 4: 7 + Epic 5: 5 + Epic 6: 4 + Epic 7: 3).

| FR | Epic.Story | Capability |
|---|---|---|
| FR1 | 1.6 | Seed-list ingestion |
| FR2 | 2.1 | Snowball expansion |
| FR3 | 2.6 | Tor SOCKS5 onion connectivity |
| FR4 | 2.2 | ASN + protocol-version provenance |
| FR5 | 1.7 (partial), 1.8 (full) | Persistent asyncio TCP/SSL pool |
| FR6 | 1.7 | `headers.subscribe` capture with monotonic-ns |
| FR7 | 2.3 | Periodic stable-RPC polling at full scale |
| FR8 | 1.5 (schema), 1.7 (runtime) | Connection-event metadata at connect-time |
| FR9 | 1.8 | Uptime/downtime event emission |
| FR10 | 1.8 | Per-server probe rate throttling |
| FR11 | 1.5 (Protocol surface), 1.11 (production invariant) | Append-only raw rows + schema_version |
| FR12 | 1.4 (utility), 1.5 (schema), 1.11 (production invariant) | Time-pair invariant |
| FR13 | 1.5 (schema), 1.11 (runtime persistence) | Per-window NTP-discipline manifest |
| FR14 | 1.5 | Forward-compat-only schema migrations |
| FR15 | 2.7 | SQLite → TimescaleDB migration |
| FR16 | 1.4 (utility), 1.5 (use in upserts) | BLAKE2b-256 opaque server identifiers |
| FR17 | 3.3 | `bitcoin-data/stale-blocks` fork-race ingest |
| FR18 | 3.4 | Per-pair pairwise-delta variance |
| FR19 | 3.5 | 1-D Wasserstein over fee-rate CDFs |
| FR20 | 3.6 | Synchronized-downtime detection |
| FR21 | 3.8 | Multi-signal threshold engine |
| FR22 | 3.7 | Baseline noise-floor distribution |
| FR23 | 3.9 | DBSCAN + Ward clustering with FDR + CIs |
| FR24 | 3.1 | Fee-histogram 5-frontend calibration harness |
| FR25 | 4.1 | Parquet+Zstd snapshot per `bitcoin-data` conventions |
| FR26 | 4.2 | `manifest.json` per release |
| FR27 | 4.3 | Bit-identical re-derivation ship gate |
| FR28 | 4.4 | Idempotent `bitcoin-data` PR flow |
| FR29 | 4.5 | Idempotent Zenodo DOI minting |
| FR30 | 4.6 | arXiv preprint upload citing DOI |
| FR31 | 5.1 (engine), 5.2 (CI gate) | Phrasing-bank audit as release gate |
| FR32 | 5.3 | "What a flagged cluster does NOT mean" text |
| FR33 | 5.4 | Flagged-operator disclosure issue + 48h SLA |
| FR34 | 5.5 | Operator contextual note appended with consent |
| FR35 | 6.1 | Bilingual README/guide/schema/CLI parity |
| FR36 | 6.2 | Spanish-language issues/PRs at same SLA |
| FR37 | 6.3 | Bilingual staleness CI flag (>14 days) |
| FR38 | 6.4 | Stale-translation rollback (>30 days) |
| FR39 | 7.1 | Rolling 30-day uptime monitoring + alerting |
| FR40 | 2.4 | Collection-gap enumeration |
| FR41 | 7.2 | PR-review SLA tracking + `review-queued` tagging |
| FR42 | 7.3 | 26-item launch-blocker checklist tracking |

✅ **42 / 42 FRs covered. No orphans. No duplicates.**

### Phase-Gate Verification Stories

Each milestone-transition gate is closed by an explicit verification story:

| Gate | Story | AR |
|---|---|---|
| M0 → M1 | 1.11 | AR40 |
| M1 → M2 | 2.5 | AR41 |
| M2 → M3 | 2.9 | AR42 |
| M3 analysis ship-readiness | 3.10 | AR26 |
| M3 launch | 4.7 | AR43 |

### Cross-Cutting CI Gates (consumed by Story 4.7)

| Verification | Source story | Mechanism |
|---|---|---|
| 1. Bit-identical self-test | 4.3 | `verify_release` exits 0 |
| 2. `bitcoin-data` PR merged | 4.4 | `gh pr view` returns `MERGED` |
| 3. Zenodo DOI resolves | 4.5 | `https://doi.org/<doi>` HTTP 200 |
| 4. arXiv preprint timestamped | 4.6 | `https://arxiv.org/abs/<id>` HTTP 200 + DOI in abstract |
| 5. Phrasing-bank audit green | 5.2 | `audit.yml` workflow passing |
| 6. Bilingual mirror parity | 6.3 | `bilingual-staleness.yml` no `block` state |
| 7. 26-item LB checklist 100% cleared | 7.3 | `launch_blockers.yaml` all `status: cleared` |
| 8. Required paper sections present | 4.7 lint | `docs/papers/main.tex` documentation lint |
| 9. Three-tier archival independent failure domains | 4.7 | Stories 4.4/4.5/4.6 confirmed each independently functional |
