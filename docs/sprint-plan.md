# Sprint Plan · electrum-sybil-detector

**Created:** 2026-04-27
**Horizon:** 12 months M0 → M3 launch
**Inputs:** [`epics.md`](../_bmad-output/planning-artifacts/epics.md) (49 stories) + [`launch_blockers.yaml`](./launch_blockers.yaml) (26 LBs, 1 cleared)

This plan layers two parallel tracks:

- **Code track (Amelia):** 49 stories from `epics.md` implemented via `bmad-create-story` → `bmad-dev-story` loop
- **Maintainer track (Ifuensan):** non-code launch blockers — paper writing, real-world conversations, fact-checks, operational coordination

Status tracking lives in [`sprint-status.yaml`](../_bmad-output/implementation-artifacts/sprint-status.yaml) (BMad-template format) and [`launch_blockers.yaml`](./launch_blockers.yaml) (the 26-item LB tracker, anticipating Story 7.3's audit CLI).

Sprints are 1–2 week windows. Owner column: **A** = Amelia (code), **I** = Ifuensan (maintainer), **A+I** = paired work.

---

## 🚨 Start THIS WEEK (regardless of sprint)

| Item | Owner | Lead time | Why now |
|---|---|---|---|
| **LB#11** open conversation with b10c on `bitcoin-data` contribution | I | 4–6 weeks minimum, asynchronous | Hard prerequisite for Story 4.4 (M3 launch). No code blocks on this; the conversation happens on b10c's calendar, not ours. Mandar primer mensaje (issue / email) y crear `docs/bmad-binnacle/13_lb11_b10c_socialization.md` con `status: pending` + fecha de primer contacto. |

---

## Sprint 0 — Foundation skeleton (Week 1)

**Goal:** Project is `git clone`-able, dev tooling works, CI is green on a no-op commit.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 1.1 | Bespoke M0 project skeleton | A | Bootstrapping commit. Sin deps. |
| 1.2 | Dev tooling stack (uv + ruff + mypy --strict + pytest + pre-commit) | A | Bloqueante de 1.3+. |
| 1.3 | GitHub Actions CI baseline matrix | A | Verde en commit vacío. |

**Maintainer parallel:** primer mensaje a b10c (LB#11).

---

## Sprint 1 — Core utilities + cross-cutting M0 (Weeks 2–3)

**Goal:** Las utilidades compartidas + Output Guardrails audit + bilingüe scaffold + uptime monitor stub están listos. Quick fact-checks bajados.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 1.4 | Core utilities (time discipline + hashing + exceptions + structured logging) | A | Bloqueante de 1.5+. |
| 5.1 | Phrasing-bank engine + audit runner | A | Paralelo. |
| 6.1 | Bilingual scaffold (READMEs, first-run guide, schema docs, CLI --help, contributing) | A | Paralelo. Closes LB#5 con walkthrough. |
| 7.1 (M0–M1 stub) | Uptime monitor via journalctl parsing | A | Stub mínimo. Grafana viene en M2+. |
| **LB#9** | Methodology-ancestor citation verification (CoinScope, TxProbe, Grundmann, Node-Probe) | I | ~1-2h por ancestor. ~6h total. |
| **LB#10** | CoinDesk 2021 article URL + claims | I | ~30 min. |
| **LB#14** | AS24940 (Hetzner) example check | I | ~30 min. |
| **LB#17** | I2P claim re-phrase | I | ~30 min. |
| **LB#11** | Follow-up con b10c si respondió | I | Asincrónico. |

---

## Sprint 2 — Storage + Discovery + first connect (Weeks 4–6)

**Goal:** El daemon habla con UN Electrum server real, persiste en SQLite WAL, y cumple el invariant time-pair + append-only.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 1.5 | SQLite WAL storage backend + initial schema + migration runner | A | Story más chunky de Epic 1. |
| 1.6 | Seed-list ingestion (Discovery M0) | A | Hardcoded seed list. |
| 1.7 | Connect to one Electrum server end-to-end | A | Primera notification real. |
| 5.2 | Audit CI gate (release-blocking enforcement) | A | Closes LB#24. |
| **LB#11** | Sigue conversación b10c | I | Continuar engagement. |

---

## Sprint 3 — Multi-server pool + self-test + M0 deploy + M0→M1 gate (Weeks 7–10)

**Goal:** Daemon corriendo 24/7 en AWS EC2 contra 10–20 seeds con uptime ≥95% sobre 7-day soak. M0→M1 gate cleared.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 1.8 | Persistent multi-server connection pool (TaskGroup + reconnect + rate limit + lifecycle) | A | Story chunky. |
| 1.9 | Reproducibility self-test scaffold + CI gate | A | NFR15 scaffold. |
| 1.10 | AWS production deploy (Terraform + chrony + systemd + IPv6 dual-stack gate) | A+I | Amelia escribe Terraform; Ifuensan ejecuta `terraform apply`, opera el deploy host. Closes LB#26. |
| 1.11 | M0→M1 gate verification + per-window NTP manifest persistence | A+I | 7-day soak en AWS. Ifuensan opera; Amelia analiza resultados. |
| 6.2 | Bilingual issue + PR templates + same-SLA workflow | A | Cross-cutting. |
| 6.3 | Bilingual staleness CI (>14d warn, >30d block) | A | Closes operational requirement. |
| 6.4 | Stale-translation rollback workflow | A | Cross-cutting. |
| 7.2 | PR-review SLA tracker + `review-queued` tagging | A | Cross-cutting. |
| 7.3 | Launch-blocker checklist tracker (CLI consumes `launch_blockers.yaml` ya creado) | A | Trabaja sobre el YAML que creamos hoy. |

**Maintainer parallel:** sigue LB#11 si necesario; arrancar borrador de LB#22 (paper measurement-ethics) y LB#23 (paper threat model + evasion paths) — multi-day writing tasks que se benefician de empezar temprano.

**Gate de transición:** AR40 cleared. Epic 2 puede empezar.

---

## Sprint 4–5 — Epic 2 M1 (Months 3–4)

**Goal:** Snowball converge ≤24h, ≥150 servers reached, IPv6-only end-to-end, 14-day soak ≥95% uptime. M1→M2 gate cleared.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 2.1 | Snowball discovery via `server.peers.subscribe` | A | M1 entry. |
| 2.2 | Discovery provenance enrichment (ASN + protocol-version) | A | Primera runtime dep: `pyasn`. |
| 2.3 | Periodic stable-RPC polling suite at full network scale | A | Implementa FR7 completo. |
| 2.4 | Collection gap enumeration | A | Storage-side. |
| 2.5 | M1→M2 gate verification (full-network reach + IPv6-only + 14-day soak) | A+I | Soak operacional. |
| **LB#16** | 1209k.com uptime cross-validation (deferred from Phase 1) | I | Rolls into snowball weighting calibration. |
| **LB#22** | Paper measurement-ethics section (continúa borrador) | I | Multi-day. |
| **LB#23** | Paper threat model + evasion paths section (continúa borrador) | I | Multi-day. |

**Gate de transición:** AR41 cleared.

---

## Sprint 6 — Epic 2 M2 (Months 5–6)

**Goal:** Tor SOCKS5 operacional + TimescaleDB swap completo + retention policy aplicada. M2→M3 gate cleared.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 2.6 | Tor SOCKS5 transport plug-in + .onion reach | A | Nueva impl del Transport Protocol. |
| 2.7 | TimescaleDB backend + storage backend swap | A+I | Amelia codea; Ifuensan ejecuta migración SQLite→TimescaleDB en deploy host. |
| 2.8 | 90-day downsampling retention policy | A | Sólo sobre TimescaleDB. |
| 2.9 | M2→M3 gate verification | A+I | 14-day soak con full population incl. Tor. |
| **LB#11** | Conversación b10c sigue cerrando | I | A esta altura debería estar cerca de cleared. |

**Gate de transición:** AR42 cleared.

---

## Sprint 7–9 — Epic 3 Analysis methodology + paper finalization (Months 7–9)

**Goal:** Pipeline de análisis produce findings de cluster con BH-FDR + bootstrap CIs. M3 analysis ship-readiness gate verde.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 3.1 | Fee-histogram drift calibration harness (5-frontend matrix, LB#2) | A+I | Amelia escribe docker-compose; Ifuensan opera infra (Bitcoin Core + 5 frontends). Closes LB#2 fully. |
| 3.2 | Derived-tier scaffolding (`derived_run_id` + thresholds.yaml + statistical-rigor utilities) | A | Bloqueante de 3.4+. |
| 3.3 | Fork-race event ingestion from `bitcoin-data/stale-blocks` + fork-observer cross-check | A | Closes LB#1 + LB#8. |
| 3.4 | Pairwise-delta variance over fork-race windows | A | Signal #1 backend-state. |
| 3.5 | 1-D Wasserstein distance over fee-rate CDFs | A | Signal #2 backend-state. |
| 3.6 | Synchronized-downtime detection via interval-overlap | A | Signal #3 backend-state. |
| 3.7 | Baseline noise-floor distribution (independent-server set bootstrap + permutation) | A+I | Ifuensan curates `independent_servers.yaml` (declaración manual de pares conocidos). |
| 3.8 | Multi-signal threshold engine (frozen rule classification) | A | Frozen pre-M3. |
| 3.9 | DBSCAN + Ward clustering + BH-FDR + bootstrap CIs + power analysis | A | Outputs `cluster_assignments`. |
| 3.10 | M3 analysis-pipeline ship-readiness gate (frozen thresholds + pure-Python audit + LB re-eval) | A+I | git-tag `thresholds-frozen-pre-m3-<date>`. |
| **LB#22** | Paper measurement-ethics section (FINAL) | I | Cierra acá. |
| **LB#23** | Paper threat model + evasion paths section (FINAL) | I | Cierra acá. |
| **LB#11** | Conversación b10c CLOSED (cleared status en YAML) | I | Hard prerequisite de Story 4.4 en próximo sprint. |
| **LB#12** | Zenodo account + sandbox testing + DOI reservation | I | Pre-launch infra. |
| **LB#13** | arXiv account creation | I | Pre-launch admin. |

**Gate de transición:** AR26 + AR42 cleared. Epic 4 ready.

---

## Sprint 10–11 — Epic 4 + Epic 5 disclosure flow (Months 10–11)

**Goal:** Citable bundle assembled. Three-tier archival operational pre-launch. Disclosure flow live.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 4.1 | Parquet snapshot generator (`bitcoin-data` conventions, Tier 1) | A | |
| 4.2 | `manifest.json` builder | A | |
| 4.3 | Bit-identical re-derivation ship gate (full NFR15 contract M3 scale) | A | Closes LB#25. |
| 4.4 | `bitcoin-data` GitHub PR via `gh` CLI (idempotent, Tier 2a) | A+I | Bloqueado en LB#11 cleared. Ifuensan revisa PR antes de submit. |
| 4.5 | Zenodo DOI minting via REST API (idempotent, Tier 2b) | A+I | Closes LB#12. Ifuensan opera Zenodo account. |
| 4.6 | arXiv preprint upload helper + LaTeX bundle (Tier 3) | A+I | Closes LB#13. Amelia bundlea; Ifuensan ejecuta upload manual. |
| 5.3 | "What a flagged cluster does NOT mean" text (dataset README + paper sections) | A+I | Amelia drafts; Ifuensan reviews + finaliza prosa. |
| 5.4 | Flagged-operator disclosure issue template + 48h SLA workflow | A | |
| 5.5 | Operator contextual-note appending workflow with consent capture | A | |
| **LB#7** | Re-verify b10c issue #11 status pre-launch | I | ~5 min. |
| **LB#18** | Re-verify 9-month b10c-Todo dwell at actual launch date | I | ~5 min al moment of launch. |
| **LB#20** | Verify FC's recent acceptance patterns | I | ~1h. |
| **LB#21** | Re-evaluate PETS editorial mix | I | ~1h. |

---

## Sprint 12 — M3 LAUNCH (Month 12)

**Goal:** Tool + dataset + paper ship jointly. AR43 gate cleared.

| Story / LB | Title | Owner | Notes |
|---|---|---|---|
| 4.7 | M3 launch ship gate — 26-item LB checklist final pass + three-tier archival operational + cross-epic readiness | A+I | Story 4.7 invoca `scripts/publish_release.sh` que ejecuta las 9 verifications. Ifuensan supervises + autoriza launch. |

**Outputs:**
- `bitcoin-data` PR merged
- Zenodo DOI minted + resolves
- arXiv preprint timestamped citing DOI
- Phrasing-bank audit green
- Bilingual mirror parity green
- 26 / 26 LBs cleared
- Reproducibility self-test green
- Paper sections present

**Post-launch:** IQ9 anti-success-trigger window opens (6/12 months).

---

## Resumen ejecutivo de assignments para Ifuensan

Por mes, las cosas que dependen de vos (no de Amelia):

| Mes | Carga maintainer | Comentario |
|---|---|---|
| Mes 1 | LB#11 inicio + LB#9/#10/#14/#17 fact-checks (~1 día total) | Bajo, pero LB#11 es crítico arrancarlo |
| Mes 2 | LB#11 follow-up + ops del deploy (Story 1.10 Terraform apply, 1.11 soak) | Medio — primer deploy real |
| Mes 3-4 | LB#11 sigue, LB#16 cross-validation, LB#22/#23 borradores de paper | Medio — paper writing arranca |
| Mes 5-6 | Ops del M2 swap (TimescaleDB migration), LB#11 cierra | Medio |
| Mes 7-9 | LB#2 testbed infra (docker-compose), `independent_servers.yaml` curation, LB#22/#23 final, LB#12/#13 admin | Alto — concentración de trabajo no-código |
| Mes 10-11 | LB#7/#18/#20/#21 re-verifications, paper finalization, ops del three-tier archival | Alto |
| Mes 12 | M3 LAUNCH supervision + Story 4.7 coordination | Punta |

**Carga total maintainer estimada:** ~15-20 días dispersos en 12 meses para los LBs no-código + ~3-5 días por sprint para review de PRs de Amelia + ops puntuales.

---

## Cómo actualizar este plan

- Cuando una story se complete, marcar en `sprint-status.yaml` (Amelia lo hace automáticamente vía `bmad-dev-story`)
- Cuando un LB se cierre, actualizar `launch_blockers.yaml` con `status: cleared`, `cleared_by: <story-id-o-binnacle>`, `cleared_at: <date>`
- Cuando un sprint termine, considerar `bmad-retrospective` para captar lessons learned
- Cuando aparezca un cambio significativo (e.g., LB nuevo, scope change), considerar `bmad-correct-course`
