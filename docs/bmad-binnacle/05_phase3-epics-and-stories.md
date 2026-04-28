# Bitácora — Phase 3 Epics & Stories · electrum-sybil-detector

**Fase BMad / BMad Phase:** 3 — Solutioning (Epics & Stories breakdown)
**Modo / Mode:** Skill-driven (`bmad-create-epics-and-stories`)
**Sesión / Session:** 2026-04-27 (single-day, ~5h)
**Scope:** Descomponer los 42 FRs + 17 NFRs del PRD + 60+ decisiones de la Architecture en historias implementables de 1 dev session, organizadas en épicas por user value (no por technical layers)

---

## Idiomas / Languages

- 🇪🇸 [Versión en Español](#-bitácora-en-español) — sigue abajo
- 🇬🇧 [English Version](#-log-in-english) — below the Spanish version

---

## Enlaces rápidos / Quick links

- **Bitácora anterior / Previous log:** [`04_phase2-prd-and-architecture.md`](./04_phase2-prd-and-architecture.md) — Phase 2 PRD + Architecture
- **Artefacto producido / Artifact produced:** [`../../_bmad-output/planning-artifacts/epics.md`](../../_bmad-output/planning-artifacts/epics.md) — 1517 líneas, 49 historias, 7 épicas
- **PRD consumido / PRD consumed:** [`../../_bmad-output/planning-artifacts/prd.md`](../../_bmad-output/planning-artifacts/prd.md)
- **Architecture consumida / Architecture consumed:** [`../../_bmad-output/planning-artifacts/architecture.md`](../../_bmad-output/planning-artifacts/architecture.md)

---

<a id="-bitácora-en-español"></a>

## 🇪🇸 Bitácora en Español

> 🌐 [Switch to English Version](#-log-in-english)

### Contexto

Phase 2 cerró el 2026-04-26 EOD con PRD + Architecture ambos `status: complete`. El siguiente paso del workflow BMad es Phase 3: descomponer los FRs en épicas y stories. La sesión del 2026-04-27 ejecutó el workflow `bmad-create-epics-and-stories` end-to-end en una sola sesión continua.

Tres restricciones operacionales únicas a esta Phase 3:

1. **No UX document** — el proyecto es research-daemon archetype, sin UI. La architecture explícitamente dice "N/A (no UI). Output Guardrails phrasing-bank audit is the closest analogue" (architecture.md L141). Esto invalida el path típico de "extract UX-DRs" del workflow.
2. **AR1 load-bearing** — la architecture rechazó todos los starter templates. La primera historia del proyecto (Story 1.1) tenía que ser un bespoke skeleton, no un "init from cookiecutter". Esto exige que las épicas honren la decisión sin re-litigarla.
3. **Phase-gate transitions del PRD/Architecture (M0→M1→M2→M3 launch→M4)** son inputs estructurales — las épicas tienen que respetar la secuencia o explicarse por qué se desvían.

### Inputs consumidos

Solo dos documentos primarios:

- `_bmad-output/planning-artifacts/prd.md` (645 L, 42 FRs, 17 NFRs, 26 LBs)
- `_bmad-output/planning-artifacts/architecture.md` (1277 L, 8 steps, 60+ decisiones D1–D7)

Documentos suplementarios (NO re-parseados — ya estaban absorbidos en PRD/Architecture frontmatter):

- PRFAQ + distillate
- Technical research
- Validation report 2026-04-26
- Las 3 binnacles previas
- Los 2 experimentos de Phase 1

El step-01 del workflow validó que estos eran inputs suficientes y que la ausencia de UX doc era apropiada.

### Step-by-step de la sesión

#### Step 01 — Requirements extraction

- 42 FRs extraídos verbatim del PRD §Functional Requirements, agrupados por las 8 categorías originales (Server Discovery FR1–FR4, Probing FR5–FR10, Storage FR11–FR16, Analysis FR17–FR24, Publication FR25–FR30, Output Guardrails FR31–FR34, Bilingual FR35–FR38, Operational Health FR39–FR42).
- 17 NFRs extraídos verbatim del PRD §Non-Functional Requirements en 7 categorías.
- 44 ARs (Additional Requirements) extraídos de la Architecture, organizados en 9 sub-áreas: starter (AR1), language/runtime/dev tooling (AR2–AR6), module boundaries (AR7–AR11), time/hash/determinism (AR12–AR15), storage backend (AR16–AR19), connection layer (AR20–AR22), analysis pipeline (AR23–AR27), infrastructure (AR28–AR36), calibration harness (AR37), bilingual ops (AR38–AR39), phased gates (AR40–AR43), launch-blocker tracking (AR44).
- UX-DRs section explícitamente N/A con cita de architecture.md L141.

Confirmación del usuario: "go" — extracted requirements aprobados sin modificaciones.

#### Step 02 — Epic design

Diseño colaborativo de 7 épicas organizadas por user value (no technical layer), con cada épica anclada a una persona del PRD §User Journeys:

| Épica | Persona | User outcome |
|---|---|---|
| 1 | Ifuensan | Run a deterministic measurement collector on production host (M0) |
| 2 | Ifuensan | Full-network coverage with sustained collection (M1→M2) |
| 3 | Lukas (analyst) | Produce statistically-rigorous cluster findings (M3 entry) |
| 4 | Sarah / Lukas | Cite the dataset by Zenodo DOI (M3 launch) |
| 5 | Camila / Diego | Output guardrails + flagged-operator disclosure (M0 audit → M3 disclosure) |
| 6 | Óscar | Bilingual EN+ES parity (M0 → ongoing) |
| 7 | Ifuensan | Operational stewardship: uptime, SLAs, LB tracking (M0 → ongoing) |

Verificaciones de epic-independence + within-epic-dependency-flow pasaron en review. Coverage map: 42/42 FRs mapeados a exactamente una épica, sin orphans, sin duplicados.

Confirmación del usuario: "C" — epic structure aprobada.

#### Step 03 — Story generation (sequential per epic)

Generación de las 49 stories en 7 sub-pasos, uno por épica. Por cada épica:

1. Propuesta de breakdown en tabla (story title + capability + FR/NFR/AR coverage + phase) → review del usuario con preguntas específicas (ej. "stories OK?", "fold X+Y?", "introduce dep X?").
2. Tras "go" del usuario, escritura de las stories completas con Given/When/Then ACs en lenguaje testable.
3. Append al `epics.md` (no overwrite — preserva todo lo previo).
4. Verificación de cobertura tras cada épica (tabla FR → Story).

Resumen final por épica:

| Épica | Stories | FRs | Líneas |
|---|---|---|---|
| 1 (M0 Foundation) | 11 (1.1–1.11) | FR1, FR5, FR6, FR8–FR14, FR16 | ~240 |
| 2 (M1→M2 Discovery+Collection) | 9 (2.1–2.9) | FR2, FR3, FR4, FR7, FR15, FR40 | ~200 |
| 3 (Analysis methodology) | 10 (3.1–3.10) | FR17–FR24 | ~205 |
| 4 (Publication) | 7 (4.1–4.7) | FR25–FR30 | ~155 |
| 5 (Output Guardrails) | 5 (5.1–5.5) | FR31–FR34 | ~120 |
| 6 (Bilingual) | 4 (6.1–6.4) | FR35–FR38 | ~100 |
| 7 (Operational) | 3 (7.1–7.3) | FR39, FR41, FR42 | ~95 |

#### Step 04 — Final validation

Pasos verificados:

- ✅ FR coverage: 42/42 mapped, no orphans, no duplicates
- ✅ Architecture compliance: AR1 (no starter) honored en Story 1.1; database tables creadas solo cuando la story las necesita (incremental migrations 0001–0012); no upfront big technical work
- ✅ Story quality: Single-dev-session sized; Given/When/Then ACs concretos con file paths + function signatures + table schemas; no forward-dependencies (5.3 tiene una forward reference a 5.4, pero no forward dependency — el link puede ser placeholder)
- ✅ Epic independence: cada épica delivers value standalone usando solo épicas previas
- ✅ Within-epic story dependency flow: cada story builds solo en stories previas

Frontmatter actualizada a `status: complete`, `completedAt: 2026-04-27`, `stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04']`.

### Pivotes y decisiones clave durante la sesión

**Pivote 1 — 7 épicas en lugar de 5.** La propuesta inicial podría haber consolidado Output Guardrails (5) + Bilingual (6) + Operational (7) en uno o dos epics cross-cutting. Decisión: mantenerlos separados porque (a) cada uno tiene una persona distinta del PRD, (b) cada uno tiene mecánica de implementación distinta (regex audit vs. mtime CI vs. journalctl monitoring), (c) cada uno arranca en M0 pero termina en milestones distintos. La separación da visibilidad — si fueran un epic monolítico, Spanish-language SLA de Óscar quedaría escondido detrás del flagged-operator disclosure de Diego.

**Pivote 2 — Phase-gate verification stories como first-class artifacts.** Decisión emergente en Epic 1 (Story 1.11 = "M0→M1 gate verification + per-window NTP manifest persistence") que se replicó orgánicamente en cada épica subsecuente: 2.5 (M1→M2), 2.9 (M2→M3), 3.10 (M3 analysis ship-readiness), 4.7 (M3 launch). Estas stories NO son test plans — son stories con user value ("Ifuensan can confirm M0→M1 readiness with empirical evidence captured in binnacle"). El PRD no las pedía; emergieron de la necesidad de convertir los AR40–AR43 phase gates en deliverables auditables. **Esta es la meta-lección más importante de la sesión.**

**Pivote 3 — Story 3.1 (calibration harness) FIRST in Epic 3.** El PRD ranks LB#2 como priority-1 alongside LB#11 b10c socialization. La calibration harness (FR24) tenía que ser la PRIMERA story de Epic 3 porque su output (Wasserstein threshold calibrado) es input de Story 3.8 (multi-signal threshold engine). Si la harness fuera última, Story 3.8 tendría una forward dependency. Reordenamiento: 3.1 (harness) → 3.2 (scaffolding) → 3.3 (fork-race ingest) → 3.4–3.6 (signal computations) → 3.7 (baseline noise floor) → 3.8 (threshold engine) → 3.9 (clustering) → 3.10 (gate). Backward-only deps verificadas.

**Pivote 4 — Story 4.7 como M3 launch coordinator con 9 verifications.** El PRD §Launch-Blocker Checklist + AR43 launch gate generaron un patrón natural: la última story de Epic 4 NO es "ship something new" sino "verify everything from epics 1–7 composes into a launchable package". Las 9 verificaciones (self-test green, bitcoin-data PR merged, Zenodo DOI resolves, arXiv timestamped, phrasing-bank audit green, bilingual mirror parity, LB checklist 100% cleared, paper sections present, three-tier independent failure domains) son consumed-from-other-epics signals. Esto valida la decisión de mantener Output Guardrails + Bilingual + Operational como épicas separadas: si fueran consolidadas, las verifications 5 + 6 + 7 colapsarían en un solo signal opaco.

**Decisión menor — Forward references vs forward dependencies.** Story 5.3 ("What a flagged cluster does NOT mean") referencía Story 5.4 (disclosure issue template) como destino de un link. Discusión: ¿es forward dependency? Decisión: **no, es forward reference**. La story 5.3 es completable sin que 5.4 exista; el link puede ser placeholder durante review de 5.3 y filled-in cuando 5.4 lande. Distinción documentada en validation report.

**Decisión menor — Story 1.10 (AWS deploy) ships partial Spanish docs.** Epic 6 (Bilingual) es M0-foundational pero el bilingual SLA enforcement machinery (staleness CI Story 6.3) lights up M0+. Decisión: Story 1.10 ships `docs/deploy-aws.md` + `.es.md` ambos al mismo tiempo (mismo PR), garantizando bilingual parity desde el primer commit. Epic 6 maintains the discipline; Epic 1 ships the first instance.

### Meta-lecciones de esta sesión

**1. Phase-gate verification stories son una contribución del proceso, no del template.** Ninguno de los workflows BMad standard (`bmad-create-prd`, `bmad-create-architecture`, `bmad-create-epics-and-stories`) explicita que los M0→M1→M2→M3 gates de la architecture deban materializarse como historias con user value. Pero sin ellas, los AR40–AR43 phase gates serían "checklists informales" en algún binnacle futuro. Convertirlas en stories con ACs hace que (a) Amelia sepa qué implementar en el momento del gate, (b) el progreso del proyecto tiene gates auditables en el sprint plan, (c) las binnacles asociadas (`docs/bmad-binnacle/<NN>_<gate>.md`) son entregables de stories, no aspiraciones. **Recomendación para futuros proyectos BMad: cualquier architecture con phase gates merece phase-gate verification stories en sus épicas correspondientes.**

**2. La AR1 (bespoke skeleton) load-bearing decision se honra en Story 1.1, no en una story de "init" separada.** El template del workflow asume que si la architecture especifica un starter template, "Epic 1 Story 1 must be 'Set up initial project from starter template'". Pero AR1 dice "no starter — bespoke". Story 1.1 quedó entonces como "Bespoke M0 project skeleton" con ACs específicos: PEP-621 metadata, src-layout, MIT license, bilingual READMEs, exception hierarchy stub, etc. La diferencia con un starter es real: AR1 prohíbe cookiecutter init, prohíbe `setup.py` legacy, prohíbe `requirements.txt` (todo en `pyproject.toml`). Story 1.1's ACs codifican estas prohibiciones explícitamente, no como "best practices" sino como gates verificables.

**3. La user-value organization triunfa sobre technical-layer organization en proyectos research.** Phase 3 podría haber producido épicas como "Database layer", "Network layer", "Analysis library", "Publication tooling" — eso hubiera matched la architecture's module structure 1:1. Decisión: no. Las épicas se organizan por persona del PRD (Sarah / Lukas / Camila / Óscar / Diego / Ifuensan) y eso fuerza que cada épica produzca un deliverable que una persona específica puede usar. El resultado: Epic 3 produce findings citables por Lukas, no "una librería de análisis"; Epic 4 produce un bundle citable por Sarah, no "scripts de packaging". Esta orientación user-value hace que el proyecto sea fundable (Sarah la grant reviewer ve un epic bundle que entrega valor a su persona) y reproducible (Lukas el peer reviewer ve un epic que entrega lo que él consume).

**4. Las cross-cutting épicas (5, 6, 7) arrancan en M0, no son polish de M3.** Phase 3 podría haber dejado Output Guardrails, Bilingual, Operational como épicas tardías ("una vez que la metodología funciona, agregamos guardrails"). Decisión: no. Las tres son M0-foundational:

- **Epic 5 Story 5.1 (phrasing-bank audit)** ships en M0 porque desde el primer commit los strings tienen que pasar el audit. No se puede retrofit-ear discipline legal en M3.
- **Epic 6 Story 6.1 (bilingual scaffold)** ships en M0 porque el bilingual mirror discipline tiene que existir desde el primer `README.md` que se commitea. Retrofit-ear bilingual a M3 es operativamente imposible (ya hay 6 meses de docs en EN solo).
- **Epic 7 Story 7.1 (uptime monitoring)** ships en M0 porque el rolling 30-day uptime requiere 30 días de data primero. Si arranca en M2, el primer monitor result es a M2+30d, demasiado tarde para detectar IQ5 triage trigger.

Esta decisión se reflejó en la milestone-arrival table de cada épica: cross-cutting épicas dicen "M0 → ongoing", no "M3+".

**5. 49 stories es chunky pero defendible.** El proyecto tiene 12 meses de runway M0→M3. Eso da ~1 story/semana ritmo promedio. Algunas stories son 1 dev session (Story 1.1 skeleton); otras son 1 semana (Story 2.7 TimescaleDB swap incluyendo data migration utility). Las stories chunky tienen ACs que los dividen internamente (Story 2.7 tiene una sub-AC explícita para `tests/storage/test_storage_protocol_parity.py`) — Amelia o Ifuensan pueden mergear en sub-PRs internos a una story sin romper la story como unidad de coherencia. La alternativa (split aún más fino) hubiera producido 80+ stories y cada una con menos coherencia.

### Sesgos del agente que el usuario corrigió o ratificó

**Ratificado:** Mantener phase-gate verification stories separadas (1.11, 2.5, 2.9, 3.10, 4.7). El usuario no pidió fold; al contrario, "go" aceptó el patrón en cada épica.

**Ratificado:** 7 épicas en lugar de 5. Usuario no pidió consolidar; aceptó el split por user-persona.

**Ratificado:** Tar `pyasn` como primera runtime dep en Story 2.2. Usuario no pidió alternativa con MaxMind GeoLite2. Earned-dependency principle preservada.

**Ratificado:** Story 4.7 como launch coordinator. Usuario no pidió fold en stories anteriores.

**Ratificado:** Story 6.4 escape hatch `--accept-divergence` con rationale binnacle obligatorio. Usuario no pidió strict zero-divergence enforcement.

**Ratificado:** Phasing M0/M2+ dentro de Story 7.1 en lugar de split en 7.1a + 7.1b. Earned-dependency principle preservada (Grafana entra cuando se necesita, no antes).

### Resumen / Status

| Artefacto | Estado al 2026-04-27 EOD | Métrica |
|---|---|---|
| `_bmad-output/planning-artifacts/epics.md` | ✅ COMPLETE — 4/4 workflow steps | 1517 líneas, 49 stories, 7 épicas, 42/42 FRs covered |
| Epic 1 (M0 Foundation) | ✅ Stories defined | 11 stories |
| Epic 2 (M1→M2 Discovery+Collection) | ✅ Stories defined | 9 stories |
| Epic 3 (Analysis methodology) | ✅ Stories defined | 10 stories |
| Epic 4 (Publication) | ✅ Stories defined | 7 stories |
| Epic 5 (Output Guardrails) | ✅ Stories defined | 5 stories |
| Epic 6 (Bilingual) | ✅ Stories defined | 4 stories |
| Epic 7 (Operational) | ✅ Stories defined | 3 stories |

**Phase 3 cerrada.** Natural next step: **Phase 4 — Sprint planning y dev-story execution**. Trigger: `bmad-sprint-planning` (genera sprint plan desde epics.md) → `bmad-create-story <id>` (crea story file con context completo) → `bmad-dev-story <story-file>` (Amelia implementa) → review humano → siguiente.

### Files touched / Archivos tocados

| Archivo | Naturaleza del cambio |
|---|---|
| [`_bmad-output/planning-artifacts/epics.md`](../../_bmad-output/planning-artifacts/epics.md) | New. 49 stories en 7 épicas, cada story con Given/When/Then ACs concretos, file paths, function signatures, table schemas. Coverage Verification appendix con FR matrix + phase-gate stories + cross-cutting CI gates. |
| Esta bitácora / This log | New, documents the Phase 3 Epics & Stories session. |

### Next steps

1. ~~**Epics & Stories breakdown**~~ — **closed 2026-04-27.**
2. **Phase 4a — Sprint planning.** Trigger: `bmad-sprint-planning`. Consume `epics.md`; produce sprint status tracking organizando las 49 stories en sprints implementables. Output esperado: priority order para los primeros sprints (probablemente 1.1 → 1.2 → 1.3 → 1.4, paralelizando 5.1 + 6.1 + 7.1 desde M0).
3. **Phase 4b — Dev story execution loop.** Por cada story del sprint plan: `bmad-create-story <id>` → `bmad-dev-story <file>` → human review → merge. Amelia hace coding heavy-lifting; usuario revisa, opera infra, escribe paper, mantiene conversaciones de comunidad (LB#11 b10c socialization).
4. **Phase 4c — Pre-launch infra coordination (paralelo).** Fee-histogram empirical testbed (LB#2): docker-compose con Bitcoin Core + 5 frontends. Story 3.1 incluye los Dockerfile + compose; el usuario coordina infra + ejecución cuando llega la implementación de Epic 3.
5. **Phase 5 — M3 launch + post-launch monitoring.** Story 4.7 coordinator clearance → 6/12 meses post-launch IQ9 anti-success-trigger window se abre.

### Meta lesson de la sesión, condensada

> **Cuando una architecture tiene phase gates explícitos (M0→M1, etc.), las épicas correspondientes deben tener phase-gate verification stories como first-class artifacts.** Estas stories no son test plans ni aspiraciones — son user-value-bearing deliverables que convierten transitions de fase en gates auditables. El template BMad no las pide; emergen de la lectura cuidadosa de la architecture. Recomendación para retrospectivas BMad: agregar al template la pregunta "¿esta architecture tiene phase gates? ¿hay stories que materializan cada gate?".

---

<a id="-log-in-english"></a>

## 🇬🇧 Log in English

> 🌐 [Cambiar a Versión en Español](#-bitácora-en-español)

### Context

Phase 2 closed 2026-04-26 EOD with PRD + Architecture both `status: complete`. The next step in the BMad workflow is Phase 3: decompose FRs into epics and stories. The 2026-04-27 session executed the `bmad-create-epics-and-stories` workflow end-to-end in a single continuous session.

Three operational constraints unique to this Phase 3:

1. **No UX document** — the project is a research-daemon archetype, no UI. Architecture explicitly states "N/A (no UI). Output Guardrails phrasing-bank audit is the closest analogue" (architecture.md L141). This invalidates the typical "extract UX-DRs" path of the workflow.
2. **AR1 load-bearing** — the architecture rejected all starter templates. The project's first story (Story 1.1) had to be a bespoke skeleton, not "init from cookiecutter". This requires the epics to honor the decision without re-litigating it.
3. **Phase-gate transitions from PRD/Architecture (M0→M1→M2→M3 launch→M4)** are structural inputs — the epics must respect the sequence or explain deviations.

### Inputs consumed

Only two primary documents:

- `_bmad-output/planning-artifacts/prd.md` (645 L, 42 FRs, 17 NFRs, 26 LBs)
- `_bmad-output/planning-artifacts/architecture.md` (1277 L, 8 steps, 60+ decisions D1–D7)

Supplementary documents (NOT re-parsed — already absorbed in PRD/Architecture frontmatter):

- PRFAQ + distillate
- Technical research
- Validation report 2026-04-26
- The 3 prior binnacles
- The 2 Phase-1 experiments

The workflow's step-01 validated these as sufficient inputs and that the absence of a UX document was appropriate.

### Step-by-step of the session

#### Step 01 — Requirements extraction

- 42 FRs extracted verbatim from PRD §Functional Requirements, grouped into the 8 original categories (Server Discovery FR1–FR4, Probing FR5–FR10, Storage FR11–FR16, Analysis FR17–FR24, Publication FR25–FR30, Output Guardrails FR31–FR34, Bilingual FR35–FR38, Operational Health FR39–FR42).
- 17 NFRs extracted verbatim from PRD §Non-Functional Requirements in 7 categories.
- 44 ARs (Additional Requirements) extracted from the Architecture, organized into 9 sub-areas: starter (AR1), language/runtime/dev tooling (AR2–AR6), module boundaries (AR7–AR11), time/hash/determinism (AR12–AR15), storage backend (AR16–AR19), connection layer (AR20–AR22), analysis pipeline (AR23–AR27), infrastructure (AR28–AR36), calibration harness (AR37), bilingual ops (AR38–AR39), phased gates (AR40–AR43), launch-blocker tracking (AR44).
- UX-DRs section explicitly N/A with citation to architecture.md L141.

User confirmation: "go" — extracted requirements approved without modifications.

#### Step 02 — Epic design

Collaborative design of 7 epics organized by user value (not technical layer), each epic anchored to a persona from PRD §User Journeys:

| Epic | Persona | User outcome |
|---|---|---|
| 1 | Ifuensan | Run a deterministic measurement collector on production host (M0) |
| 2 | Ifuensan | Full-network coverage with sustained collection (M1→M2) |
| 3 | Lukas (analyst) | Produce statistically-rigorous cluster findings (M3 entry) |
| 4 | Sarah / Lukas | Cite the dataset by Zenodo DOI (M3 launch) |
| 5 | Camila / Diego | Output guardrails + flagged-operator disclosure (M0 audit → M3 disclosure) |
| 6 | Óscar | Bilingual EN+ES parity (M0 → ongoing) |
| 7 | Ifuensan | Operational stewardship: uptime, SLAs, LB tracking (M0 → ongoing) |

Epic-independence + within-epic-dependency-flow checks passed in review. Coverage map: 42/42 FRs mapped to exactly one epic, no orphans, no duplicates.

User confirmation: "C" — epic structure approved.

#### Step 03 — Story generation (sequential per epic)

Generation of the 49 stories in 7 sub-steps, one per epic. For each epic:

1. Breakdown proposal in table form (story title + capability + FR/NFR/AR coverage + phase) → user review with specific questions (e.g., "stories OK?", "fold X+Y?", "introduce dep X?").
2. After user "go", writing the full stories with Given/When/Then ACs in testable language.
3. Append to `epics.md` (no overwrite — preserves all prior).
4. Coverage verification after each epic (FR → Story table).

Final summary by epic:

| Epic | Stories | FRs | Lines |
|---|---|---|---|
| 1 (M0 Foundation) | 11 (1.1–1.11) | FR1, FR5, FR6, FR8–FR14, FR16 | ~240 |
| 2 (M1→M2 Discovery+Collection) | 9 (2.1–2.9) | FR2, FR3, FR4, FR7, FR15, FR40 | ~200 |
| 3 (Analysis methodology) | 10 (3.1–3.10) | FR17–FR24 | ~205 |
| 4 (Publication) | 7 (4.1–4.7) | FR25–FR30 | ~155 |
| 5 (Output Guardrails) | 5 (5.1–5.5) | FR31–FR34 | ~120 |
| 6 (Bilingual) | 4 (6.1–6.4) | FR35–FR38 | ~100 |
| 7 (Operational) | 3 (7.1–7.3) | FR39, FR41, FR42 | ~95 |

#### Step 04 — Final validation

Verified steps:

- ✅ FR coverage: 42/42 mapped, no orphans, no duplicates
- ✅ Architecture compliance: AR1 (no starter) honored in Story 1.1; database tables created only when the story needs them (incremental migrations 0001–0012); no upfront big technical work
- ✅ Story quality: Single-dev-session sized; concrete Given/When/Then ACs with file paths + function signatures + table schemas; no forward-dependencies (5.3 has a forward reference to 5.4, but no forward dependency — the link can be a placeholder)
- ✅ Epic independence: each epic delivers value standalone using only prior epics
- ✅ Within-epic story dependency flow: each story builds only on prior stories

Frontmatter updated to `status: complete`, `completedAt: 2026-04-27`, `stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04']`.

### Pivots and key decisions during the session

**Pivot 1 — 7 epics instead of 5.** The initial proposal could have consolidated Output Guardrails (5) + Bilingual (6) + Operational (7) into one or two cross-cutting epics. Decision: keep them separate because (a) each has a distinct PRD persona, (b) each has distinct implementation mechanics (regex audit vs. mtime CI vs. journalctl monitoring), (c) each starts at M0 but ends at distinct milestones. The split provides visibility — if they were a monolithic epic, Óscar's Spanish-language SLA would be hidden behind Diego's flagged-operator disclosure.

**Pivot 2 — Phase-gate verification stories as first-class artifacts.** Emergent decision in Epic 1 (Story 1.11 = "M0→M1 gate verification + per-window NTP manifest persistence") that replicated organically in each subsequent epic: 2.5 (M1→M2), 2.9 (M2→M3), 3.10 (M3 analysis ship-readiness), 4.7 (M3 launch). These stories are NOT test plans — they are stories with user value ("Ifuensan can confirm M0→M1 readiness with empirical evidence captured in a binnacle"). The PRD did not request them; they emerged from the need to convert AR40–AR43 phase gates into auditable deliverables. **This is the most important meta-lesson of the session.**

**Pivot 3 — Story 3.1 (calibration harness) FIRST in Epic 3.** PRD ranks LB#2 as priority-1 alongside LB#11 b10c socialization. The calibration harness (FR24) had to be the FIRST story of Epic 3 because its output (calibrated Wasserstein threshold) is input to Story 3.8 (multi-signal threshold engine). If the harness were last, Story 3.8 would have a forward dependency. Reordering: 3.1 (harness) → 3.2 (scaffolding) → 3.3 (fork-race ingest) → 3.4–3.6 (signal computations) → 3.7 (baseline noise floor) → 3.8 (threshold engine) → 3.9 (clustering) → 3.10 (gate). Backward-only deps verified.

**Pivot 4 — Story 4.7 as M3 launch coordinator with 9 verifications.** The PRD §Launch-Blocker Checklist + AR43 launch gate generated a natural pattern: Epic 4's last story is NOT "ship something new" but "verify everything from epics 1–7 composes into a launchable package". The 9 verifications (self-test green, bitcoin-data PR merged, Zenodo DOI resolves, arXiv timestamped, phrasing-bank audit green, bilingual mirror parity, LB checklist 100% cleared, paper sections present, three-tier independent failure domains) are signals consumed-from-other-epics. This validates the decision to keep Output Guardrails + Bilingual + Operational as separate epics: if consolidated, verifications 5 + 6 + 7 would collapse into a single opaque signal.

**Minor decision — Forward references vs forward dependencies.** Story 5.3 ("What a flagged cluster does NOT mean") references Story 5.4 (disclosure issue template) as a link target. Discussion: is it a forward dependency? Decision: **no, it's a forward reference**. Story 5.3 is completable without 5.4 existing; the link can be a placeholder during 5.3's review and filled-in when 5.4 lands. Distinction documented in validation report.

**Minor decision — Story 1.10 (AWS deploy) ships partial Spanish docs.** Epic 6 (Bilingual) is M0-foundational but the bilingual SLA enforcement machinery (staleness CI Story 6.3) lights up M0+. Decision: Story 1.10 ships `docs/deploy-aws.md` + `.es.md` both at the same time (same PR), guaranteeing bilingual parity from the first commit. Epic 6 maintains the discipline; Epic 1 ships the first instance.

### Meta lessons from this session

**1. Phase-gate verification stories are a process contribution, not a template contribution.** None of the standard BMad workflows (`bmad-create-prd`, `bmad-create-architecture`, `bmad-create-epics-and-stories`) explicitly states that the architecture's M0→M1→M2→M3 gates should materialize as stories with user value. But without them, the AR40–AR43 phase gates would be "informal checklists" in some future binnacle. Turning them into stories with ACs makes (a) Amelia know what to implement at gate moment, (b) project progress have auditable gates in the sprint plan, (c) associated binnacles (`docs/bmad-binnacle/<NN>_<gate>.md`) be story deliverables, not aspirations. **Recommendation for future BMad projects: any architecture with phase gates deserves phase-gate verification stories in its corresponding epics.**

**2. The AR1 (bespoke skeleton) load-bearing decision is honored in Story 1.1, not in a separate "init" story.** The workflow template assumes that if the architecture specifies a starter template, "Epic 1 Story 1 must be 'Set up initial project from starter template'". But AR1 says "no starter — bespoke". Story 1.1 thus became "Bespoke M0 project skeleton" with specific ACs: PEP-621 metadata, src-layout, MIT license, bilingual READMEs, exception hierarchy stub, etc. The difference from a starter is real: AR1 forbids cookiecutter init, forbids legacy `setup.py`, forbids `requirements.txt` (everything in `pyproject.toml`). Story 1.1's ACs codify these prohibitions explicitly, not as "best practices" but as verifiable gates.

**3. User-value organization beats technical-layer organization in research projects.** Phase 3 could have produced epics like "Database layer", "Network layer", "Analysis library", "Publication tooling" — that would have matched the architecture's module structure 1:1. Decision: no. Epics are organized by PRD persona (Sarah / Lukas / Camila / Óscar / Diego / Ifuensan) and that forces each epic to produce a deliverable a specific person can use. Result: Epic 3 produces findings citable by Lukas, not "an analysis library"; Epic 4 produces a citable bundle for Sarah, not "packaging scripts". This user-value orientation makes the project fundable (Sarah the grant reviewer sees an epic bundle delivering value to her persona) and reproducible (Lukas the peer reviewer sees an epic delivering what he consumes).

**4. Cross-cutting epics (5, 6, 7) start at M0, are not M3 polish.** Phase 3 could have left Output Guardrails, Bilingual, Operational as late-stage epics ("once methodology works, we add guardrails"). Decision: no. All three are M0-foundational:

- **Epic 5 Story 5.1 (phrasing-bank audit)** ships at M0 because from the first commit strings have to pass the audit. Legal discipline cannot be retrofitted at M3.
- **Epic 6 Story 6.1 (bilingual scaffold)** ships at M0 because the bilingual mirror discipline must exist from the first `README.md` committed. Retrofitting bilingual at M3 is operationally impossible (already 6 months of EN-only docs).
- **Epic 7 Story 7.1 (uptime monitoring)** ships at M0 because rolling 30-day uptime requires 30 days of data first. If it starts at M2, the first monitor result is at M2+30d, too late to detect the IQ5 triage trigger.

This decision is reflected in each epic's milestone-arrival table: cross-cutting epics say "M0 → ongoing", not "M3+".

**5. 49 stories is chunky but defensible.** The project has 12 months of M0→M3 runway. That gives ~1 story/week average pace. Some stories are 1 dev session (Story 1.1 skeleton); others are 1 week (Story 2.7 TimescaleDB swap including data migration utility). Chunky stories have ACs that internally subdivide them (Story 2.7 has an explicit sub-AC for `tests/storage/test_storage_protocol_parity.py`) — Amelia or Ifuensan can merge in story-internal sub-PRs without breaking the story as a coherence unit. The alternative (splitting even finer) would have produced 80+ stories, each with less coherence.

### Agent biases the user corrected or ratified

**Ratified:** Keep phase-gate verification stories separate (1.11, 2.5, 2.9, 3.10, 4.7). User did not request fold; on the contrary, "go" accepted the pattern in each epic.

**Ratified:** 7 epics instead of 5. User did not request consolidation; accepted the split by user-persona.

**Ratified:** Take `pyasn` as the first runtime dep in Story 2.2. User did not request a MaxMind GeoLite2 alternative. Earned-dependency principle preserved.

**Ratified:** Story 4.7 as launch coordinator. User did not request fold into prior stories.

**Ratified:** Story 6.4 escape hatch `--accept-divergence` with mandatory rationale binnacle. User did not request strict zero-divergence enforcement.

**Ratified:** M0/M2+ phasing inside Story 7.1 instead of split into 7.1a + 7.1b. Earned-dependency principle preserved (Grafana enters when needed, not before).

### Summary / Status

| Artifact | Status as of 2026-04-27 EOD | Metric |
|---|---|---|
| `_bmad-output/planning-artifacts/epics.md` | ✅ COMPLETE — 4/4 workflow steps | 1517 lines, 49 stories, 7 epics, 42/42 FRs covered |
| Epic 1 (M0 Foundation) | ✅ Stories defined | 11 stories |
| Epic 2 (M1→M2 Discovery+Collection) | ✅ Stories defined | 9 stories |
| Epic 3 (Analysis methodology) | ✅ Stories defined | 10 stories |
| Epic 4 (Publication) | ✅ Stories defined | 7 stories |
| Epic 5 (Output Guardrails) | ✅ Stories defined | 5 stories |
| Epic 6 (Bilingual) | ✅ Stories defined | 4 stories |
| Epic 7 (Operational) | ✅ Stories defined | 3 stories |

**Phase 3 closed.** Natural next step: **Phase 4 — Sprint planning and dev-story execution**. Trigger: `bmad-sprint-planning` (generates sprint plan from epics.md) → `bmad-create-story <id>` (creates story file with full context) → `bmad-dev-story <story-file>` (Amelia implements) → human review → next.

### Files touched

| File | Change nature |
|---|---|
| [`_bmad-output/planning-artifacts/epics.md`](../../_bmad-output/planning-artifacts/epics.md) | New. 49 stories in 7 epics, each with concrete Given/When/Then ACs, file paths, function signatures, table schemas. Coverage Verification appendix with FR matrix + phase-gate stories + cross-cutting CI gates. |
| This log / Esta bitácora | New, documents the Phase 3 Epics & Stories session. |

### Next steps

1. ~~**Epics & Stories breakdown**~~ — **closed 2026-04-27.**
2. **Phase 4a — Sprint planning.** Trigger: `bmad-sprint-planning`. Consumes `epics.md`; produces sprint status tracking organizing the 49 stories into implementable sprints. Expected output: priority order for the first sprints (probably 1.1 → 1.2 → 1.3 → 1.4, parallelizing 5.1 + 6.1 + 7.1 from M0).
3. **Phase 4b — Dev story execution loop.** Per story in the sprint plan: `bmad-create-story <id>` → `bmad-dev-story <file>` → human review → merge. Amelia does coding heavy-lifting; user reviews, operates infra, writes paper, maintains community conversations (LB#11 b10c socialization).
4. **Phase 4c — Pre-launch infra coordination (parallel).** Fee-histogram empirical testbed (LB#2): docker-compose with Bitcoin Core + 5 frontends. Story 3.1 includes the Dockerfile + compose; user coordinates infra + execution when Epic 3 implementation lands.
5. **Phase 5 — M3 launch + post-launch monitoring.** Story 4.7 coordinator clearance → 6/12 months post-launch IQ9 anti-success-trigger window opens.

### Session meta-lesson, condensed

> **When an architecture has explicit phase gates (M0→M1, etc.), the corresponding epics should have phase-gate verification stories as first-class artifacts.** These stories are not test plans nor aspirations — they are user-value-bearing deliverables that turn phase transitions into auditable gates. The BMad template does not request them; they emerge from careful reading of the architecture. Recommendation for BMad retrospectives: add to the template the question "does this architecture have phase gates? are there stories materializing each gate?".
