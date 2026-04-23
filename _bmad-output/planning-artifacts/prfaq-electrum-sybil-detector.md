---
title: "PRFAQ: electrum-sybil-detector"
status: "complete"
created: "2026-04-22"
updated: "2026-04-22"
stage: "5-verdict"
concept_type: "research-output-with-open-source-tool"
inputs:
  - README.md
  - docs/papers/electrum_servers_insights.md
  - docs/papers/bitcoin_topology_insights.md
---

# "How many public Electrum servers share backend infrastructure?" HackNodes Lab releases `electrum-sybil-detector` — the open-source toolkit, longitudinal dataset, and first empirical findings behind the answer.

## A reproducible measurement pipeline for the Bitcoin security research community — built to treat shared-infrastructure detection as measurable, and surveillance attribution as a separate interpretive layer.

**[City, Launch Date]** — How many public Electrum servers share backend infrastructure? Bitcoin security researchers have asked this for years — the longitudinal behavioral dataset to measure it didn't exist. Today HackNodes Lab releases `electrum-sybil-detector`: the first open-source toolkit for fingerprinting public Electrum servers over time, the dataset it produced, and the first empirical findings on shared-backend clusters — replacing speculation about wallet surveillance with measurement.

It is taken for granted in the Bitcoin privacy community that parts of the public Electrum server network are operated by surveillance firms. Wasabi developers have claimed it; Samourai community forensics have pointed at it; researchers have proposed investigating it. But every such claim traces back to the same foundation: forum posts, isolated observations, and informed conjecture. The empirical dataset that would turn conjecture into finding — a continuous, multi-month behavioral fingerprint of the entire public Electrum network — has not been publicly collected, because building it requires sustained infrastructure a solo researcher cannot stand up on a short grant cycle. The cost of that absence compounds: wallet maintainers prune default server lists from hearsay instead of data, researchers cannot compare SPV-server behavior against existing Bitcoin P2P measurements, and policy discussions about infrastructure-layer surveillance proceed without empirical ground truth.

The release closes the gap it describes. Grant reviewers can now fund this line of research against a live, running measurement program — not a plan. Peer researchers can cite, reproduce, and extend an empirical dataset where before they could only cite forum posts. Privacy journalists covering surveillance infrastructure have a document to link to. Wallet maintainers curating default server lists can use data instead of hearsay. And the question HackNodes Lab set out to answer — how much of the public Electrum network sits on shared backends — becomes, for the first time, a measured quantity the community can argue about on evidence.

> "The Bitcoin privacy community has been carrying this question for years, and every answer rested on the same small pile of forum posts. We're a small lab, and what we wanted to build was a piece of infrastructure the next ten researchers could stand on. Whether the first findings turn out to be dramatic or mundane matters less than the fact that the next argument about Electrum server surveillance can be about what the data means — not whether there is any."
> — Ifuensan, HackNodes Lab

### How It Works

The release gives researchers three artifacts. A **detector** — a self-hostable daemon that connects to the public Electrum server network and records behavioral signals continuously. A **dataset** — those signals, updated on a rolling basis, with full reproducibility metadata and a cited DOI. And a **findings paper** — HackNodes Lab's reading of the first months of collection, with candidate shared-backend clusters, confidence bounds, and methodology notes. A researcher reproducing the work clones the detector and runs it against an independent vantage point; their results become a cross-check on the lab's. A researcher using only the data queries the hosted dataset or downloads a snapshot archive. A journalist citing the work cites the paper and the dataset DOI. Every claim in the release traces back to a row in the data.

> "Many researchers have been quoting 'Wasabi developers claimed so' in their own articles for three years, because nothing better existed. Now there is a dataset to download, a methodology to run against other vantage points, and a reference to put in a bibliography. For this line of work, that's the difference between speculation and measurement."
> — [Peer researcher, Bitcoin privacy — real attribution to be sourced before launch]

### Getting Started

The detector is on GitHub under the **MIT license**, with a one-command Docker install and a first-run guide calibrated for a laptop-scale deployment. The dataset is released under **CC BY 4.0** with a cited DOI, snapshot archives for paper reproducibility, and a SQL endpoint for interactive queries. The findings paper is available as a preprint with the full methodology, confidence analysis, and related-work comparison against Bitcoin P2P measurement prior art. Researchers interested in contributing additional vantage points, auditing the methodology, or extending the signal set are invited to open issues on the repository or contact the lab directly.

---

<!-- coaching-notes-stage-2 -->
## Stage 2 Coaching Notes

**Headline framings considered and rejected:**
- "Finding-led" (paper-forward): demoted the tool and committed to "first empirical map" — too load-bearing if launch-day findings are scenario-2 weak signals.
- "Tool-led without findings": naked tool announcement; cedes "first finding" narrative position to whoever runs the tool first.
- "Question-led only" (without the tool anchor): elegant hook but under-sold the tool, contradicting chosen ordering.
- **Accepted:** question-hook + tool-anchor + tool→dataset→findings stack with "measurement, not speculation" closer. Earns both scenario-1 and scenario-2 honesty budgets.

**Opening-paragraph framings considered and rejected:**
- "Used to surveil wallet users at scale" — commits to surveillance framing in the first sentence; replaced by "wallet surveillance" as a speculated claim the release replaces with measurement. This is a direct application of the user's Push 3 scope reframe (shared-infra is measurable; attribution is interpretive).
- "First empirical map" phrasing in Opening — softened to "first empirical findings on shared-backend clusters," which survives weak-signal scenarios.

**Problem-paragraph framings considered and rejected:**
- Pure grievance-stack (grant-language / citation-chain / hearsay-curation) — moved into subordinate role as illustration, not the paragraph's spine.
- Pure opportunity-cost frame (read as dry/abstract for non-grant readers) — merged as the "cost of that absence compounds" pivot.
- **Accepted:** "everyone-knows-no-one-can-prove" opening + infrastructure-cost-of-gap explanation + three-pain downstream compound close.

**Solution-paragraph framings considered and rejected:**
- List-form ("Grant reviewers → X; Peer researchers → Y; Maintainers → Z") — rejected in favor of argument-form for better narrative voice; list version saved as an alternate register.
- Self-serving "fund this line of research" language flagged as mild risk; retained because a PRFAQ is an honest-pitch document.

**Leader-quote framings considered and rejected:**
- Pure mission-framed (L1): earnest but slightly generic.
- Slogan-style (L3): press-quotable but risked sounding engineered + critical of the community.
- **Accepted:** L1+L2 merge — "carrying this question for years" + "small lab" honest self-positioning + "dramatic or mundane" scenario-2 hedge + "what the data means, not whether there is any" close.

**Community-quote framings considered and rejected:**
- First-person throughout (intimate but less generalizable).
- Wallet-maintainer angle (C2) — useful as secondary voice, not canonical press-release quote; save for web launch post.
- Grant-reviewer angle (C3) — too hard to source a real attribution pre-publication.
- **Accepted:** C1 in third-person register with "vantage points" term of art.

### Licensing strategy (locked this stage)

- **Detector code → MIT.** Aligns with Bitcoin ecosystem norms (Bitcoin Core is MIT). Zero adoption friction for wallet maintainers, ElectrumX contributors, or research teams who might integrate. User rationale (direct quote): *"La herramienta no es tu moat, los hallazgos sí."*
- **Dataset → CC BY 4.0.** Enforces attribution (which is the actual moat — citations back to HackNodes Lab drive reference position) while allowing derivative work and redistribution. Compatible with academic reuse norms and FAIR data expectations.
- **Paper → preprint on arXiv + venue submission.** License at venue level (typically CC BY or venue-dependent).
- **Strategic frame:** permissive on code + data (maximize adoption and citation surface) while reputation and reference position accrue to the interpretive layer (paper + methodology + HackNodes Lab's ongoing readings of the evolving dataset).

### Out-of-scope details mentioned during drafting (survived for later stages)

- **Real quote attribution:** `[Peer researcher, Bitcoin privacy]` is a PRFAQ placeholder. Before launch, source a real quote from someone in the b10c / peer-observer / Grundmann / Electrum-maintainer orbit. Action item for Stage 5 verdict section.
- **Launch-day honesty validation:** the phrase "has not been publicly collected" (problem paragraph) is load-bearing. Re-verify via live web search + direct repo checks on b10c and peer-observer immediately before launch. If anything has been published since, rewrite. *Flagged as launch-blocker validation.*
- **City placeholder:** `[City, Launch Date]` — HackNodes Lab HQ city, date TBD.
- **Vantage-point expansion:** the community quote and How-It-Works both gesture at multiple-vantage reproducibility; this aligns with the README's M4 milestone (multi-AS collection). Deliberately not overpromised at launch.
- **Storage detail leak check:** "SQL endpoint for interactive queries" in Getting Started implies TimescaleDB/Postgres backing (README M2). Acceptable technical register for the audience; does not overspecify.

### Differentiators explored but not surfaced in the press release

- **ElectrumX anti-sybil already exists (subnet-diversity limits in `server.peers.subscribe`)** — therefore any sophisticated operator is forced across ASNs, turning ASN-correlation into an inherent fingerprint. Strong technical story but too in-the-weeds for the press release. Save for the internal FAQ / paper.
- **Methodological ancestry:** Node-Probe (99% precision / 98% recall), TxProbe, ADDR-marker as the Bitcoin P2P analogs HackNodes Lab is transferring to Electrum. Save for internal FAQ "how is this different from prior work."
- **Block-notification timing during fork races** as the single highest-confidence signal. Save for the paper.
- **Intent-attribution-as-separate-layer** as a *legal and ethical* posture (per web-researcher risk note), not just analytical. Save for internal FAQ "what's the legal exposure."

### Stage-2 exit state

Press release is complete: headline, subhead, opening, problem, solution, leader quote, How It Works, community quote, Getting Started. The release describes a gap, fills it with three artifacts stacked by priority, and frames the contribution as replacing speculation with measurement — not as exposing specific operators. Ready for Stage 3 (Customer FAQ: devil's-advocate questions from the reader's perspective).

---

## Customer FAQ

### Q1: Why hasn't this been done before — what did you figure out that others haven't?

**A:** The idea is not new — and its author said so explicitly. In July 2025, b10c (0xB10C) opened issue #11 in his public project-ideas repository, titled *"Can we spot public spy-Electrum servers run by Chainalysis?"*, detailing the exact methodology: connect to public Electrum servers, record block notification timing during forks, compare fee histograms, track downtime, fingerprint metadata. He tagged it as a ₿OSS Challenge project for the community to pick up, writing: *"If I had the time to work on this, I'd write a custom tool."* As of today, the issue status is still "Todo." Nobody has taken it on.

The analytic foundations are not the blocker. Pairwise timing correlation, protocol fingerprinting, and behavioral clustering are well-established from a decade of Bitcoin P2P topology work (CoinScope, TxProbe, Grundmann et al.). b10c's own fork-observer already supports connecting to Electrum servers and tracking which block they report as tip. The gap is **infrastructure endurance**: the fork-race discriminator requires continuous sub-second sampling across the full public Electrum network for months. That is a modest cloud cost (~$15–25/month), but it is operational overhead that academic incentive structures do not reward — grant cycles prize novel methodology, not *"we ran the obvious measurement for six months."*

Meanwhile, the threat is not theoretical. Leaked Chainalysis training materials, reported by CoinDesk in 2021, confirmed the company runs Bitcoin nodes to capture SPV wallet data and operated walletexplorer.com as an undisclosed honeypot linking IP addresses to Bitcoin addresses. Extending this to Electrum servers — which receive address queries directly — is the obvious lower-cost next step.

HackNodes Lab sits in the gap by construction: a security-research lab whose brand is infrastructure-led measurement, small enough that long-horizon operational work is competitive advantage rather than academic cost, and embedded in an ecosystem (B4OS, BOSS Challenge, Btrust, HRF) that funds exactly this kind of persistent public-good monitoring.

---

### Q2: How do you distinguish real sybil clusters from false positives — two independent servers that just happen to run the same software?

**A:** The concern is correct — two vanilla ElectrumX servers running the same version produce similar banners, similar default fee estimators, and similar protocol strings, none of which is cluster evidence. The methodology discriminates "shared backend" from "same software, different backends" by weighting **backend-state signals** (what the backing Bitcoin Core does) above **frontend-configuration signals** (what the ElectrumX software does).

The cleanest discriminator is **block-notification timing during fork races**. When Bitcoin produces a stale-block event, servers sharing a backend see the chain tip change at the same instant; servers on independent backends scatter by P2P propagation delay. The `bitcoin-data/stale-blocks` corpus shows 3–8 stale blocks per month in recent data (13 events in the first 3.5 months of 2026, including consecutive-height pairs on a single day), providing natural experiments at roughly weekly cadence — sufficient for statistical clustering within weeks of collection start. Each event is a binary natural experiment that no software-similarity null can explain.

Supporting backend-state signals include **mempool fee-histogram correlation** (backend state, not software state — independent-backend frontends produce statistically distinguishable histograms; same-backend frontends produce strongly correlated or identical output, pending empirical verification) and **synchronized downtime** (a backend-state event, not a software event).

Frontend-configuration signals (version, banner, donation address, ASN) are treated as **confirming, not sufficient** — no cluster is published on their strength alone. The study establishes a baseline similarity distribution from servers known to be independent (different operators, different ASNs, different geographies) to set the noise floor, and requires every published cluster to exceed threshold on **at least two backend-state signals AND confirm on at least one frontend-configuration signal**. Single-signal matches are reported as candidates for reproduction, not findings.

---

### Q3: Your vantage point is a single node on a specific ASN. Isn't most of what you're measuring an artifact of YOUR network position rather than a property of the servers themselves?

**A:** Single-vantage is a real limitation and the release states it openly. The primary discriminator — block-notification timing across many fork-race events — is **vantage-robust in the way that matters**, for a specific methodological reason: the test is not the absolute pairwise delta in a single event, but the **variance** of that delta across many events. The collector's path asymmetry between two servers is an approximately constant offset (network topology doesn't shift event-to-event), so it drops out of the variance calculation. What remains is driven entirely by backend behavior: shared-backend pairs show low scatter (consistent timing, same Core), independent-backend pairs show high scatter (Bitcoin P2P propagation is stochastic per event). The `bitcoin-data/stale-blocks` cadence of 3–8 events per month provides the N needed for variance estimation within weeks of collection.

The same vantage-robustness principle applies to fee-histogram correlation and synchronized-downtime detection: both are evaluated as time-series correlations, not single-point snapshots, so collector-specific artifacts drop out. Frontend-configuration signals (banner, version, donation address, ASN) are vantage-independent by construction.

What *is* genuinely vantage-dependent: **geo-targeted or ASN-targeted server responses** — a server that serves different data to different geographies. One vantage cannot see this, and it is exactly the reason multi-vantage is on the roadmap.

The honest framing: **single-vantage findings are a lower bound on shared-backend prevalence.** Multi-vantage expansion can only add clusters (catching geo- or ASN-targeted operators) — it cannot remove clusters that already passed the vantage-robust tests.

The release enables **community multi-vantage from day one**: every researcher who reproduces the detector from a different ASN is a second vantage, and their data cross-checks the hosted dataset. The lower bound strengthens with every reproduction.

---

### Q4: What happens to the dataset if HackNodes Lab loses funding or moves on?

**A:** The question is real — plenty of research datasets have decayed because they depended on a single researcher to keep paying a cloud bill. The release is structured to make that failure mode non-terminal.

**Licensing defuses single-point-of-failure risk.** MIT for the detector code, CC BY 4.0 for the dataset. Anyone — a university group, a wallet maintainer, a grant-funded peer — can fork and mirror without permission. Attribution flows back to HackNodes Lab by license terms, not by goodwill.

**Collection is architecturally replicated from day one.** Every researcher who reproduces the detector from a different vantage point is a second collection node. A dataset already running on multiple independent machines does not vanish when one of them stops paying.

**HackNodes Lab is not a solo operation.** Alignment with Librería de Satoshi embeds the project in a Bitcoin-education network with its own institutional continuity, audience, and funding relationships (Btrust, HRF). The funding landscape favors persistence: B4OS, BOSS Challenge, OpenSats, and Brink fund long-horizon public-good infrastructure monitoring. The tool, the dataset, and planned follow-on research questions share the same collection backbone, making sustained support more efficient than one-off project grants.

**Pre-launch commitment:** before public release, HackNodes Lab will publish the dataset through a three-tier archival strategy. First, `bitcoin-data` on GitHub — the community-standard home for Bitcoin network measurement datasets (stale-blocks, mining-pools, block-arrival-times), maintained by the same researcher who proposed this project. Second, Zenodo (CERN-hosted) for a persistent DOI and institutional archival guarantee independent of any GitHub account. Third, arXiv for the technical paper citing the dataset by DOI. The dataset will be citable, reproducible, and durable from day one — across three independent hosts, none of which depends on HackNodes Lab staying funded.

---

### Q5: Does this cover Tor `.onion` Electrum servers?

**A:** At launch, clearnet only. Tor `.onion` coverage is deferred — it requires a separate SOCKS5 connection path and a different correlation model, since IP and ASN clustering don't apply to onion endpoints. Behavioral signals (timing, fee histograms, banners, protocol versions) remain valid, so the detector's architecture is built to accommodate Tor in a later phase. The clearnet question is itself unmeasured and worth answering in isolation; Tor is a complementary cohort, not a replacement. If you're specifically asking the Tor-only sybil question, it's a distinct research problem this release doesn't attempt to answer — and an explicit open invitation for collaboration.

---

### Q6: What about private / embedded Electrum servers (BlueWallet, Sparrow, Green)?

**A:** The detector measures what the public Electrum network reveals through standard discovery: seed lists (1209k.com/bitcoin-eye, Electrum wallet defaults) plus peer-to-peer expansion via `server.peers.subscribe`. Vendor endpoints that happen to be publicly reachable (e.g., BlueWallet's default servers) appear in the dataset like any other public server. Truly private endpoints — servers a vendor operates but does not announce to the peer graph — are outside the dataset by definition. That's a real limitation, not a bug: the research question this release answers is the surveillance exposure of *public-facing* SPV infrastructure. Closed-vendor infrastructure is a separate question requiring vendor disclosure or client-side traffic analysis.

---

### Q7: What's the realistic infrastructure bar to reproduce this from a different vantage?

**A:** Reproducing the collection from scratch requires an always-on node — a $5/month VPS is sufficient at M0 scale. A reproducer does not need to wait three months for statistical power: the public dataset is already running, so a fresh vantage produces an *independent* cross-check dataset immediately, which can be compared against the hosted one with the provided analysis scripts. A grad student with Docker installed and a basic cloud account can replicate the full pipeline in under an hour and will have comparable data to cross-reference within a week. The three-month statistical threshold applies only to building a standalone dataset from zero; it does not gate reproduction.

---

### Q8: Does publishing sybil-cluster findings create legal exposure for HackNodes Lab?

**A:** The release names no operators. Every published cluster is described as a set of servers sharing backend infrastructure — identified by the multi-signal statistical threshold defined in Q2 — and nothing more. Intent attribution (surveillance operator vs. a hosting provider consolidating backends for cost reasons vs. a wallet vendor running multiple regional frontends) is explicitly treated as an interpretive layer separate from the measurement, and the paper publishes no intent attributions. Readers who wish to correlate the clusters with public information about ASN ownership, hosting providers, or known corporate infrastructure are welcome to do so — that is their interpretation, not HackNodes Lab's.

Where third-party sources have publicly attributed specific servers to named entities — through corporate disclosures, leaked documents, or investigative reporting — the paper may cite those attributions as external context. The distinction is between **citing a published attribution (low risk) and originating one (high risk)**. HackNodes Lab does the former, never the latter.

Where the paper reports observable network facts about clusters — such as ASN, geography, or IP subnet — these are presented as properties of the infrastructure, not as identification of the operator behind it. *"Cluster 7 resolves to three IPs in AS24940"* is a network measurement. *"Cluster 7 is operated by Hetzner's customer X"* is an attribution the paper does not make.

This posture is not only a legal choice; it reflects what the data can actually support. The discriminator proves that servers share a backend. It does not, and cannot, prove who operates that backend or why. Naming specific operators would require evidence outside the measurement — whistleblower documents, leaked materials, subpoena-obtained records — that this project does not have and does not claim to have.

The precedent for why the pattern is worth measuring at all — Chainalysis's confirmed SPV-node surveillance and walletexplorer.com honeypot, documented in CoinDesk's 2021 reporting — is cited as public background for the research question, not as attribution of specific findings. Anyone threatening defamation would first have to explain what claim the paper makes about them that the paper does not, in fact, make.

---

### Q9: What does the dataset actually look like — GBs? TBs? Can I download it?

**A:** Volume is deliberately modest. At the full public network scale (~100 clearnet servers), the detector records roughly 500 MB of raw behavioral signals per month after compression — about 6 GB per year. High-frequency signals (ping latency, mempool histograms) are downsampled after 90 days; block-notification events, feature payloads, and discovery metadata are retained indefinitely. The dataset is published as monthly Parquet snapshots (queryable in DuckDB, pandas, or Spark without a database) plus a full SQL dump of the entire historical corpus. A single `curl` pulls the latest monthly archive; the full lifetime dataset fits on a standard laptop. The hosted SQL endpoint lets researchers query without downloading anything.

---

### Q10: Is this documented in a language I can read?

**A:** The paper is published in English (as required by target peer-review venues). The detector's README, first-run guide, and dataset documentation are published in both **English and Spanish**. HackNodes Lab is aligned with Librería de Satoshi's objective to spread Bitcoin technology and make it more accessible to Spanish-speaking developers and researchers — a constituency disproportionately underserved in the global privacy-measurement landscape. Issue templates and contribution guides accept both languages. The dataset itself is schema-documented in English with a Spanish glossary and column-by-column translation. For researchers working primarily in Spanish or publishing in LATAM venues, this release is fully accessible without translation.

---

<!-- coaching-notes-stage-3 -->
## Stage 3 Coaching Notes

**Question selection and scope decisions:**
- Dropped "differentiation from b10c / peer-observer / Grundmann" from the Customer FAQ — substance migrated to Stage 4 Internal FAQ where stakeholder-skeptic positioning questions fit better.
- Added "data volume / storage" (Q9) as a practical-trust signal that also demonstrates rigor.
- Added "language / accessibility" (Q10) at user direction — converted into a strategic-positioning answer grounded in Librería de Satoshi alignment, not defensive footnote.
- Dropped candidates not raised: measurement ethics, peer-review venue, chain of custody, paper-vs-data interpretation, adversarial evasion, non-shared-backend benign interpretations. Several of these migrate to Internal FAQ.

**Gaps surfaced by customer questions and decisions made:**

| Gap | Decision | Category |
|---|---|---|
| Fork-race variance requires stable network topology at collector | Implicit assumption, to be stated explicitly in paper methodology section | Accepted trade-off |
| Fee-histogram determinism across frontends sharing a backend | Flagged as "pending empirical verification" in Q2 — must be validated pre-launch | Launch-blocker validation |
| Stale-block cadence (3–8/month) claimed from `bitcoin-data/stale-blocks` | Validated by user: 13 events in first 3.5 months of 2026 including consecutive-height pairs on a single day | Resolved |
| Tor `.onion` coverage | Deferred to later phase; architecture supports it, launch does not | Accepted scope limitation, openly stated |
| Private / embedded vendor Electrum servers | Out of scope by construction (peer-graph invisibility); framed as "different research question" | Accepted scope limitation |
| Single-vantage bias | Methodology is variance-based, therefore vantage-robust; geo/ASN-targeted responses acknowledged as genuinely vantage-dependent and addressed by multi-vantage roadmap + community reproduction from day one | Resolved via reframe |
| Sustainability when HackNodes Lab funding ends | Three-tier archival strategy: `bitcoin-data` GitHub (b10c repo) + Zenodo DOI + arXiv paper | Launch-blocker with concrete commitments |
| Legal exposure from naming operators | "Cite published attributions, never originate new ones"; ASN/geography as network facts, not operator identification | Resolved via legal style rule |
| Bilingual documentation maintenance cost | Commitment accepted; Spanish glossary for dataset schema + bilingual contribution guides | Accepted maintenance cost, aligned with mission |

**Trade-offs made:**
- **Single-vantage is a lower bound, not a ceiling.** This framing converts a weakness into a floor — the strongest rhetorical move in the whole FAQ. Stage 4 must NOT walk this back.
- **No operator naming, ever, from the paper itself.** Hard constraint. The paper cites b10c's issue #11 and CoinDesk 2021 as published third-party attributions, but originates zero new ones.
- **Multi-vantage is community-enabled from day one, not an M4-only feature.** Architectural choice with press-release, customer-FAQ, and sustainability implications all reinforcing each other.
- **Three-tier archival is the sustainability answer.** No "we'll figure it out later" — pre-launch deliverable.

**Launch-blocker validation checklist (compiled from Stage 3):**
1. Verify `bitcoin-data/stale-blocks` cadence claim (3–8/month, 13 in first 3.5 months of 2026 with consecutive-height pairs).
2. Empirically verify fee-histogram behavior on two ElectrumX frontends sharing one backend (identical vs. strongly correlated).
3. Verify 500 MB/month compressed signal volume at full public network scale — extrapolation from README's 20-server/50–100 MB figure; run actual M0 test.
4. Verify `$5/month VPS` claim against planned Rust daemon CPU profile.
5. Verify "under an hour" Docker install claim when first-run guide exists.
6. Verify BlueWallet default-server publicly-reachable claim (Q6 example) — if not publicly reachable, swap example.
7. Verify b10c issue #11 URL, status still "Todo", title match.
8. Verify b10c fork-observer Electrum-support claim.
9. Verify methodology-ancestor citations: CoinScope (author + venue), TxProbe (Delgado-Segura), Grundmann et al. (specific paper).
10. Locate CoinDesk 2021 article on Chainalysis/walletexplorer.com; verify URL + claims.
11. Pre-launch: open discussion with b10c on `bitcoin-data` dataset contribution.
12. Pre-launch: create Zenodo record, reserve DOI, cite in paper abstract.
13. Pre-launch: upload arXiv preprint citing Zenodo DOI.
14. Pre-launch: verify AS24940 (Hetzner) as style-rule example remains representative; swap if Cluster 7 example is misleading.

**Competitive intelligence surfaced:**
- b10c's `bitcoin-data` repo (home of `stale-blocks`, `mining-pools`, `block-arrival-times`) is the community-standard dataset publication path for Bitcoin network measurement. Contributing there is both the sustainability answer and the positioning move — converts HackNodes Lab's release into a contribution to the reference author's own corpus.
- b10c's fork-observer tool already connects to Electrum servers — reuse path reduces infrastructure cost further.
- CoinDesk 2021 Chainalysis leak + walletexplorer.com honeypot attribution is the documented-precedent citation that anchors the whole problem paragraph.
- B4OS, BOSS Challenge, Btrust, HRF, OpenSats, Brink are the target funding ecosystem.

**Scope/requirements signals for downstream work:**
- Paper style rule: ASN/geography/IP-subnet as **network facts**, never as operator identification. Keep this rule visible in the paper's method section.
- Documentation must be genuinely bilingual (not auto-translated) — maintained through dataset lifetime.
- Community-reproduction path must be smooth enough that a grad student can stand up a second vantage in under an hour.
- Three-tier archival must be live pre-launch, not aspirational.

---

## Internal FAQ

### IQ1: What is the hardest technical problem, and what happens if 30% of servers are flaky?

**A:** The hardest technical problem is not the fingerprinting logic or the clustering — those are solved from the methodology literature. The hardest problem is **sustained collection reliability at sub-second timing resolution across a network of operationally heterogeneous servers for months on end**. Breaking that into pieces:

1. **Sub-second timing across 50–100+ concurrent connections.** Python asyncio achieves ~1–10ms resolution, adequate because the signal (hundreds of ms between independent-backend pairs vs. near-zero between shared-backend pairs) is large compared to measurement noise. M4 Rust rewrite tightens resolution further but is not required for M3 launch.

2. **Connection reliability against flaky public servers.** Current 1209k.com monitoring shows ~90–95% of listed servers maintain >90% monthly uptime — the 30% flaky assumption is pessimistic. At the measured ~5–10% flaky rate, effective N stays near ~90% of the reachable network. Even at a pessimistic 30% (accounting for servers not listed or servers that behave differently under sustained connection), effective N of ~70% still provides sufficient statistical power against 3–8 stale-block events per month within 2–3 months of collection. The methodology is variance-based, so systematically-down servers are filtered from cluster analysis — you lose the server from the sample, not the sample from the analysis.

3. **Correlated flakiness is signal, not noise.** If flakiness is correlated across a cluster — servers sharing a backend go down together — it becomes a synchronized-downtime discriminator (one of the three primary backend-state signals in Customer FAQ Q2). Only *uncorrelated* per-server flakiness reduces effective sample size.

4. **Fee-histogram determinism** (flagged in Customer FAQ Q2). If `mempool.get_fee_histogram` is strongly-correlated-but-not-identical across frontends sharing a backend (due to ElectrumX-internal sampling), the signal weakens from "bit-identical test" to "correlation-threshold test" — survivable, reduces one discriminator's strength. Launch-blocker validation.

5. **Network size uncertainty.** The reachable Electrum server network likely ranges from 50 to 100+ unique hosts (clearnet + Tor), with exact size unknown until M1 discovery completes. Current 1209k.com lists ~25–30 unique clearnet hosts; snowball peer discovery via `server.peers.subscribe` and Tor scanning will expand this. At the conservative end (50 servers, 10% flaky), effective N of ~45 still provides sufficient statistical power within 3 months of collection.

6. **Sustained process supervision.** Operational, not algorithmic: standard systemd/Docker supervision handles process crashes; automated schema validation catches ElectrumX-version drift.

**What catastrophically breaks:** single-point-of-failure scenarios at the collector — network outage, disk corruption, ToS/legal action stopping collection. The first two are mitigated by VPS redundancy (~$10/month additional); the third is mitigated by Customer FAQ Q8's legal posture.

**I2P note.** I2P Electrum servers are not in scope for M0–M3 due to no observed public ecosystem. However, they would be a high-value target for M4: unlike Tor, I2P connections reveal the initiator's address to the server, making I2P Electrum servers potentially more useful for surveillance than Tor-based ones. If M1 snowball discovery reveals `.b32.i2p` servers, scope expands.

**The honest bound.** Each technical risk above has a known mitigation within the M3 timeline. The project's binding constraint is not technical — it is operational capacity to execute all five simultaneously while writing the paper, maintaining docs, and doing grant outreach.

---

### IQ2: What happens if launch-time findings are genuinely null (scenario 3)?

**A:** Scenario 3 is shippable, but the positioning adapts substantially. The press release's current phrasing survives scenario 2 by design; scenario 3 requires honest surgery, not a wholesale rewrite.

**What ships under scenario 3:**

- **Headline adjusts:** *"HackNodes Lab releases `electrum-sybil-detector` — the first open-source toolkit, longitudinal dataset, and empirical upper bound on shared-backend clusters in the public Electrum server network."* Question-hook and tool anchor survive; *"first empirical findings on shared-backend clusters"* becomes *"first empirical upper bound."* The change is honest: we measured, and within the statistical threshold no clusters crossed it.
- **Opening paragraph:** *"replacing speculation about wallet surveillance with measurement"* survives intact. The measurement happened; the result is a bound, not an enumeration.
- **The paper's claimed contribution becomes:** (a) validated methodology, (b) statistically bounded upper limit on shared-backend prevalence at the measurement vantage, (c) open dataset enabling reproduction and extension. FC, PETS, and IMC accept these as standalone contributions. USENIX Security and S&P typically do not.

**Honest tradeoffs of scenario 3:**

- **Grant narrative weakens substantially.** *"We found N clusters"* and *"we set an upper bound of X%"* are not equal in funding conversations. The former gets invited back; the latter gets acknowledged. This is exactly the asymmetry Push 3 identified as "hardest to sell in grants."
- **Press pickup evaporates.** Journalists write about findings, not upper bounds. The problem paragraph still lands (*"everyone suspects, no one has proven"*); the scenario-3 answer (*"we looked and did not find"*) is honest but unexciting.
- **Reference-position argument still holds.** First published longitudinal Electrum measurement with validated methodology is the citation target regardless of whether it enumerated clusters — subsequent measurement work cites HackNodes Lab's release as the reference methodology.

**When to delay vs. ship under scenario 3** (per IQ4's triple-conjunction):

- **Ship immediately if:** target venue is FC/PETS/IMC (measurement-friendly) AND land-grab pressure is active.
- **Delay to M4 (multi-vantage, 3-month extension) if:** target venue is higher-tier AND no competing publication is imminent AND multi-vantage has credible probability of converting scenario 3 to scenario 2.

**What scenario 3 does not do:** it does not kill the project. The architecture (three-tier archival, MIT/CC BY, community reproduction, Librería de Satoshi network) is designed to survive scenario 3 and transition to Path 2 or Phase 2 extension without the release posture collapsing. The release is a **bounded contribution** regardless of outcome; the contribution's strength varies, its existence does not.

---

### IQ3: Why should the Bitcoin security research community cite HackNodes Lab rather than waiting six months for b10c or peer-observer to publish the same measurement themselves?

**A:** The honest starting point: b10c or a peer-observer contributor could publish this measurement. Nothing prevents it. The bet is that they won't, for structural reasons that have held for nine months already.

**b10c has treated issue #11 as a standing `Todo` since July 2025.** His own statement — *"if I had the time to work on this, I'd write a custom tool"* — identifies bandwidth as the bottleneck. He runs peer-observer, fork-observer, and `bitcoin-data` — a mature measurement portfolio that already absorbs his maintenance capacity. Adding longitudinal Electrum-layer collection on top is exactly the operational overhead Customer FAQ Q1 identifies as the structural gap.

**Layer differentiation.** b10c's published work (peer-observer, fork-observer, `bitcoin-data`) targets the Bitcoin Core P2P layer. Grundmann's TU Darmstadt work targets the same layer from an academic-topology angle. Neither has published Electrum-server measurement, and neither is architecturally oriented toward it — peer-observer watches Bitcoin nodes, not Electrum. HackNodes Lab's contribution is the first longitudinal measurement *at the Electrum server layer*. Different corpus, not competing.

**Positioning as contribution, not competition.** The release is structured to contribute *into* b10c's ecosystem, not around it: dataset via `bitcoin-data` alongside `stale-blocks`, paper citing issue #11 as provenance, fork-observer's existing Electrum support reused rather than reimplemented. If b10c publishes a reading of the same or extended data later, HackNodes Lab's release is the reference methodology his reading cites. Publishing-first establishes the reference position; subsequent work cites rather than replaces.

**Relationship risk is real but bounded.** If b10c either (a) moves issue #11 to active work himself after seeing the PRFAQ, or (b) publishes a competing reading first, the HackNodes Lab release's positioning shifts from "first" to "parallel contribution." This is the IQ6 secondary kill scenario. Mitigation (from Customer FAQ Q4's Path 2 pre-socialization): engage b10c early in the pre-launch window with the full plan, framed as a contribution to his ecosystem — so he has the information to decline or welcome involvement, not to be surprised by it.

**The structural window.** Ship quickly enough that *"first published longitudinal Electrum measurement"* is a fact before it is a race. The 9-month-standing Todo suggests the window is open; the 12-month IQ9 threshold suggests the window is not permanent. Between those bounds is the project's window.

---

### IQ4: Tool-first vs. finding-first — is the launch compelling enough with scenario 2 weak findings, or should you delay for scenario 1?

**A:** Ship at M3 first-findings milestone — on a scenario 2 outcome if necessary — rather than delay for scenario 1. The press release is already hedged to survive scenario 2; the structural case against delay is stronger than the case for polish.

**Why not delay:**

- **Land-grab risk compounds monthly.** Every month past M3 that issue #11 remains open extends the 9-month dwell time (IQ3) toward the 12-month IQ9 ceiling. The marginal month adds more land-grab exposure than it adds finding strength.
- **Scenario 2 is "most likely" by Push 3 analysis** — the realistic outcome for 20-server M0 scale in 3 months of collection. Designing for the likely outcome is honesty, not underselling.
- **The press release is scenario-2-safe by construction.** *"First empirical findings on shared-backend clusters"* survives weak signals: "first" and "empirical" are the load-bearing words, not "dramatic." The question-hook headline works whether the answer is *"three clusters identified"* or *"no clusters meet threshold; upper bound established."*
- **Grant cycles reward execution, not optimization.** A committee choosing between *"HackNodes Lab shipped the methodology and preliminary signals on schedule"* and *"HackNodes Lab is still collecting; paper is coming"* funds the first. Reviewers have learned that projects optimizing for single-paper strength before launching tend to not launch.
- **Two papers beats one delayed paper.** Ship the M3 methodology paper (scenario 2 if necessary); the M3+X follow-up paper with stronger findings cites the M3 paper as reference methodology. This is IQ3's *"first published establishes reference position"* playing out as a two-step research program — exactly what Phase 2 grant funding rewards.

**Where delay is defensible:** the narrow conjunction of (a) M3 findings are genuinely null (scenario 3, not 2), (b) target venue treats null-methodology papers as unpublishable, AND (c) no competing publication has appeared. In that triple, a 3-month extension to M4 (multi-vantage) to generate stronger signal is defensible. Anywhere short of that triple, ship.

**The structural decision.** The press release's hedged framing, the three-scenario outlook, and the reference-position argument all assume scenario-2 shippability. If HackNodes Lab delays for scenario 1 polish after all that architectural work, the architecture becomes dead weight. Ship on the scenario the architecture was built for.

---

### IQ5: Can a solo operator sustain this post-launch?

**A:** Steady-state solo workload is ~20–35 hours per month post-M3, with intense bursts during paper revisions and grant windows. The triage story has three tiers:

**Non-negotiable (slip = release posture degrades):**
- **Data collection uptime** — the live dataset is the differentiator; lapsing more than a few days erodes both *"actively maintained"* and *"first longitudinal"* claims.
- **Legal/ethical posture compliance** — any slip is catastrophic and cannot be retroactively fixed.

**Negotiable in order (what gets traded):**
1. **Community PR response cadence** — backlog is recoverable. Weekly or bi-weekly review acceptable under pressure. Exception: a PR that fixes a data-integrity bug is non-negotiable and gets reviewed same-day regardless of other priorities.
2. **Bilingual doc updates** — English primary; Spanish on monthly-sync cadence rather than real-time.
3. **Follow-on research work** — pushed into the Phase 2 window when Phase 1 maintenance peaks.
4. **Paper revision timing** — measurement-focused venues (PETS, IMC, FC) grant extensions on request; using that flexibility is standard.
5. **Grant application cadence** — skip individual cycles if necessary. One well-executed application beats three rushed ones.

**Sacrificed last:** core tool functionality affecting measurement integrity. Any bug corrupting the dataset or invalidating a signal class is a drop-everything event.

**PR review policy:** A good external PR (bug fix, new signal, new server discovery source) is high-value and time-sensitive — the contributor's motivation decays fast if ignored. Rule: acknowledge within 48 hours (even if just *"seen, will review this week"*), substantive review within 7 days. If multiple quality PRs land during a peak period and review bandwidth is exhausted, publicly tag the backlog with *"review-queued"* and an estimated date. Transparency buys more goodwill than silence.

**Who decides:** Ifuensan. Decision criteria are pre-committed (consistent with IQ9's pattern):

- **Data collection uptime <95% for 30 days** → drop discretionary work, fix.
- **Grant window within 30 days + application in hand** → grant priority over community PR (except data-integrity PRs).
- **Paper revision within 2 weeks + paper is ship-blocker** → paper priority over all discretionary.
- **Multiple non-negotiables peaking simultaneously with no relief in sight** → consider IQ9 Path 2 handoff earlier than the 12-month threshold.

**The structural honesty:** the five negotiable workstreams are sustainable in their steady-state hours, but only in steady state. When paper revision + grant window + viral community uptake + an ElectrumX breaking change peak simultaneously, something gives. Pre-committed triage exists so the *"something"* is chosen by policy, not by panic.

---

### IQ6: What kills this project?

**A:** The architectural defenses handle most external kill scenarios: three-tier archival outlasts any single host failure, MIT/CC BY defuses permission friction, community-multi-vantage means collection outlives any single maintainer's cloud bill, and Customer FAQ Q8's legal posture defuses most operator-pushback before it starts. What the architecture does not defend against is HackNodes Lab's own operational capacity.

**The single most likely existential threat is solo-researcher capacity exhaustion.** The project requires sustained parallel commitment across data-collection reliability, ElectrumX compatibility maintenance, bilingual documentation upkeep, grant-cycle applications, community PR response, paper revision, and whatever follow-on research builds toward Phase 2 funding. If any one slips, the project degrades gracefully. If three slip simultaneously — the realistic failure mode of a solo operation — the release posture (*"active, maintained, first findings published"*) erodes into *"a 2026 snapshot nobody is updating."*

**Secondary kill scenarios, ranked by realistic probability:**

- **b10c relationship failure.** If the pre-launch conversation with b10c goes badly — he objects to framing, declines the `bitcoin-data` contribution, or publishes a competing reading before launch — Path 2 of IQ9 evaporates and IQ3's provenance anchoring weakens. Mitigation: schedule early in the pre-launch window; if lukewarm, reframe as "parallel contribution," not "dataset inheritance."
- **M0 statistical power shortfall.** If 20 servers at M0 cannot produce a cluster clearing Customer FAQ Q2's multi-signal threshold within 3 months, the launch-time *"first empirical findings"* claim collapses to scenario-2. Mitigation: the press release phrasing is deliberately hedged to survive this; the project does not die, the headline softens.
- **Sustained adversarial evasion post-publication** — treated fully in IQ7.

**Kill scenarios ranked lower:** legal threat (low given Customer FAQ Q8 posture), operator public criticism (no named target), grant rejection loop (winds down per IQ9 thresholds, does not kill the release).

The honest framing: **the architecture is strong; the human is the single point of failure.** Which is why IQ9's 12-month thresholds exist, Path 2 handoff is pre-socialized, and Phase 2 funding pursuit begins before the first paper is cited.

---

### IQ7: Does the methodology survive adversarial evasion after publication?

**A:** Some signals are harder to evade than others; the methodology is structured to fail gracefully against first-response evasion.

**Fork-race block-notification timing has asymmetric evasion cost.** An operator hiding a shared backend must actively inject per-server network-path jitter mimicking independent backend propagation — on every stale-block event, indefinitely. Over-aggressive jitter degrades user experience (stale tips, slow confirmations); under-aggressive jitter remains detectable. The detector just observes; the evader must continuously fight both the measurement and their own service quality. Any operator paying this cost is, by that fact alone, signaling the infrastructure is worth hiding.

**Mempool fee-histogram correlation is especially hard to spoof credibly.** Faking uncorrelated histograms across same-backend frontends requires either (a) running multiple real backends — defeating the cost-saving purpose of the sybil — or (b) injecting synthetic noise that creates its own statistically-distinguishable artifacts.

**Signal redundancy is the structural defense.** Customer FAQ Q2's multi-signal threshold (≥2 backend-state + ≥1 frontend-configuration) means a cluster survives partial evasion as long as two discriminators hold. Evading all three simultaneously requires effort that scales with the number of frontends being hidden — past a point, running a small number of clean real backends is cheaper than evading at scale.

**Version 2 is community-driven by design.** The detector is open-source; any evasion pattern in the wild becomes the next research question. The paper's methodology section documents the threat model and known evasion paths, so the first wave of naive evasion (jitter injection, banner rotation, timing-offset spoofing) is already anticipated. Subsequent iterations incorporate evasion-detection signals contributed by the Customer FAQ Q3 community vantage-point network.

**The meta-finding.** Coordinated evasion is itself a publishable result: if measurable shared-backend patterns disappear in the months following publication, that is evidence the measurement mattered. The detector's second-order contribution is providing an observable baseline against which operator response can be characterized.

**Honest limit:** a sufficiently resourced adversary — willing to run many real independent backends, rotate infrastructure quarterly, and mint unique banners per server — can in principle evade the current methodology. At that operational cost, the economic rationale for sybil operation (cost-sharing across frontends) inverts: the adversary spends more on evasion than on the surveillance itself. That is a win, even if no cluster is detected.

---

### IQ8: What is the peer-review venue strategy?

**A:** The venue strategy is submission-hierarchy: **arXiv preprint unconditionally**, **FC as primary**, **PETS as backup**, **IMC as tertiary**, **technical report + arXiv as final fallback**. Each step is a citation-eligible publication; none depends on the others to land.

**arXiv preprint (unconditional, launch-concurrent).** Upload before or with the public release. No reviewer gate, timestamps priority, cites the Zenodo dataset DOI, referenced by the `bitcoin-data` contribution. Preprints are citation-eligible; an arXiv-only release is already a complete research contribution in grant-conversation terms.

**Primary target: FC (Financial Cryptography).** Bitcoin-research-community native venue. Established history of publishing cryptocurrency measurement, privacy analysis, and empirical network studies (Biryukov, Meiklejohn, Bonneau lineage). Empirical and methodology-first work accepted. Audience overlap with grant funders (Btrust, HRF, OpenSats) is highest here. Short-paper track available as lower-friction option, though scenario-2 hedged findings may need full-paper space to present honestly.

**Backup: PETS (Privacy Enhancing Technologies Symposium).** Premier privacy venue, strong in Tor/anonymity-network measurement. However, recent proceedings (2023–2025) trend toward federated learning, secure computation, and ML-privacy — Bitcoin-specific measurement work is not prominent in the current editorial mix. The privacy framing fits, but the paper competes against the venue's mainstream topics. Submit if FC rejects, leaning on the surveillance-infrastructure-detection angle rather than Bitcoin-specificity.

**Tertiary: IMC (Internet Measurement Conference).** Rigorous, measurement-native. Risk: Electrum-specific may read as niche compared to broader internet-scale measurement. Submit only if reviewer feedback from FC/PETS suggests IMC reviewers would respond better.

**Final fallback: technical report + arXiv + dataset DOI + bitcoin-data contribution.** If all three peer-reviewed venues reject (unusual — one of three typically accepts methodology-first measurement), the release stands as arXiv-preprinted technical report with cited dataset DOI and reference-position claim. Not failure; venue miss. The contribution exists.

**Citation-ceiling honesty.** FC acceptance ≈ inclusion in cryptocurrency research related-work sections and immediate recognition by grant reviewers. PETS acceptance ≈ broader privacy-community reach but less Bitcoin-specific citation surface. IMC acceptance ≈ measurement-community credibility. Technical-report-only ≈ cited by readers who already know the work. The grant-narrative cost of technical-report-only versus peer-reviewed is real but bounded — about one grant cycle of slower recognition, not a project-ending outcome.

**If all fallbacks fail (unusual).** Either the methodology has a flaw all three venues catch (address and resubmit) or the work is in an editorial gap (publish as technical report, let citations build organically). Neither case is project-fatal.

---

### IQ9: What happens to the project if the first paper lands but follow-on grant funding doesn't materialize?

**A:** Yes, this scenario is realistic. The project is planned with three exit paths, not one, and the cost structure makes the "dead weight" failure mode survivable but not desirable: $15–25/month plus a few hours of monthly compatibility maintenance is a sub-$500/year drag — not existential, but not a reason to continue past the point where the work is producing research value.

**Path 1 — graceful shutdown.** The default if neither citations nor grant conversations materialize within 12 months of the paper. Collection stops, the dataset freezes at its final state, and the three archival tiers (`bitcoin-data`, Zenodo, arXiv) carry the final snapshot in perpetuity. The tool remains on GitHub under MIT for anyone who wants to continue from their own vantage. The release shipped a reproducible methodology and a bounded dataset — that is a complete contribution.

**Path 2 — community handoff.** Preferred if the dataset is being cited but HackNodes Lab cannot sustain stewardship. The natural inheritor is b10c — provenance author of issue #11, operator of `bitcoin-data` and `fork-observer`, with established stewardship of long-running Bitcoin measurement infrastructure. This is pre-socialized during the Customer FAQ Q4 launch-phase discussion so the option exists structurally on day one, not improvised at crisis point. Secondary candidates: a university measurement group that has cited the paper in its first year.

**Path 3 — carry as dead weight.** Not attractive and not a default. The only justification is pending grant conversations: 6 additional months of continued collection maintains dataset freshness while funding clarifies. Beyond that, Path 3 becomes research opportunity cost disguised as commitment.

**Decision thresholds** (pre-committed, not deferred):

- 6 months post-paper, no citations + no grant leads → **Path 1 (graceful shutdown).**
- 6–12 months, citations accumulating + no grant → **Path 3 for 6 more months,** then reassess.
- 12 months, citations + no grant → **Path 2 (community handoff).**
- Grant secured at any point → continue as Phase 2 research program.

The architecture — three-tier archival, MIT/CC BY licensing, community-multi-vantage from day one — is designed so no exit path damages the research contribution. The paper and dataset are complete whether HackNodes Lab maintains the live feed for one year or ten.

---

<!-- coaching-notes-stage-4 -->
## Stage 4 Coaching Notes

**Question selection and ordering decisions:**
- Customer FAQ's dropped Q1 (b10c differentiation) migrated here as IQ3, where stakeholder-skeptic positioning questions belong.
- Tool-first vs. finding-first tension flagged in Stage 2 answered here as IQ4 (ship on scenario 2, defensible-delay narrow carveout).
- b10c-relationship-risk woven through IQ3, IQ6, IQ9 as a shared dependency rather than a standalone question — keeps it visible without duplicating a slot.

**Feasibility risks identified and mitigations:**

| Risk | Mitigation | Category |
|---|---|---|
| Python asyncio timing resolution | M4 Rust rewrite planned; current resolution adequate for signal-vs-noise bound | Accepted trade-off |
| 30% flaky servers | Variance-based filtering; effective N of ~70% still gives statistical power within 2–3 months | Resolved |
| Correlated flakiness | Becomes a positive synchronized-downtime discriminator | Resolved, positive inversion |
| Fee-histogram determinism | Launch-blocker validation; accept correlation-threshold fallback if not identical | Known unknown with mitigation |
| Network size uncertainty | Conservative-case analysis (50 servers, 10% flaky → N=45) still sufficient | Resolved via conservative estimate |
| Collector single-point-of-failure | VPS redundancy (~$10/month additional) | Accepted cost |
| Scenario 3 (null result) | Shippable as "upper bound + validated methodology"; headline surgery specified | Accepted trade-off, weak grant narrative owned |
| Solo-researcher capacity exhaustion | Named as single most likely existential threat; triage hierarchy pre-committed; Path 2 handoff as structural escape | Acknowledged, partially mitigated |
| b10c relationship failure | Pre-launch socialization; reframe as "parallel contribution" if lukewarm | Launch-blocker dependency |
| M0 statistical power shortfall | Hedged press-release phrasing survives scenario 2 | Survivable |
| Adversarial evasion post-publication | Asymmetric evasion cost; multi-signal redundancy; community-driven v2; meta-finding reframe | Resolved via structural argument |
| Venue rejection at all three venues | Technical report + arXiv + dataset DOI + bitcoin-data is still a complete contribution | Unlikely + ownable |

**Resource/timeline estimates captured:**
- Steady-state workload: 20–35 hrs/month post-M3.
- Paper revision burst: 20–40 hrs in revision weeks.
- Grant applications: 20–40 hrs each; plan 2–3/year.
- Target ship: M3 (first-findings milestone).
- Evaluation milestones: 6 and 12 months post-paper (IQ9 thresholds).
- Cost envelope: $15–25/month base + ~$10/month VPS redundancy = sub-$500/year standing cost.

**Pre-committed decision thresholds (from IQ5 and IQ9):**
- Data collection uptime <95% for 30 days → drop discretionary, fix.
- Grant window within 30 days + application in hand → grant > community PR (except data-integrity PRs).
- Paper revision within 2 weeks + ship-blocker → paper > discretionary.
- 6 months post-paper, no citations + no grants → Path 1 (shutdown).
- 6–12 months, citations + no grants → Path 3 (6 more months, reassess).
- 12 months, citations + no grants → Path 2 (community handoff).
- Grant secured → continue as Phase 2.

**Strategic positioning decisions (Stage 4 locked):**
- **Contribution-into-ecosystem, not competition.** b10c dependency framed as collaborative via `bitcoin-data` contribution, issue #11 citation, fork-observer reuse.
- **FC as primary venue, not PETS.** FC's Bitcoin-research lineage (Biryukov, Meiklejohn, Bonneau) + grant-funder audience overlap chosen over PETS's broader privacy audience. PETS's 2023–2025 editorial drift away from Bitcoin-specific work documented as supporting rationale.
- **Ship on scenario 2.** Press release hedged to survive scenario 2; delay defensible only in triple-conjunction (scenario 3 + non-measurement venue + no land-grab pressure).
- **Community multi-vantage from day one.** Single-vantage limitation converted into "lower bound on shared-backend prevalence" that strengthens with community reproduction.
- **PR-review SLA:** 48-hour acknowledgment, 7-day substantive review, public "review-queued" tagging during peaks. Data-integrity PRs exception to all triage rules.
- **Two-papers plan locked.** M3 methodology paper + M3+X follow-up with stronger findings; Phase 2 grant funds the second.

**Technical constraints and architectural commitments:**
- Python asyncio for M3; Rust at M4 (moved from original M2 suggestion per user revision).
- Storage: local SQLite at M0, TimescaleDB/Postgres at M2, ~500 MB/month at full network scale.
- Discovery: snowball via `server.peers.subscribe` from 1209k.com + Electrum wallet hardcoded peers.
- Licensing: MIT code, CC BY 4.0 dataset.
- Archival: `bitcoin-data` GitHub + Zenodo DOI + arXiv paper, three independent hosts.
- Scope exclusions: Tor deferred to M2, I2P conditional on M1 discovery, private/embedded vendor servers out by construction.

**Launch-blocker additions from Stage 4 (compounding with Stage 3's list):**

15. Verify Python asyncio timing resolution (~1–10ms) is adequate in actual M0 collection.
16. Verify 1209k.com "~90–95% of listed servers maintain >90% uptime" claim against actual 1209k.com historical data.
17. Clarify and fact-check the I2P "reveals initiator's address" claim — likely phrase as "persistent destination identifiers enable long-term linkability" for technical accuracy.
18. Verify IQ3's 9-month b10c-Todo dwell time is accurate at actual launch date; update phrasing if launch slips.
19. **Critical-path pre-launch:** schedule b10c socialization conversation covering framing, `bitcoin-data` contribution, Path 2 handoff optionality. This is both IQ3's differentiation mitigation and IQ9's Path 2 precondition.
20. Verify FC's recent acceptance patterns for methodology-first / scenario-2-style measurement papers (Biryukov/Meiklejohn/Bonneau lineage holds through 2024–2026).
21. Verify PETS 2023–2025 editorial mix (claimed federated-learning/secure-computation dominance); reconsider primary/backup ordering if PETS is still actively publishing Bitcoin work.
22. Paper must include measurement-ethics section (OpenSats/PETS reviewer expectations: rate-limiting, disclosure, IRB-equivalent).
23. Paper must include "threat model and known evasion paths" section per IQ7.

**Competitive intelligence surfaced in Stage 4:**
- b10c's fork-observer already supports Electrum connections — reusable infrastructure.
- `bitcoin-data` repo is the community-standard dataset publication path for Bitcoin measurement.
- FC's Bitcoin-research lineage (Biryukov, Meiklejohn, Bonneau) as target-venue precedents.
- PETS editorial drift away from Bitcoin work (2023–2025) — informs venue hierarchy.

**Scope/requirements signals for downstream work:**
- Phase 2 funding pursuit must begin before the first paper cites, not after.
- Two-papers plan is the research program structure. M3 = methodology paper; M3+X = follow-up with stronger findings.
- Multi-vantage (M4) is both a roadmap milestone AND a community-enabled capability from day one.
- Paper structure must include: threat model + evasion paths (IQ7), measurement ethics statement (launch-blocker #22), related-work comparison against Bitcoin P2P measurement ancestors.

---

## The Verdict

### Overall assessment: **needs more heat, leaning toward forged**

The concept is substantively strong and internally coherent. The press release, Customer FAQ, and Internal FAQ reinforce each other rather than contradict — a rare outcome for a 10 + 9 question gauntlet. The architectural defenses (three-tier archival, MIT/CC BY licensing, community-multi-vantage, variance-based methodology, pre-committed exit thresholds) mutually reinforce: a failure in any one is caught by another. That is how you tell a research program from a research project.

But the concept is not launch-ready. Twenty-three launch-blocker validation items are accumulated across the coaching notes, and one existential-capacity risk (IQ6) is acknowledged but not mitigated. With the launch-blocker checklist executed and the b10c socialization conversation completed warmly, this becomes **forged**. Without those, the architecture is a promise, not a foundation.

---

### Forged in steel

These aspects survived the gauntlet and emerged stronger:

- **The scope reframe — "detect shared infrastructure; attribution is a separate interpretive layer."** This is the single most valuable move in the whole document. It is analytically defensible (the data *can* prove shared backends; it *cannot* prove operator identity), legally protective (Customer FAQ Q8's "cite attributions, never originate them" posture flows from it), and publishability-preserving (all three scenario outcomes remain publishable). It survives every stress test in the Internal FAQ.
- **b10c issue #11 + CoinDesk 2021 Chainalysis citation chain.** The provenance argument is concrete, citable, and converts "is this a made-up problem" into "here is the documented origin." The nine-month-standing Todo + documented precedent + citable source chain together make Q1 Customer FAQ the strongest answer in the whole document.
- **The three-tier archival commitment** (`bitcoin-data` + Zenodo + arXiv). Three independent hosts with three independent failure modes. The sustainability question (Customer FAQ Q4, IQ9) is structurally defeated, not argued away.
- **The methodological spine — fork-race variance + multi-signal threshold + "lower bound" framing.** Q2, Q3, Q7 reinforce each other: the discriminator is vantage-robust (variance drops path asymmetry), multi-signal reduces false positives, and "lower bound" converts single-vantage from weakness into floor. Community-multi-vantage from day one turns the lower bound into a ratchet.
- **Two-papers plan.** The M3 methodology paper + M3+X follow-up structure resolves the scenario-2-as-launch tension cleanly. Grant narrative benefits from a research program, not a one-shot measurement.
- **Pre-committed decision thresholds (IQ5, IQ9).** Concrete numerical triggers ("uptime <95% for 30 days," "6/12-month post-paper evaluation") replace "we'll figure it out" with structural commitments that hold under stress.
- **Licensing + bilingual strategy (MIT / CC BY / EN+ES / Librería de Satoshi alignment).** Small but fully settled decisions with clear strategic reasoning. The Librería de Satoshi alignment especially converts "solo operator" into "embedded in a network with funding relationships."
- **FC-primary venue hierarchy with named lineage (Biryukov / Meiklejohn / Bonneau).** Demonstrates domain fluency and correctly identifies audience-overlap with grant funders as the ordering criterion.
- **Legal posture — "cite published attributions, never originate them; network facts ≠ operator identification."** Precisely articulated. Reviewers, lawyers, and co-collaborators all read from the same rule.

---

### Needs more heat

Promising directions that need concrete work before they are ready for downstream PRD consumption:

- **Fee-histogram determinism verification.** Flagged twice as "pending empirical verification," and the methodology's claim that *"same-backend frontends produce strongly correlated or identical output"* is load-bearing. Before any claim in the paper or the press release, run two ElectrumX frontends against one Core and diff their `mempool.get_fee_histogram` output. If not bit-identical, the signal weakens to correlation-threshold — survivable but reduces one of three primary discriminators. **Priority: highest.**
- **b10c pre-launch socialization conversation.** The architecture treats this as critical path (IQ3 differentiation, IQ9 Path 2), but no concrete plan exists. Needs: (a) who reaches out — Ifuensan directly, or through a mutual contact; (b) when — ideally 4–6 weeks before public release, not 48 hours; (c) through what channel — GitHub issue on `bitcoin-data` or direct email; (d) with what materials — a link to the PRFAQ? A short summary? An invitation to comment on the methodology? Draft the outreach plan before Stage 5 closes in the user's mind.
- **Paper structure.** The Internal FAQ commits the paper to specific sections — threat model + known evasion paths (IQ7), measurement ethics statement (launch-blocker #22), related-work comparison against Bitcoin P2P measurement ancestors. No paper outline exists yet. A one-page outline with section headers and 2–3 sentence abstracts per section would de-risk the paper-writing burst in IQ5.
- **M0 scale calibration.** The "~20 servers at M0" figure is stated but the actual seed list and discovery sequence haven't been validated against the live network. Spend one day running the snowball discovery against 1209k.com's current listing + Electrum wallet defaults and count distinct reachable endpoints. This is the single most impactful pre-launch validation because it calibrates the statistical-power calculations in Customer FAQ Q2 and IQ1.
- **I2P phrasing precision.** Launch-blocker #17 — the "reveals initiator's address" claim is likely accurate in a narrow technical sense (persistent destination identifiers enable long-term linkability) but misleading as phrased (I2P tunnels do hide client IPs). Rewrite as "I2P's persistent destination identifiers enable long-term linkability of wallet users by Electrum server operators — a surveillance primitive Tor's rotating circuits do not provide."
- **Phase 2 funding pursuit.** Committed in IQ6 as *"begins before the first paper is cited,"* but no specific plan. Which grant calls (OpenSats next round? HRF Bitcoin Dev Fund? Btrust?), which partners (Librería de Satoshi co-PI? university collaborator?), what narrative (methodology paper in hand + follow-on research questions)? Even a one-page "Phase 2 pitch outline" would convert this commitment from aspirational to operational.
- **Real quote attribution for the community quote.** The `[Peer researcher, Bitcoin privacy]` placeholder needs a real attribution before launch. Candidates: someone in the b10c / peer-observer orbit, a cited FC/PETS Bitcoin-privacy author, or a Librería de Satoshi-network researcher. Solicit during the pre-launch window.

---

### Cracks in the foundation

Genuine risks that must be addressed deliberately:

- **Solo-researcher capacity (IQ6) is the project's single point of failure.** The architecture catches every external kill scenario; none of the architectural defenses protect against Ifuensan's own bandwidth running out. The triage hierarchy and Path 2 handoff reduce the damage of capacity exhaustion but do not prevent it. **What would it take to address?** Either (a) an explicit "collaborator call" plan at the 6-month post-paper threshold, pre-defining who might be brought in part-time and for what workstreams; or (b) a pre-identified co-maintainer (not a Path 2 inheritor — a concurrent partner) from the Librería de Satoshi network or a Bitcoin-research university group. Without (a) or (b), the capacity risk remains structurally unmitigated.
- **b10c relationship is a single point of failure for TWO load-bearing questions (IQ3 + IQ9 Path 2).** If the pre-launch conversation goes cold or adversarial, differentiation *and* sustainability weaken simultaneously. **What would it take to address?** Build a secondary Path 2 candidate — a university measurement group pre-identified as willing to take on dataset stewardship if the b10c path fails. Make the secondary candidate a concrete entity, not a generic "a university group."
- **Scenario 3 + b10c-cold + Phase-2-unfunded triple-hit** is the realistic worst-case compound failure. Each leg individually is survivable per the architecture; all three simultaneously would leave HackNodes Lab with a published methodology paper, a frozen dataset, a cold community relationship, and no Phase 2. The architecture catches the fall — the release exists, the contribution is citable — but the research program stalls at one paper. This is the honest floor. **What would it take to address?** Not prevention — that's not in your control. Rather: an explicit contingency script for this scenario in the coaching notes so future-Ifuensan doesn't have to invent it under stress. The script is essentially: *ship Path 1 graceful shutdown + keep bilingual Spanish community engagement active through Librería de Satoshi + re-enter the research landscape on a different question with the methodology paper as the credentialing artifact.* The project's failure mode is not vanishing; it is becoming a one-paper project instead of a research program.
- **The press release is dated and geo-stamped with placeholders** (`[City, Launch Date]`, `[Peer researcher, Bitcoin privacy]`). Not a crack in the concept — a reminder that the document is a draft requiring execution to become a release. Do not publish any of this without the launch-blocker checklist cleared first.

---

### Summary judgment

The PRFAQ survived the gauntlet. The concept is not a pitch — it is a research program with architectural defenses against most realistic failure modes and pre-committed decisions for the rest. The "needs more heat" items are not intellectual gaps; they are execution items that convert promises into facts. The "cracks" are real but bounded, and each has an articulated path to address.

The question this PRFAQ most clearly answers — whether HackNodes Lab *should* build this, and whether the Bitcoin security research community needs it — is unambiguously yes. The question it defers to downstream execution — whether HackNodes Lab *can* build this without capacity exhaustion and with the right community relationships — is the real work that remains.

Ship the launch-blocker checklist. Then ship the paper.

---

<!-- coaching-notes-stage-1 -->
## Stage 1 Coaching Notes

**Concept type:** Research output (published finding + longitudinal dataset) with supporting open-source tool. Non-commercial; primary success metrics are citations, reference-position, and grant leverage — not revenue or user adoption.

**Primary customer / reader:**
- **Beneficiary (who this is for):** HackNodes Lab itself, with Ifuensan as primary author.
- **Press-release reader (who it's written to):** the Bitcoin security research community — grant committees (OpenSats, HRF, Btrust), peer researchers (b10c / peer-observer orbit, Grundmann, Fanti lineage), privacy-focused technical journalists.
- **Downstream beneficiaries (post-finding):** Electrum wallet maintainers, `servers.json` curators, privacy-conscious end users. These are NOT the press-release audience.

**Primary deliverable ordering (decided by user):** Open-source tool → Dataset → Paper.
- **Coach flag to revisit in Internal FAQ:** A tool-first launch without accompanying findings risks ceding the "first empirical answer" position. The press release most likely wants to announce **tool + first findings together**, not the tool alone. User acknowledged the tension; will stress-test in Stage 4.

**Problem framing (validated):**
- The question "how many public Electrum servers are surveillance honeypots?" has been open for years (notably proposed publicly by b10c) with no empirical answer, because the **longitudinal behavioral fingerprinting dataset does not exist**.
- Publishing original empirical findings is the currency that wins grants; tool releases alone are commodity in this competitive landscape.

**Scope reframe captured in Push 3 (important):**
- Primary detection target is **shared infrastructure** (multiple frontends over one backend, correlated behavior across server endpoints). This is provable from fingerprints.
- **Intent attribution** (surveillance operator vs. legitimate cost-sharing hoster) is a **separate interpretive layer**. Even "hosting provider runs 3 Electrum frontends on one Bitcoin Core for cost" is publishable as a characterization of shared infrastructure.
- This raises the floor of publishable outcomes and de-risks the "we can't find Chainalysis" failure mode.

**Three-scenario outlook (user's own framing — hold for Internal FAQ):**
1. **Clear clusters found** — ideal; headline writes itself; user estimates high probability.
2. **Weak signals, no statistical clusters** — most likely outcome for M3 milestone with ~20 servers at M0; publishable as "methodology + preliminary signals + need to scale collection."
3. **True null result** — ninguno; publishable as "upper bound + validated methodology + open dataset for replication." Hardest to sell in grants; least useful outcome per user.

**Competitive / positioning landmarks named by user:**
- b10c (peer-observer) — originated this research question publicly; first-mover risk if they publish first.
- Fanti et al. (Dandelion) — academic lineage on Bitcoin network privacy.
- Grundmann — Bitcoin P2P topology measurement work.

**Open tensions to resolve in later stages:**
1. Tool-first branding vs. finding-first announcement (Push 1 tension).
2. Land-grab window — has b10c or anyone else already started longitudinal collection? (Stage 4 feasibility question, needs web research to validate.)
3. M0 scale (~20 servers per user) — is that enough statistical power to produce a publishable signal, or does M0 need to be larger before scenario 2 becomes scenario 1?

**Subagent findings to be merged below after Stage 1.5 research fan-out.**

### Artifact Analyzer Findings

**Documents scanned:** `README.md`, `docs/papers/electrum_servers_insights.md`, `docs/papers/bitcoin_topology_insights.md`.

**Prior-art gap (validates the open-question framing):**
- The Electrum insights corpus explicitly notes: *"detailed empirical attack histories on Electrum servers are not available in this corpus."* No competing longitudinal Electrum-server dataset is cited in either insights doc. **First-mover position is defensible.**
- Surveyed Electrum literature covers SPV/Bloom leakage (Gervais/Karame 2014) and formal 2FA proofs — not server-operator sybil measurement. Server-side surveillance is the un-measured analog of the client-side leakage line.

**Methodological precedent exists on the Bitcoin P2P side, never applied to Electrum:**
- **Node-Probe (Essaid et al., IJNM 2020/2023):** 99% precision / 98% recall on multi-week snapshots 2018–2022; ~4× more communities than random graph; propagation gains up to ×25 with master-node scheme.
- **TxProbe (Delgado-Segura):** orphan-TX propagation for topology inference.
- **ADDR-marker:** gossip-timing inference, &lt;10% degree error, 40–56% precision/recall on real network. *Establishes that behavioral inference without protocol-level ground truth is accepted academic practice.*
- **Partition framing (Shetti et al.):** &lt;10 high-degree peers can fragment Bitcoin — sharpens the "why shared backends matter" narrative for grant readers.
- **Structural precedent for "shared infrastructure" framing:** Essaid et al. + Pedro et al. ("All that Glitters is not Bitcoin") document heavy-tailed degree and centralized IP-level nature in the Bitcoin P2P layer.

**Detection signal hierarchy already laid out in README:**
- **Very High:** block-notification timing during fork races; shared `donation_address` (trivially evaded).
- **High:** synchronized downtime; identical fee histograms (Wasserstein ε).
- **Medium:** banner/version similarity.

**ElectrumX already ships anti-sybil logic** (subnet-diversity limits in `server.peers.subscribe`), meaning any sophisticated operator is forced to spread across ASNs — which becomes its own ASN-correlation fingerprint. This is a gift to the detector.

**Named landmarks check:**
- **b10c** is credited in the README as "Original idea" source — anchors peer-observer lineage as the direct antecedent.
- **Grundmann / Fanti** are NOT directly cited in the scanned insights docs; Essaid (Node-Probe) and Delgado-Segura (TxProbe) are the actual measurement-methodology reference points for this project.

### Web Researcher Findings

> ⚠️ **Caveat:** Live WebSearch was blocked in this session. The web researcher synthesized from Jan 2026 knowledge cutoff only. **Every claim about "what's been published" or "what's funded" below should be re-verified via live search or direct contact with sources before the paper ships.** Most load-bearing: the claim that the land-grab window is still open.

**Competitive landscape (per knowledge cutoff):**
- **b10c / peer-observer:** longitudinal Bitcoin P2P / mempool / mining measurement — NOT Electrum servers. No known published Electrum sybil/honeypot longitudinal dataset as of late 2025.
- **Grundmann et al. (TU Darmstadt):** academic Bitcoin P2P topology + sybil-resistance — core Bitcoin P2P only, not Electrum / SPV.
- **Dandelion lineage (Fanti, Venkatakrishnan):** protocol-level design work, not empirical SPV measurement.
- **Static Electrum server lists** (1209k.com, electrum.org defaults): uptime/version only; no behavioral fingerprinting, no backend-cluster inference.

**Market / grant context:**
- OpenSats, HRF Bitcoin Dev Fund, Brink, Spiral, Btrust all actively funded Bitcoin privacy + network-measurement work 2024–2025; typical grants $25k–$150k.
- Recent OpenSats cohorts leaned toward Silent Payments, Payjoin, Nostr, P2P tooling. **Empirical surveillance measurement is under-represented.**
- Academic venues (FC, IMC, PETS, USENIX) publish 1–3 Bitcoin measurement papers/year; Electrum privacy is a notable gap.
- Grant reviewers at OpenSats/HRF have publicly favored **reproducible tooling + datasets over one-shot papers** — friendly to the tool-first ordering.

**Timing / opportunity:**
- Land-grab window appears OPEN per cutoff data (but SEE CAVEAT).
- peer-observer tooling + ClickHouse/Parquet pipelines lower the bar for a solo researcher to ship credible longitudinal data.
- Samourai prosecution + Tornado precedent → heightened reviewer/press appetite for empirical surveillance evidence.

**New risks surfaced (important for Internal FAQ):**
1. **Attribution risk (legal):** naming specific operators (e.g., Chainalysis) without airtight evidence invites pushback. **Mitigation:** frame public-facing claims as "clusters of shared backend infrastructure" and let readers infer. *This aligns perfectly with user's Push 3 reframe — the shared-infra vs. intent separation is not just analytically clean, it's legally protective.*
2. **Sustainability:** longitudinal datasets decay without funding. Pre-arrange hosting (Brink LTS, OpenSats LTS, or university mirror) **before launch**, not after.
3. **Ethics expectations:** large-scale probing of public Electrum servers is low-risk (they advertise publicly), but OpenSats / PETS reviewers expect **measurement-ethics statement, rate-limiting, and IRB-style disclosure up front**. Budget for this.
4. **Methodological precedent demand:** academic reviewers may require comparison to Grundmann-style sybil inference. Budget a related-work pass that treats Node-Probe / TxProbe / ADDR-marker as the direct methodological ancestors.
5. **Land-grab closure:** b10c or a peer-observer contributor could publish first. **Mitigation:** ship a public dashboard early, don't wait for the paper.

### Merged synthesis for Stage 2 framing

The press release is writing itself on these rails:
1. **The gap is real and documented** — both the internal corpus and the external landscape (at cutoff) confirm no longitudinal Electrum-server dataset exists.
2. **The method is defensible** — Node-Probe / TxProbe / ADDR-marker are the academic ancestors, well-regarded, and directly transferable to Electrum's richer protocol surface.
3. **The legal frame is settled** — "shared backend infrastructure clusters" is the safe, publishable claim. Surveillance attribution is an interpretive overlay, not the headline.
4. **The funding / press appetite is favorable** — grant makers and privacy press want empirical surveillance measurement; OpenSats has publicly favored reproducible tool+dataset releases over one-shot papers (friendly to the chosen ordering).
5. **The tool-first ordering is compatible with the "launch = dashboard + first findings" model** — HackNodes Lab's brand is tools, so the press release announces *the tool and what it has already found in early data*, not the tool alone.
