"""Bounded educational event selection from verified PUBLIC command-boundary frames."""

import heapq
from collections import Counter
from fractions import Fraction

from quantlab.demos.models import Evidence, Moment, Spec
from quantlab.demos.replay_questions import question
from quantlab.demos.replays import verified
from quantlab.research.codec import digest

PROCESS_NOTE = (
    "Process quality unknown: the journal alone does not establish "
    "your objective, forecast or decision rule. Profit alone does not "
    "establish that the decision process was sound."
)
CLASSIFICATIONS = (
    "GOOD PROCESS / GOOD OUTCOME",
    "GOOD PROCESS / BAD OUTCOME",
    "WEAK PROCESS / GOOD OUTCOME",
    "WEAK PROCESS / BAD OUTCOME",
)


def core(s):
    return s.get("core", s)


def account(s):
    c = core(s)
    if (c.get("report") or {}).get("portfolio"):
        return c["report"]["portfolio"]
    if (c.get("risk") or {}).get("portfolio"):
        return c["risk"]["portfolio"]
    return c.get("account", c.get("portfolio", c.get("accounts", {})))


def all_orders(s):
    c = core(s)
    if c.get("trading"):
        return [
            o
            for child in c["trading"].values()
            if isinstance(child, dict)
            for o in all_orders({"core": child})
        ]
    if "markets" in c:
        return [o for market in c["markets"] for o in market.get("orders", [])]
    return c.get("orders", c.get("stock", {}).get("orders", []))


def all_fills(s):
    c = core(s)
    if c.get("trading"):
        return [
            f
            for child in c["trading"].values()
            if isinstance(child, dict)
            for f in all_fills({"core": child})
        ]
    if "stock" in c:
        return c.get("option_trades", []) + c["stock"].get("trades", [])
    return c.get("fills", c.get("trades", []))


def inventory(s):
    a = account(s)
    if isinstance(a, dict):
        if isinstance(a.get("position"), (int, float)):
            return abs(a["position"])
        positions = a.get("positions", core(s).get("positions", []))
        if isinstance(positions, list):
            return sum(abs(float(p.get("quantity", 0))) for p in positions)
    return 0


def number(s, metric):
    a = account(s)
    keys = {"pnl": ("total_pnl", "pnl"), "drawdown": ("drawdown", "max_drawdown")}[metric]
    for k in keys:
        if isinstance(a, dict) and a.get(k) is not None:
            try:
                return float(Fraction(str(a[k])))
            except (ValueError, TypeError):
                pass
    return 0


def classify(before, after, action):
    """Value uses magnitudes, never 'profit = skill'. Rank ties by original chronology."""
    b, c = core(before), core(after)
    tags = []
    score = 0.0
    concept = "model_risk"
    fills, old = all_fills(after), all_fills(before)
    counts = Counter(digest(f) for f in old)
    new = []
    for f in fills:
        identity = digest(f)
        if counts[identity]:
            counts[identity] -= 1
        else:
            new.append(f)
    if new:
        tags.append("execution")
        score += 3
        concept = "vwap"
        if len(new) > 1:
            tags.append("multiple fills")
            score += 5
        if len({f.get("price") for f in new}) > 1:
            tags.append("multiple price levels")
    orders, prior_orders = all_orders(after), all_orders(before)
    if (
        orders
        and orders != prior_orders
        and any(0 < o.get("filled", 0) < o.get("original", 0) for o in orders[-1:])
    ):
        tags.append("partial fill")
        score += 6
        concept = "partial_fills"
    kind = action.get("kind", "")
    if "cancel" in kind:
        tags.append("cancellation")
        score += 4
        concept = "limit_orders"
    if "hedge" in kind or kind == "stock_order" and after["engine"] == "options":
        tags.append("hedge")
        score += 6
        concept = "delta_hedging"
    if kind in ("pair", "next_leg") or after["engine"] == "statarb" and kind == "order":
        tags.append("leg risk")
        score += 7
        concept = "leg_risk"
    result = action.get("result", {})
    if result.get("ok") is False or result.get("result", {}).get("ok") is False:
        tags.append("rejected / risk warning")
        score += 6
        concept = "exposure"
    if c.get("markouts") != b.get("markouts") and c.get("markouts"):
        tags.append("markout update")
        score += 7
        concept = "markouts"
    pos = inventory(after)
    if pos != inventory(before):
        tags.append("inventory change")
        score += min(pos, 10) / 5
    movement = number(after, "pnl") - number(before, "pnl")
    if abs(movement) > 0:
        tags.append("P&L movement")
        score += min(abs(movement), 100) / 20
    if number(after, "drawdown") > number(before, "drawdown"):
        tags.append("drawdown")
        score += 2
    if after["engine"] == "risk" or c.get("risk") != b.get("risk") and c.get("risk"):
        tags.append("risk estimate")
        score += 3
        concept = "var"
    if b.get("spread") != c.get("spread"):
        tags.append("liquidity change")
        score += 2
    for tag, focus in (
        ("rejected / risk warning", "exposure"),
        ("leg risk", "leg_risk"),
        ("hedge", "delta_hedging"),
        ("partial fill", "partial_fills"),
        ("multiple fills", "vwap"),
        ("markout update", "markouts"),
    ):
        if tag in tags:
            concept = focus
            break
    return score, concept, tuple(tags)


def action_text(action):
    # Never include recorded result, diagnostics, fingerprints or later information.
    kind = action.get("kind", "observe").replace("_", " ")
    p = action.get("payload", {})
    allowed = (
        "side",
        "quantity",
        "order_type",
        "price",
        "instrument",
        "count",
        "order_id",
        "action",
    )
    return kind + (
        " · " + ", ".join(f"{k}: {p[k]}" for k in allowed if k in p)
        if any(k in p for k in allowed)
        else ""
    )


def select(frames, actions, limit=6):
    if type(limit) is not int or not 1 <= limit <= 8:
        raise ValueError("Select 1–8 teaching moments")
    if len(frames) < 2:
        return []
    candidates = []
    # O(n) scoring plus bounded heap storage. No nested scan of the entire journal.
    for i in range(1, len(frames)):
        action = actions[min(i - 1, len(actions) - 1)] if actions else {}
        rank, concept, tags = classify(frames[i - 1], frames[i], action)
        heapq.heappush(candidates, (rank, -i, concept, tags))
        if len(candidates) > limit * 4:
            heapq.heappop(candidates)
    ranked = sorted(candidates, reverse=True)
    chosen = []
    seen = set()
    # Prefer varied concepts; neither positive nor negative outcomes are filtered out.
    for row in ranked:
        if row[2] not in seen:
            chosen.append(row)
            seen.add(row[2])
        if len(chosen) == limit:
            break
    for row in ranked:
        if len(chosen) == limit:
            break
        if row not in chosen:
            chosen.append(row)
    out = []
    for rank, negative_i, concept, tags in sorted(chosen, key=lambda r: -r[1]):
        i = -negative_i
        action = actions[min(i - 1, len(actions) - 1)] if actions else {}
        q = question(frames[i - 1], action)
        # Before title/concept generic; event-derived tags/concepts are result-only in runner.
        out.append(
            Moment(
                f"replay-{i}",
                f"Your action at public point {i - 1}",
                action_text(action),
                concept,
                frames[i - 1],
                frames[i],
                q,
                observation=(
                    "Read only this public point. The saved next result has not been "
                    "revealed in this walkthrough."
                ),
                result_note="This is the verified next command-boundary result. "
                + PROCESS_NOTE,
                rank=rank,
                tags=tags,
            )
        )
    return out


def teach(raw, datasets=()):
    frames, actions, private, proof = verified(raw, datasets)
    moments = select(frames, actions)
    if not moments:
        raise ValueError("The verified session has no post-opening action to annotate")
    spec = Spec(
        "your-session",
        "Teach Me This Session",
        "Selected moments from your saved, verified session.",
        "Your replay",
        tuple(dict.fromkeys(m.concept for m in moments)),
        "replay",
        duration_minutes=6,
        environment=frames[0]["environment"]["badge"],
    )
    return Evidence(
        spec,
        moments,
        {"source": "verified saved journal; private configuration withheld"},
        (
            "Selected moments are a teaching sample, not a complete audit.",
            PROCESS_NOTE,
            (
                "Replay predictions are practice only: you may already know the "
                "outcome from your completed session."
            ),
        ),
        private=private,
        origin="saved_replay",
        verification=proof,
    )


def summary(evidence):
    ms = evidence.moments
    counts = {}
    for m in ms:
        for tag in m.tags:
            counts[tag] = counts.get(tag, 0) + 1
    best = max(ms, key=lambda m: m.rank)
    risk = max(
        ms,
        key=lambda m: (
            abs(number(m.after, "pnl") - number(m.before, "pnl")) + inventory(m.after)
        ),
    )
    return {
        "what_happened": (
            f"Verified {evidence.verification.get('frames', len(ms))} public points; "
            f"reviewed {len(ms)} selected actions."
        ),
        "key_decisions": [m.action for m in ms],
        "observed_event_types": counts,
        "key_concepts": list(evidence.spec.concepts),
        "best_learning_moment": best.id + " · " + ", ".join(best.tags),
        "biggest_risk": {
            "selected_moment": risk.id,
            "inventory_magnitude": inventory(risk.after),
            "absolute_pnl_move": abs(number(risk.after, "pnl") - number(risk.before, "pnl")),
            "note": "Largest selected exposure/P&L-move proxy, not a complete risk ranking.",
        },
        "one_thing_that_could_have_been_misleading": PROCESS_NOTE,
        "three_review_questions": [
            "What information was public before your chosen action?",
            "Which input or order explains the observed result?",
            "What evidence would distinguish sound process from good luck?",
        ],
        ("one_interview_question"): (
            "Defend one decision using only information available beforehand, "
            "then challenge one model assumption."
        ),
    }
