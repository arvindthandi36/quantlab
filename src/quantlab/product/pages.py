# ruff: noqa: E501 -- HTML and editorial strings retain readable sentence boundaries.
"""Static product overview served by the same local application as every lab."""

from html import escape as e

from quantlab.product import AUTHOR, SUBTITLE, VERSION
from quantlab.product.content import ENVIRONMENTS, FEATURED, LAB_CARDS, LIMITATIONS


def link(url, label, style=""):
    return f'<a class="{e(style)}" href="{e(url)}">{e(label)}</a>'


def flow(labels):
    return '<ol class="ql-flow">' + "".join(f"<li>{e(s)}</li>" for s in labels) + "</ol>"


def environment_table():
    headers = (
        "Environment",
        "What is real?",
        "What is simulated?",
        "What QuantLab knows",
        "What execution means",
    )
    return (
        '<div class="ql-table" tabindex="0" role="region" aria-label="Environment evidence comparison"><table><caption>Three different kinds of evidence</caption><thead><tr>'
        + "".join(f'<th scope="col">{e(h)}</th>' for h in headers)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>"
            + "".join(
                f"<{tag}>{e(v)}</{tag}>"
                for tag, v in zip(("th", "td", "td", "td", "td"), row, strict=True)
            )
            + "</tr>"
            for row in ENVIRONMENTS
        )
        + "</tbody></table></div>"
    )


def home():
    cards = "".join(
        f'<a class="ql-card" href="{e(url)}"><span class="ql-index">{n}</span><h3>{e(title)}</h3><p>{e(text)}</p><span class="ql-arrow" aria-hidden="true">↗</span></a>'
        for n, title, text, url in LAB_CARDS
    )
    demos = "".join(
        f'<a class="ql-demo-link" href="/demos#demo={key}"><strong>{e(title)}</strong><span>{e(note)}</span><b aria-hidden="true">→</b></a>'
        for key, title, note in FEATURED
    )
    return f"""<section class="ql-hero"><div><p class="ql-kicker">An independent laboratory · by {AUTHOR}</p><h1>From a model.<br>To a market.<br><em>To a decision.</em></h1><p class="ql-lead">QuantLab is an event-driven quantitative-finance laboratory for trading, derivatives, risk and systematic research.</p><p>Submit orders, hedge options, examine risk and test ideas. Then trace the mathematics and evidence behind the result.</p><div class="ql-actions">{link("/", "Start trading", "ql-primary")}{link("/demos#demo=order", "Watch a guided demo", "ql-secondary")}</div><p class="ql-explore">{link("/home#labs", "Explore the labs")}&nbsp; · &nbsp;{link("/how-it-works", "Learn how QuantLab works")}</p><p class="ql-fine">Local Python application · Simulated execution · Reproducible evidence</p></div><aside class="ql-mechanism"><p class="ql-kicker">Inside a synthetic market</p><h2>Price is an execution.</h2><p>A hidden value process influences participants. Orders meet in the book. Transactions set the traded price.</p>{flow(("Latent economic process", "Participants with different information", "Buy and sell orders", "Price-time-priority book", "Matching → transactions"))}<p class="ql-mechanism-note">Latent value, best bid, best ask and last transaction can all differ.</p>{link("/how-it-works", "Follow the whole system →")}</aside></section>
    <section class="ql-section" id="labs"><div class="ql-section-title"><div><p class="ql-kicker">What can I do?</p><h2>One application. Connected questions.</h2></div>{link("/how-it-works", "Learn how QuantLab works →")}</div><div class="ql-card-grid">{cards}</div></section>
    <section class="ql-section ql-split" id="first-demo"><div><p class="ql-kicker">See it happen</p><h2>Start with a trade.<br>Follow the consequences.</h2><p>Guided demos pause for your prediction, reveal genuine engine results and connect the outcome to its assumptions. Choose Quick, Learn, Quant or Interview.</p><p>Bring a completed journal to <a href="/demos#teach-session">Teach Me This Session</a>. Review the decisions using the information available at the time.</p>{link("/demos", "Explore all 58 topics →")}</div><div class="ql-demo-list">{demos}</div></section>
    <section class="ql-section"><p class="ql-kicker">Know your evidence</p><h2>Synthetic is not historical.</h2><p>All user execution is simulated. No real historical dataset is bundled.</p>{environment_table()}{link("/environments", "Understand the three environments →")}</section>
    <section class="ql-section ql-bottom"><div><h2>Inspect the assumptions.</h2><p>A reconciled calculation can still describe an unrealistic market.</p></div>{link("/limitations", "Read the limitations", "ql-secondary")}</section>"""


def how():
    return (
        """<p class="ql-kicker">How QuantLab works</p><h1>Follow one action through the system.</h1><p class="ql-lead">The interface submits commands. Python validates and executes them. Public views, risk reports and explanations read the resulting evidence.</p><section class="ql-section"><h2>Trading & accounting</h2>"""
        + flow(
            (
                "Market environment",
                "Agents / user",
                "Orders",
                "Matching engine",
                "Trades",
                "Accounting",
                "Positions",
                "Risk / research",
                "Tutor / Explain",
            )
        )
        + """<p>Each match uses the best available price, then arrival order at that price. Buyer fills, seller fills and recorded trade quantity must reconcile. Cash and positions follow actual fills and fees.</p><p><a href="/demos#demo=order">Watch an order walk the book</a> · <a href="/explain#vwap">Explain VWAP</a></p></section><section class="ql-section" id="synthetic"><h2>Latent value is not the traded price.</h2><p>A stochastic process supplies latent economic value: a model quantity that ordinary traders cannot directly observe. Noise and liquidity traders have different objectives. An informed trader receives an imperfect signal. These participants submit orders into a real simulated book.</p>"""
        + flow(
            (
                "Latent process",
                "Different information / objectives",
                "Orders",
                "FIFO book",
                "Matching",
                "Transactions",
                "Public traded price",
            )
        )
        + """<p>The stochastic process influences the environment; it does not assign each transaction price. Latent value, best bid, best ask and last transaction can differ. A mark is also not a promised liquidation fill.</p><p><a href="/demos#demo=synthetic-prices">Inspect actual price formation</a> · <a href="/environments">Compare evidence sources</a></p></section><section class="ql-section"><h2>Options & portfolio risk</h2>"""
        + flow(
            (
                "Underlying",
                "Option pricing / finite quotes",
                "Option position",
                "Greeks",
                "Executed stock hedge",
                "Portfolio risk",
            )
        )
        + """<p>A contract multiplier converts per-unit option values and sensitivities into portfolio quantities. A stock hedge can reduce current delta; it leaves gamma, vega, transaction costs and model risk. Risk reads the resulting positions and stated covariance/scenario assumptions.</p><p><a href="/demos#demo=delta-hedge">Try the hedge branches</a> · <a href="/explain#delta">Explain delta</a></p></section><section class="ql-section"><h2>Statistical arbitrage & research</h2>"""
        + flow(
            (
                "Multi-asset observations",
                "Past-only regression",
                "Residual",
                "Past-only z-score",
                "Signal",
                "Sequential leg execution",
                "Risk / research",
            )
        )
        + """<p>Fitting uses past observations. Research separates development from evaluation and records losing and failed runs alongside winners. A high correlation or profitable backtest does not establish a stable tradable relationship.</p><p><a href="/statarb#model">Inspect the model</a> · <a href="/demos#demo=winner">See selection bias</a></p></section><section class="ql-section"><h2>Reproducibility & information boundaries</h2><p>Named random streams separate simulation from teaching. Saved journals retain commands and evidence; verifiers reconstruct and compare them. Public replay reveals only the selected point. Hidden information requires explicit permitted hindsight.</p><p>The browser formats values and plots coordinates. Matching, accounting, pricing and risk remain in Python. Product version 1.1.0 wraps the unchanged financial replay core 1.0.0.</p><p><a href="/limitations">Assumptions and limitations</a> · <a href="/defence">Questions to challenge the architecture</a></p></section>"""
    )


def environments():
    return (
        '<p class="ql-kicker">Markets</p><h1>Three environments.<br>Different evidence.</h1><p class="ql-lead">Read the source badge before interpreting a price, fill or explanation.</p>'
        + environment_table()
        + """<section class="ql-section ql-card-grid"><article class="ql-card"><h2>Synthetic Market</h2><p>Controlled artificial agents and an order book. QuantLab knows the generating mechanism, although normal agents do not see private value.</p><a href="/#choose-environment">Open environment controls →</a></article><article class="ql-card"><h2>Historical Replay</h2><p>Import timestamped GBP OHLCV with provenance. Observe a revealed prefix and place paper orders for subsequent closes. No book depth, queue truth or historical fill is inferred.</p><a href="/demos#demo=historical">What is real in replay? →</a></article><article class="ql-card"><h2>Scenario Market</h2><p>A controlled regime using the existing trading, options or multi-asset engine. Known and hidden choices obey different reveal rules.</p><a href="/#choose-environment">Choose a scenario →</a></article></section><section class="ql-section"><h2>Changing environments is explicit.</h2><p>End the active session before switching. Compatible observations, risk and replay stay with the selected environment; opening another lab does not silently create historical option chains or invent missing evidence.</p><p>Keep imported data and metadata with your ended journal. Its source fingerprint is required to verify historical replay. The built-in artificial fixture teaches execution mechanics; it is not a real historical dataset.</p><a href="/limitations">Read execution and data limitations →</a></section>"""
    )


def limitations():
    sections = "".join(
        f'<section class="ql-section" id="{title.lower().split()[0]}"><h2>{e(title)}</h2><dl class="ql-limit-grid">'
        + "".join(
            f"<div><dt>{label}</dt><dd>{e(text)}</dd></div>"
            for label, text in zip(
                ("What is simplified?", "Why?", "What could fail?", "How production differs"),
                row,
                strict=True,
            )
        )
        + "</dl></section>"
        for title, *row in LIMITATIONS
    )
    return (
        '<p class="ql-kicker">Assumptions & limitations</p><h1>A correct model result<br>still needs judgement.</h1><p class="ql-lead">QuantLab is an independent learning, simulation and research platform. It does not establish real-world alpha, actual historical fills or regulatory risk compliance.</p>'
        + sections
        + "<p>MIT licensed. Educational use; not investment advice. Model conventions remain visible within the labs.</p>"
    )


def showcase():
    steps = (
        ("/home", "Home", "Understand the platform and evidence types."),
        (
            "/demos#demo=order",
            "Order → VWAP → Explain",
            "Predict a market buy, reveal the actual fills, then open Explain this moment.",
        ),
        (
            "/demos#demo=synthetic-prices",
            "Synthetic market",
            "Follow agents, orders and actual transaction prices. Private value needs explicit permitted hindsight.",
        ),
        (
            "/demos#demo=delta-hedge",
            "Options → hedge",
            "Buy the call, choose a full or partial hedge and inspect the residual exposure.",
        ),
        (
            "/demos#demo=tails",
            "Risk",
            "Compare equal VaR thresholds with different tail severity.",
        ),
        (
            "/risk#stress",
            "Stress",
            "Inspect a hypothetical full repricing, separate from actual ledger P&L.",
        ),
        (
            "/demos#demo=pairs",
            "Stat Arb",
            "Compare highly correlated pairs and challenge residual stability.",
        ),
        (
            "/demos#demo=winner",
            "Research",
            "Inspect all development candidates and the locked untouched evaluation.",
        ),
        (
            "/demos",
            "Guided demos",
            "Restart, choose another depth or load a verified ended journal.",
        ),
    )
    return (
        '<p class="ql-kicker">A reproducible product tour</p><h1>One route through QuantLab.</h1><p class="ql-lead">Allow five minutes for an overview, or pause for the questions. These labs share mechanisms and conventions, not one artificial position carried across every demonstration.</p><ol class="ql-tour">'
        + "".join(
            f"<li><h2>{link(url, title)}</h2><p>{e(note)}</p></li>"
            for url, title, note in steps
        )
        + "</ol><p>Use named capture states and Recording mode inside a flagship for repeatable shots. Required source labels and limitations stay visible. Watching a showcase does not earn mastery.</p>"
    )


def defence():
    return """<p class="ql-kicker">Learn · Project defence</p><h1>Understand the choices.<br>Be honest about the gaps.</h1><p class="ql-lead">Explain a mechanism, show its evidence, then state where the model could fail. Memorising a confident answer is not the aim.</p><section class="ql-section"><h2>Questions to practise</h2><ul class="ql-questions"><li>Why integer ticks and price-time priority?</li><li>Why separate latent value from transaction price?</li><li>Why can a maker lose despite earning a spread?</li><li>What does deterministic replay verify, and what does it not prove?</li><li>Why does a delta hedge leave risk?</li><li>What does ES add to VaR?</li><li>Why is correlation insufficient for pairs trading?</li><li>Why do research selection and untouched evaluation matter?</li><li>What information is missing from historical OHLCV?</li><li>Which assumptions would you change first for a particular real use?</li></ul></section><div class="ql-actions"><a class="ql-primary" href="/demos#demo=order&mode=interview">Try an interview demo</a><a class="ql-secondary" href="/learning">Open learning progress</a></div><p>For the tutor's Project defence mode, expand “Revisit a concept / Interview / Project defence” in a lab. Speaking fluency and project ownership are not automatically graded.</p><p><a href="/how-it-works">System overview</a> · <a href="/limitations">Limitations</a> · <a href="/explain">Concept explorer</a></p>"""


PAGES = {
    "/home": ("Home", home),
    "/how-it-works": ("How it works", how),
    "/environments": ("Markets", environments),
    "/limitations": ("Limitations", limitations),
    "/showcase": ("Product tour", showcase),
    "/defence": ("Project defence", defence),
}


def render(path):
    title, body = PAGES[path]
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>QuantLab · {title}</title><meta name="description" content="{SUBTITLE}"><link rel="stylesheet" href="/style.css"></head><body class="ql-editorial"><header><strong>QuantLab</strong></header><main>{body()}</main><footer>QuantLab {VERSION} · {AUTHOR} · MIT licensed · Educational simulations<br>{SUBTITLE}</footer></body></html>'
