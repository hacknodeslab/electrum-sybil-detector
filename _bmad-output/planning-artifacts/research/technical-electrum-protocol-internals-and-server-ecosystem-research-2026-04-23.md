---
stepsCompleted: [1]
inputDocuments: []
workflowType: 'research'
lastStep: 2
research_type: 'technical'
research_topic: 'Electrum protocol internals and server ecosystem'
research_goals: 'Primary: background/related-work for the Electrum Sybil Detector paper. Secondary: internal reference while building detection heuristics. Tertiary: public-facing explainer (Librería de Satoshi). Style: broad survey. Focus priority: (1) server implementations — ElectrumX, electrs, Fulcrum, EPS, esplora-electrs (feature matrices, forks, behavioral differences); (2) wire protocol (JSON-RPC methods, subscriptions, versioning handshake, framing over TCP/SSL/WS/WSS); (3) server discovery & peer-gossip (server.peers.subscribe, seed list, pool construction); (4) transport & deployment (TLS, .onion, reverse proxies, hosting patterns); (5) data paths (scripthash subscriptions, merkle proofs, header chain sync).'
user_name: 'Ifuensan'
date: '2026-04-23'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-04-23
**Author:** Ifuensan
**Research Type:** technical

---

## Research Overview

[Research overview and methodology will be appended here]

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** Electrum protocol internals and server ecosystem

**Research Goals (priority-ordered):**
1. Background / related-work section for the Electrum Sybil Detector research output
2. Internal reference while building detection heuristics
3. Public-facing explainer (Librería de Satoshi material)

**Focus priority:** (b) server implementations → (a) wire protocol → (c) peer discovery & gossip → (d) transport & deployment → (e) data paths. Style: broad survey.

**Technical Research Scope:**

- Architecture Analysis — server implementation architectures (ElectrumX, electrs, Fulcrum, EPS, esplora-electrs), indexer/storage design, fork lineage, maintenance state
- Implementation Approaches — language/runtime choices, DB engines, UTXO/scripthash indexing, feature parity vs. divergence
- Technology Stack (wire protocol) — JSON-RPC surface, `server.version` handshake, `blockchain.scripthash.*` subscriptions, merkle proofs, header sync, message framing
- Integration Patterns — transports (TCP/SSL/WS/WSS/Tor), `server.peers.subscribe` gossip, hardcoded seed list, client pool construction
- Performance / Operational Considerations — deployment patterns, hosting, reverse proxies, sync cost and footprint — viewed through the lens of fingerprinting surface

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-04-23
