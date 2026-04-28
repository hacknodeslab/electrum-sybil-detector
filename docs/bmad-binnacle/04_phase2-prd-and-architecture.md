# Bitácora — Phase 2 PRD + Architecture · electrum-sybil-detector

**Fase BMad / BMad Phase:** 2 — Planning (PRD + Architecture)
**Modo / Mode:** Skill-driven (`bmad-create-prd` + `bmad-create-architecture`)
**Sesión / Session:** 2026-04-26 (closeout día completo / single-day closeout)
**Scope:** Crear el PRD desde scratch integrando los closeouts de Phase 1, luego la Architecture desde el PRD; ambos artefactos quedan como specs locked para Phase 3

---

## Idiomas / Languages

- 🇪🇸 [Versión en Español](#-bitácora-en-español) — sigue abajo
- 🇬🇧 [English Version](#-log-in-english) — below the Spanish version

---

## Enlaces rápidos / Quick links

- **Bitácora anterior / Previous log:** [`03_phase1-validations.md`](./03_phase1-validations.md) — Phase 1 closeout validations
- **Bitácora siguiente / Next log:** [`05_phase3-epics-and-stories.md`](./05_phase3-epics-and-stories.md) — Phase 3 Epics & Stories
- **PRD producido / PRD produced:** [`../../_bmad-output/planning-artifacts/prd.md`](../../_bmad-output/planning-artifacts/prd.md) — 645 líneas, 42 FRs, 17 NFRs, 26 launch-blockers
- **Architecture producida / Architecture produced:** [`../../_bmad-output/planning-artifacts/architecture.md`](../../_bmad-output/planning-artifacts/architecture.md) — 1277 líneas, 8 steps, 7 categorías de decisiones (D1–D7)
- **Validation report:** [`../../_bmad-output/planning-artifacts/validation-report-2026-04-26.md`](../../_bmad-output/planning-artifacts/validation-report-2026-04-26.md) — PRD validation pre-architecture

---

<a id="-bitácora-en-español"></a>

## 🇪🇸 Bitácora en Español

> 🌐 [Switch to English Version](#-log-in-english)

### Contexto

Phase 1 cerró el 2026-04-26 con las 3 validaciones técnicas en verde y el commit `13bec1f phase-1 closeout: 3 validations done`. Natural next step según `03_phase1-validations.md`: entrar a Phase 2 con `bmad-create-prd`. La sesión del 2026-04-26 ejecutó dos sub-sesiones encadenadas (PRD → Architecture) en el mismo día.

Tres restricciones operacionales únicas a esta Phase 2:

1. **Integración de closeouts de Phase 1 en el PRD** — los 3 closeouts (fee-histogram via lectura de código, asyncio timing benchmark, snowball IPv6 dual-stack) tenían que materializarse como FRs y NFRs concretos, no como notas al pie.
2. **Doble carve-out de complejidad** — `rigor.statistical_methodology` y `rigor.legal_framing` levantaron el bar en ejes específicos del PRD que el template default no cubría.
3. **Solo-researcher SPOF como input arquitectónico** — la architecture tenía que ser deployable y reproducible por una sola persona con $500/año, NO por un equipo.

### Sub-sesión 1 — PRD vía `bmad-create-prd`

#### Inputs consumidos

13 documentos de planning fueron alimentados al workflow (PRFAQ original + distillate, technical research, project brief, architecture stub previa, roadmap, tech-stack, references, las 3 bitácoras de Phase 0–1, los 2 experimentos de Phase 1). El `inputDocuments` del frontmatter del PRD los lista todos.

#### Pivotes clave durante la creación del PRD

**Pivote 1 — Reframe del fee-histogram testbed (FR19 + FR24 + LB#2).** El closeout de Phase 1 cerró la pregunta binaria ("¿es bit-idéntico?") por lectura de código y dijo "no, por construcción". El PRD tenía que NO tirar el testbed (era LB#2 priority-1), sino reformularlo: de "test de identidad" a "calibración de magnitud Wasserstein". Resultó en:

- **FR19** = "compute the 1-D Wasserstein distance (Earth Mover's Distance) between `mempool.get_fee_histogram` outputs across all server pairs" — la métrica canónica reemplazó la igualdad.
- **FR24** = "run the fee-histogram drift-magnitude calibration harness against a multi-frontend matrix sharing one Bitcoin Core" — el testbed sigue, pero su output cambió: ya no es boolean pass/fail, es la distribución que fija el threshold de cluster.
- **LB#2** quedó "pending — empirical drift-magnitude testbed against the 5-frontend matrix" — pero la pregunta binaria está cerrada.

**Pivote 2 — IPv6 dual-stack como M0 requirement (NFR10 + LB#26 nuevo).** La validación 3 de Phase 1 (snowball desde EC2 dual-stack vs Mac IPv4-only) midió empíricamente que ~28% de la red Electrum es IPv6-only. Eso cambia la naturaleza de "IPv6 support":

- **Antes:** roadmap nice-to-have a M2 o M3.
- **Después:** **M0 hard requirement** porque IPv4-only ve solo 246/344 servidores (28% de la red invisible). NFR10 se enriquecó con sub-bullet "tunnels banned" (Hurricane Electric / ZeroTier introducen latency hop que confunde el signal de fork-race).
- **LB#26 agregado** — operational gate verificando que el host de deploy hace IPv6 outbound antes de ir live.

**Pivote 3 — asyncio timing benchmark resultado en NFR2 con números concretos.** El benchmark midió p99 fanout-broadcast spread = 587 µs at N=100, 1.71 ms at N=200. La metodología tiene signal floor de "cientos de ms" en fork-races. Eso le permitió a NFR2 escribir explícitamente "the methodology's signal floor (hundreds of ms) is large compared to this measurement noise; tighter resolution is M4 Rust-rewrite territory, not M3" — cerrando LB#15 con números empíricos en lugar de aspiraciones.

#### Decisiones estructurales del PRD

- **Three-tier archival** locked desde la Executive Summary: `bitcoin-data` GitHub + Zenodo DOI + arXiv preprint. Failure domains independientes (loss de uno no invalida la contribución).
- **Cited-only intent attribution rule** — locked como subsección de Output Guardrails. La distinción entre "shared infrastructure clusters" (originable) y "operator X runs Y" (cited-only desde b10c issue #11 + CoinDesk 2021) es ahora un ítem auditable, no un soft preference.
- **Two-papers plan** — M3 methodology paper + M3+X multi-vantage follow-up. Convierte la tensión "ship-weak-or-delay" en programa de research, no one-shot. Decision lock en Step 2b del workflow.
- **Anti-success triggers explícitos** (IQ9 paths) — 6/12 meses post-launch pre-committed: Path 1 (graceful shutdown), Path 2 (handoff a b10c orbit / academic group), Path 3 (continue 6 more months). Pre-comprometido EN el PRD, no después.
- **26-item launch-blocker checklist** — items 1–23 verbatim del PRFAQ Stage 3+4, items 24+25 promovidos del cuerpo del PRD, item 26 agregado tras la validación de Phase 1. La numeración es estable.

#### Validation report y editHistory

El PRD pasó por una validation pass intermedia (`validation-report-2026-04-26.md`) antes de cerrar. Resultado: PASS. El `editHistory` del frontmatter documenta los 3 bloques de cambios post-Phase-1: Block 1 (fee-histogram reframe), Block 2 (asyncio LB#15 cleared), Block 3 (IPv4+IPv6 M0 requirement + LB#26).

### Sub-sesión 2 — Architecture vía `bmad-create-architecture`

#### Inputs consumidos

10 documentos: el PRD recién cerrado + PRFAQ + distillate + technical research + validation report + project-brief + architecture stub previa (`docs/architecture.md`) + tech-stack + roadmap + references. La architecture lee TODO porque cada decisión tiene que ser trazable a un FR, NFR, o constraint operacional.

#### Decisión load-bearing — Starter template = NONE

El step-02 del workflow (Starter Template Evaluation) evaluó 6 candidatos (`cookiecutter-pypackage`, `cookiecutter-data-science`, `python-poetry` starter, `oclif`, Next.js / Vite / T3 / Expo / NestJS) y los rechazó a todos. Razones:

1. **M0 stdlib-only constraint** del PRD §Roadmap — cualquier starter inyecta dependencias antes de que se las haya ganado.
2. **`fork-observer` reuse posture (LB#8)** — Discovery + Collection se diseñaron para consumir o compartir code paths con la herramienta de b10c; un scaffold opinionado competiría con esa integración.
3. **Reproducibility-driven acceptance** — el tool se juzga por regeneración determinista del dataset, no por DX o packaging polish. Un starter optimiza el eje incorrecto.

Resultado: **bespoke project skeleton**. Story 1.1 de Phase 3 (futura) hereda esta decisión como AR1 load-bearing — la primera historia del proyecto NO es "init from cookiecutter", es "scaffold a mano según el layout documentado en architecture.md L120–L131".

#### Las 7 categorías de decisiones (D1–D7)

El step-04 ratificó 60+ decisiones agrupadas en 7 categorías. Highlights:

**D1 — Language & Runtime.** Python ≥ 3.11 floor (TaskGroup + `time.monotonic_ns` + pandas 3.0/pyarrow 24/scipy/sklearn baselines lo requieren). CI matrix 3.11/3.12/3.13/3.14. `mypy 1.20+ --strict`. M0 stdlib-only enforced. M4 Rust pin diferido a M4 entry.

**D2 — Data Architecture & Storage.** Two-tier (raw append-only + derived churnable). M0–M1 = SQLite WAL + window files. M2+ = TimescaleDB 2.26+ on PostgreSQL 18 (PG 15 disqualified — EOL junio 2026). Parquet via pyarrow 24.x con Zstd. **BLAKE2b-256 stdlib hash** para opaque server identifiers (mantiene M0 stdlib-only). `monotonic_ns BIGINT` + `wall_clock_ns BIGINT` siempre dos columnas, nunca una.

**D3 — Connection & Transport Architecture.** `asyncio.TaskGroup` pool, una task por server (validado por NFR2 empírico). `Transport` Protocol class con TCP + SSL impls a M0; Tor SOCKS5 dropea como nuevo impl a M2 SIN re-arquitectura. Opportunistic TLS (no pinning — self-signed certs comunes en Electrum ecosystem). `happy-eyeballs disabled` — siempre intentar v6 primero cuando AAAA existe (Phase-1 V3 evidence).

**D4 — Module Boundaries.** 5 módulos producción + 3 supporting (`audit/`, `selftest/`, `harness/`). **Inter-module surface = Python `Protocol` classes** — no DI framework, no message bus. **Storage como single integration point** — sólo `storage/` posee mutating database operations. Esta invariante es lo que hace que el SQLite→TimescaleDB swap sea backend-swap, no rewrite project-wide.

**D5 — Analysis Pipeline.** `scipy.stats.wasserstein_distance` (1-D) canónico — la métrica canónica DEBE usar la librería canónica, no re-implementar. Thresholds en `selftest/thresholds.yaml` **frozen pre-M3** para prevenir post-hoc tuning. **DBSCAN primario + Ward secondary** para sensitivity analysis (sklearn 1.6+). **Benjamini–Hochberg FDR** + bootstrap CIs + power analysis disclosed. **Pure Python a M3** — sin Cython, sin Numba (reproducibility > raw speed a M3 scale).

**D6 — Infrastructure & Deployment.** AWS EC2 t4g.small (ARM Graviton, 2 vCPU, 2 GB) en us-east-1 — credits del usuario + native v6 explícito en VPC. Debian 13 ARM64 AMI. `chrony` NTP (mejor accuracy reporting que ntpd). systemd con `Restart=on-failure` + structured-JSON logs a journal. **No Docker a M0–M1** — Docker añade isolation layer que complica monotonic-ns guarantees (LB#5 cubre Docker como user-facing first-run-guide convenience, NOT deploy reality). Three-tier archival via idempotent helper scripts. **Bilingual CI staleness via GitHub Action** diff-eando `*.md` vs `*.es.md` mtimes con >14d warn / >30d release-blocking.

**D7 — Dev Tooling.** `hatchling` build backend (PEP-621 native). **`uv` (Astral)** para venv + lockfile + Python version mgmt — `uv.lock` pina entire tree byte-by-byte (alineado con reproducibility contract). **`ruff` 0.15.12+** con strict ruleset (E, F, W, I, N, UP, B, A, C4, SIM, ARG, PL). **`pytest 8.4+` + `pytest-asyncio 1.3.x`** (evitar `1.4.0a1` prerelease). `pre-commit 4.x`. Sin Sphinx a M0–M3 — bilingual `README.md` + `README.es.md` + `schema.json` + sidecars suficientes.

#### Step 7 — Implementation Patterns + Step 8 — Project Structure

El step-07 documentó 17 áreas de conflicto donde AI agents podrían divergir, y pinó cada uno: naming patterns (snake_case ubicuo, `_ns`/`_ts` time columns, `_hash` columns, `_id` foreign keys), structure patterns (PEP 621 + src-layout, no `utils/` package), format patterns (time pair invariant, JSON snake_case, manifest schema), communication patterns (Protocol classes only, Storage write discipline, `derived_run_id` discipline), process patterns (exception hierarchy, async cancellation handling, reconnection backoff con código exacto, determinism contract).

El step-08 documentó toda la estructura del proyecto con tags `[M0]` / `[M1]` / `[M2]` / `[M3]` / `[M4]` por archivo — single source of truth para Phase 3 epic+story design.

### Meta-lecciones de esta sesión

**1. Doc-as-locked-spec discipline funcionó.** El `editHistory` del frontmatter del PRD documenta cada bloque de cambios post-cierre con commit reference, scope del cambio, y rationale. Esto convierte el PRD en un artefacto auditable cuando 6 meses después alguien pregunta "¿por qué FR19 dice Wasserstein y no bit-identity?" — la respuesta vive en el editHistory + cross-reference a `03_phase1-validations.md`.

**2. Los carve-outs (`rigor.statistical_methodology` + `rigor.legal_framing`) shaped specific PRD sections.** Sin ellos, la sección "Output Guardrails" hubiera sido un párrafo soft. Con el carve-out legal, se materializó en: phrasing bank versionado, audit pre-publication como launch gate, "what a flagged cluster does NOT mean" text mandatory en dataset README + paper, disclosure issue template, cited-only intent attribution rule. Los carve-outs de complejidad NO son metadata; son inputs estructurales del documento.

**3. La architecture's "Implementation Sequence" (11 stories) emergió como el spine para Phase 3.** El step-04 produjo una secuencia ordenada de 11 stories que cubren M0→M3 launch. Phase 3 (epics & stories) tomó esa secuencia como starting point pero la re-organizó por user value en lugar de seguir la secuencia técnica horizontal. La secuencia técnica de architecture se mantiene como referencia ortogonal.

**4. Reading order matters: Phase 1 closeouts → PRD → Architecture, no concurrent.** Si hubiera saltado del Phase 1 closeout directo a Architecture (sin PRD), la architecture no hubiera tenido las 26 launch blockers ni los carve-outs ni los anti-success triggers como inputs ratificados. El PRD existe para ser un contract previo a la architecture, no un artifact paralelo.

**5. La architecture es deliberadamente conservadora en dependencias.** PG 15 disqualified por EOL junio 2026; PG 18 elegido para evitar un ciclo de upgrade pre-M3. `pytest-asyncio 1.4.0a1` rechazado por ser prerelease. Cada dep adoptada es earned (M0 stdlib-only; M1+ analytical stack solo cuando el módulo lo necesita). Esto ralentiza la primera implementación pero protege la reproducibilidad longitudinal.

### Resumen / Status

| Artefacto | Estado al 2026-04-26 EOD | Líneas | Próximo consumidor |
|---|---|---|---|
| `_bmad-output/planning-artifacts/prd.md` | ✅ COMPLETE — 5/5 validations passed | 645 | Architecture (consumed); Epics & Stories |
| `_bmad-output/planning-artifacts/architecture.md` | ✅ COMPLETE — 8/8 steps | 1277 | Epics & Stories |
| `_bmad-output/planning-artifacts/validation-report-2026-04-26.md` | ✅ PASS | — | Bitácora histórica |

**Phase 2 cerrada.** Natural next step: Phase 3 con `bmad-create-epics-and-stories` consumiendo PRD + Architecture.

### Files touched / Archivos tocados

| Archivo | Naturaleza del cambio |
|---|---|
| [`_bmad-output/planning-artifacts/prd.md`](../../_bmad-output/planning-artifacts/prd.md) | New. PRD completo con 42 FRs, 17 NFRs, 26 launch-blockers, 5 forced top-level sections (dataset_requirements, publication_requirements, measurement_validity, output_guardrails, bilingual_parity), 2 carve-outs (rigor.statistical_methodology + rigor.legal_framing). |
| [`_bmad-output/planning-artifacts/architecture.md`](../../_bmad-output/planning-artifacts/architecture.md) | New. Architecture decision document con 8 steps: Project Context, Starter Template Evaluation (= NONE), Core Architectural Decisions (D1–D7), Implementation Patterns, Project Structure & Boundaries. |
| [`_bmad-output/planning-artifacts/validation-report-2026-04-26.md`](../../_bmad-output/planning-artifacts/validation-report-2026-04-26.md) | New. PRD validation pass report. |
| Esta bitácora / This log | New, documents the Phase 2 PRD + Architecture session. |

### Next steps

1. ~~**PRD creation**~~ — **closed 2026-04-26.**
2. ~~**Architecture creation**~~ — **closed 2026-04-26.**
3. **Phase 3 (Epics & Stories)** — natural next step. Trigger: `bmad-create-epics-and-stories`. Consume PRD + Architecture; produce `epics.md` con FRs decompuestos en historias implementables. Cubierto en bitácora `05_phase3-epics-and-stories.md`.
4. **Pendiente paralelo:** fee-histogram empirical testbed (LB#2 priority-1) — requiere coordinación con infra (Bitcoin Core + 5 frontends en docker-compose). NO bloquea Phase 3 (la calibration harness es Story 3.1 de Phase 3, pero la implementación efectiva del testbed corre en paralelo a la implementación de Story 1.x).

---

<a id="-log-in-english"></a>

## 🇬🇧 Log in English

> 🌐 [Cambiar a Versión en Español](#-bitácora-en-español)

### Context

Phase 1 closed 2026-04-26 with the 3 technical validations green and commit `13bec1f phase-1 closeout: 3 validations done`. Natural next step per `03_phase1-validations.md`: enter Phase 2 with `bmad-create-prd`. The 2026-04-26 session executed two chained sub-sessions (PRD → Architecture) on the same day.

Three operational constraints unique to this Phase 2:

1. **Phase 1 closeouts integrated into PRD** — the 3 closeouts (fee-histogram via code reading, asyncio timing benchmark, snowball IPv6 dual-stack) had to materialize as concrete FRs and NFRs, not footnotes.
2. **Two complexity carve-outs** — `rigor.statistical_methodology` and `rigor.legal_framing` raised the bar on specific PRD axes the default template did not cover.
3. **Solo-researcher SPOF as architectural input** — the architecture had to be deployable and reproducible by a single person with $500/year, NOT by a team.

### Sub-session 1 — PRD via `bmad-create-prd`

#### Inputs consumed

13 planning documents were fed into the workflow (original PRFAQ + distillate, technical research, project brief, prior architecture stub, roadmap, tech-stack, references, the 3 binnacles from Phase 0–1, the 2 Phase-1 experiments). The PRD's frontmatter `inputDocuments` lists them all.

#### Key pivots during PRD creation

**Pivot 1 — Fee-histogram testbed reframe (FR19 + FR24 + LB#2).** The Phase 1 closeout closed the binary question ("is it bit-identical?") via code reading and answered "no, by construction". The PRD had to NOT discard the testbed (it was LB#2 priority-1) but reformulate it: from "identity test" to "Wasserstein magnitude calibration". Resulted in:

- **FR19** = "compute the 1-D Wasserstein distance (Earth Mover's Distance) between `mempool.get_fee_histogram` outputs across all server pairs" — the canonical metric replaced equality.
- **FR24** = "run the fee-histogram drift-magnitude calibration harness against a multi-frontend matrix sharing one Bitcoin Core" — the testbed remains, but its output changed: no longer boolean pass/fail, it's the distribution that fixes the cluster threshold.
- **LB#2** stayed "pending — empirical drift-magnitude testbed against the 5-frontend matrix" — but the binary question is closed.

**Pivot 2 — IPv6 dual-stack as M0 requirement (NFR10 + new LB#26).** Phase 1's Validation 3 (snowball from EC2 dual-stack vs Mac IPv4-only) measured empirically that ~28% of the Electrum network is IPv6-only. This changes the nature of "IPv6 support":

- **Before:** roadmap nice-to-have at M2 or M3.
- **After:** **M0 hard requirement** because IPv4-only sees only 246/344 servers (28% of network invisible). NFR10 was enriched with sub-bullet "tunnels banned" (Hurricane Electric / ZeroTier introduce a latency hop confounding the fork-race signal).
- **LB#26 added** — operational gate verifying the deploy host does IPv6 outbound before going live.

**Pivot 3 — asyncio timing benchmark result in NFR2 with concrete numbers.** The benchmark measured p99 fanout-broadcast spread = 587 µs at N=100, 1.71 ms at N=200. Methodology has signal floor of "hundreds of ms" in fork-races. That allowed NFR2 to write explicitly "the methodology's signal floor (hundreds of ms) is large compared to this measurement noise; tighter resolution is M4 Rust-rewrite territory, not M3" — closing LB#15 with empirical numbers instead of aspirations.

#### Structural PRD decisions

- **Three-tier archival** locked from the Executive Summary: `bitcoin-data` GitHub + Zenodo DOI + arXiv preprint. Independent failure domains (loss of one does not invalidate the contribution).
- **Cited-only intent attribution rule** — locked as a sub-section of Output Guardrails. The distinction between "shared infrastructure clusters" (originable) and "operator X runs Y" (cited-only from b10c issue #11 + CoinDesk 2021) is now an auditable item, not a soft preference.
- **Two-papers plan** — M3 methodology paper + M3+X multi-vantage follow-up. Converts the "ship-weak-or-delay" tension into a research program, not a one-shot. Decision lock at workflow Step 2b.
- **Explicit anti-success triggers** (IQ9 paths) — 6/12 months post-launch pre-committed: Path 1 (graceful shutdown), Path 2 (handoff to b10c orbit / academic group), Path 3 (continue 6 more months). Pre-committed IN the PRD, not after.
- **26-item launch-blocker checklist** — items 1–23 verbatim from PRFAQ Stage 3+4, items 24+25 promoted from PRD body, item 26 added after Phase-1 validation. Numbering is stable.

#### Validation report and editHistory

The PRD passed an intermediate validation pass (`validation-report-2026-04-26.md`) before closing. Result: PASS. The frontmatter's `editHistory` documents the 3 blocks of post-Phase-1 changes: Block 1 (fee-histogram reframe), Block 2 (asyncio LB#15 cleared), Block 3 (IPv4+IPv6 M0 requirement + LB#26).

### Sub-session 2 — Architecture via `bmad-create-architecture`

#### Inputs consumed

10 documents: the just-closed PRD + PRFAQ + distillate + technical research + validation report + project-brief + prior architecture stub (`docs/architecture.md`) + tech-stack + roadmap + references. The architecture reads EVERYTHING because every decision must be traceable to an FR, NFR, or operational constraint.

#### Load-bearing decision — Starter template = NONE

Workflow step-02 (Starter Template Evaluation) evaluated 6 candidates (`cookiecutter-pypackage`, `cookiecutter-data-science`, `python-poetry` starter, `oclif`, Next.js / Vite / T3 / Expo / NestJS) and rejected all of them. Reasons:

1. **PRD §Roadmap M0 stdlib-only constraint** — any starter injects dependencies before they're earned.
2. **`fork-observer` reuse posture (LB#8)** — Discovery + Collection were designed to consume or share code paths with b10c's tool; an opinionated scaffold would compete with that integration.
3. **Reproducibility-driven acceptance** — the tool is judged by deterministic dataset regeneration, not by DX or packaging polish. A starter optimizes the wrong axis.

Result: **bespoke project skeleton**. Future Phase-3 Story 1.1 inherits this decision as load-bearing AR1 — the project's first story is NOT "init from cookiecutter", it's "scaffold by hand per the layout documented in architecture.md L120–L131".

#### The 7 decision categories (D1–D7)

Step-04 ratified 60+ decisions grouped into 7 categories. Highlights:

**D1 — Language & Runtime.** Python ≥ 3.11 floor (TaskGroup + `time.monotonic_ns` + pandas 3.0/pyarrow 24/scipy/sklearn baselines require it). CI matrix 3.11/3.12/3.13/3.14. `mypy 1.20+ --strict`. M0 stdlib-only enforced. M4 Rust pin deferred to M4 entry.

**D2 — Data Architecture & Storage.** Two-tier (raw append-only + derived churnable). M0–M1 = SQLite WAL + window files. M2+ = TimescaleDB 2.26+ on PostgreSQL 18 (PG 15 disqualified — EOL June 2026). Parquet via pyarrow 24.x with Zstd. **BLAKE2b-256 stdlib hash** for opaque server identifiers (preserves M0 stdlib-only). `monotonic_ns BIGINT` + `wall_clock_ns BIGINT` always two columns, never one.

**D3 — Connection & Transport Architecture.** `asyncio.TaskGroup` pool, one task per server (validated by NFR2 empirical). `Transport` Protocol class with TCP + SSL impls at M0; Tor SOCKS5 drops in as new impl at M2 WITHOUT re-architecture. Opportunistic TLS (no pinning — self-signed certs common in Electrum ecosystem). `happy-eyeballs disabled` — always try v6 first when AAAA exists (Phase-1 V3 evidence).

**D4 — Module Boundaries.** 5 production modules + 3 supporting (`audit/`, `selftest/`, `harness/`). **Inter-module surface = Python `Protocol` classes** — no DI framework, no message bus. **Storage as single integration point** — only `storage/` owns mutating database operations. This invariant is what makes the SQLite→TimescaleDB swap a backend-swap, not a project-wide rewrite.

**D5 — Analysis Pipeline.** `scipy.stats.wasserstein_distance` (1-D) canonical — the canonical metric MUST use the canonical library, not re-implement. Thresholds in `selftest/thresholds.yaml` **frozen pre-M3** to prevent post-hoc tuning. **DBSCAN primary + Ward secondary** for sensitivity analysis (sklearn 1.6+). **Benjamini–Hochberg FDR** + bootstrap CIs + power analysis disclosed. **Pure Python at M3** — no Cython, no Numba (reproducibility > raw speed at M3 scale).

**D6 — Infrastructure & Deployment.** AWS EC2 t4g.small (ARM Graviton, 2 vCPU, 2 GB) in us-east-1 — user's credits + native v6 explicit in VPC. Debian 13 ARM64 AMI. `chrony` NTP (better accuracy reporting than ntpd). systemd with `Restart=on-failure` + structured-JSON logs to journal. **No Docker at M0–M1** — Docker adds isolation layer that complicates monotonic-ns guarantees (LB#5 covers Docker as user-facing first-run-guide convenience, NOT deploy reality). Three-tier archival via idempotent helper scripts. **Bilingual CI staleness via GitHub Action** diffing `*.md` vs `*.es.md` mtimes with >14d warn / >30d release-blocking.

**D7 — Dev Tooling.** `hatchling` build backend (PEP-621 native). **`uv` (Astral)** for venv + lockfile + Python version mgmt — `uv.lock` pins entire tree byte-by-byte (aligned with reproducibility contract). **`ruff` 0.15.12+** with strict ruleset (E, F, W, I, N, UP, B, A, C4, SIM, ARG, PL). **`pytest 8.4+` + `pytest-asyncio 1.3.x`** (avoid `1.4.0a1` prerelease). `pre-commit 4.x`. No Sphinx at M0–M3 — bilingual `README.md` + `README.es.md` + `schema.json` + sidecars sufficient.

#### Step 7 — Implementation Patterns + Step 8 — Project Structure

Step-07 documented 17 conflict areas where AI agents could diverge, and pinned each: naming patterns (ubiquitous snake_case, `_ns`/`_ts` time columns, `_hash` columns, `_id` foreign keys), structure patterns (PEP 621 + src-layout, no `utils/` package), format patterns (time pair invariant, JSON snake_case, manifest schema), communication patterns (Protocol classes only, Storage write discipline, `derived_run_id` discipline), process patterns (exception hierarchy, async cancellation handling, reconnection backoff with exact code, determinism contract).

Step-08 documented the entire project structure with `[M0]` / `[M1]` / `[M2]` / `[M3]` / `[M4]` tags per file — single source of truth for Phase 3 epic+story design.

### Meta lessons from this session

**1. Doc-as-locked-spec discipline worked.** The PRD frontmatter's `editHistory` documents each block of post-close changes with commit reference, change scope, and rationale. This turns the PRD into an auditable artifact when 6 months later someone asks "why does FR19 say Wasserstein and not bit-identity?" — the answer lives in the editHistory + cross-reference to `03_phase1-validations.md`.

**2. The carve-outs (`rigor.statistical_methodology` + `rigor.legal_framing`) shaped specific PRD sections.** Without them, the "Output Guardrails" section would have been a soft paragraph. With the legal carve-out, it materialized into: versioned phrasing bank, pre-publication audit as launch gate, "what a flagged cluster does NOT mean" mandatory text in dataset README + paper, disclosure issue template, cited-only intent attribution rule. Complexity carve-outs are NOT metadata; they are structural inputs to the document.

**3. The architecture's "Implementation Sequence" (11 stories) emerged as the spine for Phase 3.** Step-04 produced an ordered sequence of 11 stories covering M0→M3 launch. Phase 3 (epics & stories) took that sequence as a starting point but re-organized it by user value rather than following the horizontal technical sequence. The architecture's technical sequence remains as orthogonal reference.

**4. Reading order matters: Phase 1 closeouts → PRD → Architecture, not concurrent.** If I had jumped from Phase 1 closeout straight to Architecture (without PRD), the architecture would not have had the 26 launch blockers nor the carve-outs nor the anti-success triggers as ratified inputs. The PRD exists to be a contract prior to the architecture, not a parallel artifact.

**5. The architecture is deliberately conservative on dependencies.** PG 15 disqualified due to EOL June 2026; PG 18 chosen to avoid an upgrade cycle pre-M3. `pytest-asyncio 1.4.0a1` rejected for being prerelease. Every dep adopted is earned (M0 stdlib-only; M1+ analytical stack only when the module needs it). This slows down the first implementation but protects longitudinal reproducibility.

### Summary / Status

| Artifact | Status as of 2026-04-26 EOD | Lines | Next consumer |
|---|---|---|---|
| `_bmad-output/planning-artifacts/prd.md` | ✅ COMPLETE — 5/5 validations passed | 645 | Architecture (consumed); Epics & Stories |
| `_bmad-output/planning-artifacts/architecture.md` | ✅ COMPLETE — 8/8 steps | 1277 | Epics & Stories |
| `_bmad-output/planning-artifacts/validation-report-2026-04-26.md` | ✅ PASS | — | Historical binnacle |

**Phase 2 closed.** Natural next step: Phase 3 with `bmad-create-epics-and-stories` consuming PRD + Architecture.

### Files touched

| File | Change nature |
|---|---|
| [`_bmad-output/planning-artifacts/prd.md`](../../_bmad-output/planning-artifacts/prd.md) | New. Full PRD with 42 FRs, 17 NFRs, 26 launch-blockers, 5 forced top-level sections (dataset_requirements, publication_requirements, measurement_validity, output_guardrails, bilingual_parity), 2 carve-outs (rigor.statistical_methodology + rigor.legal_framing). |
| [`_bmad-output/planning-artifacts/architecture.md`](../../_bmad-output/planning-artifacts/architecture.md) | New. Architecture decision document with 8 steps: Project Context, Starter Template Evaluation (= NONE), Core Architectural Decisions (D1–D7), Implementation Patterns, Project Structure & Boundaries. |
| [`_bmad-output/planning-artifacts/validation-report-2026-04-26.md`](../../_bmad-output/planning-artifacts/validation-report-2026-04-26.md) | New. PRD validation pass report. |
| This log / Esta bitácora | New, documents the Phase 2 PRD + Architecture session. |

### Next steps

1. ~~**PRD creation**~~ — **closed 2026-04-26.**
2. ~~**Architecture creation**~~ — **closed 2026-04-26.**
3. **Phase 3 (Epics & Stories)** — natural next step. Trigger: `bmad-create-epics-and-stories`. Consumes PRD + Architecture; produces `epics.md` with FRs decomposed into implementable stories. Covered in binnacle `05_phase3-epics-and-stories.md`.
4. **Pending parallel:** fee-histogram empirical testbed (LB#2 priority-1) — requires infra coordination (Bitcoin Core + 5 frontends in docker-compose). Does NOT block Phase 3 (the calibration harness is Story 3.1 of Phase 3, but the actual testbed implementation runs in parallel to Story 1.x implementation).
