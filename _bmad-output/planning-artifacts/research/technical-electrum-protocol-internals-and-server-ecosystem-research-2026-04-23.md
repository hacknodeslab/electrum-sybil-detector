---
stepsCompleted: [1, 2, 3]
inputDocuments: []
workflowType: 'research'
lastStep: 4
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

---

## Technology Stack Analysis

> **Scope of this section.** The Electrum ecosystem has an unusual shape: the "technology stack" is not a cloud-vs-frameworks matrix but a small constellation of **reference implementations** (one canonical client + a handful of servers) glued by a **JSON-RPC protocol** that has no formal standards body. This section therefore diverges from the generic template and maps the stack in the terms that actually structure the ecosystem: (1) **server implementations** (the dominant axis of divergence), (2) **wire protocol & specification authority**, (3) **storage / indexing engines**, (4) **clients & libraries**, (5) **deployment & infrastructure**, (6) **adoption and population trends** — including what little public data exists on who actually runs what in the public mesh.

### 1. Server Implementations

Five implementations define the ecosystem; all others are coin-specific forks of these.

#### 1.1 ElectrumX (Neil Booth → spesmilo)

- **Origin.** `kyuupichan/electrumx` by Neil Booth, written in **Python (≥ 3.10)**, MIT-licensed. The original upstream explicitly **dropped Bitcoin** support to focus on altcoins.
  - [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx) · [spesmilo/electrumx](https://github.com/spesmilo/electrumx)
- **Canonical fork.** `spesmilo/electrumx` is the Bitcoin-maintained fork, tracked by the Electrum wallet project itself. Current docs describe **ElectrumX 1.19.0**.
  - [ElectrumX docs (spesmilo) 1.19.0](https://electrumx-spesmilo.readthedocs.io/)
- **Architecture.** Async Python, explicitly designed for **public-server deployment** (multi-user, high concurrency).
- **Storage.** LevelDB or RocksDB backend selectable (`plyvel` / `python-rocksdb`); stores block heights and tx-hashes as flat linear arrays on disk for O(1) lookup.
- **Transports.** TCP (`50001`), SSL (`50002`), and WSS (`50004`) servers built in.
  - [ElectrumX Environment Variables](https://electrumx.readthedocs.io/en/latest/environment.html)
- **Protocol range.** Min 1.4, current max **1.6** (implemented on the spesmilo line).
- **Positioning.** *"Designed with public server use in mind"* — heavier index and operational footprint than electrs, slower to sync. _Confidence: HIGH (multiple operator sources agree)._
  - [Blockstream blog: Alternatives to ElectrumX](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)

#### 1.2 electrs — romanz/electrs (Rust, upstream)

- **Repository.** [romanz/electrs](https://github.com/romanz/electrs) — *"An efficient re-implementation of Electrum Server in Rust."*
- **Recent releases.** **v0.11.0** (2025-11-17) and **v0.11.1** (2026-02-22). Release bumps rust-rocksdb to 0.36, requires dynamic RocksDB ≥ **9.10.0**, adds `blockchain.transaction.broadcast_package`. DB format breaks forward compatibility on upgrade.
  - [romanz/electrs releases](https://github.com/romanz/electrs/releases) · [RELEASE-NOTES.md](https://github.com/romanz/electrs/blob/master/RELEASE-NOTES.md)
- **Storage.** RocksDB; a *minimal* index — stores compact metadata and **re-parses blocks on the fly** to answer many queries. Trades disk for CPU.
- **Positioning.** Explicitly targeted at **personal-use** / home-node operators: *"lower storage requirements (but higher CPU usage)"*. Most commonly bundled into home-node packages.
- **Deprecation axis.** *Not* deprecated; still the upstream for all major explorer forks below.

#### 1.3 Fulcrum — cculianu/Fulcrum (C++)

- **Repository.** [cculianu/Fulcrum](https://github.com/cculianu/Fulcrum) — "A fast & nimble SPV Server for BCH, BTC, and LTC."
- **Recent releases.** **v2.1.0** (2025-11-17) — support for **Electrum Cash protocol v1.6** with BTC-targeted tweaks; binaries use **RocksDB 9.2.1** (statically linked).
  - [Fulcrum releases](https://github.com/cculianu/Fulcrum/releases) · [v2.1.0 notes](https://newreleases.io/project/github/cculianu/Fulcrum/release/v2.1.0)
- **Language & concurrency.** Modern C++20, multi-threaded + async. The 2.x series introduced a **platform-neutral** DB format (portable across Linux/macOS/Windows and big-endian).
- **Dependency on Bitcoin Core.** Will run without ZMQ, but gets **faster block notifications** when `zmqpubhashblock` is enabled.
- **Positioning.** A comprehensive index, larger than electrs but faster to build than ElectrumX; **dominant query performance** per recent benchmarks (see §6).

#### 1.4 Electrum Personal Server (EPS) — chris-belcher/electrum-personal-server

- **Repository.** [chris-belcher/electrum-personal-server](https://github.com/chris-belcher/electrum-personal-server)
- **Model.** *No indexer.* Uses **Bitcoin Core's wallet** to watch a fixed set of user-imported descriptors/xpubs and serves them over the Electrum protocol. Single-user.
- **Status.** Repo is **not formally archived** (open issues through 2024/2025), but community guidance increasingly recommends against it: *"EPS is a bit slow and you can only connect one wallet at a time, and the configuration of wallets is not user-friendly."* — multiple operator guides now default to electrs/Fulcrum instead.
  - [Bitcointalk: alternatives to EPS](https://bitcointalk.org/index.php?topic=5500087.0) · [The Road to Node: EPS](https://theroadtonode.com/bitcoin-core-extensions/electrum-personal-server)
- **Relevance to Sybil detection.** Because EPS exposes only the *user's* own addresses, an EPS instance is typically single-tenant, non-public, and **not advertised on the peer mesh** — making it largely irrelevant to Sybil population studies but important to understand as the ecosystem's "privacy-first" baseline.

#### 1.5 esplora-electrs (Blockstream) and mempool/electrs

- **Blockstream/electrs.** Fork of `romanz/electrs` powering the **Esplora** block explorer (blockstream.info). Adds an HTTP API and a different index schema. [Blockstream/electrs](https://github.com/Blockstream/electrs)
- **mempool/electrs.** Further fork of Blockstream's, powering **mempool.space**. Release **v3.0.0** (2025-09-05) is the first compatible with mempool 3.x; Mempool 3.x **no longer supports Blockstream/electrs** — production users must migrate. Indexes are **incompatible** across the three lineages (romanz, Blockstream, mempool). [mempool/electrs](https://github.com/mempool/electrs) · [mempool/electrs releases](https://github.com/mempool/electrs/releases)
- **Relevance.** These lineages typically power **public HTTP block-explorer** back-ends rather than the public Electrum peer mesh that Sybil detectors target — but the Electrum-protocol endpoint is real and operators sometimes expose it publicly.

#### 1.6 Coin-fork lineage (brief)

Most Electrum servers outside Bitcoin are direct forks: **Electron-Cash / Fulcrum-RPA** (BCH), **ElectrumSV** (BSV), **ElectrsCash** (BitcoinUnlimited, BCH, Rust), **fujicoin/esplora-electrs**, and numerous altcoin-branded ElectrumX forks. For the Sybil detector, the practical relevance is **banner-string parsing** — these forks all expose `server.version` with distinctive substrings that can be used as implementation fingerprints.

---

### 2. Wire Protocol — Specification Authority & Basics

> **Primary sources for this subsection.** The content below is derived from direct reads of the canonical spec and reference-server docs repositories: [spesmilo/electrum-protocol/docs](https://github.com/spesmilo/electrum-protocol/tree/master/docs) (spec authority) and [kyuupichan/electrumx/docs](https://github.com/kyuupichan/electrumx/tree/master/docs) (reference-server behavior). Where the text quotes the spec, it is quoted verbatim.

#### 2.1 Specification authority

There is **no BIP or formal standards body** for the Electrum protocol. The canonical spec is maintained in the **[spesmilo/electrum-protocol](https://github.com/spesmilo/electrum-protocol)** repository and rendered at **[electrum-protocol.readthedocs.io](https://electrum-protocol.readthedocs.io/en/latest/)** (currently version **1.6.x**). ElectrumX's own docs ([electrumx.readthedocs.io](https://electrumx.readthedocs.io/en/latest/protocol-methods.html)) are the de-facto server-side reference.

Fulcrum / Bitcoin Cash track a parallel **"Electrum Cash Protocol"** (currently 1.6.0) at [electrum-cash-protocol.readthedocs.io](https://electrum-cash-protocol.readthedocs.io/en/latest/protocol-methods.html) and [bitcoincash.network/electrum/](https://bitcoincash.network/electrum/protocol-methods.html). Divergences are minor but **real** for BTC servers running Fulcrum.

> **Confidence flag:** No authoritative single spec. For Sybil-detector fingerprinting, this is actually an *asset* — implementation-specific divergences in method support, return shapes, and version strings are themselves fingerprint vectors.

#### 2.2 JSON-RPC framing and ports (canonical)

_The following is taken verbatim from the canonical spec repository [spesmilo/electrum-protocol/docs/protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst)._

- **JSON-RPC version.** Both **JSON-RPC 1.0 and 2.0 are permitted**; *"use of version 2.0 is encouraged but not required."*
- **Transports.** Explicitly lists **TCP, SSL, WS, WSS**.
- **Framing.** *"Over TCP and SSL raw sockets each RPC call, and each response, MUST be terminated by a single newline to delimit messages. Websocket messages are already framed so they MUST NOT be newline terminated."*
- **Version negotiation.** *"The client must send a `server.version` RPC call as the first message on the wire, in order to negotiate the precise protocol version."* — this was **tightened in v1.6**: `server.version` **must be the first message** (see §2.3 change-log).
- **Default ports (de-facto, from ElectrumX env vars & operator practice).** `50001` — plain TCP (scheme letter **`t`**); `50002` — TLS (**`s`**); `50004` — WSS (ElectrumX). Historical HTTP/HTTPS letters **`h` / `g`** on ports 8081/8082 are legacy — modern deployments use `t`/`s` (and increasingly `.onion` + `s`).
  - [ElectrumX environment docs](https://electrumx.readthedocs.io/en/latest/environment.html) · [Electrum SSL docs](https://electrum.readthedocs.io/en/latest/ssl.html)

> **Note on transport encryption.** Unlike Bitcoin Core's P2P, which gained **BIP324** (v2 encrypted transport with ChaCha20-Poly1305 handshake) — see [bitcoinops.org BIP324](https://bitcoinops.org/en/topics/v2-p2p-transport/) / [BIP-324](https://bips.dev/324/) — **no equivalent proposal has landed for the Electrum client-server protocol.** Transport security is entirely TLS + Tor today. This is a research gap worth noting in the paper's related-work.

#### 2.3 Protocol version history (canonical change-log)

_Source: [spesmilo/electrum-protocol/docs/protocol-changes.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-changes.rst)._ Abridged.

| Version | Key changes |
|---|---|
| **1.0** | Baseline. Deprecated: `blockchain.utxo.get_address`, `blockchain.numblocks.subscribe`. |
| **1.1** | **Scripthash methods introduced** (`get_balance`, `get_history`, `get_mempool`, `listunspent`, `subscribe`) replacing UTXO-based. `server.features`, `server.add_peer` added. `server.version` negotiation semantics changed. |
| **1.2** | `verbose` param on `blockchain.transaction.get`; `raw` on `blockchain.headers.subscribe`; `server.ping` added; `blockchain.block.headers` and `mempool.get_fee_histogram` added; address-based methods deprecated. |
| **1.3** | `raw=True` default on `headers.subscribe`; `blockchain.block.header` replaces `block.get_header`; address-based methods **removed**. |
| **1.4** | `raw` removed from `headers.subscribe` (deserialized headers no longer available). `cp_height` merkle proof parameter added; `blockchain.transaction.id_from_pos` added. |
| **1.4.1–1.4.3** | AuxPoW truncation; unsubscribe functionality (1.4.2 adds `blockchain.scripthash.unsubscribe`); name resolution with proofs. |
| **1.6** | **Breaking**: `server.version` must be the first message on the wire. `blockchain.block.headers` output format changed from concatenated hex to list. `blockchain.relayfee` removed (replaced by `mempool.get_info`). `mode` param added to `blockchain.estimatefee`. `sorted` results in `scripthash.get_mempool`. |

> **Sybil-detector implication.** A server's **supported version range** (obtained from `server.version` reply and/or `server.features.protocol_min/protocol_max`) is a *first-class fingerprint vector*. Servers stuck at 1.4 vs. those at 1.6 reveal both implementation choice and operator patch cadence.

#### 2.4 Canonical method surface (authoritative)

_Source: [spesmilo/electrum-protocol/docs/protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst). "Type" = request (req) / subscription (sub). Version annotations = earliest spec version in which the method/feature appeared._

**`server.*` — server-control & peer-mesh namespace**

| Method | Type | Purpose |
|---|---|---|
| `server.version` | req | Handshake / protocol-version negotiation. **Must be first wire message (v1.6+)**. |
| `server.banner` | req | Returns human-readable banner (operator free-form text — **fingerprint vector**). |
| `server.donation_address` | req | Returns operator's donation address (**fingerprint vector**). |
| `server.features` | req | Dict of server capabilities (genesis hash, protocol_min/max, hosts map, hash_function, pruning, server_version) — **a goldmine of fingerprint data**. |
| `server.peers.subscribe` | req | Returns peer list from server's local peer DB. *Core input to Sybil detection crawls.* |
| `server.add_peer` (v1.1+) | req | Advertise self to peer. |
| `server.ping` (v1.2+) | req | Heartbeat. |

**`blockchain.*` — chain & wallet-query namespace**

| Method | Type | Purpose |
|---|---|---|
| `blockchain.headers.subscribe` | sub | Tip updates (new block headers). |
| `blockchain.block.header` (v1.3+) | req | Single header; optional merkle proof via `cp_height` (v1.4+). |
| `blockchain.block.headers` (v1.2+) | req | Multiple headers; `cp_height` (v1.4+); list-format output (v1.6+). |
| `blockchain.scripthash.subscribe` (v1.1+) | sub | Subscribe to scripthash status. |
| `blockchain.scripthash.unsubscribe` (v1.4.2+) | req | Cancel subscription. |
| `blockchain.scripthash.get_history` (v1.1+) | req | Confirmed + mempool history for scripthash. |
| `blockchain.scripthash.get_balance` (v1.1+) | req | Confirmed / unconfirmed balance. |
| `blockchain.scripthash.get_mempool` (v1.1+) | req | Mempool-only txs for scripthash (sorted v1.6+). |
| `blockchain.scripthash.listunspent` (v1.1+) | req | UTXO list for scripthash. |
| `blockchain.transaction.get` | req | Raw or decoded tx (`verbose` v1.2+). |
| `blockchain.transaction.broadcast` | req | Submit tx (error-handling changed in 1.1). |
| `blockchain.transaction.broadcast_package` | req | Atomic package broadcast (recent addition; supported in latest romanz/electrs). |
| `blockchain.transaction.get_merkle` | req | Merkle inclusion proof for a tx. |
| `blockchain.transaction.id_from_pos` (v1.4+) | req | Tx hash lookup by (height, position). |
| `blockchain.estimatefee` | req | Fee-rate estimate for target confirm depth; `mode` arg v1.6+. |

**`mempool.*` — mempool-state namespace**

| Method | Type | Purpose |
|---|---|---|
| `mempool.get_fee_histogram` (v1.2+) | req | Global mempool fee distribution. |
| `mempool.get_info` | req | Minimum fees / mempool policy (**replaces `blockchain.relayfee` in v1.6**). |

**Altcoin extensions.** `masternode.*` (Dash), `blockchain.name.*` (Namecoin), BCH/SV-specific additions — per the same methods reference, *"additional methods exist for altcoins beyond those listed above."*

> **Fingerprint-surface summary.** The methods most useful for Sybil / identity attribution — beyond banner strings — are `server.version`, `server.features`, `server.peers.subscribe`, and `server.banner`/`donation_address`. Error-message shapes for `transaction.broadcast` and timing distributions for `scripthash.*` queries are secondary signals.

---

### 3. Database & Storage Technologies

| Implementation | DB engine | Index style | Notes |
|---|---|---|---|
| ElectrumX | LevelDB *or* RocksDB (configurable) | Comprehensive (scripthash history, UTXO, tx lookup) | Adds ~21 GB txid lookup vs. electrs. Python, single-threaded parse. |
| romanz/electrs | RocksDB (≥ 9.10.0 since v0.11) | **Minimal** — stores compact metadata, **re-parses blocks** for many queries | Small disk footprint, higher steady-state CPU. |
| Fulcrum | RocksDB **9.2.1** (static) | Comprehensive, platform-neutral format in 2.x | Fastest query responses. |
| Blockstream/electrs | RocksDB | Comprehensive + HTTP/REST API | Schema incompatible with romanz. |
| mempool/electrs | RocksDB | Comprehensive + mempool-optimized | Schema incompatible with both romanz and Blockstream. |
| EPS | — (uses Bitcoin Core wallet) | No index | Single-user only. |

Benchmark synthesis (from [Sparrow "Server Performance"](https://sparrowwallet.com/docs/server-performance.html) and [Casa 2022 report](https://blog.casa.io/electrum-server-performance-report-2022/)) — _Confidence: MEDIUM, numbers are environment-dependent:_

- **Initial sync time.** electrs ≈ 1 day; Fulcrum ≈ 2–3 days; ElectrumX ≈ 1 week.
- **Index size (BTC mainnet).** ElectrumX ≈ 75 GB; Fulcrum slightly larger; electrs smaller.
- **Query latency (initial wallet load).** Fulcrum ≈ 22× faster than ElectrumX, ≈ 300× faster than electrs (whose on-demand re-parse is the bottleneck). Wallet **refresh**: Fulcrum ≈ 8× ElectrumX, 1.5× electrs.

**Block/mempool ingestion.** All servers read from a Bitcoin Core full node via RPC. Most can *optionally* use **ZMQ** (`zmqpubhashblock`, `zmqpubrawtx`) for push-style new-block notifications; Fulcrum's docs explicitly note improved behavior when linked against libzmq.
- [bitcoin/doc/zmq.md](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md) · [ZeroMQ interface primer](https://bitcoindev.network/accessing-bitcoins-zeromq-interface/)

**`txindex=1` requirement.** All full-index servers (ElectrumX, Fulcrum, Blockstream/electrs, mempool/electrs) recommend or require `txindex=1` on the underlying Bitcoin Core. romanz/electrs **does not** require `txindex=1` (compact-index design). — [ElectrumX HOWTO](https://electrumx-spesmilo.readthedocs.io/en/latest/HOWTO.html)

**Privacy leak precedent (storage-layer).** A 2022 issue documented electrs **logging scripthash values** to disk — a privacy regression later fixed: [electrs#724](https://github.com/romanz/electrs/issues/724). Relevant because it demonstrates that storage-layer behaviors leak fingerprintable operator characteristics.

---

### 4. Clients & Libraries Speaking the Protocol

**Reference client — Electrum wallet** ([spesmilo/electrum](https://github.com/spesmilo/electrum)).
- Python, Qt (PyQt) GUI; uses `libsecp256k1`. The wallet ships a **hardcoded bootstrap peer list** and then calls `server.peers.subscribe` to expand. Users can see "number of blocks and response time" per server in the selection window — i.e., the client already fingerprints servers for reliability. ([electrum FAQ](https://github.com/spesmilo/electrum-docs/blob/master/faq.rst))
- Historical scheme letters `g` / `h` (HTTP/HTTPS on 8081/8082) still appear in old docs but the modern defaults are `t` and `s`. The old `#electrum` IRC-on-Freenode side-channel for server discovery is **deprecated** — discovery today is exclusively via hardcoded seed + `server.peers.subscribe` gossip (see §5 below for the authoritative mechanism).

**Sparrow Wallet** ([sparrowwallet.com](https://sparrowwallet.com/docs/server-performance.html)).
- Java/JavaFX. *"Depends on the Electrum server protocol for retrieving and sending transaction information."* Supports public servers, private Electrum servers, and Bitcoin Core directly. Ships server-performance guidance favoring Fulcrum/electrs over ElectrumX.

**BlueWallet** (mobile, React Native). Historically uses public Electrum servers as back-end; also supports BWT. _(Confidence: MEDIUM — search results were thin on specifics; worth a follow-up in Step 5.)_

**Coin forks.** ElectrumSV (BSV), Electrum-LTC, Electron-Cash (BCH), Electrum-Dash — each speaks a lightly-diverged Electrum protocol and sources from its own coin-specific peer mesh.

**Library: rust-electrum-client** ([docs.rs reference](https://docs.rs/crate/electrs/0.1.0)) — the Rust client library companion to `romanz/electrs`. Used by wallets and indexers needing to speak Electrum protocol programmatically.

---

### 5. Deployment & Infrastructure Stack

**TLS.** Port `50002` expects TLS. **Self-signed certificates are common**; operators routinely generate them with one-liner OpenSSL invocations. The Electrum wallet supports pinning by **SSL certificate SHA-256 fingerprint** embedded in the server URI — i.e., the client ecosystem *acknowledges* that the public-CA trust model doesn't fit Electrum. Many operators front the server with **nginx/haproxy** to handle TLS termination and ACME/Let's-Encrypt.
- [Electrum SSL config](https://electrum.readthedocs.io/en/latest/ssl.html) · [Start9 enabling 50002 via nginx](https://community.start9.com/t/enabling-ssl-port-50002-in-electrs-tor/1387)

**Tor.** **Very common** deployment. Servers are typically exposed as a v3 hidden service with `HiddenServicePort 50002 127.0.0.1:50002`. Clients connect using `--proxy socks5:127.0.0.1:9050` (or 9150 for Tor Browser).
- [openoms: Tor hidden service for electrs](https://openoms.github.io/bitcoin-tutorials/electrs/Tor_Hidden_Service_for_Electrs.html)

**Node packages (distribution channel for public/semi-public Electrum servers).**
- **RaspiBlitz** ([raspiblitz/raspiblitz](https://github.com/raspiblitz/raspiblitz)) — bundles electrs and optionally Fulcrum, exposes via Tor by default.
- **Umbrel** ([apps.umbrel.com/app/electrs](https://apps.umbrel.com/app/electrs)) — electrs as a first-class app.
- **Start9 (Embassy)** ([community.start9.com](https://community.start9.com/t/enabling-ssl-port-50002-in-electrs-tor/1387)) — electrs + nginx + Tor.
- **MyNode** ([mynodebtc/mynode](https://github.com/mynodebtc/mynode)) — Electrum server packaged; historical Issue #360 notes TLS setup friction.
- **RaspiBolt / MiniBolt** ([raspibolt.org](https://raspibolt.org/guide/bonus/bitcoin/fulcrum.html), [v2.minibolt.info](https://v2.minibolt.info/bitcoin/bitcoin/electrum-server)) — curated manuals, default to Fulcrum in recent revisions.
- [RaspiBolt issue #894: "Prefer Fulcrum to Electrs"](https://github.com/raspibolt/raspibolt/issues/894) — documents the community pivot toward Fulcrum as default.

> **Sybil-detector implication.** Node-package distribution shapes the operator population: home-node kits have **default banners, default ports, default Tor config patterns, and predictable software versions tied to package release cadence.** A plausible large fraction of the "honest" public mesh is kit-derived. This is the shared-infrastructure axis the detector should exploit (matches the project's Push-3 reframing).

---

### 6. Adoption, Population Distribution & Prior Sybil Evidence

**Which implementation dominates the public BTC mesh?** No rigorous, peer-reviewed census was surfaced in the search. Operator-community signal as of late 2025 / early 2026:

- **Public-server operators skew toward Fulcrum and ElectrumX** (both designed for multi-user loads); **home-node operators skew toward electrs** (bundled by Umbrel/RaspiBlitz/MyNode).
- [Bitcointalk operator poll "Guys, what electrum server you run"](https://bitcointalk.org/index.php?topic=5433223.0) is anecdotal but consistent with the above distribution. _Confidence: LOW — self-report sample._

**Documented Sybil incident (2019).** A Sybil attack on the Electrum peer mesh was documented by **PortSwigger / Daily Swig**, reporting that **471 of 657 active nodes (≈71%)** were attacker-controlled at the time of observation. This is the foundational incident motivating detector work; detailed in [portswigger.net/daily-swig](https://portswigger.net/daily-swig/deep-dive-into-electrum-hack-reveals-70-of-network-was-controlled-by-attackers) and [Malwarebytes 2019 coverage](https://www.malwarebytes.com/blog/news/2019/04/electrum-bitcoin-wallets-under-siege).

**Historical anti-Sybil proposal.** Chris Belcher's 2015 bitcoin-dev post "[Making Electrum more anonymous](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2015-July/009653.html)" is early prior-art on client-side privacy.

**Canonical Sybil mitigations codified in ElectrumX** — directly from [kyuupichan/electrumx/docs/peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst) (verbatim quotes):

- **Seeding.** *"A list of hard-coded, well-known peers seeds the peer discovery process."* Per-coin property; aims for ≥ 4 reliable servers as ground truth.
- **Reply filtering.** *"Only one peer from each IPv4/16 netmask is returned, and the number of onion peers is limited."* (from `server.peers.subscribe` handler)
- **Subnet-aware anti-Sybil.** *"in the response to `server.peers.subscribe` calls, consider limiting the number of peers on similar IP subnets to protect against sybil attacks, and in the case of onion servers the total returned."*
- **`server.add_peer` validation.** *"A receiving server should not replace existing information about the host(s) given, but instead schedule a separate connection to verify the information for itself."* Plus: *"care should be taken with the `server.add_peer` call. Consider only accepting it once per connection. Clearnet peer requests should check the peer resolves to the requesting IP address, to prevent attackers from being able to trigger arbitrary outgoing connections from your server. This doesn't work for onion peers so they should be rate-limited."*
- **Network validation.** *"At a minimum the genesis hash should be compared (if the peer supports `server.features`), and also that the peer's reported height is within a few blocks of your own server's height."*
- **Hostname hygiene.** *"peer host names should be checked for validity before accepting them; and `localhost` should probably be rejected. If it is an IP address it should be a normal public one (not private, multicast or unspecified)."*
- **Source-rate limiting.** *"you should limit the number of new peers accepted from any single source to at most a handful, to limit the effectiveness of malicious peers wanting to trigger arbitrary outgoing connections or fill your peer tables with junk data."*
- **Connection cadence.** *"ElectrumX tries to reconnect to a good peer at least once every 24 hours, and a failing [peer] after 5 minutes but with exponential backoff. It forgets a peer entirely if a few days have passed since a successful connection."*

> **Why this matters for the detector.** These are the *defensive* heuristics implemented inside servers. A Sybil detector operating **externally** (crawling the public mesh) can validate that individual servers are respecting these limits — and a server that *does not* (e.g., returns many peers from the same /16) is itself a candidate anomaly. Crucially, the ElectrumX defenses are **intra-server**; they do nothing against an attacker that spins up many independent, well-configured servers. That is exactly the gap the shared-infrastructure attribution approach targets.

**Emerging trends (2024–2026).**
- Protocol has moved **1.4 → 1.5 → 1.6** on the spesmilo line; Fulcrum tracks via its Electrum Cash Protocol cousin.
- RocksDB version ratchet (romanz requiring 9.10; Fulcrum 9.2.1) creates **operator-version churn** — a potential timing signal for detectors.
- **No encrypted-transport upgrade** (no BIP-324 equivalent) — TLS + Tor remain the only options.
- Community default is shifting from electrs → Fulcrum on public-facing servers.

---

### Sources (consolidated for this section)

**Server implementations.**
- [kyuupichan/electrumx](https://github.com/kyuupichan/electrumx) · [spesmilo/electrumx](https://github.com/spesmilo/electrumx) · [ElectrumX docs 1.19.0](https://electrumx-spesmilo.readthedocs.io/)
- [romanz/electrs](https://github.com/romanz/electrs) · [releases](https://github.com/romanz/electrs/releases) · [RELEASE-NOTES](https://github.com/romanz/electrs/blob/master/RELEASE-NOTES.md)
- [cculianu/Fulcrum](https://github.com/cculianu/Fulcrum) · [releases](https://github.com/cculianu/Fulcrum/releases) · [v2.1.0 notes](https://newreleases.io/project/github/cculianu/Fulcrum/release/v2.1.0)
- [chris-belcher/electrum-personal-server](https://github.com/chris-belcher/electrum-personal-server)
- [Blockstream/electrs](https://github.com/Blockstream/electrs) · [mempool/electrs](https://github.com/mempool/electrs)
- [Blockstream blog: Esplora and alternatives to ElectrumX](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)
- [BitcoinUnlimited/ElectrsCash](https://github.com/BitcoinUnlimited/ElectrsCash)

**Protocol spec (primary sources).**
- [spesmilo/electrum-protocol — docs/](https://github.com/spesmilo/electrum-protocol/tree/master/docs) (canonical spec repo)
  - [protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst) · [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst) · [protocol-changes.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-changes.rst)
- [kyuupichan/electrumx — docs/](https://github.com/kyuupichan/electrumx/tree/master/docs) (reference server docs, incl. peer discovery)
  - [peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst) · [protocol.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/protocol.rst)
- [electrum-protocol readthedocs 1.6.x](https://electrum-protocol.readthedocs.io/en/latest/protocol-basics.html) · [ElectrumX readthedocs protocol-methods](https://electrumx.readthedocs.io/en/latest/protocol-methods.html) · [protocol-ideas](https://electrumx.readthedocs.io/en/latest/protocol-ideas.html)
- [Electrum 4 protocol](https://electrum.readthedocs.io/en/latest/protocol.html)
- [Electrum Cash Protocol (Fulcrum)](https://electrum-cash-protocol.readthedocs.io/en/latest/protocol-methods.html) · [bitcoincash.network/electrum](https://bitcoincash.network/electrum/protocol-methods.html)
- [BIP-324 (context for missing Electrum analogue)](https://bips.dev/324/) · [bitcoinops BIP324 topic](https://bitcoinops.org/en/topics/v2-p2p-transport/)

**Peer discovery & Sybil history.**
- [ElectrumX peer_discovery](https://electrumx.readthedocs.io/en/latest/peer_discovery.html)
- [Chris Belcher, "Making Electrum more anonymous" (2015)](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/2015-July/009653.html)
- [PortSwigger: 70% of Electrum network controlled by attackers (2019)](https://portswigger.net/daily-swig/deep-dive-into-electrum-hack-reveals-70-of-network-was-controlled-by-attackers)
- [Malwarebytes: Electrum wallets under siege (2019)](https://www.malwarebytes.com/blog/news/2019/04/electrum-bitcoin-wallets-under-siege)

**Storage, benchmarks, infrastructure.**
- [Sparrow: Server Performance](https://sparrowwallet.com/docs/server-performance.html)
- [Casa: Electrum Server Performance Report 2022](https://blog.casa.io/electrum-server-performance-report-2022/)
- [bitcoin/doc/zmq.md](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md) · [ZMQ interface primer](https://bitcoindev.network/accessing-bitcoins-zeromq-interface/)
- [Electrum SSL config](https://electrum.readthedocs.io/en/latest/ssl.html)
- [openoms Tor hidden service for electrs](https://openoms.github.io/bitcoin-tutorials/electrs/Tor_Hidden_Service_for_Electrs.html)
- [electrs#724 scripthash logging (privacy leak)](https://github.com/romanz/electrs/issues/724)

**Clients & deployment.**
- [spesmilo/electrum](https://github.com/spesmilo/electrum) · [electrum-docs/faq.rst](https://github.com/spesmilo/electrum-docs/blob/master/faq.rst)
- [Sparrow docs](https://sparrowwallet.com/docs/quick-start.html)
- [RaspiBolt: Fulcrum](https://raspibolt.org/guide/bonus/bitcoin/fulcrum.html) · [RaspiBolt issue #894](https://github.com/raspibolt/raspibolt/issues/894) · [MiniBolt: Fulcrum](https://v2.minibolt.info/bitcoin/bitcoin/electrum-server)
- [Umbrel electrs app](https://apps.umbrel.com/app/electrs) · [mynodebtc/mynode issue #360](https://github.com/mynodebtc/mynode/issues/360) · [Start9: SSL 50002](https://community.start9.com/t/enabling-ssl-port-50002-in-electrs-tor/1387)
- [Bitcointalk: which server operators run](https://bitcointalk.org/index.php?topic=5433223.0)

---

## Integration Patterns

> **Framing.** Generic microservices / API-gateway patterns do not apply to the Electrum ecosystem. The integration surface is a single **long-lived JSON-RPC session** between a light-client wallet and a server, plus a lightweight **peer gossip mesh** between servers. This section documents the patterns that actually govern the system: interaction model, session lifecycle, client-side pool management, inter-server gossip dataflow, backend integration with Bitcoin Core, and DoS/rate-limit patterns — all read through the lens of what a Sybil detector can observe.

### 1. Interaction model — request / response / subscription

**Three interaction modes over a single TCP/TLS/WS(S) connection** — per the canonical [electrum-protocol/docs/protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst):

1. **Request/response.** Standard JSON-RPC call and single reply.
2. **Subscription.** The initial call returns a response immediately; thereafter the server emits **JSON-RPC notifications** (requests with no `id`) whenever the subscribed state changes. *"The method of the notification is the same as the method of the subscription."* Only two real subscriptions exist: `blockchain.headers.subscribe` and `blockchain.scripthash.subscribe`.
3. **Batch requests.** Supported; the spec warns: *"clients making batch requests should limit their size depending on the nature of their query, because servers will limit response size as an anti-DoS mechanism."*

**JSON-RPC version enforcement.** *"A client or server should only indicate JSON RPC 2.0 by setting the `jsonrpc` member… if it supports the version 2.0 protocol in its entirety. ElectrumX does and will expect clients advertising so to function correctly. Those that do not will be disconnected and possibly blacklisted."* — i.e., a malformed 2.0 advertisement is a **reason for server-initiated disconnect**. This is itself a fingerprint vector: different implementations are stricter or looser about this.

**Key subscription notification shapes** (from the canonical [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst) and cross-validated against [electrumx.readthedocs.io/protocol-methods](https://electrumx.readthedocs.io/en/latest/protocol-methods.html)):

- `blockchain.headers.subscribe` → notification carries `{height, hex}` — the new tip.
- `blockchain.scripthash.subscribe` → notification carries `(scripthash, status)` where `status` is a SHA-256 rollup of `"tx_hash:height|tx_hash:height|…"` across the scripthash's history. **In protocol 2.0 the semantics change** — `status` becomes the last confirmed `tx_hash`, with mempool diffs delivered via a new `mempool.changes()` notification. This version-dependent semantics is a live **compatibility fingerprint** across the mesh.

> **Counterintuitive fact.** `server.peers.subscribe`, **despite its name, is not a subscription** — no notifications are sent; it is a one-shot request/response. The name is a historical artifact.

### 2. Session lifecycle & transport advertisement

**Mandatory first message: `server.version`.** From v1.6 onward, *"the `server.version` message must be the first message sent."* The return value is `[server_software_version, protocol_version]` — both strings flow directly into the **banner-based fingerprint layer** of any detector. Example: `["ElectrumX 1.2.1", "1.2"]`.

**`server.features` — the canonical capability advertisement.** Example response from [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst):

```json
{
  "genesis_hash": "000000000933ea01ad0ee984209779baaec3ced90fa3f408719526f8d77f4943",
  "hosts": {"14.3.140.101": {"tcp_port": 51001, "ssl_port": 51002}},
  "protocol_max": "1.0",
  "protocol_min": "1.0",
  "pruning": null,
  "server_version": "ElectrumX 1.0.17",
  "hash_function": "sha256"
}
```

The `hosts` dict is the server's **self-declared address map** — a single operator running multiple endpoints can advertise them all here. For the Sybil detector, this is a **direct self-disclosure channel**: operators co-advertising endpoints under one `hosts` dict are admitting identity. Conversely, disjoint `hosts` dicts that nevertheless resolve to the same ASN / certificate authority are the detector's primary inference signal.

**No client authentication.** The protocol has **no notion of client identity or authentication**. Any connecting TCP/TLS socket can query any address. The server only distinguishes clients by connection (for session state and rate-limiting). This has major privacy implications but also simplifies the detector's job — an external crawler needs nothing but a socket.

**Session duration.** Long-lived by design; Electrum wallets keep ~10 concurrent sessions open for hours to days. `server.ping` (v1.2+) is the standard keepalive.

**Idle / eviction.** Implementation-specific and operator-configurable. ElectrumX has env vars for session limits and idle timeouts ([ElectrumX env docs](https://electrumx.readthedocs.io/en/latest/environment.html)); Fulcrum and electrs expose similar knobs. Variation in eviction behavior (max session, max subscriptions-per-session, idle timeout) is **fingerprint-able** — a careful probe sequence can infer which implementation + which config preset is in use.

### 3. Client-side pool & rotation (critical Sybil-detector context)

Read from the Electrum reference client ([spesmilo/electrum](https://github.com/spesmilo/electrum) — `electrum/interface.py`, `electrum/network.py`) and [electrum FAQ](https://electrum.readthedocs.io/en/latest/faq.html):

- **Default pool size: ~10 concurrent servers.** The wallet maintains this many TLS sessions simultaneously.
- **One "main" server, the rest are "lookup"/header servers.** *"One of the servers, arbitrarily, is selected as the 'main' server. For all connected servers except one, that is all they are used for. Getting block headers from multiple sources is useful to detect lagging servers, chain splits, and forks."*
- **The main server sees the user's wallet queries** — address subscriptions, history requests, broadcast. The other ~9 only see `blockchain.headers.subscribe` traffic.
- **Spread heuristics.** `interface.py` enforces "a healthy spread of connected servers" — diversity across IPs/subnets. The **main interface is exempted from spread checks** to make failover easier.
- **Automatic vs. manual.** Default is automatic rotation (random main); users can disable via the GUI traffic-light → "Select server automatically" → right-click → "Use as server" for a fixed pinning. `--oneserver` CLI flag forces single-server mode (commonly used with Tor+`.onion`).
- **Failover.** Not graceful / stateful — the wallet just picks another server from the pool when the current main degrades.

> **Sybil-detector implication — the precise attacker value function.** A Sybil attacker maximizes expected value not by owning many servers but by maximizing the probability of being **picked as the `main` server**. Owning 50% of the healthy-spread-deduplicated pool ≈ 50% chance of becoming main per wallet session. The 2019 attack achieving ~71% of the mesh is an **upper bound** on what an uncoordinated sock-puppet fleet can achieve; an attacker investing in cross-ASN, cross-subnet, cross-CA diversity could raise that ceiling. This precisely motivates the shared-infrastructure-attribution framing of the detector: the ceiling is breached when multiple nodes *look* independent but share operator substrate.

**Server-side failover exists too.** ElectrumX can be configured with multiple `DAEMON_URL` backends and will round-robin if a bitcoind instance fails ([ElectrumX features](https://electrumx.readthedocs.io/en/latest/features.html)). This is operator-side redundancy, invisible to clients.

### 4. Inter-server peer-mesh gossip (dataflow)

Consolidating §1.6 from Step 2 and the canonical [kyuupichan/electrumx/docs/peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst):

```
┌────────────────┐    server.peers.subscribe    ┌────────────────┐
│  hard-coded    │◄────────────────────────────►│   remote       │
│  seed list     │                               │   server       │
│  (per coin,    │    server.add_peer           │   peer DB      │
│   ≥4 servers)  │◄────────────────────────────►│                │
└───────┬────────┘                               └────────────────┘
        │
        ▼
┌────────────────┐
│  local server  │   — validates new peers by:
│   peer DB      │     1. genesis_hash match (via server.features)
│                │     2. height within a few blocks of our own
│  in-memory     │     3. clearnet peers: hostname resolves to requester IP
│                │     4. onion peers: rate-limited (cannot verify IP)
│                │     5. hostname validity (reject localhost / RFC1918 / multicast)
└────────────────┘
```

**The `server.peers.subscribe` response format** — from [protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst):

```
[IP_address, hostname, features_list]
```

Example: `["107.150.45.210", "e.anonyhost.org", ["v1.0", "p10000", "t", "s995"]]`

The **compact feature-string letters** in the third element:
- `v1.0` → protocol version
- `p10000` → pruning limit (or absent if full node)
- `t` → plain TCP (default port 50001)
- `s` → SSL (default port 50002); `s995` → SSL on port 995
- `g` / `h` → legacy HTTPS / HTTP (rare today)

> **Sybil-detector data source.** `server.peers.subscribe` is the single richest observable input to a detector. Crawling it from many vantage points yields (a) the claimed topology, (b) which servers each node considers "good" enough to gossip, and (c) the compact feature strings themselves as fingerprints. Disagreements in the gossip graph (server A says B is a peer; B doesn't know A) are a *direct* anomaly signal.

**Gossip hygiene controls** (verbatim, [peer_discovery.rst](https://github.com/kyuupichan/electrumx/blob/master/docs/peer_discovery.rst)):

- One peer per IPv4/16 subnet in the reply.
- Onion peer count capped separately.
- `server.add_peer` accepted once per connection; clearnet peer IP must equal the requesting IP.
- Source-rate limit: "at most a handful of new peers accepted from any single source".

### 5. Backend integration — Bitcoin Core ↔ Electrum server

All indexing server implementations (ElectrumX, Fulcrum, electrs, Blockstream/electrs, mempool/electrs) share the same backend integration surface with Bitcoin Core:

| Channel | Direction | Purpose | Requirement |
|---|---|---|---|
| **JSON-RPC** | server → bitcoind | Block and tx data pull; mempool queries; `sendrawtransaction` relay | **Mandatory.** Typically `127.0.0.1:8332` with cookie auth. |
| **ZMQ (`zmqpubhashblock`, `zmqpubrawtx`)** | bitcoind → server | Push notification of new blocks / accepted txs | Optional but **strongly recommended** for low-latency tip updates. Fulcrum: *"will run just fine without linking against libzmq, but it will run better if you do."* |
| **`blocknotify` hook** | bitcoind → shell → server | Legacy push mechanism via user-defined shell command | Rare today; superseded by ZMQ. |
| **`txindex=1`** | bitcoind internal | Full transaction index on Core's side | **Required by ElectrumX, Fulcrum, Blockstream/electrs, mempool/electrs.** romanz/electrs does **not** require it (compact-index design). |

Sources: [bitcoin/doc/zmq.md](https://github.com/bitcoin/bitcoin/blob/master/doc/zmq.md) · [ElectrumX HOWTO](https://electrumx-spesmilo.readthedocs.io/en/latest/HOWTO.html) · [ZMQ interface primer](https://bitcoindev.network/accessing-bitcoins-zeromq-interface/) · [Fulcrum README](https://github.com/cculianu/Fulcrum).

> **Detector-relevant timing signals.** Because each server hears about new blocks via *its own* bitcoind's ZMQ or polling cadence, **new-tip propagation latency** across servers is a direct observable. Servers that reliably publish new headers within a tight time-window have **infrastructure-proximate bitcoind instances**, and those timing correlations survive across blocks. Clusters of servers that consistently co-publish within a few hundred milliseconds of each other are candidates for shared-infrastructure attribution.

### 6. DoS / rate-limit / resource-governance patterns

There is **no protocol-level rate limiting** — every implementation invents its own. This is itself a fingerprint.

- **ElectrumX.** Operator-tunable via env vars: `MAX_SESSIONS`, `MAX_SEND`, `MAX_RECV`, `COST_SOFT_LIMIT`, `COST_HARD_LIMIT`, `BANDWIDTH_UNIT_COST`. Sessions that exceed cost limits are paused then disconnected. ([env docs](https://electrumx.readthedocs.io/en/latest/environment.html))
- **Fulcrum.** Compiled-in defaults + config options `max_clients_per_ip`, `max_subscriptions_per_client`, `subs_limit`; DoS-resistant by design (C++ + threadpool) ([Fulcrum README](https://github.com/cculianu/Fulcrum)).
- **romanz/electrs.** Explicitly **not recommended for public use**; has minimal DoS hardening. ([electrs config](https://github.com/romanz/electrs/blob/master/doc/config.md)).
- **Blockstream/electrs** and **mempool/electrs.** Hardened forks tuned for public-facing explorer deployments at the cost of higher resource usage ([Blockstream blog](https://blog.blockstream.com/en-esplora-and-other-alternatives-to-electrumx/)).

> **Detector-relevant fingerprint.** The **shape of rate-limit enforcement** (whether a server slows, disconnects, or silently drops on burst; which queries cost more; whether per-IP or per-session limits dominate) is probe-able with careful load sequences and is a strong implementation fingerprint. This is a Step-5 heuristic; mentioned here to mark the seam.

### 7. Security & authentication patterns

- **Transport TLS.** Optional and **typically self-signed**. Electrum wallets support **fingerprint-pinning** (SHA-256 of the cert embedded in the server URI) because CA-based trust doesn't fit the deployment model. ([Electrum SSL docs](https://electrum.readthedocs.io/en/latest/ssl.html))
- **No peer authentication.** Servers do not authenticate one another when gossiping. The `server.add_peer` call is validated only by IP equality (clearnet) or nothing (onion).
- **No client authentication.** As noted above, any socket can query any scripthash.
- **Tor.** The default privacy mitigation; most community guides recommend the wallet connect via SOCKS5 to `127.0.0.1:9050` (system Tor) or `9150` (Tor Browser bundle). ([openoms tutorial](https://openoms.github.io/bitcoin-tutorials/electrs/Tor_Hidden_Service_for_Electrs.html))
- **No BIP-324-equivalent transport encryption** for the Electrum protocol itself — repeated for emphasis.

### 8. Privacy integration patterns

- **Scripthash obfuscation.** Subscriptions travel as SHA-256(reversed `scriptPubKey`) instead of raw addresses. This denies a naïve observer a direct address mapping — but from the server's perspective, **the set of scripthashes queried over a session precisely identifies the wallet**. Protocol privacy defenses are weak by design.
- **Multi-server header sharding** (see §3). Reduces *consistency-attack* risk (detecting chain splits) but does **not** split the address-query load.
- **Tor-only mode.** `--oneserver` + a pinned `.onion` is the best-available privacy stance for the reference client.
- **Operator-side log hygiene.** The 2022 scripthash-leak-in-logs bug ([electrs#724](https://github.com/romanz/electrs/issues/724)) showed that implementation bugs can turn server logs into a privacy sink — a recurring theme worth raising in the paper's related-work.

### Sources (additional to Step 2)

- [electrum-protocol/docs/protocol-methods.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-methods.rst) — authoritative method shapes and examples.
- [electrum-protocol/docs/protocol-basics.rst](https://github.com/spesmilo/electrum-protocol/blob/master/docs/protocol-basics.rst) — subscription semantics, batch and JSON-RPC enforcement.
- [spesmilo/electrum — interface.py](https://github.com/spesmilo/electrum/blob/master/electrum/interface.py) · [network.py](https://github.com/spesmilo/electrum/blob/master/electrum/network.py) — reference client pool behavior.
- [Electrum FAQ](https://electrum.readthedocs.io/en/latest/faq.html) — "~10 servers, one main" description.
- [Electrum Tor guide](https://electrum.readthedocs.io/en/latest/tor.html).
- [ElectrumX env vars (rate-limit knobs)](https://electrumx.readthedocs.io/en/latest/environment.html) · [ElectrumX features](https://electrumx.readthedocs.io/en/latest/features.html).
- [romanz/electrs config](https://github.com/romanz/electrs/blob/master/doc/config.md).
- [BlueWallet electrum-servers-pool](https://github.com/BlueWallet/BlueWallet/wiki/Electrum-servers-pool).
