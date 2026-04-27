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

**Tracker para LB#11 / Tracker for LB#11** — `docs/launch_blockers.yaml`. Esta entrada se actualiza con cada round de la conversación con b10c. Hard prerequisite for Story 4.4 (M3 launch).

---

## 🇪🇸 Resumen

LB#11 requiere abrir y cerrar una conversación con b10c sobre tres temas:

1. **Framing** — ¿le parece OK el framing "shared infrastructure clusters" + cited-only intent attribution?
2. **`bitcoin-data` conventions** — ¿qué convenciones / preferencias tiene para contribuciones al repo?
3. **Path 2 handoff optionality** — ¿está dispuesto a ser un Path 2 handoff candidate, o prefiere quedar fuera de esa lista?

LB#11 cierra cuando b10c ha respondido sustantivamente a los 3 temas (incluso si la respuesta es "let's revisit closer to M3"). Status flips a `cleared` en `launch_blockers.yaml` con `cleared_by: docs/bmad-binnacle/13_lb11_b10c_socialization.md` + `cleared_at: <date>`.

## 🇬🇧 Summary

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
