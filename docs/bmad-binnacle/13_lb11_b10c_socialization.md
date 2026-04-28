---
lb_id: 11
status: pending
opened_at: null  # fill with ISO date when first contact sent
channel: null    # github_issue | email | other
contact_url: null  # GitHub issue URL or other reference
last_response_at: null
items_to_cover:
  framing_acceptance: pending
  bitcoin_data_conventions: pending
  path_2_handoff_optionality: pending
---

# LB#11 — b10c socialization (electrum-sybil-detector)

**Tracker for LB#11** — `docs/launch_blockers.yaml`. This entry is updated with each round of conversation with b10c. Hard prerequisite for Story 4.4 (M3 launch).

🇪🇸 Spanish mirror: [`13_lb11_b10c_socialization.es.md`](./13_lb11_b10c_socialization.es.md)

---

## Summary

LB#11 requires opening and closing a conversation with b10c on three topics:

1. **Framing** — does the "shared infrastructure clusters" + cited-only intent attribution framing read OK from their side?
2. **`bitcoin-data` conventions** — what conventions / preferences does b10c have for repo contributions?
3. **Path 2 handoff optionality** — willing to be a Path 2 handoff candidate, or prefer to be off that list?

LB#11 clears when b10c has substantively addressed all 3 items (even if the answer is "let's revisit closer to M3"). Status flips to `cleared` in `launch_blockers.yaml` with `cleared_by: docs/bmad-binnacle/13_lb11_b10c_socialization.md` + `cleared_at: <date>`.

---

## Timeline

(Update with each interaction)

- **<YYYY-MM-DD>** — first contact opened. Channel: `<github_issue|email|other>`. URL/ref: `<>`.
- **<YYYY-MM-DD>** — b10c response received. Topic addressed: `<framing|conventions|path_2|all>`. Substance: `<brief note>`.
- **<YYYY-MM-DD>** — follow-up sent / received. ...
- **<YYYY-MM-DD>** — LB#11 cleared. All 3 items addressed. Closing reference: `<>`.

---

## Conversation items checklist

| Item | Status | b10c response | Resolution |
|---|---|---|---|
| Framing acceptance | pending | — | — |
| `bitcoin-data` contribution conventions | pending | — | — |
| Path 2 handoff optionality | pending | — | — |

---

## Cleared-when criteria

LB#11 transitions from `pending` → `cleared` in `docs/launch_blockers.yaml` ONLY when ALL of the following are true:

- All 3 conversation items above have a substantive b10c response captured in the timeline
- The frontmatter status field is updated to `cleared`
- The `cleared_by` reference in `launch_blockers.yaml` points to this binnacle file
- The `cleared_at` date in `launch_blockers.yaml` matches the date of the final substantive response
- (Cross-cutting) LB#19 (same content, different PRFAQ entry) is also cleared together

---

## If LB#11 stalls

- **No response after 2 weeks:** consider follow-up email if address is known, or a brief Mastodon/Twitter ping. Do NOT escalate to other forums (PR backlog spam is anti-pattern).
- **No response after 6 weeks:** flag as `blocked` in `launch_blockers.yaml` and re-evaluate Path 2 candidate list. The project does not depend on b10c specifically — `bitcoin-data` is the canonical archive but other archival paths exist (Zenodo + arXiv are independent failure domains per AR33).
- **Negative response on framing or conventions:** capture in timeline, adjust project artifacts as needed. Negative response is still a substantive response — it clears the conversation item.
- **Path 2 opt-out:** acceptable — update `launch_blockers.yaml` notes for LB#11 + LB#19 to reflect b10c is off the Path 2 list. Identify alternative Path 2 candidate (e.g., Grundmann / TU Darmstadt orbit).

---

## Issue draft (this is what to post on `b10c/bitcoin-data`)

**Title:** `Proposal: electrum-sybil-detector dataset contribution + alignment on bitcoin-data conventions`

**Body:**

> Hi @b10c,
>
> Following up on your project-ideas issue #11 ("Can we spot public spy-Electrum servers run by Chainalysis?"), I'm building `electrum-sybil-detector` — a measurement project producing a longitudinal dataset and methodology paper on shared backend infrastructure across the public Electrum server network. I'd like to open an early conversation about contributing the dataset to `bitcoin-data` once ready (~12 months).
>
> ### Methodology technical summary
>
> The primary discriminator is **per-pair monotonic-ns delta variance on block notifications during fork-race events** (with `bitcoin-data/stale-blocks` as the canonical event source). In a fork-race, servers sharing a backend see the tip change simultaneously; independent backends scatter by Bitcoin P2P propagation latency. It's a binary natural experiment that bypasses any self-declared identity (banner, version, donation address) — properties trivially evadable.
>
> The test is **variance-of-pairwise-delta across many events**, not absolute delta on one. Collector path asymmetry is constant and drops out. This makes single-vantage findings a strict lower bound on shared-backend prevalence — community reproductions from other ASNs can only strengthen the bound, never weaken it.
>
> **Pre-committed multi-signal threshold** for published clusters: ≥2 backend-state signals + ≥1 frontend-config signal.
>
> - **Backend-state:** (a) fork-race timing variance, (b) 1-D Wasserstein distance over `mempool.get_fee_histogram` (canonical via `scipy.stats.wasserstein_distance` — cross-instance bit-identity is false by construction after reading `spesmilo/electrumx/src/electrumx/server/mempool.py:154-209`: refresh phase offset, mempool-mirror drift, adaptive bucketing `bin_size *= 1.1`), (c) synchronized downtime via interval-overlap on `connection_events`.
> - **Frontend-config:** banner, `server.features` version range, ASN, donation_address.
>
> **Statistical rigor:** Benjamini-Hochberg FDR correction, bootstrap confidence intervals on every cluster, power analysis disclosed for the M3 dataset window, noise-floor distribution from a curated independent-server set (bootstrap + permutation test). DBSCAN as primary clustering, Ward hierarchical as secondary for sensitivity analysis.
>
> **Data discipline:** monotonic-ns timestamps with wall-clock stored separately (never used in computed deltas), one canonical NTP source per collection window, append-only raw tier with `schema_version` per row, BLAKE2b-256 opaque server identifiers (hostname mapping unpublished by default).
>
> ### Pre-launch validations already cleared
>
> - **Fee-histogram determinism** — closed by code reading (2026-04-25): strongly correlated, not bit-identical, by construction. Binary question resolved; pending: empirically measure drift magnitude against a 5-frontend matrix sharing one Bitcoin Core (ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs) — same routine doubles as a recurring CI check for methodology drift between releases.
> - **asyncio resolution** — benchmark measured p99 fanout-broadcast spread = 587 µs at N=100, 1.71 ms at N=200. The hundreds-of-ms signal floor in fork-races dominates collector jitter by orders of magnitude.
> - **Real network size in dual-stack IPv4+IPv6** — snowball crawler from EC2 reached ≥344 mainnet servers. Structural conclusion: ~28% of the network is IPv6-only; an IPv4-only deployment leaves nearly a third of the observable space invisible.
>
> ### Reproducibility and archival
>
> **Reproducibility contract:** code hash + raw-input fingerprint → bit-identical derived dataset (or per-column floating-point tolerance documented). Self-test ships with every release and reviewers can re-run independently; CI budget ≤30 min on the M3 dataset window. Parquet snapshots with Zstandard compression via pyarrow.
>
> **Three-tier archival** with independent failure domains: `bitcoin-data` GitHub + Zenodo DOI + arXiv preprint. Loss of any single tier does not invalidate the contribution; the Zenodo DOI is the canonical citation handle.
>
> ### Three questions
>
> **1. Framing.** The project publishes findings as "infrastructure-shared clusters" — explicitly NOT originating operator/intent attribution. Intent-attribution language is cited-only (your issue #11 + CoinDesk 2021 materials are the only references). Does this framing read OK from your side?
>
> **2. `bitcoin-data` conventions.** I want to align from day one (directory structure, Parquet snapshot cadence, CHANGELOG format, manifest.json with code_hash + raw_input_fingerprint + Zenodo DOI). Beyond the existing residents (`stale-blocks` / `mining-pools` / `block-arrival-times`) as references, are there contribution docs / conventions / preferences I should align with?
>
> **3. Optional Path 2 handoff.** The project includes an explicit anti-success trigger: if 12 months post-launch there are citations but no grant funding, methodology stewardship hands off to a community-maintained successor. Your orbit is a pre-identified candidate. Flagging early because the conversation is more useful now than at the deadline — open to discussing whether that lands appropriately, or if you'd prefer to be off the list.
>
> ### Artifacts in the repo (draft state)
>
> - PRD: https://github.com/hacknodeslab/electrum-sybil-detector/blob/main/_bmad-output/planning-artifacts/prd.md
> - Architecture: https://github.com/hacknodeslab/electrum-sybil-detector/blob/main/_bmad-output/planning-artifacts/architecture.md
>
> No timeline pressure — the launch window is ~12 months out, but the `bitcoin-data` PR depends on this conversation, so getting it in motion early is the safer move.
>
> Thanks for `bitcoin-data` and `fork-observer` — both are referenced extensively, and we use `fork-observer` as a read-only HTTP/JSON consumer rather than reimplementing tip tracking.
>
> — Ifuensan / HackNodes Lab / Librería de Satoshi
