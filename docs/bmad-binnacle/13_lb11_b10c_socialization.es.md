# LB#11 — socialización con b10c (electrum-sybil-detector)

**Tracker para LB#11** — `docs/launch_blockers.yaml`. Esta entrada se actualiza con cada ronda de la conversación con b10c. Prerrequisito imprescindible para la Story 4.4 (lanzamiento M3).

🇬🇧 English authoritative version: [`13_lb11_b10c_socialization.md`](./13_lb11_b10c_socialization.md) — that file holds the machine-readable frontmatter (`status`, `opened_at`, `channel`, etc.) and is the single source of truth for status updates. This Spanish file is the documentation mirror.

---

## Resumen

LB#11 requiere abrir y cerrar una conversación con b10c sobre tres temas:

1. **Encuadre** — ¿le parece adecuado el encuadre "clústeres de infraestructura compartida" + atribución de intención solo citada?
2. **Convenciones de `bitcoin-data`** — ¿qué convenciones / preferencias tiene b10c para contribuciones al repositorio?
3. **Traspaso opcional como Path 2** — ¿está dispuesto a ser candidato Path 2 de traspaso, o prefiere quedar fuera de esa lista?

LB#11 se cierra cuando b10c ha respondido sustantivamente a los 3 temas (incluso si la respuesta es "lo retomamos cerca de M3"). El estado pasa a `cleared` en `launch_blockers.yaml` con `cleared_by: docs/bmad-binnacle/13_lb11_b10c_socialization.md` + `cleared_at: <fecha>`.

---

## Cronograma

(Actualizar con cada interacción)

- **<YYYY-MM-DD>** — primer contacto abierto. Canal: `<github_issue|email|otro>`. URL/ref: `<>`.
- **<YYYY-MM-DD>** — respuesta de b10c recibida. Tema cubierto: `<encuadre|convenciones|path_2|todos>`. Sustancia: `<nota breve>`.
- **<YYYY-MM-DD>** — seguimiento enviado / recibido. ...
- **<YYYY-MM-DD>** — LB#11 cerrado. Los 3 temas tratados. Referencia de cierre: `<>`.

---

## Lista de items de conversación

| Item | Estado | Respuesta de b10c | Resolución |
|---|---|---|---|
| Aceptación del encuadre | pendiente | — | — |
| Convenciones de contribución a `bitcoin-data` | pendiente | — | — |
| Traspaso opcional como Path 2 | pendiente | — | — |

---

## Criterios de cierre

LB#11 transita de `pending` → `cleared` en `docs/launch_blockers.yaml` SOLO cuando TODO lo siguiente sea cierto:

- Los 3 items de conversación tienen una respuesta sustantiva de b10c registrada en el cronograma
- El campo `status` del frontmatter (en el archivo `.md` autoritativo en inglés) está actualizado a `cleared`
- La referencia `cleared_by` en `launch_blockers.yaml` apunta a este archivo de bitácora
- La fecha `cleared_at` en `launch_blockers.yaml` coincide con la fecha de la última respuesta sustantiva
- (Transversal) LB#19 (mismo contenido, distinta entrada del PRFAQ) también se cierra junto con este

---

## Si LB#11 se estanca

- **Sin respuesta tras 2 semanas:** considerar email de seguimiento si la dirección es conocida, o un ping breve por Mastodon/Twitter. NO escalar a otros foros (saturar canales con PRs es antipatrón).
- **Sin respuesta tras 6 semanas:** marcar como `blocked` en `launch_blockers.yaml` y reevaluar la lista de candidatos Path 2. El proyecto no depende específicamente de b10c — `bitcoin-data` es el archivo canónico, pero existen otras rutas de archivado (Zenodo + arXiv son dominios de fallo independientes según AR33).
- **Respuesta negativa sobre encuadre o convenciones:** registrar en el cronograma, ajustar los artefactos del proyecto si fuera necesario. Una respuesta negativa sigue siendo una respuesta sustantiva — cierra el item de conversación.
- **Renuncia al Path 2:** aceptable — actualizar las notas de `launch_blockers.yaml` para LB#11 + LB#19 reflejando que b10c queda fuera de la lista Path 2. Identificar candidato Path 2 alternativo (p. ej., órbita Grundmann / TU Darmstadt).

---

## Borrador del issue (versión en español, para revisión interna)

> ⚠️ **Importante:** la versión que se publica en `b10c/bitcoin-data` debe ir en inglés (ver el archivo autoritativo). Esta traducción al español sirve para revisión interna o consulta con Librería de Satoshi antes de publicar.

**Título:** `Propuesta: contribución del dataset electrum-sybil-detector + alineación sobre convenciones de bitcoin-data`

**Cuerpo:**

> Hola @b10c,
>
> Como continuación de tu issue #11 en project-ideas ("Can we spot public spy-Electrum servers run by Chainalysis?"), estoy construyendo `electrum-sybil-detector` — un proyecto de medición que producirá un dataset longitudinal y un paper de metodología sobre infraestructura backend compartida en la red pública de servidores Electrum. Quiero abrir una conversación temprana sobre contribuir el dataset a `bitcoin-data` cuando esté listo (~12 meses).
>
> ### Resumen técnico de la metodología
>
> El discriminador primario es la **varianza del delta por pares en las notificaciones de bloque durante eventos de fork-race** (con `bitcoin-data/stale-blocks` como fuente canónica de eventos). En una fork-race, los servidores que comparten backend ven el cambio de tip simultáneamente; los backends independientes se dispersan según la latencia P2P de Bitcoin. Es un experimento natural binario que evita cualquier identidad auto-declarada (banner, version, donation address) — propiedades trivialmente evadibles.
>
> La prueba es **varianza del delta por pares sobre muchos eventos**, no delta absoluto sobre uno solo. La asimetría del recorrido del recolector es constante y se cancela. Esto convierte la observación desde un único punto en una cota inferior estricta sobre la prevalencia de backend compartido — las reproducciones desde otros ASNs solo pueden fortalecer la cota, nunca debilitarla.
>
> **Umbral multi-señal pre-comprometido** para los clústeres publicados: ≥2 señales de estado del backend + ≥1 señal de configuración del frontend.
>
> - **Estado del backend:** (a) varianza del timing en fork-races, (b) distancia Wasserstein 1-D sobre `mempool.get_fee_histogram` (canónica vía `scipy.stats.wasserstein_distance` — la identidad bit a bit entre instancias es falsa por construcción tras leer `spesmilo/electrumx/src/electrumx/server/mempool.py:154-209`: desfase de refresco entre instancias, deriva del mirror local del mempool, agrupamiento adaptativo `bin_size *= 1.1`), (c) caídas sincronizadas vía solapamiento de intervalos sobre `connection_events`.
> - **Configuración del frontend:** banner, rango de versión de `server.features`, ASN, donation_address.
>
> **Rigor estadístico:** corrección Benjamini-Hochberg FDR, intervalos de confianza por remuestreo bootstrap sobre cada clúster, análisis de potencia declarado para la ventana de medición, distribución del suelo de ruido a partir de un conjunto curado de servidores conocidos como independientes (remuestreo bootstrap + prueba de permutación). DBSCAN como clustering primario, Ward jerárquico como secundario para análisis de sensibilidad.
>
> **Disciplina de datos:** marcas temporales en monotonic-ns con el reloj de pared almacenado por separado (nunca usado en cálculos de delta), una única fuente NTP por ventana de colección, capa de datos crudos append-only con `schema_version` por fila, identificadores opacos BLAKE2b-256 (el mapeo a hostname no se publica por defecto).
>
> ### Validaciones técnicas ya cerradas
>
> - **Determinismo del fee-histogram** — cerrada por lectura de código (2026-04-25): fuertemente correlacionado, no idéntico bit a bit, por construcción. La pregunta binaria está resuelta; queda pendiente medir empíricamente la magnitud de la deriva contra una matriz de 5 frontends sobre un único Bitcoin Core (ElectrumX × 2 + Fulcrum + mempool-electrs + Blockstream/electrs) — la misma rutina se ejecuta como verificación recurrente en CI para detectar deriva metodológica entre versiones.
> - **Resolución de asyncio** — un benchmark midió una dispersión p99 en difusiones a múltiples consumidores de 587 µs con N=100 y 1,71 ms con N=200. El suelo de señal de cientos de ms en las fork-races domina por órdenes de magnitud cualquier fluctuación del recolector.
> - **Tamaño real de la red en doble pila IPv4+IPv6** — un rastreador en bola de nieve desde EC2 alcanzó ≥344 servidores en la red principal. Conclusión estructural: aproximadamente el 28 % de la red es solo IPv6; un despliegue solo-IPv4 deja invisible casi un tercio del espacio observable.
>
> ### Reproducibilidad y archivado
>
> **Contrato de reproducibilidad:** hash del código + huella de los datos crudos → dataset derivado idéntico bit a bit (o tolerancia documentada en coma flotante por columna). El autotest se incluye con cada versión y los revisores pueden re-ejecutarlo de forma independiente; el presupuesto en CI es ≤30 min sobre la ventana de medición. Instantáneas en Parquet con compresión Zstandard vía pyarrow.
>
> **Archivado en tres niveles** con dominios de fallo independientes: `bitcoin-data` en GitHub + DOI en Zenodo + preprint en arXiv. La pérdida de cualquier nivel no invalida la contribución; el DOI de Zenodo es el identificador canónico de citación.
>
> ### Tres preguntas
>
> **1. Encuadre.** El proyecto publica los hallazgos como "clústeres de infraestructura compartida" — explícitamente NO origina atribución de operador o intención. El lenguaje de atribución de intención es solo citado (tu issue #11 + los materiales de CoinDesk 2021 son las únicas referencias). ¿Te parece adecuado este encuadre?
>
> **2. Convenciones de `bitcoin-data`.** Quiero alinear desde el primer día (estructura de directorios, cadencia de las instantáneas en Parquet, formato del CHANGELOG, manifest.json con hash de código + huella de los datos crudos + DOI de Zenodo). Más allá de los datasets existentes (`stale-blocks` / `mining-pools` / `block-arrival-times`) como referencia, ¿hay documentación, convenciones o preferencias adicionales con las que debería alinearme?
>
> **3. Traspaso opcional como Path 2.** El proyecto incluye un disparador de salida explícito: si a 12 meses tras el lanzamiento hay citas pero no hay financiación, la custodia de la metodología se cede a un sucesor mantenido por la comunidad. Tu órbita está pre-identificada como candidata. Lo menciono pronto porque es más útil ahora que cerca del plazo — abierto a discutir si te parece adecuado, o si prefieres quedar fuera.
>
> ### Artefactos en el repositorio (estado de borrador)
>
> - PRD: https://github.com/hacknodeslab/electrum-sybil-detector/blob/main/_bmad-output/planning-artifacts/prd.md
> - Arquitectura: https://github.com/hacknodeslab/electrum-sybil-detector/blob/main/_bmad-output/planning-artifacts/architecture.md
>
> Sin presión de plazos — la ventana de lanzamiento está a unos 12 meses, pero el PR a `bitcoin-data` depende de esta conversación, así que ponerla en marcha temprano es la opción más segura.
>
> Gracias por `bitcoin-data` y `fork-observer` — ambos están referenciados extensamente, y usamos `fork-observer` como consumidor de solo lectura de su salida HTTP/JSON en lugar de reimplementar el seguimiento del tip.
>
> — Ifuensan / HackNodes Lab / Librería de Satoshi
