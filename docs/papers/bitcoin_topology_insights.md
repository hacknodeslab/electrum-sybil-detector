## TL;DR

Node‑Probe is a recursive active crawler that enumerates reachable Bitcoin peers and builds full snapshots; it achieved ~99% precision and ~98% recall in longitudinal measurements from 2018–2022. The network is highly non‑random, with heavy long‑running hubs, strong community structure, and measurable deanonymization and partition risks.

----

## Node-Probe method

Node‑Probe uses active, recursive scanning to discover all reachable Bitcoin P2P peers and infer the overlay links; the project collected multi‑week snapshots of the mainnet from 2018 to 2022 to analyze topology and dynamics [1]. The approach repeatedly connects probe nodes to the network, explores neighbor lists, and aggregates reachable IPs to build full connectivity graphs with very high accuracy [1].

Substantive details and measurement results
- **Discovery mechanism** Node‑Probe performs iterative network crawling by connecting to peers and recursively querying their known-address databases to enumerate reachable nodes and potential links [1].  
- **Accuracy** Node‑Probe reports a topology inference precision of **99%** and recall of **98%** on the datasets used for validation [1].  
- **Temporal coverage** Measurements were performed as long snapshots (multi‑week) allowing study of dynamicity, churn, and long‑running nodes [1].  
- **Analyses enabled** The full snapshots were used to compute community structure, degree distributions, clustering coefficients, connectivity, and to evaluate alternative propagation designs (e.g., master‑node propagation) [1].

----

## Measurement methods comparison

This section compares Node‑Probe with other published topology discovery techniques and toolkits. The opening summarizes comparative strengths and inputs for researchers choosing a measurement method.

Comparison table of representative techniques

| Method | Core signal | Typical accuracy reported | Operational notes |
|---|---:|---:|---|
| Node‑Probe | Recursive active crawling of peer address databases | Precision 99% Recall 98% [1] | Long snapshots, multi‑week, full reachable graph [1] |
| ADDR‑marker and timing inference | Injected ADDR marker addresses + timing of ADDR gossip | Degree error <10%; connection inference ~40% (per experiment) [2] | Exploits ADDR gossip quirks; countermeasures reduce but do not eliminate inference [2] |
| ADDR‑marker with classifier (thesis) | Marker recurrence + delay analysis | Degree estimator low bias; precision/recall varied (e.g., 40%/99.8% idealized; 56%/56% realistic) [3] | Validation in simulation and testbeds; sensitivity tuning affects precision/recall [3] |
| TxProbe | Orphan transaction handling and propagation | Testnet precision and recall >90% reported [4] | Requires crafting orphan TXs; validated on testnet snapshots [4] |
| BTCmap crawler | Sniffer + peer emulation to collect local address DBs | Snapshot capture within ~56 min window (reported) [5] | Fast capture of address DBs; used to show connected snapshot in 2018 [5] |
| Active crawler / Vivisecting | Aggressive active crawling and long‑term monitoring | Large collections of nodes; geographic and stability analyses reported [6] | Useful for geography and evolution studies [6] |

Key operational contrasts
- **Signal type** Node‑Probe and BTCmap rely on active neighbor/address lists; TxProbe and ADDR‑marker exploit protocol behavior (orphan TXs, ADDR gossip) to infer links [1] [2] [4] [5].  
- **Accuracy tradeoffs** Protocol‑exploitation methods can infer links with high precision on controlled testnets but show lower precision in the wild without careful tuning [2] [3] [4].  
- **Time vs completeness** BTCmap is optimized for a quick snapshot window; Node‑Probe targets deeper, multi‑week completeness at the cost of longer measurement periods [1] [5].

----

## Topology findings and statistics

This section summarizes measured structural properties reported by Node‑Probe and complementary studies and ties them to propagation and resilience observations.

Opening summary connects measurements to structural conclusions and dynamics. Node‑Probe snapshots and complementary inference papers reveal a Bitcoin overlay far from a random uniform graph: node degrees are heterogeneous, communities are over‑represented, clustering varies locally, and a small set of stable heavy nodes underpins propagation [1] [2] [3].

Empirical structural results
- **Degree distribution** Measurements indicate a heterogeneous (heavy‑tailed) degree distribution with a fraction of high‑degree long‑running nodes acting as hubs rather than a uniform degree across peers [1] [2].  
- **Clustering** Local clustering coefficients and neighborhood patterns deviate from random expectations, showing higher-than‑random local clustering in parts of the graph [2] [1].  
- **Community structure** The network contains substantially more communities than a comparable random graph (reported as ~4× more communities than expected) [1].  
- **Connectivity and components** Full reachable snapshots show a generally connected main component in practice, but the presence of hub nodes creates fragility to targeted removal [5] [1].  
- **Persistence and dynamicity** The topology is sustained by heavy, long‑running nodes (stable peers) that dominate connectivity over time, while many peers churn frequently [1].  
- **Propagation implications** Simulated improvements such as introducing master nodes were measured to potentially reduce propagation delay by proximity up to **×25** compared with the default propagation scheme reported in Node‑Probe analyses [1].

Where specific measurement techniques produced quantitative error or performance metrics
- **Degree estimation accuracy** ADDR‑based degree estimators report relative degree errors below 10% in controlled experiments [2] [3].  
- **Connection inference accuracy** ADDR timing and marker methods yield moderate link‑inference precision (e.g., ~40–60% in realistic setups) while TxProbe reported >90% precision/recall on testnet experiments [2] [3] [4].

----

## Peer discovery and security implications

This section ties peer discovery methods and topology structure to deanonymization, partitioning, and network robustness concerns identified by Node‑Probe and related work.

Opening paragraph links measurement capability to concrete security and privacy risks. Accurate topology maps enable deanonymization and targeted attacks; multiple works demonstrate practical inference vectors and show the Bitcoin overlay is vulnerable to small sets of targeted removals [1] [2] [7].

Main security and privacy findings
- **Deanonymization and K‑anonymity risk** Node‑Probe analysis notes that a transaction originating from an autonomous system (AS) containing only a single Bitcoin node can be linked to that AS and hence to users’ IP information, undermining K‑anonymity protections [1].  
- **Topology inference as an enabler** Protocol‑exploitation techniques (ADDR markers, timing analysis, orphan‑TX probes) make it feasible to infer degrees and many links with modest resources, enabling adversaries to map the overlay in practice [2] [3] [4].  
- **Partition and robustness risk** Structural studies show that targeting a small number of highly connected peers can partition the network; specifically, targeting fewer than ten high‑degree peers can fragment Bitcoin into disconnected components in measured graphs [7].  
- **Operational countermeasures and limits** Countermeasures in the reference client (trickling, rate limiting) mitigate but do not eliminate the ability to perform topology inference; inference accuracy depends on method and environment [2] [3] [4] [1].

Practical notes for measurement and mitigation
- **Measurement resources** Many methods were shown to work with modest infrastructure (few monitor or probe machines) and short time windows in practice [2] [4] [5].  
- **Mitigation directions** Hardening address gossip, diversifying peer selection, and limiting exposed neighbor information are among the suggested defenses implicit in the literature to reduce inference and partition risk [2] [3] [1].

## References

[1]M. Essaid, S. Park, and H. Ju, “Bitcoin’s dynamic peer-to-peer topology,” International Journal of Network Management, vol. 30, no. 5, Sept. 2020, doi: 10.1002/NEM.2106.

[2]“Bitcoin Network Topology Discovery Using Timing Analysis,” Feb. 2023, doi: 10.34726/hss.2023.104666.

[3]C. Pedro, R. Matteo, D. Benoit, S. Rainer, and H. Bernhard, “All that Glitters is not Bitcoin -- Unveiling the Centralized Nature of the BTC (IP) Network,” Feb. 2022, doi: 10.48550/arxiv.2001.09105.

[4]“Topology Discovery within the Bitcoin Network,” Feb. 2024, doi: 10.34726/hss.2024.87425.

[5]S. Delgado-Segura et al., “TxProbe: Discovering Bitcoin’s Network Topology Using Orphan Transactions,” pp. 550–566, Feb. 2019, doi: 10.1007/978-3-030-32101-7_32.

[6]M. Essaid, C.-M. Lee, and H. Ju, “Characterizing the Bitcoin network topology with Node‐Probe,” International Journal of Network Management, Apr. 2023, doi: 10.1002/nem.2230.

[7]S. Shetti, S. Dsa, and M. Mudda, “An Eﬃcient Bitcoin Network Topology Discovery Algorithm for Dynamic Display,” International Research Journal on Advanced Science Hub, vol. 7, no. 08, pp. 738–745, Aug. 2025, doi: 10.47392/irjash.2025.082.