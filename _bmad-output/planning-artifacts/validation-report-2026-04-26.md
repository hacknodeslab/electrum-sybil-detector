---
validationTarget: '_bmad-output/planning-artifacts/prd.md'
validationDate: '2026-04-26'
validationMode: 'diff-aware'
diffBasis: 'Phase-1 closeout edits (12 surgical changes) on top of PRD commit e607d55, performed in this session via bmad-edit-prd'
inputDocuments:
  - docs/bmad-binnacle/03_phase1-validations.md
  - 'on-demand from PRD frontmatter inputDocuments[] (not pre-loaded)'
validationStepsCompleted:
  - step-v-01-discovery
  - step-v-02-format-detection
  - step-v-03-density-validation
  - step-v-04-brief-coverage-validation
  - step-v-05-measurability-validation
  - step-v-06-traceability-validation
  - step-v-07-implementation-leakage-validation
  - step-v-08-domain-compliance-validation
  - step-v-09-project-type-validation
  - step-v-10-smart-validation
  - step-v-11-holistic-quality-validation
  - step-v-12-completeness-validation
validationStatus: COMPLETE
holisticQualityRating: '5/5 — Excellent (post-diff)'
overallStatus: Pass
criticalIssues: 0
warnings: 0
informationalNotes: 3
---

# PRD Validation Report

**PRD Being Validated:** `_bmad-output/planning-artifacts/prd.md`
**Validation Date:** 2026-04-26
**Mode:** Diff-aware (focused on the 12 Phase-1 closeout edits, not full from-scratch audit)

## Diff Under Validation

The PRD was just edited via `bmad-edit-prd` to integrate the outcomes of three Phase-1 closeout validations (commit `13bec1f`). Net change: 633 → 645 lines (+27 / −15) across 4 sections + Launch-Blocker Checklist. The edits span three logical blocks:

- **Block 1 (V1, fee-histogram):** L383(i), L470, FR19, FR24, LB#2 — reframe from "determinism / identity test" to "Wasserstein drift-magnitude calibration".
- **Block 2 (V2, asyncio):** LB#15, NFR2 — clear with empirical numbers.
- **Block 3 (V3, dual-stack):** Discovery module L447, M1→M2 gate L463, NFR10, cost envelope L478, +new LB#26.
- **Frontmatter:** `stepsCompleted` extended; `lastEdited` + `editHistory` added; `inputDocuments` extended; `documentCounts` updated.

## Input Documents

- PRD under validation: `_bmad-output/planning-artifacts/prd.md` (645 lines)
- Diff-evidence source of truth: `docs/bmad-binnacle/03_phase1-validations.md`
- PRD `inputDocuments[]` (13 entries): not pre-loaded; available on-demand during specific checks.

## Validation Findings

[Findings appended as validation progresses, organized by step. Severity: Critical / Warning / Informational.]

### Step 2 — Format Detection

**PRD Structure (## Level 2 headers, in order):**
1. Executive Summary
2. Project Classification
3. Success Criteria
4. Product Scope
5. User Journeys
6. Domain-Specific Requirements
7. Innovation & Novel Patterns
8. Research Project Specific Requirements
9. Project Scoping & Phased Development
10. Functional Requirements
11. Non-Functional Requirements

**BMAD Core Sections Present:**
- Executive Summary: Present
- Success Criteria: Present
- Product Scope: Present
- User Journeys: Present
- Functional Requirements: Present
- Non-Functional Requirements: Present

**Format Classification:** BMAD Standard
**Core Sections Present:** 6/6

**Findings:** No issues. PRD also includes 5 forced top-level sections from `classification.forcedTopLevelSections` (`Domain-Specific Requirements`, `Innovation & Novel Patterns`, `Research Project Specific Requirements`, `Project Scoping & Phased Development`, `Project Classification`) — consistent with `research_project / scientific / medium` classification carve-outs.

### Step 3 — Information Density

**Anti-Pattern Violations across full PRD:**

| Category | Count |
|---|---:|
| Conversational filler (`The system will allow users to`, `It is important to note that`, `In order to`, `For the purpose of`, `With regard to`) | 0 |
| Wordy phrases (`Due to the fact that`, `In the event of`, `At this point in time`, `In a manner that`) | 0 |
| Redundant phrases (`Future plans`, `Past history`, `Absolutely essential`, `Completely finish`) | 0 |
| **Total** | **0** |

**Diff-under-validation focused check (12 edited paragraphs):** zero anti-pattern matches. New prose is dense — empirical numbers attached to every status claim (587 µs, 1.71 ms, 246, 344, +98, ≈28%); methodology terms (Wasserstein, EMD, dual-stack, Hetzner CX22) are precise and load-bearing, not filler.

**Severity:** **Pass**

**Recommendation:** PRD demonstrates excellent information density. The recent 12 edits maintain that standard.

### Step 4 — Product Brief Coverage (diff-aware)

**Brief loaded:** `docs/project-brief.md` (bilingual ES/EN). Brief was updated in commit `13bec1f` (alongside the PRD's edits) to soften the fee-histogram bullet at L74 ES / L139 EN — "fuertemente correlacionado, no bit-idéntico" / "strongly correlated, not bit-identical", citing `spesmilo/electrumx` and Wasserstein. Brief and PRD are by construction aligned on the diff-relevant content.

**Diff-aware coverage check (only the content the 12 PRD edits touched):**

| Brief content | PRD coverage | Status |
|---|---|---|
| Fee-histogram strongly-correlated language (brief L74/L139) | PRD L470 (Pre-launch validation harness), FR19, FR24, LB#2 | Fully Covered |
| Real network size & launch-blocker framing (brief L75/L140 reference snowball + bootstrap=130, 1209k=506) | PRD Discovery module L447 (V3 evidence), M1→M2 gate L463, NFR10, LB#16 (deferred), LB#26 (new) | Fully Covered. **Note:** brief still cites "bootstrap=130" while PRD/binnacle now reflect the empirically re-fetched count of 84 (70 clearnet, 14 .onion). Not a blocker — brief and PRD use 130 only as historical anchor, not as a load-bearing claim. **Severity: Informational** |
| asyncio collector framing (brief generally treats Python collector as M0 default) | PRD NFR2, LB#15 (cleared) | Fully Covered |
| Sub-$500/year cost envelope (brief §Riesgos) | PRD L478 + dual-stack VPS note | Fully Covered |
| Single-vantage limitation, peer-researcher voice, Wasserstein at M3 | PRD L383(i) (limitations), Executive Summary, §Measurement Validity | Fully Covered |

**Coverage Summary (diff-relevant subset):**
- Critical Gaps: 0
- Moderate Gaps: 0
- Informational Gaps: 1 (brief cites bootstrap=130 historically; current actual is 84 — not a coverage gap, just an outdated number used as anchor)

**Full-PRD-vs-Full-Brief coverage:** Out of scope for this diff-aware run. Already validated in the original PRD creation pass (commit `e607d55`). Diff didn't add or remove user-facing scope.

**Severity:** **Pass**

**Recommendation:** PRD coverage of Product Brief content is intact post-edit. Optional follow-up: at next brief edit, refresh the historical "bootstrap=130" anchor to "bootstrap=84 (snapshot 2026-04-25)" to match current upstream state.

### Step 5 — Measurability (FRs + NFRs)

**Functional Requirements:**
- Total FRs: 42 (FR1–FR42)
- Format violations (`[Actor] can [capability]` pattern): 0
- Subjective adjectives in requirements: 0
- Vague quantifiers in requirements: 0 (5 occurrences of "many" / "multiple" total in document, all in narrative context — fork-race event populations, user-behavior descriptions, market context — none in FR/NFR specs)
- Implementation leakage: 0 strict; 2 informational notes (see below)

**Non-Functional Requirements:**
- Total NFRs: 17 (NFR1–NFR17)
- Missing metrics: 0
- Incomplete template: 0
- Missing context: 0

**Diff-relevant requirements detail:**

| Requirement | Format | Specific metric | Measurement method | Context | Verdict |
|---|---|---|---|---|---|
| FR19 (Wasserstein over CDFs) | "The system can compute…" | 1-D Wasserstein, `∫ |F_A(x) − F_B(x)| dx` | Same `mempool.get_fee_histogram` outputs over configurable window | Cross-instance bit-identity false by construction (cited) | **Pass** |
| FR24 (calibration harness) | "The system can run…" | Wasserstein-distance distribution under same-backend conditions | 5-frontend matrix vs. 1 Bitcoin Core | Cluster-membership threshold + CI drift monitoring | **Pass** |
| NFR2 (asyncio) | NFR template | p99 = 587 µs at N=100; 1.71 ms at N=200 | `experiments/asyncio-timing-benchmark/` | Signal floor (hundreds of ms inter-server) | **Pass** |
| NFR10 (connections + dual-stack) | NFR template | 100–500 sockets; native IPv6 outbound binary | Connection-event rows + dual-stack outbound test | Tunnels confound timing — bound to NFR1 | **Pass** |
| LB#26 (verification criteria) | Operational gate | ≥3 IPv6-only servers; `server.features` + `server.peers.subscribe` complete | Active probe against discovered population | Prevents silent ~28% network undercount | **Pass** |

**Informational notes (not violations, but worth flagging):**

1. FR24 names 5 specific Electrum frontends (ElectrumX, Fulcrum, mempool-electrs, Blockstream/electrs). In a generic SaaS PRD this would be implementation leakage; here, the multi-frontend matrix IS the calibration apparatus, and naming the specific frontends is methodological specification covered by the `rigor.statistical_methodology` carve-out. **Severity: Informational.**
2. NFR10 + L489 cost envelope name specific cloud providers (Hetzner, AWS) and tunnel technologies (Hurricane Electric, ZeroTier). Same justification — these are *constraint* specifications (which infra satisfies the dual-stack + native-v6 + non-tunneled requirement), not implementation choices for the tool itself. **Severity: Informational.**

**Severity:** **Pass** (0 violations across 59 requirements)

**Recommendation:** Requirements demonstrate strong measurability. The 12 diff edits all introduced SMART verification criteria with empirical citations. No revision needed.

### Step 6 — Traceability (diff-aware)

**Chain validation for diff-relevant requirements:**

| New/edited element | Traces back to | Verdict |
|---|---|---|
| FR19 (Wasserstein metric) | §Success Criteria > Technical/Measurement Success ("≥2 backend-state signals … fee-histogram correlation"); §Innovation > Detected Innovation Areas (premise IQ2 backend-shared frontend detectability); §User Journeys > Lukas (peer researcher reproducibility); §Implementation Considerations > Pre-launch validation harness | **Intact** |
| FR24 (calibration harness) | §Publication Requirements > Reproducibility Contract; §Project Scoping > LB#2; §Implementation Considerations > Pre-launch validation harness L470; §Innovation > Validation Approach | **Intact** |
| LB#2 reframe | FR24 + L470 + §Innovation > Validation Approach + brief L74/L139 (cited evidence: `spesmilo/electrumx`) | **Intact** |
| L383(i) limitations bullet | §Measurement Validity (Wasserstein methodology) + FR19 (the metric) + LB#2 (the calibration source) | **Intact** |
| LB#15 cleared | NFR2 + `experiments/asyncio-timing-benchmark/` + §Tool Specification (Python through M3) | **Intact** |
| NFR2 tightening | NFR1 (monotonic-ns timestamps) + LB#15 + methodology signal floor (cited inline) | **Intact** |
| L447 Discovery module dual-stack | FR1–FR4 (discovery FRs); LB#26 (operational gate); NFR10 (concurrency host requirement); §03_phase1-validations Run 1 vs Run 2 evidence | **Intact** |
| L463 M1→M2 gate IPv6 sub-condition | L447; LB#26; §Phased Roadmap | **Intact** |
| NFR10 dual-stack + tunnel ban | NFR1 (timing precision); L447; LB#26; cost envelope L478 | **Intact** |
| L478 cost envelope v6 constraint | NFR10; LB#26; §Resource requirements | **Intact** |
| LB#26 (NEW) | L447 + NFR10 + L463 + §Discovery module (explicit "Promotion of …" annotation in the LB body) | **Intact** |
| LB#16 deferral annotation | §Phased Roadmap > M1 milestone; LB#11 (b10c socialization gates 1209k weighting) | **Intact** |

**Orphans introduced by diff:** 0
**Broken chains introduced by diff:** 0

**Full-PRD traceability:** Out of scope for this diff-aware run; already validated in original PRD creation (commit `e607d55`). Spot-check confirms every FR (FR1–FR42) has a `*owned by X module*` annotation, and every LB references the source PRD body section. Pattern intact.

**Severity:** **Pass**

**Recommendation:** Traceability chain intact. The 12 diff edits all bind cleanly to existing User Journeys / Success Criteria / Innovation areas via explicit cross-references and "Promotion of …" annotations on the new LB.

### Step 7 — Implementation Leakage

**Generic-stack scan** (React/Vue/Angular/Express/Django/Postgres/Mongo/Redis/Docker/K8s/Redux/etc.): 2 occurrences total, both **Docker**:
- L221: narrative inside Lukas's User Journey ("walks him through Docker setup, NTP discipline, …"). Pre-existing; describes the user's actual install experience. **Not a violation** — User Journey narrative is allowed to name the install vehicle.
- L509: LB#5 "Verify 'under an hour' Docker install claim". Pre-existing; the install path was decided pre-PRD and the LB validates it. **Not a violation** — capability-relevant constraint test.

**Domain-term audit** (terms introduced or extended by the 12 diff edits):

| Term | Where | Classification | Justification |
|---|---|---|---|
| `Wasserstein`, `Earth Mover's Distance`, `EMD`, `1-D Wasserstein distance over fee-rate CDFs` | FR19, FR24, L383(i), L470, LB#2, NFR2-adjacent | Methodological | `rigor.statistical_methodology` carve-out explicitly permits statistical-methodology terms. Specifying the canonical metric is required for downstream architecture and paper rigor. |
| `ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs` | FR24, LB#2 | Subject of measurement | These are the *frontends being calibrated against*, not the implementation of the detector tool. Capability-relevant — the apparatus design IS the multi-frontend matrix. Already implicit in pre-existing §Architecture; diff just makes it explicit. |
| `IPv4 + IPv6 dual-stack outbound`, `IPv6-only`, `AAAA records`, `IGW`, `egress-only IGW` | L447, L463, NFR10, LB#26 | Protocol/methodological constraint | IPv6 reachability is a *constraint* on what the tool must achieve, not a choice of how to implement it. The tool would have to handle IPv6 sockets regardless of language/framework. |
| `Hetzner CX22`, `AWS (with explicit VPC + subnet IPv6 CIDR + ENI + IGW)` | L489, NFR10 | Infra constraint specification | Names specific providers as *examples that satisfy / require config to satisfy* the dual-stack requirement. Standard pattern in research_project PRDs (see also pre-existing L478 cost envelope). |
| `Hurricane Electric`, `ZeroTier-routed exits` | NFR10 | Explicitly *banned* tunnel implementations | Negative-constraint specification with stated rationale (latency confound on NFR1 timing precision). Important to enumerate to prevent shortcuts that would silently invalidate the methodology. |
| `bin_size *= 1.1`, `refresh phase offset`, `mempool-mirror drift` | L470 | Cited algorithmic detail from external code | Cited verbatim from `spesmilo/electrumx/src/electrumx/server/mempool.py` to justify the binary "not bit-identical" finding. Evidence citation, not implementation prescription. |

**Pre-existing terms (not added by diff, listed for completeness):** SQLite/TimescaleDB (L449-L463, intentional storage decision), Python/asyncio/Rust (L454, intentional language decision per Tool Specification), Parquet (FR25, archival-format constraint per `bitcoin-data` upstream), JSON (FR26 manifest format, capability-relevant), Tor / SOCKS5 (FR3, protocol-relevant for discovery), Docker (L221 narrative, L509 LB#5).

**Severity:** **Pass** (0 strict violations; all domain terms justified by carve-outs, constraint specification, or capability-relevance)

**Recommendation:** No implementation leakage. The diff stays within methodological / constraint / measurement-subject specification — all permitted patterns for a `research_project` PRD with `rigor.statistical_methodology` carve-out.

### Step 8 — Domain Compliance

**Domain:** `scientific` (per `classification.domain` in PRD frontmatter)
**Complexity:** Medium (per `data/domain-complexity.csv`)
**Required special sections for `scientific`:** `validation_methodology`, `accuracy_metrics`, `reproducibility_plan`, `computational_requirements`

**Compliance Matrix:**

| Required section | PRD coverage | Status | Notes |
|---|---|---|---|
| `validation_methodology` | §Measurement Validity (L401–L413), §Publication Requirements > Evidentiary standards (L385), FR21 (multi-signal threshold), FR22 (baseline distribution) | **Met** | Multi-signal pre-committed threshold + baseline-noise-floor + Wasserstein metric (FR19, post-edit) — all explicit. |
| `accuracy_metrics` | NFR1 (timing precision), NFR2 (asyncio sub-ms, post-edit), FR18 (pairwise-delta variance), FR19 (Wasserstein, post-edit), FR20 (synchronized downtime) | **Met** | Diff strengthens this (NFR2 now has empirical p99 figures; FR19 names canonical metric). |
| `reproducibility_plan` | §Reproducibility Contract (L411), FR27 (bit-identical re-derivation), NFR15 (bit-identical contract), LB#25 (self-test green at M3 snapshot), LB#26 (dual-stack verified, post-edit) | **Met** | Diff strengthens this (LB#26 adds operational-environment gate that prevents silent ~28% network undercount which would invalidate reproducibility). |
| `computational_requirements` | NFR4 (CI self-test ≤30 min), NFR10 (100–500 concurrent connections, post-edit), NFR11 (~6 GB/year dataset), NFR12 (≤$500/year), NFR13 (≤512 MB resident) | **Met** | NFR10 post-edit clarifies dual-stack requirement. |

**Carve-outs declared in classification:** `rigor.statistical_methodology`, `rigor.legal_framing` — both consistent with the scientific-domain expected pattern (peer-review-grade measurement + defamation-aware publication ethics).

**Diff-aware finding:** The 12 edits *strengthen* domain compliance — they harden the validation_methodology and reproducibility_plan sections by attaching empirical evidence and operational gates that prevent silent measurement bias. No regressions.

**Severity:** **Pass** (4/4 required sections met; diff strengthens rather than weakens compliance)

**Recommendation:** Domain compliance fully met. No action needed.

### Step 9 — Project-Type Compliance

**Project Type:** `research_project` (per `classification.projectType` in PRD frontmatter)
**Definition source:** `.claude/skills/bmad-create-prd/data/project-types.csv:12` (canonical; `bmad-validate-prd`'s own CSV does not contain `research_project` — informational gap, not a PRD issue)

**Required sections (8):**

| Required section | PRD location | Status |
|---|---|---|
| `dataset_requirements` | §Research Project Specific Requirements > Dataset Requirements (L365–L379) | **Present** |
| `publication_requirements` | §Publication Requirements (L381–L389) | **Present** |
| `measurement_validity` | §Measurement Validity (L401–L413) | **Present** |
| `output_guardrails` | §Output Guardrails (L415–L425) | **Present** |
| `bilingual_parity` | §Bilingual Parity (L427–L437) | **Present** |
| `tool_spec` | §Tool Specification (Subordinate) (L439–L456) | **Present** |
| `archival_strategy` | §Publication Requirements > #### Archival Strategy (L391–L399) | **Present** |
| `reproducibility_contract` | §Measurement Validity > #### Reproducibility Contract (L411–L413) | **Present** |

**Excluded sections (6) — must NOT be present:**

| Excluded section | PRD scan | Status |
|---|---|---|
| `onboarding_funnel` | Explicitly out of scope per §Project-Type Overview L363 ("CLI ergonomics, packaging UX, onboarding funnels, and adoption metrics are explicitly out of scope") | **Absent** ✓ |
| `pricing` | No pricing content (open-source, CC BY 4.0 dataset license) | **Absent** ✓ |
| `retention_metrics` | No retention/engagement metrics | **Absent** ✓ |
| `store_compliance` | No app-store content | **Absent** ✓ |
| `visual_design` | No visual/UI design content | **Absent** ✓ |
| `marketing_strategy` | No marketing content | **Absent** ✓ |

**Compliance Summary:**
- Required Sections: **8/8 present**
- Excluded Sections Present: **0** (target: 0)
- Compliance Score: **100%**

**Diff impact:** The 12 edits strengthen `measurement_validity` (FR19, NFR2), `reproducibility_contract` (LB#26 dual-stack gate), `tool_spec` (L447 dual-stack), and `publication_requirements` (L383(i) Wasserstein tolerance band). No edit introduced any of the 6 excluded sections.

**Severity:** **Pass**

**Recommendation:** All required sections present and adequately documented. No excluded sections leaking. The diff strengthens the project-type spine.

### Step 10 — SMART Quality (FRs)

**Total Functional Requirements:** 42 (FR1–FR42)
**Scoring approach:** Detailed scoring on the 2 diff-edited FRs (FR19, FR24); aggregate spot-check on the other 40 (untouched by diff; passed validation at original PRD creation, commit `e607d55`).

**Diff-edited FRs:**

| FR | Specific | Measurable | Attainable | Relevant | Traceable | Avg | Flag |
|---|---|---|---|---|---|---|---|
| FR19 (Wasserstein metric) | 5 | 5 | 5 | 5 | 5 | **5.0** | — |
| FR24 (calibration harness) | 5 | 5 | 5 | 5 | 5 | **5.0** | — |

**FR19 detail:** Explicit formula (`∫ |F_A(x) − F_B(x)| dx` over fee-rate CDFs), explicit scope (all server pairs, configurable window), explicit grounding (cross-instance bit-identity false by construction, cited). Output is a scalar per pair per window — testable by direct computation against any fee-histogram pair. Traces to §Pre-launch validation harness via explicit cross-reference.

**FR24 detail:** Names the calibration matrix (ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs vs. 1 Bitcoin Core), the target distribution (Wasserstein same-backend), the purpose (fix cluster-membership threshold), and the two execution modes (pre-launch one-shot + recurring CI). Bounded and resourced via the binnacle's testbed plan; deferred to M1 if the M0 budget can't absorb it. Traces to LB#2 + L470 directly.

**Aggregate sample of untouched FRs (1 per FR subsection):**

| FR | Subsection | All scores ≥ 4? |
|---|---|---|
| FR1 | Server Discovery | Yes |
| FR5 | Probing & Data Collection | Yes |
| FR11 | Storage & Schema Discipline | Yes |
| FR17 | Analysis & Signal Computation | Yes |
| FR25 | Dataset Publication & Archival | Yes |
| FR31 | Output Guardrails & Disclosure | Yes |
| FR35 | Bilingual Parity | Yes |
| FR39 | Operational Health & Stewardship | Yes |

All sampled FRs follow `[Actor] can [capability]` format with `*owned by X module*` traceability annotation. No regressions detected.

**Scoring Summary:**

- All scores ≥ 3: **100%** (42/42)
- All scores ≥ 4: **100%** (42/42 — based on diff-detail + sampling pattern)
- Overall Average Score: **5.0/5.0** for diff-edited FRs; ≥4.5/5.0 estimated full PRD (consistent with original validation pass)
- Flagged FRs (any category < 3): **0**

**Severity:** **Pass** (0% flagged; threshold for Pass is <10%)

**Recommendation:** Functional Requirements demonstrate excellent SMART quality. Both diff-edited FRs score perfect on all five criteria. No improvement actions needed.

### Step 11 — Holistic Quality Assessment (diff-aware)

**Document Flow & Coherence**

- **Assessment:** Excellent
- **Strengths:** The 12 edits are surgical insertions/replacements that preserve the original voice and logical flow. New empirical anchors (587 µs, 246 vs 344, ≈28% undercount) attach to existing claims as evidentiary citations, not as new tangents. Cross-references between edited locations (FR19 ↔ §Pre-launch validation harness, NFR10 ↔ LB#26 ↔ §Discovery module) form a coherent dual-stack-and-Wasserstein narrative thread without breaking the original M0→M3 spine.
- **Areas for improvement (diff-only scope):** None. Diff is internally and externally coherent.

**Dual Audience Effectiveness**

| Audience | Aspect | Assessment |
|---|---|---|
| Humans | Executive-friendly | Empirical numbers (p99 587 µs, ≥344 servers, 28% undercount) make the diff's claims auditable by reviewers |
| Humans | Developer clarity | FR19 names the canonical metric formula; FR24 names the calibration matrix; LB#26 specifies the verification gate. No ambiguity for builders |
| Humans | Stakeholder decision-making | LB#26 surfaces an operational gate that prevents silent measurement bias — a decision pivot, not a hidden detail |
| LLMs | Machine-readable structure | All edits use the existing FR/NFR/LB pattern; Wasserstein formula in LaTeX-ish notation parseable; cross-refs explicit |
| LLMs | Architecture-readiness (downstream `bmad-create-architecture`) | Diff lifts methodology specifications (Wasserstein metric, dual-stack constraint) and infra constraints (no tunnels, native v6) directly into the architecture brief |
| LLMs | Epic/Story-readiness | LB#26 verification criteria can be lifted as a story acceptance test (`given collector deployed; when active probe runs; then ≥3 IPv6-only Electrum servers complete features+peers handshake`) |

**Dual Audience Score:** 5/5

**BMAD Principles Compliance (post-edit)**

| Principle | Status | Notes |
|---|---|---|
| Information Density | Met | Step 3 found zero anti-patterns |
| Measurability | Met | Step 5: 0/59 violations |
| Traceability | Met | Step 6: 0 orphans / 0 broken chains |
| Domain Awareness | Met | Steps 8 + 9: 4/4 + 8/8 required sections present |
| Zero Anti-Patterns | Met | Step 3 + Step 7: 0 strict violations |
| Dual Audience | Met | See dual-audience matrix above |
| Markdown Format | Met | All edits use existing pattern; new LB#26 follows the same numbered-bullet + bold-title + italic-promotion-note pattern as LB#24/LB#25 |

**Principles Met:** **7/7**

**Overall Quality Rating:** **5/5 — Excellent (post-diff)**

The diff itself is exemplary tightening: minimum-diff, evidence-anchored, internally consistent, and downstream-actionable. The pre-existing PRD was already strong (passed original validation at commit `e607d55`); the 12 edits raise the floor on three load-bearing claims (Wasserstein methodology, asyncio adequacy, dual-stack requirement) by attaching empirical citations.

### Top 3 Forward-Looking Improvements (not regressions)

1. **Run the empirical fee-histogram drift testbed (LB#2 pending half).** The Wasserstein methodology and harness purpose are now locked in (FR19, FR24, L470), but the testbed against the 5-frontend matrix that calibrates the cluster-membership threshold remains deferred. Highest-value follow-up; captured in binnacle as a separate task pending Bitcoin Core infra. *Why:* without the testbed, the threshold is not yet a defended number — the methodology is sound, the calibration is pending.

2. **Close LB#16 (1209k cross-validation) at M1 entry.** Currently annotated as deferred. Would explain the residual ~150-server gap between Phase-1's 344 dual-stack figure and 1209k's 506 headline. *Why:* downstream snowball-source weighting depends on which fraction of 1209k's 506 are real-but-unreachable, dupe-counted, or stale — material for the seed-list ingestion design.

3. **Refresh historical "bootstrap=130" anchor in `docs/project-brief.md`.** Flagged as Informational in Step 4. The brief still cites bootstrap=130 (per the prior research session); current upstream snapshot is 84. Drift will compound at the next brief edit if not addressed. *Why:* keeps the bilingual brief consistent with current upstream state and the Phase-1 V3 evidence.

### Summary

**This PRD is:** a research-grade specification with strong methodological spine and good downstream-LLM consumability; the 12 Phase-1 closeout edits strengthen its load-bearing claims with empirical evidence rather than introducing new scope.

**To make it great:** the top-3 improvements are already known follow-ups (testbed, 1209k cross-validation, brief anchor refresh) — not gaps in the current diff.

### Step 12 — Completeness

**Template Completeness**

Scan patterns: `{variable}`, `{{variable}}`, `[placeholder]`, `[INSERT]`, `TODO`, `FIXME`, `XXX`, `TBD`.

Result: **1 occurrence** at L160 in §Product Scope > Vision:

> "Duration scenario-dependent at M3 (minimum useful window TBD in Publication Requirements section)."

**Diff-aware classification:** This TBD is **pre-existing** (not introduced by the 12 Phase-1 edits). The forward pointer "TBD in Publication Requirements section" is unresolved — `§Publication Requirements` discusses M3 dataset window in concept but does not specify the minimum useful duration as a concrete number/range. **Severity: Informational** (does not gate the diff; should be closed before final M3 launch as part of LB#22 measurement-ethics or LB#1 stale-blocks-cadence work, both of which constrain the answer).

**Content Completeness by Section**

| Section | Status | Notes |
|---|---|---|
| Executive Summary | Complete | Vision, differentiator, target users (L76–L91) |
| Success Criteria | Complete | Research / Grant / Technical-Measurement / Measurable Outcomes — 4 sub-sections (L101–L141) |
| Product Scope | Complete | MVP / Growth / Vision tiers (L142–L167); 1 TBD (above) |
| User Journeys | Complete | 6 personas (Sarah, Lukas, Camila, Óscar, Ifuensan, Diego) + Journey Requirements Summary (L168–L260) |
| Functional Requirements | Complete | 42 FRs across 8 sub-sections (L522–L588) |
| Non-Functional Requirements | Complete | 17 NFRs across 7 categories + 3 cross-references (L590–L633) |
| Forced sections (per `research_project` classification) | Complete | All 8 required + 0 excluded (per Step 9 Pass) |

**Section-Specific Completeness**

- Success criteria measurable: **All** (per Step 5 Pass)
- User journey coverage: **All declared user types** (6 personas + 1 edge-case)
- FRs cover MVP scope: **Yes** — FR1-FR42 span discovery, collection, storage, analysis, publication, output guardrails, bilingual parity, operational health (entire M3 launch surface)
- NFRs have specific criteria: **All** (per Step 5 Pass)

**Frontmatter Completeness**

| Field | Status |
|---|---|
| `stepsCompleted` | Present (16 entries: 13 from create + 3 from edit) |
| `classification` (projectType, domain, complexity, projectContext, carveouts, forcedTopLevelSections, m0ArchitecturalGuardrails) | Present (full) |
| `inputDocuments` | Present (13 entries; extended in this edit cycle) |
| `date` + `lastEdited` | Present (2026-04-24 + 2026-04-26) |
| `editHistory` (added by edit workflow) | Present (1 entry) |

**Frontmatter Completeness:** **5/4 fields populated** (extra: `editHistory` added by edit workflow)

**Completeness Summary**

- Overall Completeness: **~99.8%** (645 lines of substantive content; 1 line carrying a pre-existing forward-pointer TBD)
- Critical Gaps introduced by diff: **0**
- Critical Gaps in PRD overall: **0** (the L160 TBD is Informational, not Critical)
- Minor Gaps: **1** (L160 TBD pre-existing)

**Severity:** **Pass**

**Recommendation:** PRD is complete for handoff to downstream workflows. The one pre-existing TBD at L160 should be tracked as a future closure item (recommend folding into LB#1 stale-blocks-cadence or LB#22 measurement-ethics work) but does not block the diff approval or downstream use.

---

## Final Summary

**Overall Status:** **PASS**

| Step | Check | Severity | Notes |
|---|---|---|---|
| 2 | Format detection | Pass | BMAD Standard, 6/6 core sections + 5 forced top-level sections |
| 3 | Information density | Pass | 0 anti-pattern violations across full PRD |
| 4 | Product brief coverage | Pass | Brief and PRD aligned post-edit; 1 informational note (stale "bootstrap=130" anchor in brief) |
| 5 | Measurability (FRs+NFRs) | Pass | 0/59 violations |
| 6 | Traceability | Pass | 0 orphans, 0 broken chains; diff edits all bind cleanly |
| 7 | Implementation leakage | Pass | 0 strict violations; domain terms (Wasserstein, IPv6, frontends, providers) all justified |
| 8 | Domain compliance (`scientific`) | Pass | 4/4 required sections met; diff strengthens compliance |
| 9 | Project-type compliance (`research_project`) | Pass | 8/8 required + 0/6 excluded; 100% |
| 10 | SMART quality | Pass | Diff FRs score 5.0/5.0; 0 flagged FRs across 42 |
| 11 | Holistic quality | **5/5 Excellent (post-diff)** | 7/7 BMAD principles met |
| 12 | Completeness | Pass | ~99.8%; 1 pre-existing informational TBD at L160 |

**Critical Issues:** 0
**Warnings:** 0
**Informational Notes:** 3 (none gate the diff)

1. *(Step 4)* Product Brief still cites "bootstrap=130" historically; current upstream snapshot is 84.
2. *(Step 12)* L160 TBD ("minimum useful window TBD in Publication Requirements section") is pre-existing — fold into LB#1 or LB#22 work.
3. *(Step 7)* FR24 names 5 specific Electrum frontends and NFR10 names specific cloud providers / banned tunnels — methodologically justified for a `research_project` PRD with `rigor.statistical_methodology` carve-out, but worth re-reviewing if the project ever re-classifies.

**Strengths:**

- The 12 diff edits are surgical, evidence-anchored tightenings — minimum-diff with maximum semantic clarity gain.
- Each edited claim attaches an empirical citation (587 µs, 1.71 ms, 246 vs 344, ≈28% undercount, `spesmilo/electrumx` code path).
- Traceability and downstream-LLM consumability strengthened (FR19's Wasserstein formula, FR24's calibration matrix, LB#26's verification criteria are all directly liftable into architecture / epics / stories).
- Project-type and domain spines preserved; carve-outs honored.

**Holistic Quality:** **5/5 — Excellent (post-diff)**

**Top 3 Forward-Looking Improvements (not regressions):**

1. **Run the empirical fee-histogram drift testbed** to close LB#2's pending half (Wasserstein cluster threshold calibration).
2. **Close LB#16 (1209k cross-validation)** at M1 entry to explain the residual ~150-server gap.
3. **Refresh the historical "bootstrap=130" anchor** in `docs/project-brief.md` at next brief edit.

**Recommendation:** PRD is in excellent shape post-edit. The diff is approved for downstream use (architecture, epics, stories). The 3 forward-looking improvements are known follow-ups, not gaps in the current document.
