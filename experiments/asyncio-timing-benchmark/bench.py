"""
Phase-1 validation #2 — asyncio timing-resolution benchmark.

Question: does Python asyncio's event-loop scheduling delay add >10ms of jitter
to timestamp capture when many concurrent tasks are woken near-simultaneously?

Operational context: the detector's M0 collector holds N~100 concurrent TCP/SSL
connections to Electrum servers and stamps the arrival time of each
`blockchain.headers.subscribe` notification. In a fork race, several servers
may push within a tight window. Intra-window spread of stamps must be small
relative to the real inter-server delta we want to measure.

Decision triggered (per binnacle 03_phase1-validations.md):
  - p99 spread <= 5ms  -> Python asyncio OK for M0
  - 5ms < p99 <= 15ms  -> marginal, document limitation
  - p99 > 15ms         -> rewrite collector in Rust BEFORE M0

Two probes:
  1. naked_tick : N tasks looping `t=monotonic_ns(); await sleep(0)`; measures
                  per-tick latency floor of the scheduler.
  2. fanout     : 1 producer sets an asyncio.Event simultaneously visible to N
                  consumers; each consumer stamps monotonic_ns() on wakeup.
                  Spread = max-min stamp across consumers per broadcast. This
                  is the metric that maps to the operational scenario.

Run:  python3 bench.py [--cpu-load]
"""

import argparse
import asyncio
import os
import statistics
import sys
import time
from typing import Iterable


def pcts(values: Iterable[int]) -> dict:
    xs = sorted(values)
    if not xs:
        return {}
    n = len(xs)
    return {
        "n": n,
        "min_us": xs[0] / 1_000,
        "p50_us": xs[n // 2] / 1_000,
        "p95_us": xs[min(n - 1, int(n * 0.95))] / 1_000,
        "p99_us": xs[min(n - 1, int(n * 0.99))] / 1_000,
        "max_us": xs[-1] / 1_000,
        "mean_us": statistics.mean(xs) / 1_000,
        "stdev_us": (statistics.stdev(xs) / 1_000) if n > 1 else 0.0,
    }


def fmt_row(label: str, s: dict) -> str:
    return (
        f"{label:<32s} n={s['n']:>6d}  "
        f"min={s['min_us']:>8.1f}  p50={s['p50_us']:>8.1f}  "
        f"p95={s['p95_us']:>8.1f}  p99={s['p99_us']:>8.1f}  "
        f"max={s['max_us']:>9.1f}  "
        f"mean={s['mean_us']:>8.1f}  stdev={s['stdev_us']:>8.1f}   (us)"
    )


# ---------- probe 1: naked scheduler tick ----------

async def _tick_worker(iters: int, deltas: list):
    prev = time.monotonic_ns()
    for _ in range(iters):
        await asyncio.sleep(0)
        now = time.monotonic_ns()
        deltas.append(now - prev)
        prev = now


async def probe_naked_tick(n_tasks: int, iters: int) -> dict:
    deltas: list = []
    workers = [asyncio.create_task(_tick_worker(iters, deltas)) for _ in range(n_tasks)]
    await asyncio.gather(*workers)
    return pcts(deltas)


# ---------- probe 2: fanout dispatch ----------

async def _fanout_consumer(idx: int, trigger: asyncio.Event,
                           done: asyncio.Event, rounds: int,
                           stamps: list):
    for _ in range(rounds):
        await trigger.wait()
        ts = time.monotonic_ns()
        stamps.append(ts)
        trigger.clear()
        done.set()


async def probe_fanout(n_consumers: int, rounds: int,
                       inter_round_sleep_s: float = 0.005) -> dict:
    triggers = [asyncio.Event() for _ in range(n_consumers)]
    dones = [asyncio.Event() for _ in range(n_consumers)]
    stamps: list = [[] for _ in range(n_consumers)]

    consumers = [
        asyncio.create_task(_fanout_consumer(i, triggers[i], dones[i],
                                             rounds, stamps[i]))
        for i in range(n_consumers)
    ]
    # Let consumers reach `await trigger.wait()`.
    await asyncio.sleep(0.02)

    spreads: list = []
    for r in range(rounds):
        for d in dones:
            d.clear()
        # Fire all triggers in the same event-loop iteration.
        for t in triggers:
            t.set()
        # Wait for every consumer to stamp.
        await asyncio.gather(*(d.wait() for d in dones))
        round_stamps = [stamps[i][r] for i in range(n_consumers)]
        spreads.append(max(round_stamps) - min(round_stamps))
        await asyncio.sleep(inter_round_sleep_s)

    for c in consumers:
        c.cancel()
    for c in consumers:
        try:
            await c
        except asyncio.CancelledError:
            pass

    return pcts(spreads)


# ---------- background CPU load ----------

async def _cpu_burner(stop: asyncio.Event):
    """Tight loop that yields to the event loop frequently. Simulates other
    coroutines doing work between the broadcast and the consumer wakeups."""
    x = 0
    while not stop.is_set():
        for _ in range(2_000):
            x = (x * 1103515245 + 12345) & 0x7fffffff
        await asyncio.sleep(0)


# ---------- runner ----------

async def main_async(cpu_load: bool) -> int:
    plat = f"{sys.platform} python={sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"# host: {plat}  pid={os.getpid()}  cpu_load={cpu_load}")
    print(f"# clock: time.monotonic_ns()  resolution={time.get_clock_info('monotonic').resolution*1e9:.1f}ns")
    print()

    burners: list = []
    stop = asyncio.Event()
    if cpu_load:
        burners = [asyncio.create_task(_cpu_burner(stop)) for _ in range(4)]
        # let them get scheduled
        await asyncio.sleep(0.05)

    print("== probe 1: naked scheduler tick (per-task delta around `await sleep(0)`) ==")
    for n in (1, 10, 50, 100, 200):
        s = await probe_naked_tick(n_tasks=n, iters=500)
        print(fmt_row(f"  N={n:>3d} tasks", s))
    print()

    print("== probe 2: fanout broadcast (Event.set -> spread of consumer wakeups) ==")
    for n in (1, 10, 50, 100, 200):
        s = await probe_fanout(n_consumers=n, rounds=200)
        print(fmt_row(f"  N={n:>3d} consumers, spread", s))
    print()

    if burners:
        stop.set()
        for b in burners:
            try:
                await asyncio.wait_for(b, timeout=1.0)
            except asyncio.TimeoutError:
                b.cancel()

    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu-load", action="store_true",
                    help="Run with 4 background coroutines doing CPU work between yields")
    args = ap.parse_args()
    return asyncio.run(main_async(args.cpu_load))


if __name__ == "__main__":
    raise SystemExit(main())
