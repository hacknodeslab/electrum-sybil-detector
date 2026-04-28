# Project Brief — electrum-sybil-detector

**Tipo / Format:** 2-pager (Amazon-style strategic narrative memo) · **Audiencia / Audience:** grant reviewers + Bitcoin-research peers
**Fecha / Date:** 2026-04-23 · **Autor / Author:** Ifuensan (HackNodes Lab · Librería de Satoshi)

---

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
- **Determinismo de fee-histogram** — launch-blocker #2. Verificación empírica pendiente: correr dos frontends ElectrumX contra un Core, comparar output. Si no es bit-idéntico, se suaviza el lenguaje a "fuertemente correlacionado".
- **Tamaño real de red** — bootstrap=130, 1209k=506, true size > (Tor no cuantificado). Snowball desde M1 lo resolverá.
- **Datasets pasivos (Shodan/Censys) son ciegos al protocolo Electrum** — hallazgo empírico confirmado en la sesión de technical research 2026-04-23. El crawler debe ser activo; Shodan/CT/ASN son pivots de atribución downstream, no fuente primaria.

### Ask / próximo paso

- **Grant reviewers:** evaluar el proyecto bajo el escenario 2 como baseline esperado (no bajo escenario 1). La contribución principal es la metodología reproducible con umbrales pre-comprometidos y archival durable, no un titular de hallazgos. Two-papers plan explícito (M3 methodology + M3+X follow-up) convierte "shipear débil o retrasar" en programa de investigación fondeable.
- **Peer researchers:** la reproducción desde un ASN distinto es arquitectónicamente **una segunda vantage** que fortalece el lower bound sin posibilidad de debilitarlo. Invitación a reproducir desde el día uno.
- **Decisión inmediata pendiente:** completar los 25 launch-blockers (lista completa en el PRFAQ) antes del release público. Priorizado: (1) outreach a b10c, (2) verificación empírica de fee-histogram, (3) completar PRD con el skill `bmad-create-prd`.

---
