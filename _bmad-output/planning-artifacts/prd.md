---
workflowType: 'prd'
project_name: electrum-sybil-detector
author: Ifuensan
date: 2026-04-24
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
visionLocks:
  bilingualReach: asymmetric-operational-principle
  twoPapersPlan: launch-first-program-committed-hybrid
  executiveSummaryVoice: peer-researcher-lead-scope-reframe-as-framing-principle
classification:
  projectType: research_project
  domain: scientific
  complexity: medium
  projectContext: greenfield-with-rich-planning-artifacts
  complexityCarveouts:
    - rigor.statistical_methodology
    - rigor.legal_framing
  forcedTopLevelSections:
    - dataset_requirements
    - publication_requirements
    - measurement_validity
    - output_guardrails
    - bilingual_parity
  subordinateSections:
    - tool_spec
  m0ArchitecturalGuardrails:
    - timestamp_precision_monotonic_ns
    - raw_event_schema_append_only
    - connection_metadata_captured_at_connect
    - one_canonical_ntp_time_source_per_window
  partyModeRounds: 4
  partyModeAgents:
    - Mary
    - John
    - Winston
    - Paige
inputDocuments:
  - docs/project-brief.md
  - _bmad-output/planning-artifacts/prfaq-electrum-sybil-detector.md
  - _bmad-output/planning-artifacts/prfaq-electrum-sybil-detector-distillate.md
  - _bmad-output/planning-artifacts/research/technical-electrum-protocol-internals-and-server-ecosystem-research-2026-04-23.md
  - docs/architecture.md
  - docs/roadmap.md
  - docs/tech-stack.md
  - docs/references.md
  - docs/bmad-binnacle/01_prfaq-challenge.md
  - docs/bmad-binnacle/02_technical-research.md
documentCounts:
  briefs: 1
  research: 2
  prfaq: 2
  projectDocs: 4
  bmadBinnacle: 2
projectClassification: greenfield-with-rich-planning-artifacts
---

# Product Requirements Document - electrum-sybil-detector

**Author:** Ifuensan
**Date:** 2026-04-24

## Executive Summary

`electrum-sybil-detector` measures the public Electrum server network at the level of **shared backend infrastructure** using **fork-race block-notification timing variance** as primary discriminator — a binary natural experiment that bypasses every self-declared server identity and that no prior Electrum measurement has used. It ships as a three-artifact bundle — open-source MIT collection daemon, CC BY 4.0 longitudinal dataset with three-tier archival (`bitcoin-data` GitHub + Zenodo DOI + arXiv), and a peer-reviewed methodology paper — designed to become the citable reference baseline for Electrum-layer privacy research, with a reproducibility contract tying derived dataset output to raw inputs + code hash. Pre-committed evidentiary thresholds (≥2 backend-state signals + ≥1 frontend-config signal per published cluster) and a two-paper structure — **M3 methodology paper + M3+X multi-vantage follow-up** — convert the ship-weak-or-delay tension into a fundable research program rather than a one-shot.

The work measures shared backend infrastructure, **not operator intent** — intent attribution is a separate interpretive layer this project does not originate, only cites from published third parties (b10c project-ideas issue #11; CoinDesk 2021 Chainalysis training-materials reporting on walletexplorer.com as undisclosed SPV honeypot). Primary audiences: Bitcoin privacy research peers (FC / PETS / IMC venues, b10c / Grundmann / Biryukov–Meiklejohn–Bonneau lineage), grant committees funding public-good Bitcoin infrastructure monitoring (OpenSats, HRF, Btrust, B4OS, BOSS Challenge, Brink), and Electrum-ecosystem maintainers (spesmilo, kyuupichan, Umbrel / Start9 / RaspiBlitz). The window is empirically defined: b10c issue #11 ("Can we spot public spy-Electrum servers run by Chainalysis?") has carried 9 months of `Todo` status since July 2025; no public Electrum census has been published since the 2019 Electrohunt study; the Chainalysis / walletexplorer.com SPV-honeypot precedent is publicly documented and recent.

English is the language of the paper and peer-review venues; tool, dataset documentation, and contribution channels are **bilingual EN+ES**, aligned with HackNodes Lab / Librería de Satoshi's mission to bring Bitcoin research into the Spanish-speaking developer community. Execution runs at sub-$500/year cost envelope on solo-researcher capacity, with a pre-identified Path 2 handoff (b10c or secondary academic measurement group) at 12-month post-launch threshold if citation and grant signals are absent.

### What Makes This Special

- **Physics-level discriminator.** Fork-race block-notification timing during stale-block events (3–8/month per `bitcoin-data/stale-blocks`) is a binary natural experiment: same-backend servers see the tip change simultaneously; independent-backend servers scatter by Bitcoin P2P propagation latency. No software-similarity null can explain this. Every prior Electrum fingerprinting approach (banner, version, donation address, Electrohunt 2019 phishing detection) operates on self-declared identity that is trivially evadable; fork-race timing is not.
- **Vantage-robust by construction.** The test is **variance of pairwise delta across many events**, not absolute single-event delta. Collector path asymmetry is constant and drops out. Single-vantage findings are a strict lower bound; community reproductions from different ASNs can only strengthen findings, never weaken them. Multi-vantage is therefore an architectural property, not a roadmap milestone.
- **Scope reframe as legal posture.** Public-facing claims frame findings as "shared backend infrastructure clusters," never as "operator X runs these servers." Intent attribution lives only in cited published third-party material. This separation is analytically honest and defamation-defensible — protects the work without weakening the contribution.
- **Reuse, not reinvention.** b10c's `fork-observer` already supports Electrum server connections; `bitcoin-data` provides the canonical archival ecosystem; methodological ancestors (CoinScope, TxProbe / Delgado-Segura, Grundmann et al. / TU Darmstadt, Node-Probe / Essaid et al.) are already established in the literature. This work fills the Electrum-shaped gap in an existing ecosystem rather than building a new framework.
- **Scenario-robust publishability.** All three M3 outcome scenarios are publishable under the locked framing: (1) clear shared-backend clusters → findings paper; (2) weak signals + upper bound + validated methodology → methodology paper (assumed default at M3 scale); (3) true null + upper bound → methodology paper as reference. The two-paper plan (M3 methodology + M3+X multi-vantage follow-up) is the structural answer to scenario uncertainty.

## Project Classification

- **Project Type:** `research_project` — added as first-class entry in local `project-types.csv`. Required PRD sections: `dataset_requirements`, `publication_requirements`, `measurement_validity`, `output_guardrails`, `bilingual_parity`, `tool_spec`, `archival_strategy`, `reproducibility_contract`.
- **Domain:** `scientific` — Bitcoin privacy research / network measurement.
- **Complexity:** `medium` with two non-negotiable carve-outs: `rigor.statistical_methodology` (power analysis, multiple-testing correction, confidence intervals on cluster claims) and `rigor.legal_framing` (every public-facing string audited against the Output Guardrails phrasing bank).
- **Project Context:** `greenfield` with rich planning artifacts (PRFAQ, project brief, technical research, architecture, roadmap, tech stack, references all drafted; no implementation code yet).
- **Deliverable bundle.** Tool (apparatus) + dataset (primary product) + paper (primary product). Tool acceptance criteria are reproducibility-driven (deterministic dataset regeneration from raw inputs + code hash), not UX-driven; CLI ergonomics receive bare minimum.
- **M0 architectural guardrails (non-negotiable, even at laptop scale).** Monotonic-ns timestamp precision (wall-clock stored separately); append-only raw-event schema with version tags; connection metadata (banner, TLS fingerprint, resolved IP, Tor circuit ID) captured at connect-time, never re-derived; one canonical NTP-disciplined time source per collection window.

## Success Criteria

### Research Success

- **Citations accumulating within 12 months of M3 launch**, specifically from FC / PETS / IMC-adjacent venues and from the target research lineage (b10c orbit, Grundmann / TU Darmstadt, Biryukov–Meiklejohn–Bonneau-tracked groups). Counted as "accepted" if citations quote the methodology or reference the dataset by DOI.
- **Community reproductions from different ASNs** — each reproduction is architecturally a new vantage that strengthens the lower bound on shared-backend prevalence. Target: ≥1 independent reproduction within 6 months of M3, ≥3 within 12 months.
- **Ecosystem-maintainer uptake** — ElectrumX / wallet / sovereignty-kit maintainers (spesmilo, kyuupichan, Umbrel / Start9 / RaspiBlitz) publicly referencing the dataset in hardening discussions, release notes, or documentation.
- **Librería de Satoshi signal** — Spanish-language engagement on dataset/tool documentation (issues opened in Spanish, translations contributed, forks from Spanish-speaking developers). Not a gating metric; a qualitative indicator of bilingual-parity mission fit.

### Grant / Program Success

- **At least one grant secured within 12 months of M3 launch** from {OpenSats, HRF, Btrust, B4OS, BOSS Challenge, Brink}, with the measurement contribution named as the funded line item.
- **Phase 2 activation** — M3+X multi-vantage follow-up paper funded and in progress.
- **Network capital** — invitations to Bitcoin privacy research events; co-authorship opportunities with b10c-orbit or TU Darmstadt-orbit groups.
- **Anti-success triggers (pre-committed, from IQ9):**
  - 6 months post-paper, no citations + no grant leads → Path 1 (graceful shutdown + methodology-paper-as-credentialing-artifact).
  - 6–12 months post-paper, citations accumulating + no grants → Path 3 (continue 6 more months, reassess).
  - 12 months post-paper, citations + no grants → Path 2 (community handoff to b10c or pre-identified secondary academic measurement group).
  - Grant secured at any point → continue as Phase 2 research program.

### Technical / Measurement Success

- **Collection uptime ≥95% over any rolling 30-day window** from M0 onward. Uptime <95% for 30 days → drop discretionary work and fix (IQ5 triage trigger).
- **Reproducibility contract honored** — raw inputs + code hash → bit-identical derived dataset, or documented floating-point tolerance per column.
- **Timestamp precision at capture** — monotonic-ns stored; wall-clock drift bound documented per collection window; one canonical NTP-disciplined time source per window.
- **Multi-signal evidentiary threshold honored for every published cluster** — ≥2 backend-state signals (fork-race timing variance, fee-histogram correlation, synchronized downtime) + ≥1 frontend-config signal (banner, version, ASN, donation address). Single-signal matches are candidates for reproduction, not findings.
- **Three-tier archival operational at launch** — `bitcoin-data` GitHub contribution accepted; Zenodo DOI reserved pre-launch and cited in paper abstract; arXiv preprint uploaded.
- **PR review SLA honored** — 48h acknowledgment, 7-day substantive review, public `review-queued` tagging during peak load. Data-integrity PRs exempt from triage (same-day review).

### Measurable Outcomes

Time-bound, pre-committed:

| Milestone | Outcome | Threshold |
|---|---|---|
| **M3 launch** | Tool + dataset + paper released simultaneously | 25-item launch-blocker checklist cleared; three-tier archival operational |
| **M3 + 6 months** | Citations and/or grant leads | ≥3 independent citations OR ≥1 grant lead → proceed; else → IQ9 Path 3 triage |
| **M3 + 12 months** | Grant conversion or handoff | ≥1 grant secured OR Path 2 handoff activated |
| **Ongoing (M0 →)** | Collection discipline | Uptime ≥95% / 30-day rolling; all published clusters exceed multi-signal threshold |
| **Ongoing** | PR stewardship | 48h ack SLA / 7d substantive SLA met on ≥90% of PRs |

## Product Scope

### MVP — M3 Launch (Minimum Shippable Research Contribution)

- **Collection daemon** covering clearnet Electrum servers discovered via snowball from seed lists (1209k.com/bitcoin-eye + Electrum wallet hardcoded defaults) + `server.peers.subscribe` expansion; Tor `.onion` coverage via SOCKS5.
- **Storage:** SQLite-backed at M0 → TimescaleDB at production scale (M2). Monotonic-ns timestamps + append-only raw-event schema with version tags + connection metadata captured at connect-time.
- **Methodology paper** covering: threat model, measurement ethics (rate-limiting, disclosure, IRB-equivalent), signal hierarchy, multi-signal threshold, baseline similarity distribution, results (clusters OR upper bound), related work (CoinScope, TxProbe, Grundmann, Node-Probe), known evasion paths, limitations (single vantage, scale).
- **Longitudinal dataset** published under CC BY 4.0 on `bitcoin-data` GitHub + Zenodo DOI. Duration scenario-dependent at M3 (minimum useful window TBD in Publication Requirements section).
- **Bilingual EN+ES documentation** (launch gate, not nice-to-have): README, first-run guide, dataset schema + Spanish glossary, column-by-column translation. Staleness SLA documented.
- **Output Guardrails enforced** across CLI stdout, dataset README, and paper abstract — canonical phrasing bank ("shared infrastructure clusters," never "operator X runs Y").
- **Launch-blocker checklist cleared** — 25 items from PRFAQ, priority order: (1) b10c socialization, (2) empirical fee-histogram verification, (3) fork-observer Electrum-support verification, (4) stale-blocks cadence verification, (5) methodology-ancestor citation verification.

### Growth Features (Post-M3, targeting M4 and M3+X)

- **M4: Rust rewrite** of collection daemon for production stability and lower resource footprint.
- **Multi-vantage expansion** — 2–3 additional collectors in different ASes (may also arrive earlier via community reproductions, architecturally).
- **TimescaleDB production migration** (M2 target; may slip past M3 without blocking the dataset-publication track if SQLite snapshot is sufficient for M3).
- **Public dashboard or API** for community consumption of live cluster status.
- **I2P `.b32.i2p` servers** — conditional on M1 snowball discovery revealing I2P ecosystem; high-value target given I2P's persistent-destination long-term-linkability primitive Tor does not provide.

### Vision (Future)

- **M3+X multi-vantage follow-up paper** with strengthened findings from extended collection and community reproductions; cites M3 as reference methodology. Phase 2 research program activated by successful grant.
- **Methodology adopted baseline** for cross-network measurements — Electrum measurement methodology ported to other SPV-served chains, or integrated into peer-observer-style broader observation networks.
- **Community-maintained project stewardship** — transition to multi-maintainer governance with Librería de Satoshi retaining editorial stewardship; pre-identified Path 2 candidate (b10c orbit or secondary academic measurement group) as structural backstop for IQ9 exit path.

## User Journeys

### Sarah — Grant Reviewer (OpenSats)

**Opening.** Sarah reviews ~40 Bitcoin-research applications per cycle. The hardest signal to find is *durability* — most applications promise findings without a structural answer to "what if the findings come in weak?"

**Rising action.** She opens the `electrum-sybil-detector` submission. The project brief opens with fork-race timing variance as primary discriminator, names the methodological ancestors (CoinScope, TxProbe, Grundmann, Node-Probe), and links to a PRFAQ with 25 pre-committed launch blockers and three pre-defined outcome scenarios. She skims the appendix and finds an explicit two-paper plan (M3 methodology + M3+X follow-up) and IQ9 exit paths — the proposal has named what happens if it underperforms, before underperforming.

**Climax.** Sarah does not need to ask the proposal what happens if scenario 2 (weak signals + upper bound) is the outcome. The proposal answers: ship a methodology paper as reference; structure M3+X to convert into a research program. The structural commitment is *the deliverable*, not just a finding.

**Resolution.** She funds it. The grant closes a structural gap in the OpenSats Electrum-research portfolio that has been open since 2019.

**Capabilities revealed.** Discoverable PRFAQ + project brief; explicit pre-committed thresholds + IQ9 exit paths; methodology-paper-first framing; reference-position language.

### Lukas — Peer Researcher (FC venue, b10c orbit, TU Darmstadt-adjacent)

**Opening.** Lukas works on Bitcoin P2P measurement. He has a reproducibility problem — most measurement papers in Bitcoin research are not reproducible six months later because the network has shifted and the dataset is gone.

**Rising action.** He encounters the M3 paper on arXiv. The paper cites a Zenodo DOI in its abstract; the dataset is downloadable in CC BY 4.0 Parquet; the methodology section specifies a code-hash + raw-input → bit-identical-derived-output contract. The `bitcoin-data` GitHub copy provides a redundant deposit. He re-runs the clustering algorithm against the published dataset; figures reproduce.

**Climax.** Lukas wants to extend. He runs the published tool from his TU Darmstadt vantage (different AS, different ASN). The tool's first-run guide takes him under an hour to a working collection daemon. His ASN-2 collection produces a second vantage that, by the project's own architecture, can only strengthen the lower bound on shared-backend prevalence.

**Resolution.** He contributes his ASN-2 dataset back via the `bitcoin-data` PR flow. The PR is acknowledged in 48 hours, substantively reviewed in 7 days. His contribution is cited in the M3+X follow-up paper as one of the multi-vantage extensions.

**Capabilities revealed.** Reproducibility contract enforced; arXiv preprint with Zenodo DOI in abstract; tool first-run guide ≤1 hour (English); `bitcoin-data` PR flow with documented review SLA; multi-vantage architecturally additive.

### Camila — ElectrumX Maintainer (spesmilo/kyuupichan-orbit, sovereignty-kit-adjacent)

**Opening.** Camila maintains a hardening patch backlog for ElectrumX. The 2019 anti-sybil hardening (subnet-dedup in `server.peers.subscribe`, IP validation in `add_peer`, source rate-limits) was the last empirically-grounded round; subsequent decisions have leaned on assumptions about server-mesh independence she cannot verify.

**Rising action.** The M3 paper provides empirical grounding for shared-backend cluster prevalence, with cluster boundaries defined by externally-observable signals her current hardening patches do not address. She reads the methodology and the known-evasion-paths section. She identifies which hardening directions the data supports and which do not.

**Climax.** Camila uses the dataset to characterize a class of clustered servers previously invisible to ElectrumX's intra-server defenses. She drafts a hardening proposal that addresses fleet-on-shared-infrastructure, citing the dataset by DOI as empirical ground.

**Resolution.** Her hardening proposal lands with empirical citation rather than speculation. The dataset becomes the ongoing reference for ElectrumX hardening decisions.

**Capabilities revealed.** Methodology paper with known-evasion-paths section; dataset with stable, citeable DOI; output guardrails (Camila gets infrastructure properties she can act on, not operator names she cannot legally assert).

### Óscar — Downstream Tool Operator (Spanish-speaking university-adjacent researcher)

**Opening.** Óscar wants to reproduce the M3 finding from his university's network. He reads Spanish more fluently than English; previous Bitcoin-research tools have stalled him at English-only README + first-run guides.

**Rising action.** He clones `electrum-sybil-detector`. The README is bilingual — Spanish next to English, both at parity. The first-run guide in Spanish walks him through Docker setup, NTP discipline, and the SQLite output schema. The dataset documentation includes column-by-column Spanish translation. He files an issue in Spanish and gets acknowledged in 48 hours.

**Climax.** Óscar runs the daemon from his vantage for 90 days, produces a reproducible dataset, contributes back via the PR flow. His contribution is reviewed in Spanish (Spanish-language issues accepted as locked in Bilingual Parity). He is named in the M3+X paper's reproduction acknowledgments.

**Resolution.** Óscar joins the contributor pool. Librería de Satoshi gains a real-world signal that the bilingual commitment landed. The dataset gains a vantage that, architecturally, only strengthens the lower bound.

**Capabilities revealed.** Bilingual EN+ES README + first-run guide + dataset schema with column-by-column translation; Spanish-language issue templates accepted; same PR review SLA in Spanish; staleness SLA on translations enforced.

### Ifuensan — Internal Researcher Operating the Daemon (admin/operations)

**Opening.** Ifuensan is at M2.5: collection has been running ~6 months, snowball discovery has expanded to ~150 servers including Tor coverage, SQLite has migrated to TimescaleDB, and the M3 launch window is 4 weeks out.

**Rising action.** The 25-item launch-blocker checklist drives the sequence: b10c socialization conversation (4–6 weeks pre-launch); empirical fee-histogram verification against two ElectrumX frontends sharing one Core; `fork-observer` Electrum-support verification; Zenodo DOI reservation; arXiv preprint upload citing the DOI; `bitcoin-data` GitHub PR opened. Collection uptime over the 30-day pre-launch window stays at ≥95%; the M3 dataset snapshot passes the reproducibility self-test.

**Climax.** Launch day. Tool, dataset, and paper release simultaneously. The Zenodo DOI in the paper abstract resolves; the `bitcoin-data` PR is accepted; the arXiv preprint is timestamped. Output guardrails are enforced across all three artifacts ("shared infrastructure clusters," never "operator X runs Y").

**Resolution.** M3 ships under scenario 2 (the assumed default) — methodology + upper bound + dataset. The two-paper structure carries; first independent reproduction lands within 6 weeks; first grant lead within 4 months.

**Capabilities revealed.** Pre-launch validation tooling (fee-histogram diff harness, reproducibility self-test); collection uptime monitoring with 95%/30-day trigger; multi-tier archival pipeline (Zenodo + bitcoin-data + arXiv); launch-blocker tracking.

### Diego — Sovereignty-Kit Operator Flagged in a Cluster (defamation-risk audience, edge case)

**Opening.** Diego runs three Electrum servers — one on a Hetzner VPS, one on a home node behind a residential ASN, one on a friend's RaspiBlitz on a third ASN. They share one Bitcoin Core running on the home node — set up that way deliberately, for cost reasons, with no surveillance intent.

**Rising action.** Diego is correctly flagged as a shared-backend cluster in the M3 dataset. He encounters the finding via a peer's mention on Bitcoin Twitter. He reads the dataset README and the paper section "what a flagged cluster does NOT mean." The text is explicit: shared backend infrastructure ≠ operator surveillance ≠ Diego specifically.

**Climax.** Diego confirms his three-server cluster shares one Core. The output guardrails — "shared infrastructure clusters," never "operator X runs Y" — work as designed. He is not accused of anything; he is accurately classified as one of N infrastructure-shared clusters with no claim on intent.

**Resolution.** Diego writes a public note explaining his deployment. His note becomes part of the qualitative literature around the dataset — "here's what a benign shared-backend cluster looks like." The Output Guardrails posture has done its work: accurate finding without defamation exposure.

**Capabilities revealed.** Output guardrails documentation in dataset README + paper; explicit "what a flagged cluster does NOT mean" text accessible to flagged operators; disclosure / response channels (issues, contact) for flagged operators.

### Journey Requirements Summary

Capabilities revealed across the six journeys, mapped to PRD sections that will formalize them in subsequent steps:

| Capability cluster | Journey source | Maps to PRD section |
|---|---|---|
| Discoverable PRFAQ + project brief, pre-committed thresholds | Sarah | Publication Requirements; Risks/Open Questions |
| Reproducibility contract (raw + code → bit-identical) | Lukas, Ifuensan | Reproducibility Contract; Tool Spec |
| Three-tier archival w/ Zenodo DOI in paper abstract | Lukas, Ifuensan | Archival Strategy; Publication Requirements |
| Tool first-run guide ≤1 hour, bilingual | Lukas, Óscar | Bilingual Parity; Tool Spec |
| `bitcoin-data` PR flow + 48h/7d review SLA | Lukas, Óscar | Archival Strategy; PR Stewardship |
| Methodology paper sections (threat model, ethics, known-evasion-paths, related work) | Sarah, Lukas, Camila | Publication Requirements |
| Bilingual issue templates, Spanish-language acceptance, translation column-by-column | Óscar | Bilingual Parity |
| Output guardrails phrasing bank applied to CLI + dataset + paper | Camila, Diego | Output Guardrails |
| Pre-launch validation harness (fee-histogram diff, reproducibility self-test) | Ifuensan | Tool Spec; M0 Architectural Guardrails |
| Collection uptime monitoring, 95%/30-day triage trigger | Ifuensan | Technical/Measurement Success |
| Disclosure / response channels for flagged operators | Diego | Output Guardrails |
| Multi-vantage architecturally additive (community reproductions) | Lukas, Óscar | Vision; Methodology |

## Domain-Specific Requirements

### Compliance & Regulatory

- **Measurement ethics (FC / PETS / IMC reviewer expectations).** Paper must include an explicit measurement-ethics section: rate-limiting policy on probes, disclosure protocol if a vulnerability is incidentally observed in a measured server, IRB-equivalent oversight statement (the project is solo-researcher with no institutional IRB; the section justifies why the methodology meets IRB-equivalent standards — public infrastructure measurement only, no user data, public-protocol probes only). Launch-blocker #22.
- **Defamation law (jurisdiction-aware framing).** Every public-facing string in CLI output, dataset README, paper abstract, and contribution channels is reviewed against the canonical Output Guardrails phrasing bank pre-publication. The framing rule "shared infrastructure clusters, never operator X runs Y" is a domain-level legal requirement, not just a stylistic preference. Originating intent attribution in any artifact = defamation exposure. Cited intent attribution from published third parties (b10c issue #11; CoinDesk 2021 Chainalysis materials) is the only permissible attribution language.
- **Open-science licensing.** Code under MIT (Bitcoin ecosystem norm; zero adoption friction). Dataset under CC BY 4.0 (enforces attribution = the actual moat). Paper as arXiv preprint + peer-reviewed venue. License compatibility verified against `bitcoin-data` repository conventions and Zenodo deposit requirements pre-launch.
- **Statistical validity (rigor.statistical_methodology carve-out).** Every published cluster claim accompanied by confidence intervals; multiple-testing correction applied across the many fork-race events; pre-committed multi-signal threshold (≥2 backend-state + ≥1 frontend-config) prevents post-hoc cluster construction. Power analysis disclosed for the M3 dataset window.
- **Reproducibility (publication-standard).** Code hash + raw-input → bit-identical-derived-output contract enforced. Reproducibility self-test ships with the M3 dataset release; CI-equivalent invocation path documented.

### Technical Constraints

- **Sub-second timing precision** for fork-race block-notification events. Monotonic-ns clock at capture, wall-clock recorded separately, NTP-disciplined host with declared stratum, drift bound documented per collection window. (M0 architectural guardrail.)
- **Sustained collection reliability** over months. Asyncio-based persistent connection management to 100–500 heterogeneous TCP/SSL sockets; reconnection with exponential backoff; per-server connection lifecycle metadata captured at connect-time. Collection uptime ≥95% over rolling 30-day windows; uptime <95% triggers IQ5 triage.
- **Tor SOCKS5 transport layer** at M2 for `.onion` server coverage. Tor circuit metadata logged per probe; vantage diversity declared in dataset manifest.
- **Append-only raw-event schema** with version tags. Derived tables (clusters, features) may churn; raw events cannot. (M0 architectural guardrail.)
- **Storage durability and migration path.** SQLite at M0 (laptop scale); TimescaleDB migration at M2 (production scale); schema designed for migration compatibility from day one.
- **Computational footprint.** Sub-$500/year cost envelope (VPS + storage + redundancy). Dataset volume ~6 GB/year compressed at full-network scale. Solo-researcher operational capacity is the architectural SPOF — see Risk Mitigations.

### Integration Requirements

- **`bitcoin-data` GitHub conventions** (b10c-maintained repository for Bitcoin network measurement datasets; existing residents include `stale-blocks`, `mining-pools`, `block-arrival-times`). Conformance to: directory layout, Parquet snapshot frequency, dataset-level CHANGELOG, README structure, license declaration. Pre-launch socialization with b10c (4–6 weeks, not 48h) to confirm contribution acceptance and conventions. Launch-blocker #11.
- **Zenodo DOI minting** (CERN-hosted, persistent identifier independent of any GitHub account). DOI reserved pre-launch and cited in paper abstract; subsequent versions cross-referenced. Launch-blocker #12.
- **arXiv preprint workflow** (no reviewer gate; timestamps priority). Preprint cites Zenodo DOI; LaTeX source archived with submission. Launch-blocker #13.
- **`fork-observer` reuse** (b10c's existing tool already supports Electrum-server connections and tip tracking). The collection daemon either consumes `fork-observer` data or re-uses its connection-management code paths rather than reimplementing. Launch-blocker #8 verifies the integration surface.
- **`stale-blocks` dataset as primary fork-race event source** (b10c-maintained). Cite by dataset version; document the cadence claim (3–8 events/month) against actual data. Launch-blocker #1.
- **Electrum protocol conformance.** Use stable RPCs only: `blockchain.headers.subscribe`, `server.version`, `server.features`, `server.banner`, `server.donation_address`, `blockchain.estimatefee(n)`, `blockchain.relayfee`, `mempool.get_fee_histogram`, `server.ping`. No reliance on undocumented behavior. Protocol version range advertised in `server.features` is recorded for every connect.

### Risk Mitigations

- **Solo-researcher SPOF.** Pre-identified Path 2 candidate (b10c orbit or secondary academic measurement group) committed pre-launch. Path 2 handoff activates at 12-month post-launch threshold if citation + grant signals are absent. Mitigation is structural (named candidate), not vague ("a university group").
- **Defamation exposure.** Output Guardrails section (own top-level PRD section) defines the canonical phrasing bank. Every public-facing string audited pre-publication. "What a flagged cluster does NOT mean" text accessible to flagged operators. Disclosure / response channel (issue templates, contact path) documented for flagged operators.
- **Reproducibility collapse.** Code hash + raw input → bit-identical derived output contract + three-tier archival (`bitcoin-data` + Zenodo + arXiv) + reproducibility self-test in CI. Schema versioning prevents silent drift.
- **Single-vantage bias.** Declared explicitly in paper limitations section. Findings framed as a strict lower bound on shared-backend prevalence; community reproductions from different ASNs strengthen the bound architecturally. Multi-vantage is a property of the methodology, not an open question.
- **Methodology obsolescence (e.g., post-launch hardening that defeats the discriminator).** Known-evasion-paths section in the paper enumerates how a sophisticated adversary could defeat each signal in the multi-signal threshold. The paper's contribution is the methodology + reference dataset; even successful future evasion does not retroactively invalidate the M3 measurement.
- **Fee-histogram non-determinism.** Empirical verification pending pre-launch (run two ElectrumX frontends against one Core, diff `mempool.get_fee_histogram`). If output is not bit-identical, methodology language softens to "strongly correlated" with documented tolerance. Launch-blocker #2 — highest priority alongside b10c socialization.
- **Tor vantage misattribution.** Tor exit diversity logged per probe. If different exits produce divergent observations, this is captured in the dataset manifest as vantage variance, not silently smoothed.

## Innovation & Novel Patterns

### Detected Innovation Areas

- **Fork-race timing variance as primary discriminator.** A binary natural experiment irreducible to software-similarity null. When Bitcoin produces a stale-block event (3–8/month per `bitcoin-data/stale-blocks`), same-backend Electrum servers see the tip change simultaneously; independent-backend servers scatter by Bitcoin P2P propagation latency. No prior Electrum measurement — including Electrohunt 2019 — uses this signal. This is the methodological spine, not a marginal addition.
- **Vantage-robust by construction.** The test is variance of pairwise delta across many events, not absolute single-event delta. Collector path asymmetry is constant and drops out. Single-vantage findings are mathematically a strict lower bound; community reproductions can only strengthen, never weaken. Multi-vantage is therefore an *architectural property* of the methodology, not a roadmap milestone — innovation in how measurement work composes across reproductions.
- **Pre-committed evidentiary threshold.** Multi-signal threshold (≥2 backend-state signals + ≥1 frontend-config signal) committed *before* the M3 dataset window opens, with locked statistical-validity carve-outs (confidence intervals, multiple-testing correction, power analysis). This shifts the discipline from "found patterns, here is what passed" to "pre-set bar, here is who cleared it." Innovation in *measurement-paper publication discipline*, not in the underlying statistics.
- **Reproducibility contract.** Code hash + raw input → bit-identical-derived dataset (or documented per-column floating-point tolerance), shipped with a CI-equivalent self-test. Rare in Bitcoin-network measurement work. Combined with three-tier archival (`bitcoin-data` GitHub + Zenodo DOI + arXiv), the contribution is durable across any single-host failure.
- **Legal-framing discipline as structural artifact.** Output Guardrails phrasing bank applied uniformly to CLI output, dataset README, and paper abstract. "What a flagged cluster does NOT mean" text accessible to operators flagged in the dataset. Cited-only intent attribution (b10c issue #11; CoinDesk 2021) — never originated. Innovation in *adversarial-measurement publication ethics*: defamation-defensible by construction, not by post-hoc legal review.
- **Multi-artifact bundling with three-tier archival.** Tool (MIT) + dataset (CC BY 4.0) + paper (arXiv + peer-reviewed venue) shipped as a co-equal joint launch. Three-tier archival (`bitcoin-data` + Zenodo DOI + arXiv) provides redundancy across independent hosts. Not standard practice in Bitcoin research; most projects are tool-only or paper-only with single-host distribution.
- **Two-papers research-program structure.** M3 methodology paper + M3+X multi-vantage follow-up, with Phase 2 grant funding the follow-up. Converts the "ship-weak-or-delay" launch-timing tension into a research program rather than a one-shot. Innovation in how research-output projects pre-commit to durability for grant readers.

### Assumptions Being Challenged

- *Anti-sybil hardening at the individual-server level is sufficient defense against shared-infrastructure attacks.* Wrong — the post-2019 ElectrumX hardening (subnet-dedup in `server.peers.subscribe`, IP validation in `add_peer`, source rate-limits) reaches no further than the individual server it runs on. A fleet deployed over shared infrastructure is invisible to those defenses.
- *Intent attribution is necessary for measurement to be useful.* Wrong — measuring shared backend infrastructure produces actionable findings (operators can audit, maintainers can harden, researchers can extend) without requiring the analytically and legally fraught step of naming operators.
- *Software-similarity fingerprints (banner, version) are adequate signals for clustering.* Wrong — these are trivially evadable by sophisticated adversaries. Fork-race timing is not.
- *Single-vantage measurement findings are inherently fragile.* Wrong — when the test statistic is variance-of-pairwise-delta, single-vantage findings are a strict lower bound that subsequent vantages can only strengthen.

### Market Context & Competitive Landscape

Prior art and adjacent work, mapped to position:

| Work | Layer | Methodology | Position relative to this work |
|---|---|---|---|
| Electrohunt (Kacherginsky / Coinbase, 2019) | Electrum | `server.banner` phishing detection | Last published Electrum measurement; methodology obsolete against the threat model this work addresses |
| CoinScope | Bitcoin P2P | Active measurement | Methodological ancestor; different layer |
| TxProbe (Delgado-Segura) | Bitcoin P2P | Transaction probing | Methodological ancestor; different layer |
| Grundmann et al. (TU Darmstadt) | Bitcoin P2P | Topology inference | Methodological ancestor; different layer |
| Node-Probe (Essaid et al.) | Bitcoin P2P | Node fingerprinting | Methodological ancestor; different layer |
| `bitnodes` | Bitcoin P2P | Node enumeration | Different layer; descriptive |
| `peer-observer` (b10c) | Bitcoin P2P | Network observation | Different layer; complementary |
| `fork-observer` (b10c) | Multiple (incl. Electrum) | Tip tracking | Reusable infrastructure for this work; does not cluster |
| 1209k.com/bitcoin-eye | Electrum | Server enumeration | Directory only; no clustering analysis |
| **b10c project-ideas issue #11** | Electrum | (Stated requirement, no execution) | Exact provenance citation; 9 months `Todo` since July 2025 |

The Electrum-shaped gap is empirically defined: no published equivalent since 2019; the question has been publicly named with detailed methodology by b10c and remained unexecuted. The CoinDesk 2021 Chainalysis / walletexplorer.com SPV-honeypot precedent makes it a documented-pattern-extension, not speculation.

### Validation Approach

Innovation-specific validation (non-redundant with Domain Risk Mitigations already in the PRD):

- **Pre-launch empirical premise tests.** The methodological spine assumes (a) fork-race timing variance is discriminative across same-backend vs. independent-backend pairs and (b) `mempool.get_fee_histogram` is bit-identical or strongly-correlated for shared-backend frontends. Both are testable pre-M3 in isolation:
  - Fee-histogram determinism: run two ElectrumX frontends against one Bitcoin Core, diff `mempool.get_fee_histogram` output. If not bit-identical, methodology language softens to "strongly correlated" with documented tolerance. Launch-blocker #2 — highest priority.
  - Fork-race discriminator validity: validate against `bitcoin-data/stale-blocks` cadence (3–8/month claim). Launch-blocker #1.
- **Known-independent baseline.** Establish the noise floor: compute pairwise-delta variance distribution among servers known to be independent (different operators, different ASNs, different geographies). Single-signal matches that fall within this baseline are not findings. The baseline is itself a contribution to the literature.
- **Reproducibility self-test as ship gate.** The M3 release gates on the bit-identical contract self-test passing. CI-equivalent invocation path documented in the dataset README; reviewers can re-run.
- **Peer review at FC / PETS / IMC.** External validation by the target research community. The two-papers structure reduces single-venue rejection risk: if FC rejects M3, PETS is the documented backup; IMC tertiary.
- **Community reproductions as validation surface.** Each independent reproduction from a different ASN is a vantage that strengthens the lower bound. Reproductions are validation of the methodology even when they confirm rather than extend.

### Risk Mitigation (Innovation-Specific)

Risks specifically tied to *novelty status* (not duplicating Domain Risk Mitigations):

- **Methodology premise fails empirically before launch.** Fee-histogram is non-deterministic, or fork-race timing variance does not discriminate as expected against an independent-backend baseline. Mitigation: launch-blockers #1 and #2 are pre-launch empirical tests; if either fails, methodology language is softened (not abandoned) and the affected signal is downgraded from "primary" to "supporting." The multi-signal threshold structure is robust to one signal weakening because clusters require ≥2 backend-state.
- **Parallel work appears between submission and publication.** A competing Electrum measurement is published in the FC/PETS/IMC submission window or on arXiv. Risk: this work loses canonical-reference position. Mitigation: arXiv preprint uploaded immediately at M3 launch (timestamps priority); contribution is repositioned as parallel reference rather than first-of-kind. Launch-blocker #13 (arXiv upload pre-launch) is structural defense.
- **Innovation pattern is "discipline" not "discovery."** Several innovations here (pre-committed thresholds, reproducibility contract, legal-framing discipline) are *practice innovations*, not algorithmic novelties. Risk: peer reviewers categorize the work as "engineering" rather than "research contribution." Mitigation: paper foregrounds methodological novelty (fork-race timing variance + vantage-robust pairwise-delta-variance) as the algorithmic contribution; the discipline innovations are framed as enabling conditions, not as the central claim.
- **Two-papers framing reads as hedging in M3.** Risk: peer reviewers reading the M3 paper interpret the M3+X follow-up commitment as "the authors are admitting the M3 findings are weak." Mitigation: the M3 paper itself stands alone without the program framing (Step 2b lock); the program framing lives in the PRD Executive Summary and grant proposals, not in the paper abstract.
- **Multi-artifact bundling sets a higher quality bar than tool-only or paper-only releases.** Three things must ship together at M3 — any one slipping delays all. Mitigation: 25-item launch-blocker checklist drives the joint sequence; pre-committed M3 ship gate is "tool + dataset + paper bit-identical-reproducible AND archival operational AND launch-blocker checklist cleared" — none of those is a paper-only or tool-only gate.

## Research Project Specific Requirements

### Project-Type Overview

`electrum-sybil-detector` is a `research_project` — a three-artifact bundle with the **tool as apparatus** (reproducibility scaffolding) and the **dataset + paper as the primary products** (where the citation economy and grant leverage attach). Acceptance criteria for each artifact reflect that allocation: the tool is judged by whether it deterministically regenerates the dataset from raw inputs + code hash; the dataset is judged by schema stability, archival durability, and field-policy compliance; the paper is judged by methodological rigor, peer-review acceptance, and durable reference position. CLI ergonomics, packaging UX, onboarding funnels, and adoption metrics are explicitly out of scope.

### Dataset Requirements

**Schema (raw-event tier).** Append-only event rows with version tag (`schema_version`). One canonical NTP-disciplined time source per collection window declared in the dataset manifest. Per-event fields include: monotonic-ns timestamp at capture; wall-clock timestamp (separate); server identifier (opaque hash, not the public hostname/IP — see Output Guardrails for field policy); ASN; protocol-version range from `server.features`; probe type; probe payload digest. Connection metadata (banner, TLS fingerprint, resolved IP, Tor circuit ID where applicable) recorded at connect-time with a separate `connection_event` row. Schema migrations are forward-compatible-only; deprecated fields kept until at least the next major dataset version.

**Schema (derived tier).** Cluster assignments, per-pair similarity scores, signal-by-signal breakdown. Derived tables MAY churn between dataset versions; raw events MAY NOT. Every derived row links to the raw events that produced it via deterministic identifiers.

**Versioning contract.** Dataset releases follow `semver`-equivalent semantics: MAJOR for incompatible raw-schema changes; MINOR for additive raw-schema changes or new derived tables; PATCH for derived-table corrections without raw changes. Each release ships with a CHANGELOG documenting schema deltas, collection-window boundaries, and the code hash that produced the derived tier.

**Field-policy compliance.** No field in any tier names an operator. Server identifiers are opaque hashes derived from public-protocol fingerprints, not from operator-claimed identity. The mapping from public hostname to opaque hash is published only if doing so does not enable defamation exposure (default: not published; rejoined to public hostname only inside the dataset documentation's worked examples, which use deliberately benign cluster examples).

**License.** CC BY 4.0. License text included in dataset README and Zenodo record. Attribution requirement enforces dataset citation = the actual moat (per locked positioning).

**Bilingual schema documentation.** Column-by-column English schema documentation has a mirror Spanish translation. Both documents reference the same authoritative schema declaration (machine-readable JSON Schema or Parquet schema export).

**Reproducibility manifest per release.** Each release ships a `manifest.json` declaring: code hash, raw-input fingerprint, NTP stratum, collection-window boundaries, dataset version, release timestamp, Zenodo DOI. The manifest is itself part of the dataset and citable.

### Publication Requirements

**Paper artifact deliverable contract.** The M3 methodology paper must include the following sections, each with a definition-of-done before submission: (a) abstract citing Zenodo DOI; (b) introduction including provenance citation (b10c issue #11) and CoinDesk 2021 Chainalysis precedent; (c) threat model (launch-blocker #23); (d) measurement-ethics statement (launch-blocker #22); (e) related work covering CoinScope, TxProbe, Grundmann et al., Node-Probe, Electrohunt 2019, with verified author attribution (launch-blocker #9); (f) methodology, including signal hierarchy, multi-signal threshold, vantage-robustness derivation, baseline computation; (g) results, including either positive-finding clusters (scenario 1) or upper-bound + null distribution (scenarios 2 and 3); (h) known evasion paths (per Innovation Risk Mitigation); (i) limitations (single vantage, M3 scale, fee-histogram tolerance if applicable); (j) reproducibility statement linking to the dataset DOI and self-test invocation.

**Evidentiary standards (multi-signal threshold).** Every published cluster claim exceeds the threshold on ≥2 backend-state signals (fork-race timing variance, fee-histogram correlation, synchronized downtime) and ≥1 frontend-config signal (banner, version, ASN, donation address). Single-signal matches are listed in the dataset as candidates for reproduction, never as findings. Confidence intervals on every cluster claim. Multiple-testing correction across the fork-race-event population. Power analysis disclosed for the M3 dataset window. (Carve-out: `rigor.statistical_methodology`.)

**Venue hierarchy (locked).** Primary: FC (Financial Cryptography). Backup: PETS. Tertiary: IMC. Final fallback: technical report + arXiv + dataset DOI + `bitcoin-data` contribution (not failure; venue miss). NOT targeting USENIX Security or S&P (novelty bias against measurement-first work). Submission decisions made against a pre-committed timeline; venue-miss does not gate the M3 dataset / tool launch.

**arXiv preprint posture.** arXiv preprint upload is unconditional and launch-concurrent or launch-preceding. Cites the Zenodo DOI in the abstract. LaTeX source archived with the submission. (Launch-blocker #13.)

#### Archival Strategy

Three-tier durable archival, each independent of the others:

1. **`bitcoin-data` GitHub** (b10c-maintained community repository). Conformance to upstream conventions: directory layout matching existing residents (`stale-blocks`, `mining-pools`, `block-arrival-times`); Parquet snapshot at the cadence specified in the dataset CHANGELOG; dataset-level CHANGELOG required; README with license declaration. Pre-launch socialization with b10c (4–6 weeks ahead, not 48h) confirms acceptance and conventions. (Launch-blocker #11.)
2. **Zenodo DOI** (CERN-hosted, persistent identifier, independent of any GitHub account). DOI reserved pre-launch, cited in paper abstract before launch. Subsequent dataset versions get cross-referenced DOIs. (Launch-blocker #12.)
3. **arXiv preprint** (timestamps priority). Cites the Zenodo DOI; LaTeX source archived. (Launch-blocker #13.)

The three tiers are independent failure domains — loss of any single tier does not invalidate the contribution. The Zenodo DOI is the canonical citation handle.

### Measurement Validity

**Clock discipline.** Monotonic nanosecond timestamps stored at capture. Wall-clock timestamps stored separately (used only for human-readable display, never for computed-delta metrics). NTP stratum declared in the dataset manifest. Wall-clock drift bound documented per collection window. One canonical NTP-disciplined time source per collection window. (M0 architectural guardrail.)

**Connection heterogeneity.** Methodology treats per-server handshake timing as server-attributed, not client-attributed. TCP-stack variance across heterogeneous servers (different OS / kernel / connection-stack) is explicitly modeled in the timing-variance derivation, not silently averaged.

**Longitudinal continuity.** A "gap" is any interval > N seconds (N declared per collection window) between successful probes for a given server. Gaps are enumerated in the dataset manifest, not smoothed. Continuous-collection windows are bounded explicitly; analyses that span gap boundaries declare the gap structure.

**Vantage correctness.** Single-vantage bias is declared explicitly in the paper's limitations section. Findings are framed as a strict lower bound on shared-backend prevalence. For Tor-routed probes, exit-circuit diversity is logged per probe; if different exits produce divergent observations, the divergence is captured in the dataset manifest as vantage variance, not silently smoothed.

#### Reproducibility Contract

Code hash + raw-input fingerprint → bit-identical derived dataset, OR documented per-column floating-point tolerance with bounds. The contract is enforced by a CI-equivalent self-test that ships with every dataset release. The self-test invocation path is documented in the dataset README; reviewers can re-run independently. Schema versioning prevents silent drift: any change to derived-tier outputs is gated on either bit-identical reproduction with the new code hash or an explicit dataset version bump with documented deltas.

### Output Guardrails

**Canonical phrasing bank.** A versioned phrasing bank is maintained as part of the project documentation. Approved language: "shared infrastructure clusters," "infrastructure-shared cluster," "backend-shared frontend group," "cluster of common-backend Electrum servers." Prohibited language anywhere in CLI output, dataset README, paper abstract, or contribution channels: "operator X runs servers Y," "Chainalysis runs," "surveillance operator," any phrasing that originates an intent attribution. Cited intent attribution from published third parties (b10c issue #11; CoinDesk 2021) is the only permissible attribution language.

**Pre-publication audit.** Every public-facing string in CLI output, dataset README, paper abstract, contribution-channel documentation, and Spanish translations is audited against the phrasing bank before any release. The audit is a launch gate; release is blocked on audit completion.

**"What a flagged cluster does NOT mean" text.** Mandatory in dataset README and paper. Explicit list of plausible benign explanations for shared-backend infrastructure (e.g., cost-sharing across personal nodes; one operator running multiple frontends for redundancy; community-sovereignty-kit shared deployments). Operators flagged in the dataset are directed to this text first.

**Disclosure / response channel.** Issue template specifically for flagged operators. Process: operator opens issue → maintainer acknowledges within 48h → maintainer reviews evidence and responds → if classification is empirically wrong, dataset is corrected in the next release with the correction documented in the CHANGELOG; if classification stands, operator's contextual note is added to the dataset's qualitative literature (with operator consent).

**Cited-only intent attribution rule.** No artifact (CLI, dataset, paper, blog post, talk slides) originates intent attribution. All intent claims are cited from published third-party material with full attribution. (Carve-out: `rigor.legal_framing`.)

### Bilingual Parity

**Scope of bilingual deliverables.** Tool README, first-run guide, CLI `--help` text, dataset schema documentation, dataset README, contribution guide, issue templates. Both English and Spanish at parity (synchronized version; no content present in one language and absent in the other).

**Out of scope for bilingual.** The paper itself is English only (peer-review venue constraint). Internal development documentation, code comments, and commit messages are English only.

**Staleness SLA.** When a bilingual document is updated in either language, the other language must be updated within 14 days. Documents older than 14 days post-update in either language are flagged in CI and visible publicly as "translation pending." Stale > 30 days = translation rolled back to the prior synchronized version (rather than ship divergent content).

**Issue and PR templates.** Both English and Spanish accepted. Issues opened in Spanish receive Spanish acknowledgment within the same 48h SLA as English issues. PR reviews in either language follow the same 7-day substantive-review SLA.

**Sustainability commitment.** The bilingual posture is operationally sustained through the dataset lifetime by HackNodes Lab / Librería de Satoshi. If sustainability becomes infeasible at any point post-launch, the public commitment is to roll back all bilingual artifacts to a documented "frozen English-only with archival Spanish snapshot" state, not to silently let translations rot.

### Tool Specification (Subordinate)

**Acceptance criteria.** The tool is judged by whether it deterministically regenerates the dataset from raw inputs + code hash. CLI ergonomics, polished `--help` text, packaging quality, onboarding flow, and runtime efficiency are explicitly secondary. CI gate: reproducibility self-test passes; ship gate adds: bilingual first-run guide ≤1 hour to working collection; output guardrails phrasing bank applied to all CLI outputs.

**M0 architectural guardrails (non-negotiable, even at laptop scale).** Monotonic-ns timestamp precision (wall-clock stored separately); append-only raw-event schema with version tags; connection metadata captured at connect-time, never re-derived; one canonical NTP-disciplined time source per collection window. (See Project Classification > M0 architectural guardrails.)

**Module structure.**

- *Discovery module.* Seed-list ingestion (1209k.com/bitcoin-eye + Electrum wallet hardcoded defaults); snowball expansion via `server.peers.subscribe`; ASN diversity handling for ElectrumX's subnet-similarity anti-sybil filter; clearnet at M0–M1, Tor at M2.
- *Collection module.* Asyncio-based persistent connection management to all discovered servers; subscriptions to `blockchain.headers.subscribe`; periodic polling of `server.version`, `server.features`, `server.banner`, `server.donation_address`, `server.ping`, `blockchain.estimatefee(n)`, `blockchain.relayfee`, `mempool.get_fee_histogram`. Reconnection with exponential backoff. Per-server uptime/downtime event logging.
- *Storage module.* SQLite (M0) → TimescaleDB (M2). Append-only raw tier; derivable derived tier. Schema migrations forward-compatible-only.
- *Analysis module.* Fork-race event ingestion from `bitcoin-data/stale-blocks`; per-pair pairwise-delta variance computation; multi-signal threshold evaluation; baseline similarity-distribution computation from known-independent servers; clustering (DBSCAN or hierarchical on weighted similarity matrix). Output: cluster assignments + per-pair signal breakdowns.
- *Dataset publication module.* Monthly Parquet snapshot generation; Zenodo DOI minting (idempotent); `bitcoin-data` GitHub PR flow (idempotent); reproducibility self-test invocation; manifest generation.
- *Reuse, not reinvention.* `fork-observer` is reused for tip tracking where its surface fits; not reimplemented.

**Implementation language.** Python (asyncio, stdlib at M0; standard data tooling at M1+) through M3. Rust rewrite at M4 for production stability and lower resource footprint. Python and Rust must produce bit-identical derived datasets from the same raw inputs at the M4 transition (or document the floating-point tolerance).

**First-run guide.** Bilingual EN+ES. Working collection daemon to first probe in ≤1 hour for a competent developer following the guide. (Launch-blocker #5.)

### Implementation Considerations

**M0 → M1 → M2 → M3 → M4 transition gates.**

- **M0 → M1 gate.** Asyncio collection running 24/7 against 10–20 seed servers; SQLite schema covering all data points in the architecture; M0 architectural guardrails enforced; reproducibility self-test green. No architectural shortcuts that would block M1 expansion.
- **M1 → M2 gate.** Snowball expansion complete; clearnet network covered (~150–500 servers); SQLite scale stress-tested; planning for SQLite → TimescaleDB migration in place.
- **M2 → M3 gate.** Tor coverage operational; TimescaleDB migration complete (or SQLite snapshot demonstrably sufficient for the M3 dataset window); 25-item launch-blocker checklist actively cleared; pre-launch empirical premise tests (launch-blockers #1, #2) green.
- **M3 launch gate.** All five forced PRD sections satisfied and audited; tool + dataset + paper bit-identical-reproducible against the published code hash; three-tier archival operational (`bitcoin-data` PR accepted; Zenodo DOI cited in paper abstract; arXiv preprint timestamped). Launch-blocker checklist cleared.
- **M3 → M4 gate.** Methodology paper accepted at FC/PETS/IMC OR published as technical report + arXiv + dataset DOI; first independent reproduction(s) landed; Phase 2 grant application in progress or secured.

**Reuse posture.** `fork-observer` (b10c) for tip tracking integration; `bitcoin-data/stale-blocks` as canonical fork-race event source; `bitcoin-data` repository conventions for dataset publication; methodological-ancestor citations (CoinScope, TxProbe, Grundmann, Node-Probe) for related-work positioning. The project does not invent infrastructure where reusable infrastructure exists.

**Pre-launch validation harness.** Fee-histogram-determinism test (launch-blocker #2) is a discrete validation tool, not a one-time check. Same harness exercised in CI to guard against methodology drift between releases.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP approach: reference-baseline research-contribution MVP.** The minimum shippable artifact is a citable empirical baseline — tool (apparatus) + dataset (primary product) + paper (primary product) shipped jointly at M3. "Useful" is defined by peer-researcher reproducibility and grant-committee fundability, not by end-user adoption. CLI ergonomics, packaging UX, and onboarding funnels are explicitly secondary (see §Tool Specification).

**Resource requirements:** Solo researcher (Ifuensan / HackNodes Lab); sub-$500/year operational cost envelope (VPS + storage + redundancy); ~12-month M0→M3 execution window. Solo-researcher capacity is the architectural SPOF — pre-identified Path 2 candidate (b10c orbit / secondary academic measurement group) committed pre-launch as structural backstop.

### Phased Roadmap & Risk Mitigation

To avoid duplication and drift, phased roadmap and risk mitigation live in their authoritative sections elsewhere in this PRD; this section is index only:

- **MVP / Growth / Vision tiers** → §Product Scope (MVP — M3 Launch / Growth Features — Post-M3 / Vision — Future).
- **M0→M4 transition gates** (architectural sequencing) → §Implementation Considerations.
- **Domain risk mitigations** (solo SPOF, defamation, reproducibility, single-vantage, methodology obsolescence, fee-histogram non-determinism, Tor misattribution) → §Domain-Specific Requirements > Risk Mitigations.
- **Innovation-specific risk mitigations** (premise failure, parallel work, "discipline vs. discovery" framing, two-papers-as-hedging, multi-artifact bundling) → §Innovation & Novel Patterns > Risk Mitigation.
- **Resource-risk contingency** (pre-committed anti-success triggers; Path 1 / Path 2 / Path 3 exits) → §Success Criteria > Grant / Program Success.

### Launch-Blocker Checklist (25 items)

The "25-item launch-blocker checklist" referenced throughout this PRD is enumerated here. Items 1–23 are imported verbatim from PRFAQ Stage 3 + Stage 4 coaching notes; items 24–25 promote two launch gates already present in the PRD body into numbered tracking items. No scope is introduced beyond what already exists in the document.

1. Verify `bitcoin-data/stale-blocks` cadence claim (3–8/month, 13 in first 3.5 months of 2026 with consecutive-height pairs).
2. Empirically verify fee-histogram behavior on two ElectrumX frontends sharing one backend (identical vs. strongly correlated).
3. Verify 500 MB/month compressed signal volume at full public network scale — extrapolation from README's 20-server / 50–100 MB figure; run actual M0 test.
4. Verify `$5/month VPS` claim against planned Rust daemon CPU profile.
5. Verify "under an hour" Docker install claim when first-run guide exists.
6. Verify BlueWallet default-server publicly-reachable claim — if not publicly reachable, swap example.
7. Verify b10c issue #11 URL, status still "Todo", title match.
8. Verify b10c fork-observer Electrum-support claim.
9. Verify methodology-ancestor citations: CoinScope (author + venue), TxProbe (Delgado-Segura), Grundmann et al. (specific paper).
10. Locate CoinDesk 2021 article on Chainalysis / walletexplorer.com; verify URL + claims.
11. Pre-launch: open discussion with b10c on `bitcoin-data` dataset contribution.
12. Pre-launch: create Zenodo record, reserve DOI, cite in paper abstract.
13. Pre-launch: upload arXiv preprint citing Zenodo DOI.
14. Pre-launch: verify AS24940 (Hetzner) as style-rule example remains representative; swap if Cluster 7 example is misleading.
15. Verify Python asyncio timing resolution (~1–10 ms) is adequate in actual M0 collection.
16. Verify 1209k.com "~90–95% of listed servers maintain >90% uptime" claim against actual 1209k.com historical data.
17. Clarify and fact-check the I2P "reveals initiator's address" claim — phrase as "persistent destination identifiers enable long-term linkability" for technical accuracy.
18. Verify IQ3's 9-month b10c-Todo dwell time is accurate at actual launch date; update phrasing if launch slips.
19. **Critical-path pre-launch:** schedule b10c socialization conversation covering framing, `bitcoin-data` contribution, and Path 2 handoff optionality (IQ3 differentiation + IQ9 Path 2 precondition).
20. Verify FC's recent acceptance patterns for methodology-first / scenario-2-style measurement papers (Biryukov / Meiklejohn / Bonneau lineage holds through 2024–2026).
21. Verify PETS 2023–2025 editorial mix (claimed federated-learning / secure-computation dominance); reconsider primary/backup ordering if PETS is still actively publishing Bitcoin work.
22. Paper must include measurement-ethics section (OpenSats / PETS reviewer expectations: rate-limiting, disclosure, IRB-equivalent).
23. Paper must include "threat model and known evasion paths" section per IQ7.
24. **Output Guardrails phrasing-bank audit complete** across CLI output, dataset README, paper abstract, contribution-channel documentation, and Spanish translations. Audit is a launch gate; release blocked on completion. *(Promotion of §Output Guardrails > Pre-publication audit.)*
25. **Reproducibility self-test green at M3 dataset snapshot** — code hash + raw-input fingerprint → bit-identical derived dataset (or per-column floating-point tolerance documented). Self-test invocation path documented in dataset README; reviewers can re-run independently. *(Promotion of §Reproducibility Contract + §Tool Specification ship gate.)*

**Priority-1 cluster** (per §Product Scope > MVP — M3 Launch): #11 (b10c socialization) → #2 (fee-histogram) → #8 (fork-observer) → #1 (stale-blocks cadence) → #9 (methodology-ancestor citations).

## Functional Requirements

### Server Discovery

- **FR1:** The system can ingest seed-list server endpoints from configured sources (1209k.com / bitcoin-eye and Electrum wallet hardcoded defaults). — *owned by Discovery module*
- **FR2:** The system can expand the discovered server population via `server.peers.subscribe` snowball traversal until convergence. — *owned by Discovery module*
- **FR3:** The system can connect to `.onion` Electrum servers via SOCKS5 to a Tor circuit. — *owned by Discovery module*
- **FR4:** The system can record per-server discovery provenance (source, discovery timestamp, observed ASN, advertised `server.features` protocol-version range) so vantage diversity can be declared in the dataset manifest. — *owned by Discovery module*

### Probing & Data Collection

- **FR5:** The system can maintain persistent asyncio TCP/SSL connections to all discovered servers concurrently, with reconnection via exponential backoff on disconnect. — *owned by Collection module*
- **FR6:** The system can subscribe to `blockchain.headers.subscribe` on every connected server and capture each header notification with monotonic-ns and wall-clock timestamps. — *owned by Collection module*
- **FR7:** The system can periodically poll the stable Electrum RPC suite (`server.version`, `server.features`, `server.banner`, `server.donation_address`, `server.ping`, `blockchain.estimatefee(n)`, `blockchain.relayfee`, `mempool.get_fee_histogram`) at a configurable per-server cadence. — *owned by Collection module*
- **FR8:** The system can capture connection-event metadata (banner, TLS fingerprint, resolved IP, Tor circuit ID where applicable) at connect-time and never re-derive it later. — *owned by Collection module*
- **FR9:** The system can emit per-server uptime / downtime events with monotonic-ns timestamps so synchronized-downtime can be computed downstream. — *owned by Collection module*
- **FR10:** The system can throttle probe rates per server in conformance with the documented measurement-ethics rate-limiting policy. — *owned by Collection module*

### Storage & Schema Discipline

- **FR11:** The system can store all probe results as append-only raw-event rows with a `schema_version` tag; existing rows are immutable. — *owned by Storage module*
- **FR12:** The system can persist monotonic-ns and wall-clock timestamps per event in separate columns, never substituting one for the other in computed-delta metrics. — *owned by Storage module*
- **FR13:** The system can persist a per-collection-window NTP-discipline manifest (declared canonical NTP source, stratum, drift bound). — *owned by Storage module*
- **FR14:** The system can apply forward-compatible-only schema migrations: deprecated raw-tier columns are retained until at least the next MAJOR dataset version. — *owned by Storage module*
- **FR15:** The system can migrate raw + derived storage from SQLite (M0–M1) to TimescaleDB (M2+) without loss or schema divergence. — *owned by Storage module*
- **FR16:** The system can emit opaque server identifiers (hash of public-protocol fingerprints) in all published artifacts; the public-hostname mapping is not exported by default. — *owned by Storage module*

### Analysis & Signal Computation

- **FR17:** The system can ingest fork-race events from `bitcoin-data/stale-blocks` and identify the windowed time interval surrounding each event. — *owned by Analysis module*
- **FR18:** The system can compute per-pair pairwise-delta variance for `blockchain.headers.subscribe` notifications across all observed servers within a fork-race window. — *owned by Analysis module*
- **FR19:** The system can compute correlation scores for `mempool.get_fee_histogram` outputs across all server pairs over a configurable window. — *owned by Analysis module*
- **FR20:** The system can detect synchronized downtime across server pairs and emit a synchronized-downtime signal. — *owned by Analysis module*
- **FR21:** The system can evaluate the pre-committed multi-signal threshold (≥2 backend-state signals + ≥1 frontend-config signal) per cluster candidate and classify each as *finding*, *candidate-for-reproduction*, or *below-threshold*. — *owned by Analysis module*
- **FR22:** The system can compute the known-independent baseline similarity distribution from a declared independent-server set, producing a noise-floor reference distribution. — *owned by Analysis module*
- **FR23:** The system can produce cluster assignments via DBSCAN or hierarchical clustering on the weighted similarity matrix, with confidence intervals and multiple-testing correction applied. — *owned by Analysis module*
- **FR24:** The system can run the fee-histogram-determinism diff harness against two ElectrumX frontends sharing one Bitcoin Core — both as one-time pre-launch validation and as a recurring CI check guarding methodology drift between releases. — *owned by Analysis module / CI tooling*

### Dataset Publication & Archival

- **FR25:** The system can generate a Parquet snapshot of raw + derived tiers at a configurable cadence (default monthly) conformant with `bitcoin-data` repository conventions (directory layout, CHANGELOG, README). — *owned by Dataset publication module*
- **FR26:** The system can produce a `manifest.json` per release declaring code hash, raw-input fingerprint, NTP stratum, collection-window boundaries, dataset version, release timestamp, and Zenodo DOI. — *owned by Dataset publication module*
- **FR27:** The system can re-derive the derived tier from raw inputs + code hash and self-test for bit-identical reproduction (or per-column floating-point tolerance), failing the release on mismatch. — *owned by Dataset publication module*
- **FR28:** A maintainer can open a `bitcoin-data` PR for a dataset release using the project's idempotent submission flow, including the upstream-mandated CHANGELOG entry and directory-layout conformance.
- **FR29:** A maintainer can mint a Zenodo DOI for a dataset release using the project's idempotent submission flow, with version cross-references preserved across releases.
- **FR30:** A maintainer can upload an arXiv preprint citing the Zenodo DOI in its abstract, with the LaTeX source archived alongside the submission.

### Output Guardrails & Disclosure

- **FR31:** A maintainer can run a phrasing-bank audit pass over CLI output, dataset README, paper abstract, contribution-channel documentation, and Spanish translations, with the audit functioning as a release gate (release blocked on audit completion).
- **FR32:** A flagged operator can locate a "What a flagged cluster does NOT mean" explanatory text within both the dataset README and the methodology paper, with explicit enumeration of plausible benign explanations.
- **FR33:** A flagged operator can open a disclosure issue via a dedicated template and receive maintainer acknowledgment within 48 hours; if classification is empirically wrong, the dataset is corrected in the next release with the correction documented in the CHANGELOG.
- **FR34:** A maintainer can append a flagged operator's contextual note (with operator consent) to the dataset's qualitative literature when the operator confirms the classification stands but provides benign-deployment context.

### Bilingual Parity

- **FR35:** A Spanish-speaking contributor can read README, first-run guide, dataset schema documentation, dataset README, contribution guide, and CLI `--help` text in Spanish at synchronized parity with English (no content present in one language and absent in the other).
- **FR36:** A Spanish-speaking contributor can open issues and pull requests in Spanish, and receive acknowledgment within the same 48-hour SLA and substantive review within the same 7-day SLA as English-language submissions.
- **FR37:** The system can flag bilingual documents updated in only one language for >14 days as "translation pending" via a CI check, visible publicly. — *owned by CI tooling*
- **FR38:** A maintainer can roll back a stale-translation document (>30 days divergent) to the prior synchronized version rather than ship divergent content.

### Operational Health & Stewardship

- **FR39:** A researcher operating the daemon can monitor collection uptime over rolling 30-day windows and is alerted when uptime falls below the 95% threshold. — *owned by Collection module / operational tooling*
- **FR40:** The system can enumerate collection gaps (intervals exceeding the per-window-declared N seconds without successful probes for a given server) so analyses spanning gap boundaries can declare the gap structure explicitly. — *owned by Storage module*
- **FR41:** A maintainer can track PR-review SLA conformance (48-hour acknowledgment, 7-day substantive review) and publicly tag PRs as `review-queued` during peak load; data-integrity PRs are exempt from triage and reviewed same-day.
- **FR42:** A maintainer can track launch-blocker checklist completion (the 25 items enumerated in §Project Scoping & Phased Development) and surface per-blocker status (cleared / pending / blocked).

## Non-Functional Requirements

This section consolidates measurable quality attributes scattered across the PRD into one testable inventory, plus six newly bounded items. Categories 5–7 cross-reference authoritative sections elsewhere; not restated to avoid drift.

### Performance

- **NFR1 — Timing precision at capture.** Monotonic-ns clock at probe receipt; wall-clock recorded separately and never used in computed-delta metrics. NTP-disciplined host with declared stratum per collection window.
- **NFR2 — Asyncio event-loop resolution.** Adequate for ~1–10 ms event handling at full-network scale (~150–500 concurrent connections). The methodology's signal floor (hundreds of ms between independent-backend pairs) is large compared to this measurement noise; tighter resolution is M4 Rust-rewrite territory, not M3.
- **NFR3 — Cold-start time-to-first-probe.** ≤ 60 seconds from daemon launch to first successful `blockchain.headers.subscribe` notification ingestion at full-network scale.
- **NFR4 — CI reproducibility self-test runtime.** ≤ 30 minutes for the bit-identical re-derivation pass on the M3 dataset window. If exceeded, sample-based verification with documented sampling parameters is the fallback.
- **NFR5 — Snowball convergence bound.** ≤ 24 hours per discovery sweep, after which discovery is suspended and resumed in the next scheduled sweep. Prevents unbounded recursive expansion.

### Reliability

- **NFR6 — Collection uptime.** ≥ 95% over any rolling 30-day window, measured both per server and at fleet aggregate. Uptime < 95% for 30 days triggers the IQ5 triage protocol (drop discretionary work, fix collection).
- **NFR7 — Reconnection discipline.** Per-server reconnection on disconnect via exponential backoff with documented base / cap / jitter parameters; reconnection events captured as connection-event rows (not silently retried).
- **NFR8 — Tor circuit-failure retry budget.** ≤ 3 retries per probe over ≤ 300 seconds, then mark probe-failed and continue collection without poisoning the longitudinal record (distinguishes Tor failure semantics from clearnet's persistent-connectivity assumption).
- **NFR9 — Planned-downtime accounting.** Planned downtime ≤ 24 h cumulative per rolling 30-day period is excluded from the NFR6 uptime calculation; planned downtime > 24 h cumulative counts against uptime. Distinguishes operational maintenance from collection failure.

### Scalability & Cost

- **NFR10 — Concurrent-connection scale.** 100–500 heterogeneous TCP / SSL sockets sustained at full-network scale (clearnet at M0–M1; clearnet + Tor at M2+).
- **NFR11 — Dataset-volume budget.** ~ 6 GB / year compressed at full-network scale. Compression algorithm and ratio documented per release manifest.
- **NFR12 — Operational cost envelope.** ≤ $500 / year total (VPS + storage + redundancy + Zenodo deposit + arXiv hosting). Cost overage triggers IQ5-equivalent triage and a Path 2 / Path 3 readiness check.
- **NFR13 — Memory footprint envelope.** ≤ 512 MB resident at the daemon process at full-network scale, leaving headroom for OS and supervision on $5 / month VPS-class hosts.
- **NFR14 — Storage migration timeline.** SQLite at M0–M1; TimescaleDB by M2, OR explicit demonstration that SQLite snapshot is sufficient for the M3 dataset window (latter requires §M2→M3 transition gate sign-off).

### Reproducibility & Determinism

- **NFR15 — Bit-identical contract.** Code hash + raw-input fingerprint → bit-identical derived dataset, OR documented per-column floating-point tolerance with bounds. Self-test ships with every dataset release; reviewers can re-run independently.
- **NFR16 — Schema discipline.** Forward-compatible-only migrations on the raw tier; deprecated columns retained until at least the next MAJOR dataset version (per §Dataset Requirements > Versioning contract).
- **NFR17 — PR-review SLA.** 48-hour acknowledgment, 7-day substantive review for non-data-integrity PRs; same-day review for data-integrity PRs. SLA conformance is a PR-stewardship metric (per §Success Criteria > Technical / Measurement Success).

### Compliance & Measurement Ethics

*Authoritative content: §Domain-Specific Requirements > Compliance & Regulatory. Bounds the measurement-ethics statement (rate-limiting policy, disclosure protocol, IRB-equivalent oversight), defamation-aware framing (cited-only intent attribution), open-science licensing (MIT / CC BY 4.0 / arXiv + peer-reviewed venue), statistical-validity carve-out (confidence intervals, multiple-testing correction, power analysis), and publication-standard reproducibility.*

### Documentation & Translation Parity

*Authoritative content: §Bilingual Parity. Bounds EN + ES synchronized parity for tool README, first-run guide, CLI `--help`, dataset schema documentation, dataset README, contribution guide, and issue templates; 14-day soft staleness SLA with public "translation pending" flag; 30-day frozen-rollback policy; identical 48 h / 7 d acknowledgment / review SLA on Spanish-language issues and PRs.*

### Integration Conformance

*Authoritative content: §Domain-Specific Requirements > Integration Requirements. Bounds `bitcoin-data` GitHub directory layout / CHANGELOG / README conventions; Zenodo DOI minting + cross-reference across versions; arXiv preprint workflow citing Zenodo DOI in abstract; `fork-observer` (b10c) reuse for tip tracking; `stale-blocks` dataset version pinning as canonical fork-race event source; Electrum protocol stable-RPC subset (`blockchain.headers.subscribe`, `server.version`, `server.features`, `server.banner`, `server.donation_address`, `blockchain.estimatefee(n)`, `blockchain.relayfee`, `mempool.get_fee_histogram`, `server.ping`).*
