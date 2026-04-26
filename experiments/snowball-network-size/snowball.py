"""
Phase-1 validation #3 — Electrum mainnet snowball crawl.

Question: how many mainnet Electrum servers are actually reachable?

Method: BFS from the bootstrap list. For each host, RPC `server.features` (to
filter by genesis_hash) and `server.peers.subscribe` (to discover new peers).
Add new clearnet hosts to the frontier. Loop until fixed point.

Scope cuts (per binnacle 03_phase1-validations.md — throwaway one-shot):
  - Clearnet only. .onion peers are counted but not probed (no SOCKS proxy).
  - SSL only, cert validation OFF (most servers use self-signed certs).
  - 1209k HTML scrape skipped as seed (snowball reaches it transitively).
  - No retries, no DB, no resumability. One pass, write JSON, done.

Output:
  - discovered.json : { host -> {ports, features_subset, source, status} }
  - stdout         : summary table + breakdown by genesis_hash + failure reasons.
"""

import argparse
import asyncio
import collections
import json
import pathlib
import ssl
import sys
import time
from typing import Optional

HERE = pathlib.Path(__file__).resolve().parent
BOOTSTRAP = HERE / "bootstrap.json"
OUTPUT = HERE / "discovered.json"

CONNECT_TIMEOUT = 8.0
READ_TIMEOUT = 8.0
CONCURRENCY = 50
PROTOCOL_VERSION = "1.4"
BTC_MAINNET_GENESIS = (
    "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
)

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


# ---------- low-level RPC ----------

async def _rpc_session(host: str, port: int):
    """Open SSL conn, do version+features+peers, return (features, peers)."""
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port, ssl=SSL_CTX),
        timeout=CONNECT_TIMEOUT,
    )
    try:
        async def call(method: str, params: list, rid: int):
            req = json.dumps({"jsonrpc": "2.0", "id": rid,
                              "method": method, "params": params}) + "\n"
            writer.write(req.encode())
            await writer.drain()
            line = await asyncio.wait_for(reader.readline(), timeout=READ_TIMEOUT)
            if not line:
                raise ConnectionError("eof")
            resp = json.loads(line.decode())
            if "error" in resp and resp["error"] is not None:
                raise RuntimeError(f"rpc-error: {resp['error']}")
            return resp.get("result")

        # server.version negotiation — many servers refuse other calls without it
        await call("server.version", ["snowball-crawler/0.1", PROTOCOL_VERSION], 1)
        features = await call("server.features", [], 2)
        peers = await call("server.peers.subscribe", [], 3)
        return features, peers
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


# ---------- peer parsing ----------

def parse_peer_record(record) -> Optional[tuple]:
    """server.peers.subscribe entry -> (host, ssl_port_or_None, tcp_port_or_None).
    Format per protocol: [ip, hostname, [features...]] where features are strings
    like "v1.4", "s50002", "t50001", "p1000"."""
    try:
        _ip, hostname, feats = record[0], record[1], record[2]
    except Exception:
        return None
    if not isinstance(hostname, str) or not hostname:
        return None
    s_port = t_port = None
    for f in feats:
        if not isinstance(f, str) or not f:
            continue
        tag, rest = f[0], f[1:]
        if tag == "s":
            try:
                s_port = int(rest) if rest else 50002
            except ValueError:
                pass
        elif tag == "t":
            try:
                t_port = int(rest) if rest else 50001
            except ValueError:
                pass
    return (hostname, s_port, t_port)


def load_seed():
    """Bootstrap servers.json -> {host: ssl_port}."""
    raw = json.loads(BOOTSTRAP.read_text())
    out = {}
    for host, info in raw.items():
        port = info.get("s")
        if port:
            try:
                out[host] = int(port)
            except ValueError:
                pass
    return out


# ---------- crawler ----------

class Crawler:
    def __init__(self, max_hosts: int):
        self.max_hosts = max_hosts
        self.queue: asyncio.Queue = asyncio.Queue()
        self.seen: set[str] = set()
        self.results: dict[str, dict] = {}
        self.sem = asyncio.Semaphore(CONCURRENCY)
        self.in_flight = 0
        self.finished = asyncio.Event()
        self.tor_seen: set[str] = set()

    def enqueue(self, host: str, ssl_port: Optional[int],
                tcp_port: Optional[int], source: str):
        host = host.strip().lower()
        if not host:
            return
        if host.endswith(".onion"):
            self.tor_seen.add(host)
            return
        if host in self.seen:
            return
        if len(self.seen) >= self.max_hosts:
            return
        self.seen.add(host)
        port = ssl_port or 50002
        self.queue.put_nowait((host, port, source))

    async def worker(self):
        while True:
            try:
                host, port, source = await asyncio.wait_for(
                    self.queue.get(), timeout=2.0)
            except asyncio.TimeoutError:
                if self.in_flight == 0 and self.queue.empty():
                    return
                continue
            self.in_flight += 1
            try:
                async with self.sem:
                    await self._probe(host, port, source)
            finally:
                self.in_flight -= 1
                self.queue.task_done()

    async def _probe(self, host: str, port: int, source: str):
        rec = {"host": host, "port_tried": port, "source": source,
               "status": "unknown"}
        t0 = time.monotonic()
        try:
            features, peers = await _rpc_session(host, port)
            rec["status"] = "ok"
            rec["latency_s"] = round(time.monotonic() - t0, 3)
            rec["genesis_hash"] = features.get("genesis_hash")
            rec["server_version"] = features.get("server_version")
            rec["protocol_min"] = features.get("protocol_min")
            rec["protocol_max"] = features.get("protocol_max")
            rec["pruning"] = features.get("pruning")
            rec["hosts"] = features.get("hosts")
            rec["peers_advertised"] = len(peers) if peers else 0

            # Add discovered peers to frontier (only same-genesis)
            if rec["genesis_hash"] == BTC_MAINNET_GENESIS:
                for p in peers or []:
                    parsed = parse_peer_record(p)
                    if not parsed:
                        continue
                    new_host, s_port, t_port = parsed
                    self.enqueue(new_host, s_port, t_port,
                                 source=f"peer-of:{host}")
        except asyncio.TimeoutError:
            rec["status"] = "timeout"
        except (OSError, ssl.SSLError) as e:
            rec["status"] = "net-error"
            rec["error"] = f"{type(e).__name__}: {e}"
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {e}"
        rec["latency_s"] = round(time.monotonic() - t0, 3)
        self.results[host] = rec

    async def run(self):
        seed = load_seed()
        for host, port in seed.items():
            self.enqueue(host, port, None, source="bootstrap")

        workers = [asyncio.create_task(self.worker())
                   for _ in range(CONCURRENCY)]
        await asyncio.gather(*workers)


# ---------- summary ----------

def summarize(results: dict, tor_seen: set, elapsed: float, seed_count: int):
    total = len(results)
    ok = [r for r in results.values() if r["status"] == "ok"]
    by_status = collections.Counter(r["status"] for r in results.values())
    by_genesis = collections.Counter(r.get("genesis_hash") for r in ok)
    mainnet = [r for r in ok if r.get("genesis_hash") == BTC_MAINNET_GENESIS]

    print()
    print("=" * 70)
    print(f"snowball complete in {elapsed:.1f}s")
    print(f"seed (bootstrap clearnet): {seed_count}")
    print(f"hosts probed total       : {total}")
    print(f"reachable (status=ok)    : {len(ok)}")
    print(f"  └─ btc mainnet         : {len(mainnet)}")
    print(f".onion peers seen (not probed): {len(tor_seen)}")
    print()
    print("status breakdown:")
    for st, cnt in by_status.most_common():
        print(f"  {st:<12s} {cnt}")
    print()
    print("genesis_hash breakdown (reachable only):")
    for g, cnt in by_genesis.most_common():
        marker = " <- BTC mainnet" if g == BTC_MAINNET_GENESIS else ""
        print(f"  {(g or '<none>')[:32]+'…':<35s} {cnt}{marker}")
    print()

    if mainnet:
        srcs = collections.Counter(
            "bootstrap" if r["source"] == "bootstrap" else "peer-discovered"
            for r in mainnet
        )
        print("mainnet reachable hosts by discovery source:")
        for s, c in srcs.most_common():
            print(f"  {s:<20s} {c}")
        print()
        latencies = sorted(r["latency_s"] for r in mainnet if "latency_s" in r)
        if latencies:
            print(f"latency (s): min={latencies[0]:.2f} "
                  f"p50={latencies[len(latencies)//2]:.2f} "
                  f"p95={latencies[min(len(latencies)-1,int(len(latencies)*0.95))]:.2f} "
                  f"max={latencies[-1]:.2f}")
    print("=" * 70)


async def main_async(max_hosts: int):
    seed = load_seed()
    print(f"loaded {len(seed)} clearnet bootstrap hosts from {BOOTSTRAP.name}")
    print(f"concurrency={CONCURRENCY} connect_timeout={CONNECT_TIMEOUT}s "
          f"read_timeout={READ_TIMEOUT}s max_hosts={max_hosts}")

    crawler = Crawler(max_hosts=max_hosts)
    t0 = time.monotonic()
    await crawler.run()
    elapsed = time.monotonic() - t0

    OUTPUT.write_text(json.dumps({
        "meta": {
            "elapsed_s": round(elapsed, 2),
            "seed_count": len(seed),
            "tor_peers_seen": sorted(crawler.tor_seen),
            "concurrency": CONCURRENCY,
            "connect_timeout": CONNECT_TIMEOUT,
            "read_timeout": READ_TIMEOUT,
        },
        "hosts": crawler.results,
    }, indent=2, sort_keys=True))
    print(f"wrote {OUTPUT.name} ({len(crawler.results)} host records)")

    summarize(crawler.results, crawler.tor_seen, elapsed, len(seed))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-hosts", type=int, default=2000,
                    help="hard cap on hosts probed (safety stop)")
    args = ap.parse_args()
    return asyncio.run(main_async(args.max_hosts))


if __name__ == "__main__":
    raise SystemExit(main())
