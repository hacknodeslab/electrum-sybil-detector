# Bitácora — PRFAQ Challenge · electrum-sybil-detector

**Fase BMad / BMad Phase:** 1 — Analysis
**Skill:** `bmad-prfaq` (Working Backwards stress-test)
**Sesión / Session:** 2026-04-22 → 2026-04-23

---

## Idiomas / Languages

- 🇪🇸 [Versión en Español](#-bitácora-en-español) — sigue abajo
- 🇬🇧 [English Version](#-log-in-english) — below the Spanish version

---

<a id="-bitácora-en-español"></a>

## 🇪🇸 Bitácora en Español

> 🌐 [Switch to English Version](#-log-in-english)

### Contexto

PRFAQ Challenge ejecutado para el proyecto `electrum-sybil-detector` — Working Backwards stress-test. Buen fit dado que el problema es research-driven. Punto de partida: un `README.md` técnico ya redactado con problem statement + arquitectura. Resultado: PRFAQ completo + distillate + 25 launch-blocker items + dos memorias de proyecto persistentes.

### Cómo abordamos el trabajo

El skill se ejecutó como un **gauntlet de 5 stages**, cada uno con un papel distinto del coach (de aliado a adversario):

#### Stage 1 — Ignition (concepto crudo + contextual gathering)

- Punto de partida: `README.md` técnico ya redactado (problem statement + arquitectura).
- **Tres "pushes" del coach** que el usuario tuvo que defender:
  1. ¿Cuál es el deliverable primario? → Decidido: **tool → dataset → paper**.
  2. ¿Customer ≠ Reader? → Customer = HackNodes Lab; Reader = Bitcoin security research community.
  3. ¿Qué pasa con un null result? → Tres escenarios: clusters claros / señales débiles / null verdadero.
- **Reframe crítico ("Push 3"):** detectar **shared infrastructure** es lo medible; **atribución de intent** (vigilancia vs. cost-sharing) es una capa interpretativa separada. Este reframe protege legalmente Y eleva el suelo de outcomes publicables.
- **Subagentes en paralelo:** artifact-analyzer (escaneó `docs/papers/*_insights.md` + README) + web-researcher (sintetizó landscape; WebSearch denegado, marcado como caveat).
- **Output:** documento de trabajo creado en `_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md` con coaching notes Stage 1.

#### Stage 2 — Press Release (forja iterativa)

Construido sección por sección, ofreciendo 2–3 borradores con auto-crítica para que el usuario eligiera o mezclara:

- **Headline:** mezcla de B+C — question-hook + tool-anchor + tool→dataset→findings stack.
- **Subheadline:** clausura crítica *"shared-infrastructure detection as measurable, surveillance attribution as a separate interpretive layer."*
- **Opening paragraph:** mezcla 2+3, recortado a 60 palabras exactas.
- **Problem paragraph:** mezcla 2+3, ~130 palabras. Wasabi/Samourai forensics nombrados como evidencia circunstancial.
- **Solution paragraph:** ~100 palabras, cierre *"a measured quantity the community can argue about on evidence."*
- **Leader quote:** L1+L2 merge — voz auténtica de "small lab" + hedge "dramatic or mundane."
- **Community quote:** C1 en tercera persona con "vantage points."
- **How It Works** y **Getting Started** drafted juntos.
- **Decisión de licenciamiento del usuario:** MIT para código + CC BY 4.0 para dataset. Razón: *"La herramienta no es tu moat, los hallazgos sí."*

#### Stage 3 — Customer FAQ (devil's advocate del lector)

10 preguntas duras del peer reviewer / grant reviewer:
- Las 5 fácticas (Q5–Q10) drafted como first-pass.
- Las 5 load-bearing (Q1, Q2, Q3, Q4, Q8) trabajadas una por una.
- **Aporte fuerte del usuario en Q1:** convirtió la answer genérica en una con **provenance citable** (b10c issue #11 desde julio 2025, todavía `Todo`) + **precedente documentado** (CoinDesk 2021 sobre Chainalysis + walletexplorer.com).
- **Aporte fuerte en Q4:** estrategia de **archival de tres niveles** (`bitcoin-data` GitHub + Zenodo DOI + arXiv). Tres hosts independientes, cada uno con failure mode distinto.
- **Aporte fuerte en Q8:** distinción legal *"cite published attributions, never originate them"* + regla de estilo *"AS24940 es un hecho de red; Hetzner's customer X es una atribución."*
- Migrada al Internal FAQ: la pregunta de diferenciación frente a b10c.

#### Stage 4 — Internal FAQ (stakeholder escéptico interno)

9 preguntas que deberían quitar el sueño al fundador. Trabajadas en orden estratégico para que cada respuesta heredara las anteriores:

- IQ9 (exit path) → IQ6 (qué mata el proyecto) → IQ7 (evasión adversaria) → IQ3 (diferenciación b10c) → IQ4 (tool-first vs. finding-first) → IQ2 (null result) → IQ1 (problema técnico más duro) → IQ5 (bandwidth solo) → IQ8 (venue strategy).
- **Decisiones estratégicas locked:**
  - **Ship en escenario 2** en M3, no esperar a escenario 1.
  - **FC primary venue, no PETS** (corrección del usuario: lineage Biryukov/Meiklejohn/Bonneau + audience overlap con grant funders).
  - **Reescritura de I2P** (clarificación: persistent destination identifiers vs. "reveal IP").
  - **PR review SLA:** 48h ack / 7d substantive review / public "review-queued" tagging.
  - **Path 2 handoff a b10c** pre-socializado pre-launch.
  - **Two-papers plan:** M3 methodology + M3+X follow-up.

#### Stage 5 — Verdict + Distillate

- Veredicto: **needs more heat, leaning toward forged** — concepto sustantivamente fuerte e internamente coherente; 25 launch-blocker items por ejecutar antes de release; un riesgo existencial (capacidad solo) sin mitigación arquitectónica.
- **Tres categorías:** 9 forged / 7 needs heat / 4 cracks.
- **Distillate generado** en `prfaq-electrum-sybil-detector-distillate.md` para alimentar el PRD downstream.

### Patrones del coaching que funcionaron

1. **Borradores múltiples + auto-crítica + invitación a elegir** → mantuvo control del usuario sin parálisis de "página en blanco."
2. **Push 3 reframe captado en Stage 1** → load-bearing en TODAS las respuestas posteriores (legal, methodological, scenario-handling).
3. **Pre-committed thresholds** (IQ5 + IQ9) → convirtió "lo decidiré entonces" en compromisos estructurales que sobreviven al estrés.
4. **Coaching notes por stage** dentro del propio documento → sobreviven a context compaction y alimentan el distillate.
5. **Subagentes en paralelo en Stage 1** → contexto externo sin saturar el main context window.
6. **Memory updates concurrentes** (HackNodes Lab + Librería de Satoshi alignment, Electrum sybil positioning) → conocimiento del proyecto persiste para futuras sesiones.

### Decisiones del usuario que cambiaron el resultado

- **Licenciamiento MIT + CC BY 4.0** con razonamiento explícito del moat.
- **Tres-niveles de archival** con `bitcoin-data` como depósito principal (cierra el loop con b10c).
- **FC ↔ PETS flip** en venue strategy (basado en conocimiento real del editorial mix 2023–2025).
- **Empirical grounding del flaky-server claim** con datos de 1209k.com.
- **Respuesta de Q1 Customer FAQ** que convirtió "infrastructure endurance" abstract en provenance citable + documented threat.
- **PR review SLA específico** + excepción para data-integrity PRs.
- **I2P como nota de M4 con observación original** sobre persistent destinations.

### Outputs producidos

| Archivo | Contenido |
|---|---|
| `_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md` | PRFAQ completo: press release + Customer FAQ (10 Qs) + Internal FAQ (9 Qs) + Verdict + 4 bloques de coaching notes |
| `_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector-distillate.md` | Distillate denso para alimentar PRD downstream |
| `~/.claude/projects/.../memory/MEMORY.md` + 2 entries | Project memory persistente: HackNodes Lab + Librería de Satoshi alignment, Electrum sybil positioning |

### Próximos pasos (encuadrados en BMad Method)

1. **Phase 1 remanente:** `bmad-technical-research` (TR) — scope acotado a validar las load-bearing technical assumptions del PRFAQ:
   - Fee-histogram determinism (highest priority — load-bearing para Q2 methodology)
   - Python asyncio timing resolution adequacy
   - 1209k.com historical uptime
   - Network size real desde snowball
2. **En paralelo, fuera de BMad:** outreach a b10c — 4–6 semanas pre-launch, no 48h. Critical path para IQ3 + IQ9 Path 2.
3. **Phase 2:** `bmad-create-prd` (CP) usando PRFAQ + distillate + TR report + outcome de b10c como inputs.
4. **Si algo se descalifica:** `bmad-correct-course` (CC) antes del PRD.

### Lección meta

El gauntlet funcionó porque cada stage cambió el papel del coach (aliado en Stage 1, escultor en Stage 2, fiscal en Stage 3, junta directiva en Stage 4, juez en Stage 5). Los push-backs y los aportes del usuario se reforzaron mutuamente: el coach forzó claridad estructural, el usuario aportó conocimiento de dominio. El documento resultante no es una promesa — es un programa de investigación con defensas arquitectónicas y compromisos pre-decisionados frente a la mayoría de los modos de fallo realistas.

---

<a id="-log-in-english"></a>

## 🇬🇧 Log in English

> 🌐 [Cambiar a versión en Español](#-bitácora-en-español)

### Context

PRFAQ Challenge run for the `electrum-sybil-detector` project — Working Backwards stress-test. Good fit since the problem is research-driven. Starting point: a technical `README.md` already drafted with problem statement + architecture. Result: complete PRFAQ + distillate + 25 launch-blocker items + two persistent project memories.

### How we approached the work

The skill ran as a **5-stage gauntlet**, each stage with the coach playing a different role (from ally to adversary):

#### Stage 1 — Ignition (raw concept + contextual gathering)

- Starting point: technical `README.md` already drafted (problem statement + architecture).
- **Three coach "pushes"** the user had to defend:
  1. What is the primary deliverable? → Decided: **tool → dataset → paper**.
  2. Customer ≠ Reader? → Customer = HackNodes Lab; Reader = Bitcoin security research community.
  3. What if the result is null? → Three scenarios: clear clusters / weak signals / true null.
- **Critical reframe ("Push 3"):** detecting **shared infrastructure** is what is measurable; **intent attribution** (surveillance vs. cost-sharing) is a separate interpretive layer. This reframe is BOTH legally protective AND raises the floor of publishable outcomes.
- **Parallel subagents:** artifact-analyzer (scanned `docs/papers/*_insights.md` + README) + web-researcher (synthesized landscape; WebSearch denied, flagged as caveat).
- **Output:** working document created at `_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md` with Stage 1 coaching notes.

#### Stage 2 — Press Release (iterative forging)

Built section by section, offering 2–3 drafts with self-critique so the user could pick or merge:

- **Headline:** B+C merge — question-hook + tool-anchor + tool→dataset→findings stack.
- **Subheadline:** critical closer *"shared-infrastructure detection as measurable, surveillance attribution as a separate interpretive layer."*
- **Opening paragraph:** 2+3 merge, trimmed to exactly 60 words.
- **Problem paragraph:** 2+3 merge, ~130 words. Wasabi/Samourai forensics named as circumstantial evidence.
- **Solution paragraph:** ~100 words, closes with *"a measured quantity the community can argue about on evidence."*
- **Leader quote:** L1+L2 merge — authentic "small lab" voice + "dramatic or mundane" hedge.
- **Community quote:** C1 in third person with "vantage points."
- **How It Works** and **Getting Started** drafted together.
- **User's licensing decision:** MIT for code + CC BY 4.0 for dataset. Reason: *"The tool is not your moat, the findings are."*

#### Stage 3 — Customer FAQ (reader's devil's advocate)

10 hard peer-reviewer / grant-reviewer questions:
- The 5 factual ones (Q5–Q10) drafted as first-pass.
- The 5 load-bearing ones (Q1, Q2, Q3, Q4, Q8) worked through one at a time.
- **Strong user contribution on Q1:** turned the generic answer into one with **citable provenance** (b10c issue #11 since July 2025, still `Todo`) + **documented precedent** (CoinDesk 2021 on Chainalysis + walletexplorer.com).
- **Strong contribution on Q4:** **three-tier archival strategy** (`bitcoin-data` GitHub + Zenodo DOI + arXiv). Three independent hosts, each with a different failure mode.
- **Strong contribution on Q8:** legal distinction *"cite published attributions, never originate them"* + style rule *"AS24940 is a network fact; Hetzner's customer X is an attribution."*
- Migrated to Internal FAQ: the b10c differentiation question.

#### Stage 4 — Internal FAQ (skeptical internal stakeholder)

9 questions that should keep the founder up at night. Worked in strategic order so each answer inherited the prior ones:

- IQ9 (exit path) → IQ6 (what kills the project) → IQ7 (adversarial evasion) → IQ3 (b10c differentiation) → IQ4 (tool-first vs. finding-first) → IQ2 (null result) → IQ1 (hardest technical problem) → IQ5 (solo bandwidth) → IQ8 (venue strategy).
- **Strategic decisions locked:**
  - **Ship on scenario 2** at M3 — do not wait for scenario 1.
  - **FC primary venue, not PETS** (user correction: Biryukov/Meiklejohn/Bonneau lineage + audience overlap with grant funders).
  - **I2P rewrite** (clarification: persistent destination identifiers vs. "reveal IP").
  - **PR review SLA:** 48h ack / 7d substantive review / public "review-queued" tagging.
  - **Path 2 handoff to b10c** pre-socialized pre-launch.
  - **Two-papers plan:** M3 methodology + M3+X follow-up.

#### Stage 5 — Verdict + Distillate

- Verdict: **needs more heat, leaning toward forged** — concept substantively strong and internally coherent; 25 launch-blocker items to execute before release; one existential risk (solo capacity) without architectural mitigation.
- **Three categories:** 9 forged / 7 needs heat / 4 cracks.
- **Distillate generated** at `prfaq-electrum-sybil-detector-distillate.md` to feed downstream PRD.

### Coaching patterns that worked

1. **Multiple drafts + self-critique + invitation to choose** → kept user in control without "blank page" paralysis.
2. **Push 3 reframe captured in Stage 1** → load-bearing across ALL subsequent answers (legal, methodological, scenario-handling).
3. **Pre-committed thresholds** (IQ5 + IQ9) → converted "I'll decide then" into structural commitments that survive stress.
4. **Per-stage coaching notes** inside the document itself → survive context compaction and feed the distillate.
5. **Parallel subagents in Stage 1** → external context without saturating the main context window.
6. **Concurrent memory updates** (HackNodes Lab + Librería de Satoshi alignment, Electrum sybil positioning) → project knowledge persists across future sessions.

### User decisions that changed the outcome

- **MIT + CC BY 4.0 licensing** with explicit moat rationale.
- **Three-tier archival** with `bitcoin-data` as primary deposit (closes the loop with b10c).
- **FC ↔ PETS flip** in venue strategy (based on real knowledge of the 2023–2025 editorial mix).
- **Empirical grounding of the flaky-server claim** with 1209k.com data.
- **Q1 Customer FAQ answer** that converted abstract "infrastructure endurance" into citable provenance + documented threat.
- **Specific PR review SLA** + data-integrity PR exception.
- **I2P as M4 note with original observation** about persistent destinations.

### Outputs produced

| File | Content |
|---|---|
| `_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md` | Complete PRFAQ: press release + Customer FAQ (10 Qs) + Internal FAQ (9 Qs) + Verdict + 4 coaching-notes blocks |
| `_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector-distillate.md` | Dense distillate to feed downstream PRD |
| `~/.claude/projects/.../memory/MEMORY.md` + 2 entries | Persistent project memory: HackNodes Lab + Librería de Satoshi alignment, Electrum sybil positioning |

### Next steps (framed within BMad Method)

1. **Phase 1 remaining:** `bmad-technical-research` (TR) — scope narrowed to validate the PRFAQ's load-bearing technical assumptions:
   - Fee-histogram determinism (highest priority — load-bearing for Q2 methodology)
   - Python asyncio timing resolution adequacy
   - 1209k.com historical uptime
   - Real network size from snowball discovery
2. **In parallel, outside BMad:** b10c outreach — 4–6 weeks pre-launch, not 48h. Critical path for IQ3 + IQ9 Path 2.
3. **Phase 2:** `bmad-create-prd` (CP) using PRFAQ + distillate + TR report + b10c outcome as inputs.
4. **If something gets disconfirmed:** `bmad-correct-course` (CC) before PRD.

### Meta lesson

The gauntlet worked because each stage shifted the coach's role (ally in Stage 1, sculptor in Stage 2, prosecutor in Stage 3, board of directors in Stage 4, judge in Stage 5). The coach's push-backs and the user's contributions reinforced each other: the coach forced structural clarity, the user contributed domain knowledge. The resulting document is not a promise — it is a research program with architectural defenses and pre-committed decisions against most realistic failure modes.
