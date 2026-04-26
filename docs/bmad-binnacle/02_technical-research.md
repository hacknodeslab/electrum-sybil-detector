# Bitácora — Technical Research · electrum-sybil-detector

**Fase BMad / BMad Phase:** 1 — Analysis
**Skill:** `bmad-technical-research` (broad survey, academic-background framing)
**Sesión / Session:** 2026-04-23
**Research topic:** Electrum protocol internals and server ecosystem

---

## Idiomas / Languages

- 🇪🇸 [Versión en Español](#-bitácora-en-español) — sigue abajo
- 🇬🇧 [English Version](#-log-in-english) — below the Spanish version

---

## Enlaces rápidos / Quick links

- **Informe principal / Main report:** [`_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md`](../../_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md)
- **Bitácora anterior / Previous log:** [`01_prfaq-challenge.md`](./01_prfaq-challenge.md) — PRFAQ Challenge (Phase 1)
- **Skill origen / Skill source:** [`.claude/skills/bmad-technical-research/`](../../.claude/skills/bmad-technical-research/)

---

<a id="-bitácora-en-español"></a>

## 🇪🇸 Bitácora en Español

> 🌐 [Switch to English Version](#-log-in-english)

### Contexto

Segunda sesión BMad de la Fase 1 (Analysis). La primera (PRFAQ Challenge) forjó la arquitectura estratégica del proyecto; esta sesión construye el **background técnico / related-work** que alimenta (a) la sección de related-work del paper final, (b) la referencia interna mientras se construyen las heurísticas del detector, y (c) material extraíble para Librería de Satoshi. Scope explícitamente amplio ("broad survey"), no deep dive.

Priorización de áreas confirmada por el usuario al arrancar: **(b) server implementations → (a) wire protocol → (c) peer discovery/gossip → (d) transport & deployment → (e) data paths**. Goal ordering: paper-first > internal reference > public explainer.

### Cómo abordamos el trabajo

El skill se ejecuta como un **workflow de 6 steps**, cada uno con su propio file y gate de continuación `[C]`:

#### Step 1 — Scope confirmation

Confirmación del scope explícita y escrita al frontmatter del informe antes de tocar nada empírico. Sin sorpresas.

#### Step 2 — Technology Stack Analysis

**Problema inmediato:** el template genérico del skill pide "microservicios, cloud, SOLID" etc. — irrelevante para un ecosistema que son 5 implementaciones de servidor + 1 cliente de referencia unidas por un JSON-RPC sin BIP formal. **Adapté el template en profundidad** antes de escribir nada, re-estructurando las secciones a lo que el subject realmente tiene (reference-implementation constellation, no framework matrix).

**Intento con subagentes paralelos falló** — los 4 agentes `general-purpose` lanzados para investigar server implementations / wire protocol / storage / clients devolvieron permission-denied en WebSearch+WebFetch+Bash (sandboxing de sub-agentes en este environment). **Pivot a investigación inline desde la main session** — más lenta pero funcional porque la main sí tenía acceso a WebSearch/WebFetch.

**Aporte crítico del usuario mid-Step-2:** señaló los repos canónicos `spesmilo/electrum-protocol/tree/master/docs` y `kyuupichan/electrumx/tree/master/docs`. Reverté el marcado de completado de Step 2 y fetcheé directamente los `.rst` canónicos — eso elevó todo el contenido de Step 2 de "síntesis de búsquedas" a **cita textual de fuentes primarias**. Hallazgos que no habría capturado sin esos repos:
- JSON-RPC 1.0 y 2.0 ambos permitidos ("2.0 encouraged not required") — distinto del snippet que había encontrado antes.
- v1.6 introdujo una regla breaking (`server.version` primer mensaje).
- Full method surface con anotaciones de versión.
- Las mitigaciones Sybil de ElectrumX citables textualmente (subnet dedup, add_peer IP check, source-rate limits).

#### Step 3 — Integration Patterns

Template otra vez genérico (microservicios/API gateway/OAuth). Re-adapté a: interaction model (request/response/sub), session lifecycle, **client-side pool** (~10 concurrent, one-main — hallazgo crítico), gossip dataflow, Bitcoin Core backend integration, DoS/rate-limit patterns, security/privacy.

**Hallazgo más importante de Step 3:** fetcheando los methods del spec canónico, confirmé que `server.peers.subscribe` — **pese al nombre, NO es subscription**, es one-shot request. Y el comportamiento de `server.features.hosts{}` (dict auto-declarado de endpoints del operador) convierte esa llamada en **fuente directa de auto-identificación operator-level** — ese dato es exactamente lo que el detector Push-3 necesita como ground-truth de atribución.

#### Step 4 — Architectural Patterns

Pedí architectural docs de electrs y electrumx, y fetcheé el `schema.md` de electrs que documenta **5 column families, key-only rows, re-parse-on-demand** — eso explica arquitectónicamente por qué electrs no necesita `txindex=1` en bitcoind. Un dato útil tanto para el paper (diferenciador de implementaciones) como operativo (para el honeypot de validación).

También documenté la **estrategia divergente de reorg-handling** (undo-log replay en ElectrumX vs. tip-pointer + reparse en electrs) — durante una reorg natural los servidores divergen observablemente, señal fingerprint-densa e imposible de falsificar sin correr el binario real.

#### Step 5 — Implementation Research

**El step con más aporte empírico del usuario.** Varios hilos convergieron aquí:

1. **Electrohunt (Kacherginsky/Coinbase 2019)** — fetcheé Part 1 y Part 2. Metodología concreta (connectrum + spider.py + electrohunt.py) + números (657 reached, 471 malicious = 71%) + detalle de las campañas (subdomain alias fanout). Prior-art directamente citable para el paper.

2. **Bootstrap list real** — el usuario señaló `electrum/chains/mainnet/servers.json`. Fetché: **130 servers, 9 `.onion` (~7%), operadores branded (Blockstream/Hodlister/Bitaroo/Bitske)**. Dato ground-truth para el paper.

3. **Sesión empírica Shodan (el usuario con ~100 créditos externos)** — le pasé queries priorizadas, ejecutó 8 y me pegó resultados. Hallazgos:
   - `port:50002` devuelve 108 754 resultados pero casi todo ruido (SSH, nginx, webcams). Shodan **no ve el protocolo Electrum** sin hablarlo.
   - `"ElectrumX" port:50002` = 2 (ambos irrelevantes — un Docker Registry mencionando la imagen).
   - `"Fulcrum" port:50002`, `port:4224 "# HELP"`, `port:8332 port:50002` = 0.
   - Lo útil salió accidentalmente: query `electrs` devolvió **~22 HTTP API endpoints de `mempool-electrs`** exponiendo headers `x-powered-by: mempool-electrs 3.x.x` + `x-bitcoin-version: /Satoshi:26.0.0/` → double-fingerprint de fork + Bitcoin Core version.
   - **Infra-leaks colaterales oro:** `34.26.44.149` (Google Cloud) con rsyncd público listando `mainnet-ord / mainnet-esplora / mainnet-bitcoind / signet-esplora`... — operator-stack-confession en un banner. `kofar.paywithspark.net` (Hetzner Helsinki) con Docker Registry abierto listando `bitcoin/electrs/electrumx/zeus/lndg`...
   - **Hallazgo metodológico mayor:** datasets pasivos **no sirven como fuente primaria de descubrimiento** (Shodan-blind al protocolo Electrum); **sí sirven como pivots de atribución** (HTTP API adjacent, Prometheus, rsyncd, Docker Registry, co-residencia de servicios).

4. **1209k analysis** — el usuario preguntó si fiarse. Fetché la página, conté 506 servers mainnet, identifiqué la metodología (solo header-subscription liveness), noté el conflict-of-interest (1209k opera varios de los servidores que monitoriza). Escribí una tabla **"usar para / no usar para"**: sí para seed-enrichment + cross-validation, no como fuente primaria ni ground-truth Sybil.

5. **Stack de implementación recomendado** para el detector: Rust (rust-electrum-client) + rustls + JARM + ASN enrichment + DuckDB/Parquet + honeypots + ética operacional (rate-limit, no tx broadcast, responsible disclosure).

#### Step 6 — Research Synthesis

Executive summary + TOC + narrativa + síntesis temática por seis temas + recomendaciones por audiencia (paper / detector team / Librería de Satoshi) + research frontiers + methodology + limitations + conclusion. También sustituí el placeholder `[Research overview and methodology will be appended here]` en el frontmatter del informe con un overview de 3 párrafos.

### Patrones del workflow que funcionaron

1. **Adaptación agresiva del template genérico** — el template BMad está pensado para software enterprise; aplicarlo literal habría producido un informe inútil para un ecosistema Bitcoin P2P. Reescribí el framing de cada step en la primera frase (> Scope of this section / > Framing) antes de escribir contenido.
2. **Pivot de sub-agents a inline** cuando los 4 agentes paralelos fallaron por sandbox permissions — reconocido rápido, sin insistir en reintentar la misma estrategia.
3. **Reversión de completado** cuando el usuario señaló fuentes primarias (repos canónicos) — el marcado de step-complete no es irreversible; enriquecer después es siempre mejor que congelar una versión inferior.
4. **Escritura textual de quotes** desde los repos canónicos con attribution inline — convierte el informe en citable para el paper sin paráfrasis que dilute la autoridad.
5. **Síntesis de Shodan empírico EN LA MISMA SESIÓN** — al hacerlo in-session (no post-hoc), pude cruzar los null-results con los findings positivos y sacar el hallazgo metodológico mayor (passive blind / active required) que vale más que cualquier query individual.
6. **Tabla "usar para / no usar para"** para fuentes de terceros (1209k) — formato reusable que deja claro el uso correcto sin descartar el valor.
7. **Primary-source repo hunting** — preferir `github.com/<org>/<repo>/blob/master/docs/*.rst` sobre readthedocs renderings (más estables, más citables, a prueba de 403 que ReadTheDocs sí dio).

### Decisiones / aportes del usuario que cambiaron el resultado

- **Priorización b/a/c/d/e** al inicio → permitió asignar peso correcto (server implementations = cabeza del informe, data paths = nota final).
- **"Run inline, don't fan out"** cuando los sub-agentes fallaron → evitó el ciclo de retry-reconfig-retry que habría quemado horas.
- **Señalar `spesmilo/electrum-protocol/docs` y `kyuupichan/electrumx/docs`** → elevó Step 2 de síntesis de búsquedas a cita textual de fuentes primarias.
- **Señalar `electrum/chains/mainnet/servers.json`** → dato ground-truth (130 servers, 9 `.onion`, branding) directamente citable.
- **Ejecutar las queries de Shodan fuera** con ~100 créditos → los null-results y el hallazgo metodológico "Shodan blind to Electrum" son aporte exclusivamente empírico de esta sesión. Sin el usuario no existiría.
- **Preguntar por 1209k antes de asumirlo fiable** → forzó el análisis de metodología + conflict-of-interest que habría quedado implícito si no se pregunta.

### Outputs producidos

| Archivo / File | Contenido / Content |
|---|---|
| [`_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md`](../../_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md) | Informe completo (1132 líneas / ~128 KB): frontmatter + research overview + 6 steps de contenido + research synthesis final con executive summary, TOC, 6 temas transversales, recomendaciones por audiencia, research frontiers, methodology y limitations |
| Esta bitácora / This log | Meta-registro de la sesión en Español + English |

### Próximos pasos (encuadrados en BMad Method)

1. **Phase 1 completa.** El `bmad-technical-research` cierra el análisis background que el PRFAQ Challenge (sesión anterior) dejaba pendiente. Los hallazgos empíricos principales (passive-blind, shared-infra attribution, Hetzner concentration, bootstrap size) están listos para alimentar el PRD.
2. **Fuera de BMad, en paralelo:** seguir con el outreach a b10c (pre-launch 4–6 semanas) — critical path para IQ3 + IQ9 Path 2 del PRFAQ.
3. **Phase 2 — `bmad-create-prd` (CP):** usar como inputs el PRFAQ + distillate + este informe técnico + outcome del outreach a b10c. Las secciones del informe que alimentan más directamente el PRD:
   - Stack de implementación (Step 5 §4) → technical architecture del PRD.
   - Detection heuristics by class (Step 5 §3) → requirements funcionales.
   - Research frontiers (Step 6) → roadmap post-M3.
   - Empirical null-results de Shodan → justifican la decisión de activo-crawl-only.
4. **Validación pendiente fuera del informe** → continuada en [`03_phase1-validations.md`](./03_phase1-validations.md):
   - ~~Fee-histogram determinism~~ **resuelto 2026-04-25** por lectura de código (spesmilo/electrumx). Verdict: fuertemente correlacionado, no bit-idéntico por construcción. Discriminador es Wasserstein, no igualdad. Detalle en bitácora 03.
   - Python asyncio timing resolution adequacy — pendiente (próxima en cola).
   - Real network size desde snowball — pendiente (próxima en cola).
   - Testbed empírico (1 Core + 5 frontends) — abierto como tarea separada para medir magnitud del drift; no decisión binaria.
5. **Si algo se descalifica:** `bmad-correct-course` antes del PRD.

### Lección meta

El workflow de 6 steps funcionó bien como **estructura de avance gradual con gates de confirmación**, pero el template genérico del skill subyacente es un peligro: escrito para arquitecturas enterprise cloud-native, aplicado literal a un ecosistema Bitcoin P2P produce secciones vacías y framings que no matchean el subject. La adaptación del framing por step (reescribir la primera frase de cada sección) fue el único movimiento que hizo el informe publicable.

El aporte del usuario cambió el perfil del trabajo dos veces:
- Señalando fuentes primarias (los repos canónicos y la bootstrap list) → elevó la autoridad citable del informe.
- Ejecutando el probing Shodan externo → el hallazgo metodológico más importante ("passive scanning is blind to the Electrum protocol") es 100% aporte empírico del usuario + síntesis en sesión. Sin el probing real, habría quedado como hipótesis sin datos.

La investigación broad-survey se justificó al final con la síntesis Push-3: el informe demostró con evidencia primaria que las defensas Sybil existentes en ElectrumX son **intra-server** y que el gap explotable se sitúa en la **atribución de infraestructura compartida** — exactamente el reframe que el PRFAQ Challenge había locked estratégicamente. El technical research, en resumen, **validó empíricamente el reframe Push-3 del PRFAQ**.

---

<a id="-log-in-english"></a>

## 🇬🇧 Log in English

> 🌐 [Cambiar a versión en Español](#-bitácora-en-español)

### Context

Second BMad session of Phase 1 (Analysis). The first (PRFAQ Challenge) forged the project's strategic architecture; this session builds the **technical background / related-work** material that feeds (a) the final paper's related-work section, (b) the internal reference used while building detector heuristics, and (c) extractable material for Librería de Satoshi. Scope explicitly **broad survey**, not deep dive.

User confirmed area priorities at start: **(b) server implementations → (a) wire protocol → (c) peer discovery/gossip → (d) transport & deployment → (e) data paths**. Goal ordering: paper-first > internal reference > public explainer.

### How we approached the work

The skill runs as a **6-step workflow**, each step with its own file and continuation `[C]` gate:

#### Step 1 — Scope confirmation

Explicit scope confirmation written to the report frontmatter before any empirical work. No surprises.

#### Step 2 — Technology Stack Analysis

**Immediate problem:** the skill's generic template asks for "microservices, cloud, SOLID" etc. — irrelevant for an ecosystem that is 5 server implementations + 1 reference client glued by a JSON-RPC protocol without a formal BIP. **I adapted the template heavily** before writing any content, restructuring the sections to match what the subject actually is (reference-implementation constellation, not framework matrix).

**Parallel sub-agent attempt failed** — 4 `general-purpose` agents launched for server implementations / wire protocol / storage / clients all returned permission-denied on WebSearch+WebFetch+Bash (sandbox permissions in this environment). **Pivoted to inline research from the main session** — slower but functional because the main session had WebSearch/WebFetch available.

**Critical user contribution mid-Step-2:** pointed at the canonical repos `spesmilo/electrum-protocol/tree/master/docs` and `kyuupichan/electrumx/tree/master/docs`. I reverted Step 2's completion marker and fetched the canonical `.rst` files directly — this lifted all of Step 2 from "search-snippet synthesis" to **primary-source verbatim quoting**. Findings I would not have captured without those repos:
- Both JSON-RPC 1.0 and 2.0 are permitted ("2.0 encouraged not required") — different from what my earlier search snippet showed.
- v1.6 introduced a breaking rule (`server.version` must be first message).
- Full method surface with version annotations.
- ElectrumX's Sybil mitigations quotable verbatim (subnet dedup, add_peer IP check, source-rate limits).

#### Step 3 — Integration Patterns

Template again generic (microservices/API gateway/OAuth). Re-adapted to: interaction model (request/response/sub), session lifecycle, **client-side pool** (~10 concurrent, one-main — critical finding), gossip dataflow, Bitcoin Core backend integration, DoS/rate-limit patterns, security/privacy.

**Most important Step 3 finding:** fetching the canonical spec methods confirmed `server.peers.subscribe` — **despite the name, is NOT a subscription**, just a one-shot request. And `server.features.hosts{}` (a self-declared dict of operator endpoints) turns that call into a **direct operator-level self-identification source** — exactly what the Push-3 detector needs as attribution ground-truth.

#### Step 4 — Architectural Patterns

Pulled architectural docs for electrs and electrumx, and fetched electrs's `schema.md` documenting **5 column families, key-only rows, re-parse-on-demand** — this architecturally explains why electrs doesn't require `txindex=1` on bitcoind. Useful for the paper (implementation discriminator) and operationally (for the validation honeypot).

Also documented the **divergent reorg-handling strategies** (undo-log replay in ElectrumX vs. tip-pointer + reparse in electrs) — during a natural reorg the servers diverge observably, a fingerprint-dense signal impossible to fake without running the actual binary.

#### Step 5 — Implementation Research

**The step with the most user empirical contribution.** Several threads converged here:

1. **Electrohunt (Kacherginsky/Coinbase 2019)** — fetched Part 1 and Part 2. Concrete methodology (connectrum + spider.py + electrohunt.py) + numbers (657 reached, 471 malicious = 71%) + campaign details (subdomain alias fanout). Directly citable prior art for the paper.

2. **Real bootstrap list** — user pointed at `electrum/chains/mainnet/servers.json`. Fetched: **130 servers, 9 `.onion` (~7%), branded operators (Blockstream/Hodlister/Bitaroo/Bitske)**. Ground-truth data for the paper.

3. **Shodan empirical session (user with ~100 external credits)** — I handed over a prioritized query list; user ran 8 and pasted results. Findings:
   - `port:50002` returns 108 754 results but almost all noise (SSH, nginx, webcams). Shodan **doesn't see the Electrum protocol** without speaking it.
   - `"ElectrumX" port:50002` = 2 (both irrelevant — one was a Docker Registry mentioning the image name).
   - `"Fulcrum" port:50002`, `port:4224 "# HELP"`, `port:8332 port:50002` = 0.
   - The useful finding came accidentally: the `electrs` query returned **~22 `mempool-electrs` HTTP API endpoints** exposing headers `x-powered-by: mempool-electrs 3.x.x` + `x-bitcoin-version: /Satoshi:26.0.0/` → double-fingerprint of fork + Bitcoin Core version.
   - **Collateral infra-leaks, gold-standard:** `34.26.44.149` (Google Cloud) with open rsyncd listing `mainnet-ord / mainnet-esplora / mainnet-bitcoind / signet-esplora`... — operator-stack-confession in a single banner. `kofar.paywithspark.net` (Hetzner Helsinki) with open Docker Registry listing `bitcoin/electrs/electrumx/zeus/lndg`...
   - **Major methodological finding:** passive datasets are **NOT a viable primary discovery source** (Shodan-blind to the Electrum protocol); they **ARE useful as attribution pivots** (adjacent HTTP APIs, Prometheus, rsyncd, Docker Registry, service co-residence).

4. **1209k analysis** — user asked whether it was trustworthy. Fetched the page, counted 506 mainnet servers, identified the methodology (header-subscription liveness only), noted the conflict-of-interest (1209k operates several of the servers it monitors). Wrote a **"use for / do not use for" table**: yes for seed-enrichment + cross-validation, no as primary source or Sybil ground-truth.

5. **Recommended implementation stack** for the detector: Rust (rust-electrum-client) + rustls + JARM + ASN enrichment + DuckDB/Parquet + honeypots + operational ethics (rate-limit, no tx broadcast, responsible disclosure).

#### Step 6 — Research Synthesis

Executive summary + TOC + narrative + thematic synthesis across six themes + per-audience recommendations (paper / detector team / Librería de Satoshi) + research frontiers + methodology + limitations + conclusion. Also replaced the placeholder `[Research overview and methodology will be appended here]` in the report's frontmatter with a 3-paragraph overview.

### Workflow patterns that worked

1. **Aggressive generic-template adaptation** — the BMad template is written for enterprise software; applied literally it would have produced a useless report for a Bitcoin P2P ecosystem. Rewrote the framing of each step in its first sentence (> Scope of this section / > Framing) before writing any content.
2. **Sub-agent-to-inline pivot** when the 4 parallel agents failed on sandbox permissions — recognized fast, no insisting on retrying the same failed strategy.
3. **Completion-state reversion** when user pointed at primary sources (canonical repos) — step-complete markers are not irreversible; enriching after is always better than freezing an inferior version.
4. **Verbatim quoting from canonical repos** with inline attribution — makes the report citable for the paper without paraphrase diluting authority.
5. **In-session synthesis of the Shodan empirical data** — by doing it in-session (not post-hoc), I could cross-reference the null-results with the positive findings and extract the major methodological finding (passive blind / active required) that is worth more than any individual query.
6. **"Use for / do not use for" table** for third-party sources (1209k) — reusable format that makes correct use explicit without discarding value.
7. **Primary-source repo hunting** — prefer `github.com/<org>/<repo>/blob/master/docs/*.rst` over readthedocs renderings (more stable, more citable, 403-proof which ReadTheDocs did return).

### User decisions / contributions that changed the outcome

- **b/a/c/d/e prioritization** at the outset → let me weight correctly (server implementations = report's head, data paths = final note).
- **"Run inline, don't fan out"** when the sub-agents failed → avoided the retry-reconfig-retry cycle that would have burned hours.
- **Pointing at `spesmilo/electrum-protocol/docs` and `kyuupichan/electrumx/docs`** → lifted Step 2 from search-snippet synthesis to verbatim quoting of primary sources.
- **Pointing at `electrum/chains/mainnet/servers.json`** → ground-truth data (130 servers, 9 `.onion`, branding) directly citable.
- **Running the Shodan queries externally** with ~100 credits → the null-results and the "Shodan blind to Electrum" methodological finding are 100% empirical contribution from this session. Without the user, they wouldn't exist.
- **Asking about 1209k before assuming it trustworthy** → forced the methodology + conflict-of-interest analysis that would have stayed implicit if not questioned.

### Outputs produced

| Archivo / File | Contenido / Content |
|---|---|
| [`_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md`](../../_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md) | Full report (1132 lines / ~128 KB): frontmatter + research overview + 6 content steps + final research synthesis with executive summary, TOC, 6 transverse themes, per-audience recommendations, research frontiers, methodology, and limitations |
| This log / Esta bitácora | Session meta-record in Spanish + English |

### Next steps (framed within BMad Method)

1. **Phase 1 complete.** `bmad-technical-research` closes the background analysis the PRFAQ Challenge (previous session) left pending. The main empirical findings (passive-blind, shared-infra attribution, Hetzner concentration, bootstrap size) are ready to feed the PRD.
2. **Outside BMad, in parallel:** continue b10c outreach (pre-launch 4–6 weeks) — critical path for IQ3 + IQ9 Path 2 from the PRFAQ.
3. **Phase 2 — `bmad-create-prd` (CP):** use as inputs the PRFAQ + distillate + this technical report + outcome of b10c outreach. Report sections that feed the PRD most directly:
   - Implementation stack (Step 5 §4) → PRD technical architecture.
   - Detection heuristics by class (Step 5 §3) → functional requirements.
   - Research frontiers (Step 6) → post-M3 roadmap.
   - Shodan empirical null-results → justify the decision for active-crawl-only.
4. **Validation pending outside this report** → continued in [`03_phase1-validations.md`](./03_phase1-validations.md):
   - ~~Fee-histogram determinism~~ **resolved 2026-04-25** via code reading (spesmilo/electrumx). Verdict: strongly correlated, not bit-identical by construction. Discriminator is Wasserstein, not equality. Detail in binnacle 03.
   - Python asyncio timing resolution adequacy — pending (next in queue).
   - Real network size from snowball — pending (next in queue).
   - Empirical testbed (1 Core + 5 frontends) — opened as a separate task to measure drift magnitude; not a binary decision.
5. **If something gets disconfirmed:** `bmad-correct-course` before the PRD.

### Meta lesson

The 6-step workflow worked well as a **gradual-advance structure with confirmation gates**, but the underlying skill's generic template is a hazard: written for enterprise cloud-native architectures, applied literally to a Bitcoin P2P ecosystem it produces empty sections and framings that don't match the subject. Per-step framing adaptation (rewriting each section's first sentence) was the single move that made the report publishable.

The user's contribution shifted the work's profile twice:
- Pointing at primary sources (canonical repos and the bootstrap list) → raised the report's citable authority.
- Running the external Shodan probing → the most important methodological finding ("passive scanning is blind to the Electrum protocol") is 100% empirical user contribution + in-session synthesis. Without real probing, it would have stayed as hypothesis without data.

The broad-survey research justified itself at the end with the Push-3 synthesis: the report demonstrated with primary evidence that existing Sybil defenses in ElectrumX are **intra-server** and that the exploitable gap lies in **shared-infrastructure attribution** — exactly the reframe the PRFAQ Challenge had locked strategically. In summary, the technical research **empirically validated the PRFAQ's Push-3 reframe**.
