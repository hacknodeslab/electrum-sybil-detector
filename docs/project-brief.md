# Project Brief — electrum-sybil-detector

**Tipo / Format:** 2-pager (Amazon-style strategic narrative memo) · **Audiencia / Audience:** grant reviewers + Bitcoin-research peers
**Fecha / Date:** 2026-04-23 · **Autor / Author:** Ifuensan (HackNodes Lab · Librería de Satoshi)

---

## Idiomas / Languages

- 🇪🇸 [Versión en Español](#-versión-en-español) — sigue abajo
- 🇬🇧 [English Version](#-english-version) — below the Spanish version

## Enlaces / Links

- [PRFAQ completo / full PRFAQ](../_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md) · [PRFAQ distillate](../_bmad-output/planning-artifacts/prfaq-electrum-sybil-detector-distillate.md)
- [Technical research report](../_bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md)
- [Bitácora PRFAQ / PRFAQ log](./bmad-binnacle/01_prfaq-challenge.md) · [Bitácora Technical Research / TR log](./bmad-binnacle/02_technical-research.md)

---

<a id="-versión-en-español"></a>

## 🇪🇸 Versión en Español

> 🌐 [Switch to English](#-english-version)

### Apertura

Los usuarios de Bitcoin que custodian sus propias llaves sin correr un nodo completo dependen de servidores Electrum ajenos para recibir su vista de la cadena y transmitir sus transacciones. Un ataque Sybil documentado en 2019 demostró que **~71% de la red pública** podía estar controlada por un solo actor. Las defensas posteriores cerraron el vector ingenuo, pero operan **a nivel de servidor individual**: no alcanzan al atacante que despliega una flota bien configurada sobre infraestructura compartida. Ese hueco existe hoy — y es medible. Este proyecto construye la herramienta, el dataset y el paper que lo miden.

### Problema y audiencia

**Problema observable.** La red pública Electrum (~500 servidores en 2026 según el monitor 1209k, frente a 130 en el bootstrap oficial, con un delta Tor no cuantificado) carece de un censo público desde el estudio Electrohunt de 2019. No hay trabajo publicado que cuantifique cuánta de esa infraestructura está realmente bajo operadores independientes. El issue [#11 del repo de ideas de b10c](https://github.com/0xB10C/projectideas/issues/11) (*"Can we spot public spy-Electrum servers run by Chainalysis?"*, abierto julio 2025, sigue `Todo`) documenta la pregunta con **9 meses de dwell time** sin ejecución. El precedente — materiales filtrados de Chainalysis publicados por CoinDesk en 2021 que incluyeron walletexplorer.com como honeypot SPV no declarado — confirma que no es especulación.

**Audiencia.** Comités de grant en el ecosistema Bitcoin (OpenSats, HRF, Btrust, B4OS, BOSS Challenge, Brink); la comunidad de Bitcoin privacy research (órbita b10c / peer-observer, Grundmann / TU Darmstadt, lineage Biryukov / Meiklejohn / Bonneau en Financial Cryptography); operadores y mantenedores del ecosistema Electrum (spesmilo, kyuupichan, kits tipo Umbrel/Start9/RaspiBlitz).

### Enfoque (scope reframe crítico)

**Qué medimos:** clusters de **infraestructura backend compartida** — múltiples "servidores" Electrum servidos por un único Bitcoin Core. Esto es derivable de señales de fingerprint observables externamente. **Qué NO originamos:** atribución de intención (¿vigilancia?, ¿reducción de costes operativos?) — es una capa interpretativa separada que se cita desde terceros publicados, nunca desde nuestro paper. Esta separación es a la vez analíticamente honesta y legalmente defendible.

**Espina metodológica.** La discriminante primaria es **timing de notificación en fork-races**: cuando Bitcoin produce un stale-block (3–8/mes según `bitcoin-data/stale-blocks`), servidores con el mismo backend ven el cambio simultáneamente; servidores con backends independientes se dispersan según la latencia de propagación P2P. Cada evento es un experimento natural binario irreducible a similitud de software. La métrica es la **varianza del delta pairwise a lo largo de muchos eventos** — vantage-robusta: la asimetría del path del colector es constante y cae. Señales backend-state adicionales: correlación de fee-histogram (`mempool.get_fee_histogram`) y downtime sincronizado. Señales frontend-config (banner, versión, ASN, donation address) son **confirmatorias, no suficientes**. Umbral multi-signal: **≥2 backend-state + ≥1 frontend-config** para cada cluster publicado.

**Lo que NO haremos:** reinventar descubrimiento (reutilizamos `fork-observer` de b10c que ya soporta Electrum); proponer frameworks generales; hacer deep-learning sobre señales cuando la física del problema ya es discriminativa.

### Criterios de éxito y entregables

**Deliverable ordering (locked):** open-source tool → longitudinal dataset → empirical paper. Tres escenarios de outcome, todos publicables bajo el framing actual:

| Escenario | Hallazgo | Publicable |
|---|---|---|
| 1 | Clusters claros de backend compartido | Paper de hallazgos |
| 2 | Señales débiles + upper bound + metodología validada | Paper de metodología (*default asumido para M3*) |
| 3 | True null + upper bound | Paper de metodología como reference |

**Timeline:** M0 (actual, ~20 servidores, laptop scale) → M1 (snowball discovery) → M2 (cobertura Tor + TimescaleDB) → **M3 = launch milestone conjunto** (tool + dataset + paper) → M3+X (follow-up con multi-vantage, Phase 2 research program).

**Coste:** sub-$500/año (VPS + storage + redundancia). Volumen dataset: ~6 GB/año comprimido a escala de red completa.

**Compromisos de ciencia abierta (locked pre-launch):**
- Código MIT · dataset CC BY 4.0 · paper arXiv preprint + venue peer-reviewed.
- **Archival de tres niveles:** `bitcoin-data` GitHub de b10c (depósito principal) + Zenodo DOI (archivo institucional independiente) + arXiv (timestamp).
- Documentación y README bilingües EN+ES alineados con la misión de Librería de Satoshi.
- PR review SLA: ack 48h / review sustantivo 7d / tagging público `review-queued` en picos.
- Venue primario FC (Financial Cryptography); backup PETS; terciario IMC.

### Contribución novedosa y gap de related work

La literatura existente cubre el descubrimiento y medición de nodos del P2P de Bitcoin (CoinScope, TxProbe, Grundmann et al., Node-Probe, bitnodes) pero **no hay equivalente publicado para la red Electrum** desde 2019. Electrohunt (Kacherginsky/Coinbase 2019) cubrió la detección de phishing por `server.banner`, metodología hoy obsoleta frente al threat model actual (atacantes sin payload visible). ElectrumX endureció sus defensas intra-servidor tras 2019 (subnet-dedup en `server.peers.subscribe`, validación IP en `add_peer`, rate-limits de fuente) — pero esas defensas **no alcanzan a una flota distribuida sobre infraestructura compartida**. La contribución de este trabajo es **atribución a nivel de substrato compartido**, no a nivel de identidad auto-declarada.

### Riesgos y preguntas abiertas

- **Capacidad solo-researcher** es el single point of failure arquitectónico. Mitigación: plan pre-comprometido de "collaborator call" a los 6 meses post-paper + identificación de candidato Path 2 (handoff a b10c u otro grupo de medición universitario).
- **Relación con b10c** es SPOF para dos cuestiones load-bearing (diferenciación + exit path). Mitigación: outreach pre-launch 4–6 semanas, no 48h.
- **Fee-histogram: fuertemente correlacionado, no bit-idéntico** — launch-blocker #2 resuelto por lectura de código (spesmilo/electrumx, `src/electrumx/server/mempool.py`, 2026-04-25). El algoritmo es determinista dado un mempool snapshot idéntico, pero dos instancias contra el mismo Core divergen por construcción: refresh phase offset (cache de 120s sin sincronización inter-instancia), drift del mempool mirror local, y bucketing adaptativo (`bin_size *= 1.1`) que amplifica micro-diferencias. **Implicación:** el discriminador no puede ser igualdad — es **distancia Wasserstein** (ya en roadmap M3). El testbed empírico pendiente mide la **magnitud** del drift bajo distintos regímenes (same-impl vs cross-impl: ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs contra un Core) para fijar el threshold de cluster.
- **Tamaño real de red** — bootstrap=130, 1209k=506, true size > (Tor no cuantificado). Snowball desde M1 lo resolverá.
- **Datasets pasivos (Shodan/Censys) son ciegos al protocolo Electrum** — hallazgo empírico confirmado en la sesión de technical research 2026-04-23. El crawler debe ser activo; Shodan/CT/ASN son pivots de atribución downstream, no fuente primaria.

### Ask / próximo paso

- **Grant reviewers:** evaluar el proyecto bajo el escenario 2 como baseline esperado (no bajo escenario 1). La contribución principal es la metodología reproducible con umbrales pre-comprometidos y archival durable, no un titular de hallazgos. Two-papers plan explícito (M3 methodology + M3+X follow-up) convierte "shipear débil o retrasar" en programa de investigación fondeable.
- **Peer researchers:** la reproducción desde un ASN distinto es arquitectónicamente **una segunda vantage** que fortalece el lower bound sin posibilidad de debilitarlo. Invitación a reproducir desde el día uno.
- **Decisión inmediata pendiente:** completar los 25 launch-blockers (lista completa en el PRFAQ) antes del release público. Priorizado: (1) outreach a b10c, (2) verificación empírica de fee-histogram, (3) completar PRD con el skill `bmad-create-prd`.

---

<a id="-english-version"></a>

## 🇬🇧 English Version

> 🌐 [Cambiar a Español](#-versión-en-español)

### Opening

Bitcoin users who hold their own keys without running a full node depend on third-party Electrum servers for their view of the chain and to broadcast their transactions. A documented 2019 Sybil attack reached **~71% control** of the public mesh by a single actor. Subsequent hardening closed the naïve vector but operates **at the individual-server level**: it does not reach the attacker deploying a well-configured fleet over shared infrastructure. That gap is open today — and it is measurable. This project builds the tool, dataset, and paper that measure it.

### Problem and audience

**Observable problem.** The public Electrum network (~500 servers per the 1209k monitor in 2026, vs. 130 in the official bootstrap, with an unquantified Tor delta) has had no published census since the 2019 Electrohunt study. No published work quantifies how much of that infrastructure is actually run by independent operators. [Issue #11 of b10c's ideas repository](https://github.com/0xB10C/projectideas/issues/11) (*"Can we spot public spy-Electrum servers run by Chainalysis?"*, opened July 2025, still `Todo`) documents the question with **9 months of dwell time** without execution. The precedent — leaked Chainalysis materials published by CoinDesk in 2021 including walletexplorer.com as an undisclosed SPV honeypot — confirms this is not speculation.

**Audience.** Grant committees in the Bitcoin ecosystem (OpenSats, HRF, Btrust, B4OS, BOSS Challenge, Brink); the Bitcoin privacy research community (b10c / peer-observer orbit, Grundmann / TU Darmstadt, Biryukov / Meiklejohn / Bonneau lineage at Financial Cryptography); operators and maintainers of the Electrum ecosystem (spesmilo, kyuupichan, Umbrel/Start9/RaspiBlitz kit maintainers).

### Approach (critical scope reframe)

**What we measure:** clusters of **shared backend infrastructure** — multiple Electrum "servers" served by a single Bitcoin Core. This is derivable from externally-observable fingerprint signals. **What we do NOT originate:** intent attribution (surveillance? cost-sharing?) — a separate interpretive layer we cite from published third parties, never originate in our paper. This separation is both analytically honest and legally defensible.

**Methodological spine.** The primary discriminator is **block-notification timing in fork races**: when Bitcoin produces a stale-block event (3–8/month per `bitcoin-data/stale-blocks`), servers with the same backend see the tip change simultaneously; independent-backend servers scatter by Bitcoin P2P propagation latency. Each event is a binary natural experiment irreducible to software-similarity null. The metric is the **variance of pairwise delta across many events** — vantage-robust: collector path asymmetry is constant and drops out. Additional backend-state signals: fee-histogram correlation (`mempool.get_fee_histogram`) and synchronized downtime. Frontend-config signals (banner, version, ASN, donation address) are **confirming, not sufficient**. Multi-signal threshold: **≥2 backend-state + ≥1 frontend-config** for each published cluster.

**What we will NOT do:** reinvent discovery (we reuse b10c's `fork-observer`, which already supports Electrum); propose general frameworks; apply deep-learning to signals when the problem's physics is already discriminative.

### Success criteria and deliverables

**Deliverable ordering (locked):** open-source tool → longitudinal dataset → empirical paper. Three outcome scenarios, all publishable under the current framing:

| Scenario | Finding | Publishable |
|---|---|---|
| 1 | Clear shared-backend clusters | Findings paper |
| 2 | Weak signals + upper bound + validated methodology | Methodology paper (*assumed default for M3*) |
| 3 | True null + upper bound | Methodology paper as reference |

**Timeline:** M0 (current, ~20 servers, laptop scale) → M1 (snowball discovery) → M2 (Tor coverage + TimescaleDB) → **M3 = joint launch milestone** (tool + dataset + paper) → M3+X (multi-vantage follow-up, Phase 2 research program).

**Cost:** sub-$500/year (VPS + storage + redundancy). Dataset volume: ~6 GB/year compressed at full-network scale.

**Open-science commitments (locked pre-launch):**
- Code MIT · dataset CC BY 4.0 · paper arXiv preprint + peer-reviewed venue.
- **Three-tier archival:** `bitcoin-data` GitHub (b10c's repo, primary deposit) + Zenodo DOI (institutional archival independent of any GitHub account) + arXiv (timestamp).
- Bilingual EN+ES README and documentation aligned with Librería de Satoshi's mission.
- PR review SLA: 48h acknowledgment / 7d substantive review / public `review-queued` tagging during peaks.
- Primary venue FC (Financial Cryptography); backup PETS; tertiary IMC.

### Novel contribution and related-work gap

Existing literature covers discovery and measurement of the Bitcoin P2P network (CoinScope, TxProbe, Grundmann et al., Node-Probe, bitnodes) but **there is no published equivalent for the Electrum network** since 2019. Electrohunt (Kacherginsky/Coinbase 2019) addressed phishing detection via `server.banner`, a methodology now obsolete against the current threat model (attackers without a visible payload). ElectrumX hardened its intra-server defenses post-2019 (subnet-dedup in `server.peers.subscribe`, IP validation in `add_peer`, source rate-limits) — but those defenses **do not reach a fleet distributed over shared infrastructure**. This work's contribution is **attribution at the shared-substrate level**, not at the self-advertised identity level.

### Risks and open questions

- **Solo-researcher capacity** is the architectural single point of failure. Mitigation: pre-committed 6-month post-paper "collaborator call" plan + pre-identified Path 2 candidate (handoff to b10c or another academic measurement group).
- **Relationship with b10c** is a SPOF for two load-bearing questions (differentiation + exit path). Mitigation: pre-launch outreach 4–6 weeks, not 48h.
- **Fee-histogram: strongly correlated, not bit-identical** — launch-blocker #2 resolved by code reading (spesmilo/electrumx, `src/electrumx/server/mempool.py`, 2026-04-25). The algorithm is deterministic given an identical mempool snapshot, but two instances against the same Core diverge by construction: refresh phase offset (120s cache with no inter-instance synchronization), local mempool-mirror drift, and adaptive bucketing (`bin_size *= 1.1`) amplifying micro-differences. **Implication:** the discriminator cannot be equality — it must be **Wasserstein distance** (already in M3 roadmap). The pending empirical testbed measures the **magnitude** of the drift across regimes (same-impl vs cross-impl: ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs against one Core) to fix the cluster threshold.
- **Real network size** — bootstrap=130, 1209k=506, true size > (Tor unquantified). M1 snowball resolves this.
- **Passive datasets (Shodan/Censys) are blind to the Electrum protocol** — empirical finding confirmed in the 2026-04-23 technical research session. The crawler must be active; Shodan/CT/ASN are downstream attribution pivots, not primary sources.

### Ask / next step

- **Grant reviewers:** please evaluate under scenario 2 as the expected baseline (not scenario 1). The primary contribution is reproducible methodology with pre-committed thresholds and durable archival, not a findings headline. An explicit two-papers plan (M3 methodology + M3+X follow-up) converts the "ship weak or delay" tension into a fundable research program.
- **Peer researchers:** reproducing from a different ASN is architecturally a **second vantage point** that strengthens the lower bound without being able to weaken it. Invitation to reproduce from day one.
- **Immediate pending decision:** complete the 25 launch-blockers (full list in the PRFAQ) before public release. Priority order: (1) b10c outreach, (2) empirical fee-histogram verification, (3) complete the PRD via the `bmad-create-prd` skill.
