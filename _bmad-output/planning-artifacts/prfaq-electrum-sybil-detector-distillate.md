---
title: "PRFAQ Distillate: electrum-sybil-detector"
type: llm-distillate
source: "prfaq-electrum-sybil-detector.md"
created: "2026-04-22"
purpose: "Token-efficient context for downstream PRD creation"
---

# PRFAQ Distillate — electrum-sybil-detector

Token-efficient context pack for the downstream PRD / implementation workflow. Every bullet is self-contained.

---

## Project identity and positioning

- **Project type:** Research output with supporting open-source tool. Non-commercial. Success metrics are citations, reference position in Bitcoin privacy research, and grant leverage — not adoption or revenue.
- **Owner:** HackNodes Lab (Ifuensan, primary author). Aligned with **Librería de Satoshi** mission to spread Bitcoin technology to Spanish-speaking developers and researchers. Not a solo operation — embedded in a network with institutional continuity and funding relationships (Btrust, HRF).
- **Primary press-release reader:** Bitcoin security research community — grant committees (OpenSats, HRF, Btrust, B4OS, BOSS Challenge, Brink), peer researchers (b10c / peer-observer orbit, Grundmann / TU Darmstadt, Fanti lineage, FC-venue Bitcoin-research community), privacy-focused technical press.
- **Deliverable ordering (locked):** open-source tool → longitudinal dataset → empirical paper. Tool is HackNodes Lab brand surface; moat is findings + reference position.
- **Three output scenarios (user's Push 3 analysis):** (1) clear clusters found — ideal, high probability, headline writes itself. (2) Weak signals, methodology + upper bound — most likely at M0/M3 scale. (3) True null — publishable as validated methodology + upper bound, but grant-unfriendly. All three are shippable under the current press-release framing with minor surgery for (3).

## Critical scope reframe ("Push 3")

- **Primary detection target:** shared backend infrastructure (multiple Electrum frontends served by a single Bitcoin Core). Measurable from fingerprint signals.
- **Intent attribution** (surveillance operator vs. legitimate cost-sharing hoster) is a **separate interpretive layer** — never conflated with the measurement. This is both analytically honest AND a legal/ethical protective posture.
- **Public-facing claims frame findings as clusters of shared backend infrastructure**, not as specific operator attributions.
- **Legal rule (Customer FAQ Q8):** cite published attributions from third parties (b10c issue #11, CoinDesk 2021 Chainalysis) as external context; never originate attributions in the paper. Network facts (ASN, geography, IP subnet) are presented as infrastructure properties, never as operator identification.

## Canonical provenance citation

- **b10c (0xB10C) issue #11** in his public project-ideas repository, opened July 2025, titled *"Can we spot public spy-Electrum servers run by Chainalysis?"*, tagged as a ₿OSS Challenge project. b10c detailed the exact methodology and wrote *"If I had the time to work on this, I'd write a custom tool."* Status still `Todo` at 2026-04-22 — 9 months of dwell time. This is the load-bearing citation for "why hasn't this been done."
- **CoinDesk 2021 leaked Chainalysis training materials** — documented precedent for SPV-surveillance + walletexplorer.com as undisclosed honeypot. Converts the problem framing from speculation to documented-pattern-extension.
- **Methodological ancestors to cite:** CoinScope, TxProbe (Delgado-Segura), Grundmann et al. (TU Darmstadt), Node-Probe (Essaid et al.). Verify specific authorship before citation.
- **Reusable infrastructure:** b10c's `fork-observer` already supports connecting to Electrum servers and tracking reported tips. Reuse, don't reimplement.

## Licensing (locked)

- **Detector code → MIT.** Aligns with Bitcoin ecosystem norms; zero adoption friction.
- **Dataset → CC BY 4.0.** Enforces attribution (which is the actual moat) while permitting reuse and derivative work.
- **Paper → arXiv preprint + target peer-review venue.**
- **User's articulated rationale:** *"La herramienta no es tu moat, los hallazgos sí."*

## Three-tier archival strategy (locked)

Pre-launch commitment — dataset will be citable, reproducible, and durable from day one across three independent hosts:

1. **`bitcoin-data` on GitHub** — b10c's community-standard repository for Bitcoin network measurement datasets (home of `stale-blocks`, `mining-pools`, `block-arrival-times`). Dual function: sustainability anchor AND positioning move (contribution into b10c's ecosystem rather than around it).
2. **Zenodo (CERN-hosted)** — persistent DOI + institutional archival guarantee independent of any GitHub account. Reserve DOI pre-launch, cite in paper abstract.
3. **arXiv** — technical paper preprint citing the Zenodo DOI. No reviewer gate; timestamps priority.

## Bilingual commitment (locked)

- **Paper:** English only (peer-review venue constraint).
- **Detector README, first-run guide, dataset documentation:** **English and Spanish.**
- **Dataset schema:** English-documented with Spanish glossary and column-by-column translation.
- **Issue templates, contribution guides:** accept both languages.
- **Maintenance cost:** accepted, aligned with Librería de Satoshi mission. Stale Spanish translation is worse than no translation — commit only if sustainable through dataset lifetime.

## Methodological spine (load-bearing for paper and FAQ)

- **Hardest technical problem:** sustained collection reliability at sub-second timing resolution across a network of operationally heterogeneous servers for months on end. NOT the fingerprinting or clustering — those are solved from literature.
- **Primary discriminator: fork-race block-notification timing.** When Bitcoin produces a stale-block event (per `bitcoin-data/stale-blocks`: 3–8/month in recent data, 13 events in first 3.5 months of 2026 including consecutive-height pairs on a single day), same-backend servers see the tip change simultaneously; different-backend servers scatter by Bitcoin P2P propagation delay. Each event is a binary natural experiment no software-similarity null can explain.
- **Vantage-robustness:** test is **variance of pairwise delta across many events**, not absolute single-event delta. Collector's path asymmetry is constant and drops out of variance. Shared-backend pairs show low variance; independent pairs show high variance.
- **Supporting backend-state signals:** mempool fee-histogram correlation (same-backend produces strongly correlated or identical `mempool.get_fee_histogram` output — pending empirical verification); synchronized downtime (correlated outages are backend-state events).
- **Frontend-configuration signals** (banner, version, donation address, ASN): treated as **confirming, not sufficient**.
- **Multi-signal threshold:** every published cluster must exceed threshold on **≥2 backend-state signals AND confirm on ≥1 frontend-configuration signal**. Single-signal matches are published as candidates for reproduction, not findings.
- **Baseline:** similarity distribution from servers known to be independent (different operators, different ASNs, different geographies) establishes the noise floor.
- **Single-vantage framing:** published findings are a **lower bound on shared-backend prevalence**. Multi-vantage expansion can only add clusters (catches geo/ASN-targeted operators invisible from single vantage); cannot remove clusters that passed vantage-robust tests.
- **Community multi-vantage from day one:** any researcher reproducing from a different ASN is a second vantage. The lower bound strengthens with every reproduction. Architectural, not roadmap-only.

## Scope decisions

- **In scope M0–M3:** clearnet public Electrum servers discoverable via seed lists (1209k.com/bitcoin-eye, Electrum wallet hardcoded defaults) + peer-to-peer expansion via `server.peers.subscribe`.
- **Deferred to M2:** Tor `.onion` servers — requires SOCKS5 connection layer and different correlation model (IP/ASN clustering doesn't apply to onion endpoints). Behavioral signals remain valid.
- **Conditional on M1 discovery:** I2P `.b32.i2p` servers. Not in scope for M0–M3 due to no observed public ecosystem. High-value target for M4: I2P's persistent destination identifiers enable long-term linkability of wallet users by Electrum server operators — a surveillance primitive Tor's rotating circuits do not provide. If M1 snowball discovery reveals I2P servers, scope expands.
- **Out of scope by construction:** private / unadvertised vendor-embedded Electrum servers (BlueWallet defaults that are publicly reachable are in; closed endpoints not announced to peer graph are out by construction). Separate research question requiring vendor disclosure or client-side traffic analysis.

## Milestones and timeline

- **M0 (current, ~20 servers):** initial collection at laptop scale + SQLite storage. Python asyncio for timing collection.
- **M1:** snowball discovery expansion via `server.peers.subscribe`. Validates network size (likely 50–100+ reachable clearnet + eventual Tor + conditional I2P).
- **M2:** Tor coverage + TimescaleDB/Postgres migration for production storage.
- **M3 (target launch milestone):** first-findings milestone; methodology paper + dataset + tool published together.
- **M4:** Rust rewrite of detector daemon (moved from original M2 suggestion); multi-vantage expansion.
- **M3+X:** follow-up paper with stronger findings (Phase 2 research program).

## Cost envelope

- **Baseline collection:** $15–25/month cloud (VPS + storage).
- **VPS redundancy for single-point-of-failure mitigation:** ~$10/month additional.
- **Total standing cost:** sub-$500/year.
- **Dataset volume:** ~500 MB/month raw behavioral signals after compression at full public network (~100 servers); ~6 GB/year. High-frequency signals downsampled after 90 days; block-notification events / feature payloads / discovery metadata retained indefinitely.

## Pre-committed decision thresholds

From IQ5 (operational triage):
- Data collection uptime <95% for 30 days → drop discretionary work, fix.
- Grant window within 30 days + application in hand → grant > community PR (except data-integrity PRs).
- Paper revision within 2 weeks + ship-blocker → paper > discretionary.
- Multiple non-negotiables peaking simultaneously → consider IQ9 Path 2 handoff earlier than 12-month threshold.

From IQ9 (exit paths):
- 6 months post-paper, no citations + no grant leads → **Path 1 (graceful shutdown).**
- 6–12 months post-paper, citations accumulating + no grants → **Path 3 (continue 6 more months, reassess).**
- 12 months post-paper, citations + no grants → **Path 2 (community handoff to b10c or secondary candidate).**
- Grant secured at any point → continue as Phase 2 research program.

From IQ4 (launch timing):
- Ship at M3 on scenario 2 — do NOT delay for scenario 1.
- Defensible delay only under triple-conjunction: scenario 3 (true null) + non-measurement-friendly venue + no land-grab pressure.

## Two-papers plan (locked)

- **M3 methodology paper:** first longitudinal Electrum measurement + shared-backend cluster findings (or upper bound under scenario 3). Reference paper for the field.
- **M3+X follow-up paper:** stronger findings from multi-vantage + extended collection; cites the M3 paper as reference methodology. Phase 2 grant funds this.
- This structure converts "ship weaker paper or delay" tension into "research program" that grant reviewers fund.

## PR review SLA (community stewardship commitment)

- **Acknowledge within 48 hours** (even "seen, will review this week").
- **Substantive review within 7 days.**
- **Public "review-queued" tagging during peak periods** — transparency buys more goodwill than silence.
- **Data-integrity PRs exempt** from all triage — same-day review regardless of other priorities.

## Peer-review venue hierarchy (IQ8)

- **arXiv preprint unconditional, launch-concurrent.** Upload before or with public release.
- **Primary: FC (Financial Cryptography).** Bitcoin-research-community native; Biryukov/Meiklejohn/Bonneau lineage; audience overlap with grant funders is highest.
- **Backup: PETS (Privacy Enhancing Technologies Symposium).** Premier privacy venue but recent (2023–2025) editorial drift toward federated learning / secure computation / ML-privacy — Bitcoin-specific work less prominent. Submit leaning on surveillance-infrastructure-detection angle rather than Bitcoin-specificity.
- **Tertiary: IMC (Internet Measurement Conference).** Rigorous, measurement-native. Electrum-specific may read as niche; submit only if FC/PETS reviewer feedback suggests IMC fit.
- **Final fallback: technical report + arXiv + dataset DOI + `bitcoin-data` contribution.** Not failure; venue miss. Grant-narrative cost ≈ one cycle of slower recognition, not project-ending.
- **NOT targeting:** USENIX Security, S&P — optimize for novelty over methodology-first; scenario-2 risk.

## Launch-blocker validation checklist (must complete before public release)

1. Verify `bitcoin-data/stale-blocks` cadence claim (3–8/month, 13 events first 3.5 months 2026 with consecutive-height pairs).
2. **Empirically verify fee-histogram behavior** — run two ElectrumX frontends against one Core, diff `mempool.get_fee_histogram`. If not identical, soften to "strongly correlated" language. **Highest priority — methodology depends on this.**
3. Verify 500 MB/month compressed signal volume at full network scale (extrapolation from README 20-server figure; run actual M0 test).
4. Verify $5/month VPS claim against planned Python asyncio daemon profile.
5. Verify "under an hour" Docker install claim when first-run guide exists.
6. Verify BlueWallet default-server publicly-reachable claim (Q6 example); swap if not publicly reachable.
7. Verify b10c issue #11 URL + title match + status still `Todo`.
8. Verify b10c fork-observer Electrum-support claim.
9. Verify methodology-ancestor citations: CoinScope (author + venue), TxProbe (Delgado-Segura), Grundmann et al. (specific paper).
10. Locate CoinDesk 2021 article on Chainalysis/walletexplorer.com; verify URL + claims.
11. Pre-launch: open discussion with b10c on `bitcoin-data` dataset contribution.
12. Pre-launch: create Zenodo record, reserve DOI, cite in paper abstract.
13. Pre-launch: upload arXiv preprint citing Zenodo DOI.
14. Pre-launch: verify AS24940 (Hetzner) style-rule example; swap if Cluster 7 example misleading.
15. Verify Python asyncio timing resolution (~1–10ms) adequate in actual M0 collection.
16. Verify 1209k.com "~90–95% of listed servers maintain >90% uptime" claim against actual historical data.
17. **Clarify I2P "reveals initiator's address" phrasing** — likely should be "persistent destination identifiers enable long-term linkability" for technical accuracy.
18. Verify IQ3's 9-month b10c-Todo dwell time still accurate at launch date; update if launch slips.
19. **Critical-path:** schedule b10c socialization conversation covering framing, `bitcoin-data` contribution, Path 2 handoff optionality. Critical path, not nice-to-have. **Priority: highest alongside #2.**
20. Verify FC acceptance patterns for methodology-first / scenario-2 papers (Biryukov/Meiklejohn/Bonneau lineage 2024–2026).
21. Verify PETS 2023–2025 editorial mix; reconsider ordering if PETS still publishing Bitcoin work.
22. Paper must include **measurement-ethics section** (OpenSats/PETS reviewer expectations: rate-limiting, disclosure, IRB-equivalent).
23. Paper must include **threat model and known evasion paths** section per IQ7.
24. Replace `[Peer researcher, Bitcoin privacy]` placeholder with real attribution (candidates: b10c-orbit researcher, cited FC/PETS Bitcoin-privacy author, or Librería de Satoshi-network researcher).
25. Replace `[City, Launch Date]` placeholder in press release before publication.

## Open questions and unknowns (not yet committed; for PRD downstream)

- **Fee-histogram empirical behavior** — bit-identical or correlation-threshold? Answer changes one of three primary discriminators' strength. (Launch-blocker #2.)
- **Actual M0 network size via snowball discovery** — 20 stated, real number unknown until M1. Affects statistical-power calculations. (Launch-blocker #3.)
- **b10c relationship outcome** — warm collaboration / lukewarm parallel contribution / cold. Affects IQ3 and IQ9 Path 2 simultaneously. (Launch-blocker #19.)
- **Grant landscape at launch date** — OpenSats / HRF / Btrust / B4OS active cycles in the M3-launch window.
- **HackNodes Lab HQ city + realistic launch date** — drives press-release placeholders.
- **Co-maintainer or collaborator call plan** — addresses IQ6 solo-capacity risk; not yet concrete.
- **Phase 2 pitch outline** — committed in IQ6 as "begins before first paper cites." No specific plan.
- **Paper outline** — threat-model section, measurement-ethics section, related-work section all committed but not drafted.

## Cracks in the foundation (must address deliberately — from Verdict)

- **Solo-researcher capacity (IQ6)** is the single point of failure. Architectural defenses do not protect against Ifuensan's bandwidth running out. **Mitigation options:** (a) pre-defined 6-month post-paper "collaborator call" plan naming candidate partners and workstreams, OR (b) pre-identified concurrent co-maintainer from the Librería de Satoshi network or university group. Without (a) or (b), the capacity risk remains structurally unmitigated.
- **b10c relationship is SPOF for TWO load-bearing questions (IQ3 differentiation + IQ9 Path 2).** **Mitigation:** pre-identify a secondary Path 2 candidate — a specific university measurement group pre-willing to take on dataset stewardship if the b10c path fails. Make it a concrete entity, not a generic "a university group."
- **Scenario 3 + b10c-cold + Phase-2-unfunded triple-hit** is the realistic worst-case. Architecture catches the fall (release exists, contribution citable) but research program stalls at one paper. **Mitigation:** explicit contingency script — Path 1 graceful shutdown + sustained bilingual Spanish community engagement through Librería de Satoshi + re-enter research on different question with the methodology paper as credentialing artifact. Capture before future-Ifuensan must invent it under stress.
- **Press release has `[City, Launch Date]` and `[Peer researcher]` placeholders.** Execution reminder, not concept crack. Do not publish without launch-blocker checklist cleared.

## Rejected framings (for PRD context on why choices were made)

- **"Finding-led" headline** (paper-forward): rejected — demoted the tool and committed to "first empirical map," too load-bearing if launch-day findings are scenario-2 weak signals.
- **"Tool-led without findings" headline**: rejected — naked tool announcement cedes "first finding" narrative position to whoever runs the tool first.
- **"First empirical map" phrasing in opening paragraph**: softened to "first empirical findings on shared-backend clusters," which survives weak-signal scenarios.
- **"Used to surveil wallet users at scale" language in opening**: rejected — commits to surveillance framing in first sentence. Replaced with "wallet surveillance" as a speculated claim the release *replaces* with measurement (Push 3 reframe).
- **List-form solution paragraph** ("Grant reviewers → X; Peer researchers → Y"): rejected in favor of argument-form for narrative voice. List version saved as alternate register.
- **L1 leader quote alone** (pure mission-framed): rejected as too generic. Merged with L2 (honest-about-motivation "small lab") for final.
- **L3 leader quote** (slogan-style "privacy questions settled by whoever tells the best story"): rejected — too quotable-engineered, risked sounding critical of the community.
- **C1 first-person community quote**: kept substance, shifted to third-person register with "vantage points" term of art per user preference.
- **C2 wallet-maintainer angle and C3 grant-reviewer angle quotes**: saved as alternate voices for secondary launch materials; not canonical press-release quotes.
- **PETS as primary venue**: rejected at Stage 4 — user flipped to FC primary based on Bitcoin-research-community audience overlap. PETS editorial drift away from Bitcoin work (2023–2025) confirmed rationale.
- **Rust M2 rewrite**: moved to M4 per user revision — matches tool-first-not-polish ordering.
- **"Collaborator-call fast track" as explicit Q6 mitigation paragraph**: user locked Q6 without it; risk remains structurally unmitigated. Flagged as verdict-level crack.
- **Customer FAQ "differentiation from b10c/peer-observer/Grundmann"**: dropped from Customer FAQ, migrated to Internal FAQ IQ3 where stakeholder-skeptic positioning belongs.
- **Customer FAQ candidates not included:** measurement ethics (migrated to paper section + launch-blocker #22), peer-review venue (migrated to Internal FAQ IQ8), chain-of-custody (not raised), adversarial evasion (migrated to Internal FAQ IQ7), non-shared-backend benign interpretations (addressed in Push 3 scope reframe).

## Downstream work for PRD

- **Architecture spec:** daemon design (asyncio for M3, Rust for M4), storage schema (SQLite M0 → TimescaleDB M2), signal-extraction pipeline, clustering algorithm (likely DBSCAN or hierarchical on weighted similarity matrix per README).
- **Discovery module:** seed-list ingestion + snowball via `server.peers.subscribe` + ASN diversity handling for ElectrumX's subnet-similarity anti-sybil.
- **Analysis module:** fork-race event ingestion from `bitcoin-data/stale-blocks`, per-pair variance computation, multi-signal threshold evaluation, baseline similarity distribution from known-independent servers.
- **Dataset publication module:** monthly Parquet snapshots + SQL dump + Zenodo DOI minting + `bitcoin-data` GitHub contribution flow.
- **Documentation plan:** bilingual (EN + ES) README, first-run guide, dataset schema + Spanish glossary, issue templates accepting both languages, contribution guide with PR-review SLA.
- **Paper structure:** abstract + intro + background (incl. CoinDesk 2021 precedent, b10c issue #11 provenance) + threat model + methodology (signal hierarchy + multi-signal threshold + baseline) + results (clusters or upper bound) + related work (CoinScope / TxProbe / Grundmann / Node-Probe) + measurement ethics statement + known evasion paths + limitations (single vantage, M0 scale) + conclusions.
- **Pre-launch execution plan:** b10c socialization conversation → empirical fee-histogram verification → launch-blocker validation sweep → Zenodo DOI + arXiv preprint + `bitcoin-data` contribution → press release date/city finalization → community quote attribution → launch.
