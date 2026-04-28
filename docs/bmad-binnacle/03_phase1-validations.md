# Bitácora — Phase 1 Validations · electrum-sybil-detector

**Fase BMad / BMad Phase:** 1 — Analysis (closeout validations)
**Modo / Mode:** Cola de validaciones técnicas ad-hoc (no skill, off-template)
**Sesión / Session:** 2026-04-25 (en curso / in progress)
**Scope:** Tres validaciones técnicas que el technical research dejó abiertas + un testbed empírico que emerge de la primera

---

## Idiomas / Languages

- 🇪🇸 [Versión en Español](#-bitácora-en-español) — sigue abajo
- 🇬🇧 [English Version](#-log-in-english) — below the Spanish version

---

## Enlaces rápidos / Quick links

- **Bitácora anterior / Previous log:** [`02_technical-research.md`](./02_technical-research.md) — Technical research (Phase 1 main)
- **Brief actualizado / Updated brief:** [`../project-brief.md`](../project-brief.md) — secciones de riesgos suavizadas tras el verdict de fee-histogram
- **Repo upstream consultado:** [`spesmilo/electrumx`](https://github.com/spesmilo/electrumx) — fork mantenido (no `kyuupichan/electrumx`, archivado y con `compact_fee_histogram` retornando `[]` hardcoded)

---

<a id="-bitácora-en-español"></a>

## 🇪🇸 Bitácora en Español

> 🌐 [Switch to English Version](#-log-in-english)

### Contexto

El technical research (sesión 2026-04-23) dejó tres validaciones técnicas explícitamente fuera del scope ("broad survey, not deep dive"), pero marcadas como pendientes antes de la Phase 2 (`bmad-create-prd`):

1. **Fee-histogram determinism** — launch-blocker #2 del PRFAQ.
2. **Python asyncio timing resolution adequacy** — load-bearing para la captura de deltas de fork-race en M0.
3. **Real network size desde snowball** — el technical research estableció lower bound (bootstrap=130, 1209k=506) pero no el tamaño real.

Esta sesión empieza por la #1 (la más load-bearing y también la más barata si se aborda por lectura de código).

### Validación 1 — Fee-histogram determinism (cerrada)

#### Cheap-first move: lectura de código antes de montar infra

El brief asumía que la validación requería montar dos ElectrumX contra un Core y diff-ear output. Decisión: **leer primero el algoritmo en spesmilo/electrumx** — si es determinista por construcción, bit-identical está implícito; si no, el experimento empírico cambia de naturaleza.

#### Hallazgos de la lectura

**Repo equivocado descubierto temprano:** `kyuupichan/electrumx` (la rama "canonical") está archivada y su `compact_fee_histogram` en `electrumx/server/session.py:1507` retorna **`[]` hardcoded**. No implementa el método. Pivot inmediato a `spesmilo/electrumx` (default branch `master`, path `src/electrumx/server/...`).

**Algoritmo en `spesmilo/electrumx/src/electrumx/server/mempool.py:154-209`:**

```python
def _update_histogram(bin_size):
    histogram = defaultdict(int)
    for tx in self.txs.values():
        fee_rate = math.floor(10 * tx.fee / tx.size) / 10  # 0.1 sat/vB res
        histogram[fee_rate] += tx.size
    return _compress_histogram(histogram, bin_size)

def _compress_histogram(histogram, bin_size):
    for fee_rate, size in sorted(histogram.items(), reverse=True):
        if size > 2*bin_size: emit prev; bin_size *= 1.1
        cum_size += size
        if cum_size > bin_size: emit (fee_rate, cum_size); bin_size *= 1.1
```

Defaults para Bitcoin (`lib/coins.py:103-105` y `:305`): `MEMPOOL_HISTOGRAM_REFRESH_SECS = 120`, `MEMPOOL_COMPACT_HISTOGRAM_BINSIZE = 30_000` vbytes. RPC sirve `cached_compact_histogram`, no recomputa on-demand.

#### Verdict

**Determinismo del algoritmo: SÍ** dado un mempool snapshot idéntico (sorted explícito, floor determinista, sin random/time/thread-order).

**Determinismo cross-instancia: NO por construcción.** Tres fuentes irreducibles:

1. **Cache refresh phase offset** — cada instancia corre su `_refresh_histogram` loop sin sincronización inter-instancia. Refresca cada 120s con fase arbitraria.
2. **Mirror local del mempool** (`self.txs`) — actualizado por loop independiente que pollea bitcoind. Latencia/orden divergen entre instancias antes incluso de computar.
3. **Bucketing adaptativo** (`bin_size *= 1.1` por bucket emitido) — micro-diferencias en input cascadean a fronteras de bucket distintas.

#### Implicación load-bearing para el PRFAQ

- "Bit-identical" es **falso por diseño**, no es cuestión de medir empíricamente.
- "Strongly correlated" es **verdadero por construcción**: misma fuente de mempool (un bitcoind), misma fórmula determinista, mismo refresh interval. Diferencia acotada por rate de churn del mempool en ≤120s.
- El discriminador del detector **no puede ser igualdad** — tiene que ser **distancia Wasserstein** (1-D Earth Mover's Distance: `∫ |F_A(x) - F_B(x)| dx` sobre las CDFs). Esto ya estaba en el roadmap M3, queda confirmado como única opción válida.

#### Acción tomada en el brief

Suavizado en `docs/project-brief.md:74` (ES) y `:139` (EN). Antes: "verificación empírica pendiente: …si no es bit-idéntico, se suaviza el lenguaje". Después: "fuertemente correlacionado, no bit-idéntico — launch-blocker #2 resuelto por lectura de código" + cita del path + reframe del testbed empírico como medición de magnitud (no como decisión binaria) + matriz de 5 frontends nombrada.

### Tarea derivada — Testbed empírico (abierto, no cerrado)

La lectura de código cerró la decisión binaria pero **abrió** la pregunta cuantitativa: ¿cuánto drift hay realmente? El testbed empírico responde:

- **Setup:** 1 Bitcoin Core (signet o mainnet, decisión pendiente — signet evita IBD pero mempool más esparso) + 5 frontends contra ese Core:
  - ElectrumX × 2 (mismo binario, configs idénticas, distintos puertos) → mide drift cross-instancia same-impl (noise floor)
  - Fulcrum (C++20)
  - mempool-electrs (Rust, fork-of-fork)
  - Blockstream/electrs (Rust, parent fork de mempool-electrs)
- **Probing:** script polling `mempool.get_fee_histogram` cada 30s a los 5, timestamp local, dump a CSV.
- **Run:** 24-48h.
- **Análisis:** distancia Wasserstein 1-D pairwise + plot temporal del drift.
- **Output esperado:** banda empírica `(W_min_same_backend, W_max_same_backend)` que fija el threshold de cluster del detector.

Por qué 5 frontends y no solo 2:
- 2× ElectrumX idénticos → noise floor del signal (drift inherente)
- ElectrumX vs Fulcrum vs mempool-electrs → signal real cross-impl (lo que el detector verá en el wild)
- Blockstream/electrs vs mempool-electrs → diff fork-vs-fork-of-fork (¿ha driftado el bucketing tras forks sucesivos?)

Pendiente de coordinar cuando se monte la infra (usuario tiene experiencia operativa con Bitcoin Core).

### Validación 2 — asyncio timing resolution (cerrada)

**Pregunta concreta:** ¿el scheduling delay del event loop de Python asyncio añade >10ms de jitter a la captura de timestamps en `blockchain.headers.subscribe`?

**Por qué importa:** la metodología principal del detector es la **varianza del delta pairwise de notificación de bloque en fork-races**. Si el jitter del collector domina el delta real entre servidores, el signal se pierde en noise antes de llegar a la métrica.

**Cheap-first move ejecutado:** script benchmark de ~200 LOC en [`experiments/asyncio-timing-benchmark/bench.py`](../../experiments/asyncio-timing-benchmark/bench.py). Dos probes:

1. **Naked scheduler tick:** N tasks haciendo `monotonic_ns / await sleep(0)` en bucle; mide overhead por tick del event loop.
2. **Fanout broadcast (la métrica que importa):** un productor llama `Event.set()` sobre N triggers en la misma iteración del loop; cada consumidor stampa `monotonic_ns()` al despertar. **Spread intra-broadcast = max − min de stamps por broadcast** — modela el escenario operativo donde varios servers notifican un bloque dentro de una ventana corta.

`SO_TIMESTAMPNS` se descartó: es Linux-only, no existe en Darwin (host de medición). `loop.time()` se redujo a `time.monotonic_ns()` directo: en CPython la primera es la segunda bajo el capó, pero `_ns` evita la pérdida de precisión del float.

#### Resultados (Apple Silicon, Python 3.14.3, Darwin 25.3.0)

**Spread fanout — la métrica de decisión** (idle, sin CPU load):

| N consumers | min | p50 | p95 | **p99** | max |
|---|---:|---:|---:|---:|---:|
| 10  | 18.1 µs | 35.2 µs | 60.1 µs | **141 µs** | 142 µs |
| 50  | 54.2 µs | 147 µs  | 266 µs  | **339 µs** | 419 µs |
| **100** | 113 µs  | 323 µs  | 516 µs  | **587 µs** | 728 µs |
| 200 | 366 µs  | 612 µs  | 1.06 ms | **1.71 ms**| 1.77 ms|

Con `--cpu-load` (4 burners en background, simulan otros coroutines trabajando entre yields) el spread baja contraintuitivamente (los consumers ya están runnable cuando llega el broadcast, se drenan back-to-back), pero el per-tick sube a ~550 µs:

| N=100 | spread p99 (idle) | spread p99 (cpu-load) | tick p99 (cpu-load) |
|---|---:|---:|---:|
|  | **587 µs** | 101 µs | 592 µs |

#### Verdict

**🟢 GREEN — Python asyncio OK para M0.**

- Umbral de la decisión: p99 ≤ 5 ms.
- Worst case medido (N=200, idle): **1.71 ms p99** → ~3× por debajo del umbral.
- Caso operativo (N=100): **587 µs p99** → ~8× por debajo del umbral.
- El signal de fork-race que se quiere medir vive en decenas/cientos de ms de delta inter-server. El jitter del collector al sub-milisegundo no domina ese signal.

#### Implicación load-bearing para el roadmap

- M0 collector se mantiene en Python/asyncio (decisión consistente con `tech-stack.md`).
- No hay que reescribir en Rust antes de M0; queda como optimización opcional para M1+ si se hace polling intensivo de muchos servers.
- La medición es un **upper bound** del jitter del scheduler: el broadcast vía `Event.set()` hace que N tasks sean runnable en el mismo tick — caso peor para drenado secuencial. La realidad TCP es mejor: las llegadas se distribuyen en el tiempo y el selector amortigua.

#### Limitaciones explícitas

- Host único (Apple Silicon, Darwin). En servidor Linux x86 los números pueden variar pero la conclusión (jitter << 5 ms) es robusta a la diferencia de plataforma.
- No se midió con I/O TCP real, solo con `asyncio.Event` como worst-case proxy. Una validación más fiel se haría tras M0 cuando exista el collector real, pero ya no es load-bearing porque el margen es enorme.
- Python 3.14 — versiones anteriores (3.11, 3.12) tienen scheduler ligeramente distinto. Si se fija a 3.11/3.12 en producción conviene re-correr el bench (5 min de trabajo).

### Validación 3 — Real network size por snowball (cerrada)

**Pregunta:** ¿cuántos servidores Electrum mainnet hay realmente accesibles?

**Datos previos:** bootstrap=130 (per `02_technical-research.md`), 1209k=506. Tor delta no cuantificado.

**Cheap-first move ejecutado:** [`experiments/snowball-network-size/snowball.py`](../../experiments/snowball-network-size/snowball.py) (~210 LOC). BFS desde bootstrap, dos RPCs por host (`server.features` + `server.peers.subscribe`), filtro por `genesis_hash == BTC mainnet`, dedup por hostname.

**Recortes vs plan original:**
- 1209k scrape NO usado como seed — el snowball alcanza transitivamente. Si hubiese gap grande con 1209k, se reabre.
- `.onion` peers **vistos pero no probados** (no SOCKS proxy disponible) — Tor delta queda lower-bounded, no resuelto.
- SSL only (port 50002 family), cert validation off. Hosts SSL-disabled-only se pierden (presumibles ~12, ver más abajo).

#### Hallazgo previo (pre-resultado): bootstrap real ≠ 130

Re-fetché `electrum/chains/mainnet/servers.json` (2026-04-25): **84 entries / 14 .onion / 70 clearnet** (de los cuales 79 advertisean puerto SSL). El "130" del `02_technical-research.md` no corresponde a este archivo en su estado actual — pudo ser otro snapshot, otra ruta, o un typo en la sesión previa. Anotado para no volver a citar 130.

#### Run 1 — 2026-04-25, IPv4 only (Mac local)

| Métrica | Valor |
|---|---:|
| Seed clearnet (bootstrap.json, con `s` port) | 79 |
| Hosts probados (incluye discovered) | 395 |
| Reachable BTC mainnet | 246 |
| └─ Vivos del bootstrap | 35 (de 79 → 44%) |
| └─ Descubiertos vía `server.peers.subscribe` | 211 |
| `.onion` peers vistos (no probados) | 43 |
| Failures totales | 149 |

Breakdown de failures: **98 IPv6 `[Errno 65] No route to host`** (limitación local, ver memoria `user_local_env_ipv6.md`), 25 timeout, 14 gaierror DNS-dead, 12 ConnectionRefused.

#### Run 2 — 2026-04-26, IPv4+IPv6 (EC2 t3.micro Ubuntu, dual-stack)

Para resolver el sesgo IPv4 del Run 1 se reejecutó el snowball desde una instancia EC2 con dual-stack. Wrapper ejecutivo: [`experiments/snowball-network-size/run-on-aws.sh`](../../experiments/snowball-network-size/run-on-aws.sh) (pre-flight v6 + scp + ssh exec + scp back, ~110 LOC). El script `snowball.py` corrió **idéntico**, sin modificaciones.

| Métrica | Valor (Run 2) | Δ vs Run 1 |
|---|---:|---:|
| Seed clearnet | 79 | 0 |
| Hosts probados | 394 | −1 |
| **Reachable BTC mainnet** | **344** | **+98** |
| └─ Vivos del bootstrap | 35 | 0 |
| └─ Descubiertos vía peer-subscribe | 309 | +98 |
| `.onion` peers vistos | 43 | 0 |
| Failures totales | 50 | −99 |

**El delta +98 coincide exactamente con los 98 IPv6 unreachables del Run 1** — confirmación causal completa, no había servers muertos en ese bucket. Eran IPv6 reales que la red local del Mac no podía alcanzar.

Breakdown de failures restantes (Run 2): 25 timeout (slow/filtered), 11 gaierror (DNS-dead reales), 11 ConnectionRefused (puerto 50002 cerrado — posibles TCP-only, no probados), 2 OSError dual-stack, 1 ConnectionError eof.

#### Verdict

**🟢 Cifra defendible: ≥ 344 servidores BTC mainnet clearnet reachable** vía cliente Electrum estándar dual-stack (snowball 2026-04-26). Bandas finales:

- **Floor probado:** 344 (IPv4+IPv6, SSL+RPC standard).
- **Plausible mid (con TCP fallback):** 344 + 13 (11 conn-refused + 2 dual-stack errors, posibles TCP-only) ≈ **357**.
- **Tor lower bound:** ≥ 43 `.onion` distintos advertised (no probados, requiere SOCKS).
- **Headline 1209k = 506:** gap residual de ~149-162 servers no reconcilable. Hipótesis posibles, en orden de probabilidad: (a) inclusión de `.onion` o servers stale en su contador, (b) probe más permisivo que el nuestro (header-only sin handshake completo), (c) entradas dup IPv4/IPv6/hostname para el mismo operador.

**Conclusión:** la red es **~4× el bootstrap, ~⅔ del headline 1209k**. La cifra para el paper es **"≥344 servers BTC mainnet clearnet reachable to a standard Electrum client (snowball 2026-04-26, dual-stack)"** con la metodología documentada.

#### Implicación load-bearing para el roadmap

- **Tamaño de problema confirmado.** El detector M1 va a operar contra ~344-400 servers steady-state. Manejable: 100 conexiones concurrentes (M0 budget) cubre la mayoría del top de la red por uptime; el snowball periódico puede expandir el pool a 350+ con tuning.
- **Bootstrap-dependency es problema operativo conocido**: 56% del bootstrap está muerto. M0 debe combinar bootstrap+snowball desde día 1 (no esperar a M1).
- **IPv6 reachability es load-bearing**: 98 hosts (≈28% del census) son IPv6-only o IPv6-preferred. **Confirmado empíricamente**: misma red en mismo momento, host IPv4-only ve 246, host dual-stack ve 344. M1 collector debe desplegarse en infra dual-stack, no es opcional.
- **Tor delta sigue abierto** pero ahora con lower bound: ≥ 43 `.onion` advertised. Resolver requiere tor daemon + SOCKS, fuera de scope de Phase 1.

#### Limitaciones explícitas

- TCP fallback (port 50001) no implementado. Los 11 conn-refused del Run 2 podrían ser TCP-only.
- Snapshots puntuales (52s + 64s, separados ~24h). Server churn no medido — la coincidencia exacta del delta +98 sugiere churn bajo en ese intervalo, pero no es estudio longitudinal.
- 1209k no se cross-validó por seed; un análisis comparativo requiere parsear su HTML y se difiere a M1.

### Outputs producidos en esta sesión

| Archivo / File | Cambio / Change |
|---|---|
| [`docs/project-brief.md`](../project-brief.md) | Suavizado del bullet de fee-histogram determinism (líneas 74 ES y 139 EN). Cita del path del código + verdict + reframe del testbed. |
| [`docs/bmad-binnacle/02_technical-research.md`](./02_technical-research.md) | Forward pointer en sección "Validación pendiente fuera del informe" (ES y EN), marcando fee-histogram como cerrado y apuntando aquí. |
| [`experiments/asyncio-timing-benchmark/bench.py`](../../experiments/asyncio-timing-benchmark/bench.py) | Nuevo. Script benchmark para Validación 2 (~200 LOC). Probes: naked scheduler tick + fanout broadcast spread. |
| [`experiments/asyncio-timing-benchmark/run-idle.log`](../../experiments/asyncio-timing-benchmark/run-idle.log), [`run-cpuload.log`](../../experiments/asyncio-timing-benchmark/run-cpuload.log) | Outputs en bruto del bench: idle y con `--cpu-load`. |
| [`experiments/snowball-network-size/snowball.py`](../../experiments/snowball-network-size/snowball.py) | Nuevo. Crawler BFS para Validación 3 (~210 LOC). |
| [`experiments/snowball-network-size/run-on-aws.sh`](../../experiments/snowball-network-size/run-on-aws.sh) | Nuevo. Wrapper para ejecutar el snowball en EC2 dual-stack (pre-flight v6 + scp + ssh + scp back). |
| [`bootstrap.json`](../../experiments/snowball-network-size/bootstrap.json), [`discovered.json`](../../experiments/snowball-network-size/discovered.json), [`run.log`](../../experiments/snowball-network-size/run.log), [`discovered-aws.json`](../../experiments/snowball-network-size/discovered-aws.json), [`run-aws.log`](../../experiments/snowball-network-size/run-aws.log) | Seed + dumps Run 1 (Mac IPv4) y Run 2 (EC2 dual-stack). |
| Esta bitácora / This log | Nueva, documenta la sesión de validaciones de cierre de Phase 1. |

### Próximos pasos

1. ~~**Validación 2 (asyncio timing benchmark)**~~ — **cerrada 2026-04-25, verdict GREEN.**
2. ~~**Validación 3 (snowball script)**~~ — **cerrada 2026-04-26, ≥344 mainnet clearnet (dual-stack run).**
3. **Testbed empírico** — coordinación con setup de infra. Tarea separada porque depende de máquina operativa con Bitcoin Core.
4. **Las 3 validaciones de Phase 1 están cerradas.** Próximo paso natural: entrar en Phase 2 (`bmad-create-prd`). El testbed empírico de fee-histogram puede ejecutarse en paralelo a Phase 2 (no es bloqueante para empezar el PRD).

### Lección meta de esta sesión

El "cheap-first move" (lectura de código antes de infra) cerró el launch-blocker #2 en una hora cuando el plan original asumía un testbed multi-día. **No siempre la validación empírica es la primera opción** — cuando el código fuente está disponible y el algoritmo es contenido, leer es estrictamente más barato y más informativo que medir (te dice no solo *qué* pasa, sino *por qué*).

Pivot importante mid-validación: el repo asumido (`kyuupichan/electrumx`) estaba archivado y su implementación de fee-histogram era stub. Sin la verificación inicial habríamos planeado un testbed contra una rama muerta.

---

<a id="-log-in-english"></a>

## 🇬🇧 Log in English

> 🌐 [Cambiar a versión en Español](#-bitácora-en-español)

### Context

The technical research (2026-04-23 session) explicitly left three technical validations out of scope ("broad survey, not deep dive") but flagged them as pending before Phase 2 (`bmad-create-prd`):

1. **Fee-histogram determinism** — PRFAQ launch-blocker #2.
2. **Python asyncio timing resolution adequacy** — load-bearing for fork-race delta capture in M0.
3. **Real network size from snowball** — the technical research established a lower bound (bootstrap=130, 1209k=506) but not the actual size.

This session starts with #1 (most load-bearing and also cheapest if approached via code reading).

### Validation 1 — Fee-histogram determinism (closed)

#### Cheap-first move: read code before standing up infra

The brief assumed validation required running two ElectrumX instances against one Core and diffing output. Decision: **read the algorithm in spesmilo/electrumx first** — if deterministic by construction, bit-identity is implied; if not, the empirical experiment changes nature.

#### Findings from the reading

**Wrong repo discovered early:** `kyuupichan/electrumx` (the "canonical" branch) is archived and its `compact_fee_histogram` at `electrumx/server/session.py:1507` returns **hardcoded `[]`**. It does not implement the method. Immediate pivot to `spesmilo/electrumx` (default branch `master`, path `src/electrumx/server/...`).

**Algorithm in `spesmilo/electrumx/src/electrumx/server/mempool.py:154-209`:**

```python
def _update_histogram(bin_size):
    histogram = defaultdict(int)
    for tx in self.txs.values():
        fee_rate = math.floor(10 * tx.fee / tx.size) / 10  # 0.1 sat/vB res
        histogram[fee_rate] += tx.size
    return _compress_histogram(histogram, bin_size)

def _compress_histogram(histogram, bin_size):
    for fee_rate, size in sorted(histogram.items(), reverse=True):
        if size > 2*bin_size: emit prev; bin_size *= 1.1
        cum_size += size
        if cum_size > bin_size: emit (fee_rate, cum_size); bin_size *= 1.1
```

Bitcoin defaults (`lib/coins.py:103-105` and `:305`): `MEMPOOL_HISTOGRAM_REFRESH_SECS = 120`, `MEMPOOL_COMPACT_HISTOGRAM_BINSIZE = 30_000` vbytes. RPC serves `cached_compact_histogram`, does not recompute on-demand.

#### Verdict

**Algorithm determinism: YES** given an identical mempool snapshot (explicit `sorted()`, deterministic `floor`, no random/time/thread-order).

**Cross-instance determinism: NO by construction.** Three irreducible sources:

1. **Cache refresh phase offset** — each instance runs its own `_refresh_histogram` loop with no inter-instance synchronization. Refreshes every 120s with arbitrary phase.
2. **Local mempool mirror** (`self.txs`) — updated by an independent loop polling bitcoind. Latency/order diverge between instances even before computation.
3. **Adaptive bucketing** (`bin_size *= 1.1` per emitted bucket) — micro-differences in input cascade into different bucket boundaries.

#### Load-bearing implication for the PRFAQ

- "Bit-identical" is **false by design**, not an empirical question.
- "Strongly correlated" is **true by construction**: same mempool source (one bitcoind), same deterministic formula, same refresh interval. Difference bounded by mempool churn rate in ≤120s.
- The detector's discriminator **cannot be equality** — it must be **Wasserstein distance** (1-D Earth Mover's Distance: `∫ |F_A(x) - F_B(x)| dx` over the CDFs). Already in the M3 roadmap, now confirmed as the only valid option.

#### Action taken on the brief

Softened at `docs/project-brief.md:74` (ES) and `:139` (EN). Before: "empirical verification pending: …if not bit-identical, soften language". After: "strongly correlated, not bit-identical — launch-blocker #2 resolved via code reading" + path citation + reframe of the empirical testbed as magnitude measurement (not binary decision) + 5-frontend matrix named explicitly.

### Derived task — Empirical testbed (open, not closed)

Code reading closed the binary decision but **opened** the quantitative question: how much drift is there really? The empirical testbed answers:

- **Setup:** 1 Bitcoin Core (signet or mainnet, decision pending — signet avoids IBD but sparser mempool) + 5 frontends against that Core:
  - ElectrumX × 2 (same binary, identical configs, different ports) → measures same-impl cross-instance drift (noise floor)
  - Fulcrum (C++20)
  - mempool-electrs (Rust, fork-of-fork)
  - Blockstream/electrs (Rust, parent fork of mempool-electrs)
- **Probing:** script polls `mempool.get_fee_histogram` every 30s to all 5, local timestamp, dumps to CSV.
- **Run:** 24-48h.
- **Analysis:** pairwise 1-D Wasserstein distance + temporal drift plot.
- **Expected output:** empirical band `(W_min_same_backend, W_max_same_backend)` that fixes the detector's cluster threshold.

Why 5 frontends, not just 2:
- 2× identical ElectrumX → signal noise floor (inherent drift)
- ElectrumX vs Fulcrum vs mempool-electrs → real cross-impl signal (what the detector will see in the wild)
- Blockstream/electrs vs mempool-electrs → fork-vs-fork-of-fork diff (has bucketing drifted across successive forks?)

Pending coordination when infra is set up (user has operational experience with Bitcoin Core).

### Validation 2 — asyncio timing resolution (closed)

**Concrete question:** does Python asyncio's event-loop scheduling delay add >10ms of jitter to timestamp capture on `blockchain.headers.subscribe`?

**Why it matters:** the detector's primary methodology is the **variance of pairwise block-notification delta in fork races**. If collector jitter dominates the real inter-server delta, the signal is lost in noise before reaching the metric.

**Cheap-first move executed:** ~200 LOC benchmark in [`experiments/asyncio-timing-benchmark/bench.py`](../../experiments/asyncio-timing-benchmark/bench.py). Two probes:

1. **Naked scheduler tick:** N tasks looping `monotonic_ns / await sleep(0)`; measures per-tick event-loop overhead.
2. **Fanout broadcast (the metric that matters):** a producer calls `Event.set()` over N triggers within a single loop iteration; each consumer stamps `monotonic_ns()` on wakeup. **Intra-broadcast spread = max − min of stamps per broadcast** — models the operational scenario where several servers push a block within a tight window.

`SO_TIMESTAMPNS` was dropped: Linux-only, doesn't exist on Darwin (measurement host). `loop.time()` was reduced to direct `time.monotonic_ns()`: in CPython the former is the latter under the hood, and `_ns` avoids float precision loss.

#### Results (Apple Silicon, Python 3.14.3, Darwin 25.3.0)

**Fanout spread — the decision metric** (idle, no CPU load):

| N consumers | min | p50 | p95 | **p99** | max |
|---|---:|---:|---:|---:|---:|
| 10  | 18.1 µs | 35.2 µs | 60.1 µs | **141 µs** | 142 µs |
| 50  | 54.2 µs | 147 µs  | 266 µs  | **339 µs** | 419 µs |
| **100** | 113 µs  | 323 µs  | 516 µs  | **587 µs** | 728 µs |
| 200 | 366 µs  | 612 µs  | 1.06 ms | **1.71 ms**| 1.77 ms|

With `--cpu-load` (4 background burners simulating other coroutines doing work between yields) the spread counterintuitively drops (consumers are already runnable when the broadcast arrives, drained back-to-back), but per-tick rises to ~550 µs:

| N=100 | spread p99 (idle) | spread p99 (cpu-load) | tick p99 (cpu-load) |
|---|---:|---:|---:|
|  | **587 µs** | 101 µs | 592 µs |

#### Verdict

**🟢 GREEN — Python asyncio OK for M0.**

- Decision threshold: p99 ≤ 5 ms.
- Measured worst case (N=200, idle): **1.71 ms p99** → ~3× under threshold.
- Operational case (N=100): **587 µs p99** → ~8× under threshold.
- The fork-race signal we want to measure lives at tens-to-hundreds of ms of inter-server delta. Sub-millisecond collector jitter does not dominate it.

#### Load-bearing implication for the roadmap

- M0 collector stays in Python/asyncio (consistent with `tech-stack.md`).
- No need to rewrite in Rust before M0; remains an optional optimization for M1+ if heavy polling across many servers becomes a bottleneck.
- The measurement is an **upper bound** on scheduler jitter: broadcast via `Event.set()` makes N tasks runnable in the same tick — worst case for sequential drain. Real TCP arrivals spread in time and the selector smooths things.

#### Explicit limitations

- Single host (Apple Silicon, Darwin). On Linux x86 servers numbers will differ but the conclusion (jitter << 5 ms) is robust to platform variance.
- Not measured against real TCP I/O, only `asyncio.Event` as a worst-case proxy. A higher-fidelity validation would happen post-M0 against the real collector, but it is no longer load-bearing — the margin is huge.
- Python 3.14 — earlier versions (3.11, 3.12) have a slightly different scheduler. If production pins 3.11/3.12 it's worth re-running the bench (5 min of work).

### Validation 3 — Real network size via snowball (closed)

**Question:** how many mainnet Electrum servers are actually reachable?

**Prior data:** bootstrap=130 (per `02_technical-research.md`), 1209k=506. Tor delta unquantified.

**Cheap-first move executed:** [`experiments/snowball-network-size/snowball.py`](../../experiments/snowball-network-size/snowball.py) (~210 LOC). BFS from bootstrap, two RPCs per host (`server.features` + `server.peers.subscribe`), filter by `genesis_hash == BTC mainnet`, dedup by hostname.

**Cuts vs original plan:**
- 1209k scrape NOT used as seed — snowball reaches it transitively. If a large gap remained vs 1209k, this would be reopened.
- `.onion` peers **seen but not probed** (no SOCKS proxy available) — Tor delta lower-bounded, not resolved.
- SSL only (port 50002 family), cert validation off. SSL-disabled-only hosts missed (presumed ~12, see below).

#### Pre-result finding: real bootstrap ≠ 130

Re-fetched `electrum/chains/mainnet/servers.json` (2026-04-25): **84 entries / 14 .onion / 70 clearnet** (of which 79 advertise an SSL port). The "130" from `02_technical-research.md` does not match this file in its current state — could be a different snapshot, different path, or a typo in the prior session. Noted to avoid re-citing 130.

#### Run 1 — 2026-04-25, IPv4 only (Mac local)

| Metric | Value |
|---|---:|
| Clearnet seed (bootstrap.json with `s` port) | 79 |
| Hosts probed (incl. discovered) | 395 |
| Reachable BTC mainnet | 246 |
| └─ Alive from bootstrap | 35 (of 79 → 44%) |
| └─ Discovered via `server.peers.subscribe` | 211 |
| `.onion` peers seen (not probed) | 43 |
| Total failures | 149 |

Failure breakdown: **98 IPv6 `[Errno 65] No route to host`** (local limitation, see memory `user_local_env_ipv6.md`), 25 timeout, 14 gaierror DNS-dead, 12 ConnectionRefused.

#### Run 2 — 2026-04-26, IPv4+IPv6 (EC2 t3.micro Ubuntu, dual-stack)

To remove the IPv4 bias of Run 1, the snowball was re-executed from a dual-stack EC2 instance. Driver wrapper: [`experiments/snowball-network-size/run-on-aws.sh`](../../experiments/snowball-network-size/run-on-aws.sh) (v6 pre-flight + scp + ssh exec + scp back, ~110 LOC). The `snowball.py` script ran **unchanged**.

| Metric | Value (Run 2) | Δ vs Run 1 |
|---|---:|---:|
| Clearnet seed | 79 | 0 |
| Hosts probed | 394 | −1 |
| **Reachable BTC mainnet** | **344** | **+98** |
| └─ Alive from bootstrap | 35 | 0 |
| └─ Discovered via peer-subscribe | 309 | +98 |
| `.onion` peers seen | 43 | 0 |
| Total failures | 50 | −99 |

**The +98 delta exactly matches the 98 IPv6 unreachables from Run 1** — full causal confirmation, those weren't dead servers in that bucket. They were real IPv6 hosts the local Mac network couldn't reach.

Remaining failures (Run 2) breakdown: 25 timeout (slow/filtered), 11 gaierror (real DNS-dead), 11 ConnectionRefused (port 50002 closed — possible TCP-only, not probed), 2 OSError dual-stack, 1 ConnectionError eof.

#### Verdict

**🟢 Defensible figure: ≥ 344 reachable BTC mainnet clearnet servers** from a standard dual-stack Electrum client (snowball 2026-04-26). Final bands:

- **Proven floor:** 344 (IPv4+IPv6, SSL+RPC standard).
- **Plausible mid (with TCP fallback):** 344 + 13 (11 conn-refused + 2 dual-stack errors, possible TCP-only) ≈ **357**.
- **Tor lower bound:** ≥ 43 distinct `.onion` advertised (not probed, requires SOCKS).
- **1209k headline = 506:** residual gap of ~149-162 servers not reconcilable. Possible hypotheses, in order of likelihood: (a) inclusion of `.onion` or stale servers in their counter, (b) more permissive probe (header-only without full handshake), (c) duplicate entries IPv4/IPv6/hostname for the same operator.

**Conclusion:** the network is **~4× the bootstrap, ~⅔ the 1209k headline**. The number for the paper is **"≥344 servers BTC mainnet clearnet reachable to a standard Electrum client (snowball 2026-04-26, dual-stack)"** with the methodology documented.

#### Load-bearing implication for the roadmap

- **Problem size confirmed.** The M1 detector will operate against ~344-400 servers steady-state. Manageable: 100 concurrent connections (M0 budget) cover most of the network's top by uptime; periodic snowball can expand the pool to 350+ with tuning.
- **Bootstrap-dependency is a known operational issue**: 56% of bootstrap is dead. M0 must combine bootstrap+snowball from day one (not wait for M1).
- **IPv6 reachability is load-bearing**: 98 hosts (~28% of the census) are IPv6-only or IPv6-preferred. **Empirically confirmed**: same network at the same moment, IPv4-only host sees 246, dual-stack host sees 344. M1 collector must be deployed on dual-stack infra — not optional.
- **Tor delta still open** but now with a lower bound: ≥ 43 `.onion` advertised. Resolving it requires a tor daemon + SOCKS, out of Phase-1 scope.

#### Explicit limitations

- TCP fallback (port 50001) not implemented. The 11 conn-refused in Run 2 could be TCP-only.
- Point-in-time snapshots (52s + 64s, ~24h apart). Server churn not measured — the exact +98 delta match suggests low churn over that interval, but this is not a longitudinal study.
- 1209k not seed-cross-validated; comparative analysis would require parsing their HTML and is deferred to M1.

### Outputs produced in this session

| Archivo / File | Cambio / Change |
|---|---|
| [`docs/project-brief.md`](../project-brief.md) | Softened the fee-histogram determinism bullet (lines 74 ES and 139 EN). Code path citation + verdict + testbed reframe. |
| [`docs/bmad-binnacle/02_technical-research.md`](./02_technical-research.md) | Forward pointer in "Validation pending outside this report" section (ES and EN), marking fee-histogram as closed and pointing here. |
| [`experiments/asyncio-timing-benchmark/bench.py`](../../experiments/asyncio-timing-benchmark/bench.py) | New. Benchmark script for Validation 2 (~200 LOC). Probes: naked scheduler tick + fanout broadcast spread. |
| [`experiments/asyncio-timing-benchmark/run-idle.log`](../../experiments/asyncio-timing-benchmark/run-idle.log), [`run-cpuload.log`](../../experiments/asyncio-timing-benchmark/run-cpuload.log) | Raw bench outputs: idle and with `--cpu-load`. |
| [`experiments/snowball-network-size/snowball.py`](../../experiments/snowball-network-size/snowball.py) | New. BFS crawler for Validation 3 (~210 LOC). |
| [`experiments/snowball-network-size/run-on-aws.sh`](../../experiments/snowball-network-size/run-on-aws.sh) | New. Wrapper to run the snowball on a dual-stack EC2 instance (v6 pre-flight + scp + ssh + scp back). |
| [`bootstrap.json`](../../experiments/snowball-network-size/bootstrap.json), [`discovered.json`](../../experiments/snowball-network-size/discovered.json), [`run.log`](../../experiments/snowball-network-size/run.log), [`discovered-aws.json`](../../experiments/snowball-network-size/discovered-aws.json), [`run-aws.log`](../../experiments/snowball-network-size/run-aws.log) | Seed + dumps from Run 1 (Mac IPv4) and Run 2 (EC2 dual-stack). |
| This log / Esta bitácora | New, documents the Phase 1 closeout validations session. |

### Next steps

1. ~~**Validation 2 (asyncio timing benchmark)**~~ — **closed 2026-04-25, verdict GREEN.**
2. ~~**Validation 3 (snowball script)**~~ — **closed 2026-04-26, ≥344 mainnet clearnet (dual-stack run).**
3. **Empirical testbed** — coordinate with infra setup. Separate task because it depends on an operational machine with Bitcoin Core.
4. **All 3 Phase-1 validations are closed.** Natural next step: enter Phase 2 (`bmad-create-prd`). The fee-histogram empirical testbed can run in parallel with Phase 2 (not a blocker for starting the PRD).

### Meta lesson from this session

The "cheap-first move" (read code before infra) closed launch-blocker #2 in an hour when the original plan assumed a multi-day testbed. **Empirical validation is not always the first option** — when source code is available and the algorithm is contained, reading is strictly cheaper and more informative than measuring (it tells you not only *what* happens, but *why*).

Important mid-validation pivot: the assumed repo (`kyuupichan/electrumx`) was archived and its fee-histogram implementation was a stub. Without the initial verification we would have planned a testbed against a dead branch.
