"""One product shell around unchanged lab pages; presentation metadata only."""

import re
from html import escape

from quantlab.product import VERSION
from quantlab.product.pages import PAGES

GROUPS = (
    (
        "Trade",
        (
            ("Trading Simulator", "/"),
            ("Market making", "/#maker"),
            ("Options", "/options"),
            ("Stat Arb", "/statarb"),
        ),
    ),
    (
        "Markets",
        (
            ("Environment guide", "/environments"),
            ("Choose environment", "/#choose-environment"),
        ),
    ),
    (
        "Risk",
        (
            ("Portfolio", "/risk"),
            ("VaR / Expected Shortfall", "/risk#models"),
            ("Stress testing", "/risk#stress"),
            ("Optimisation", "/risk#optimise"),
        ),
    ),
    (
        "Research",
        (
            ("Research", "/research"),
            ("Options experiments", "/options#research"),
            ("Risk experiments", "/risk#research"),
            ("Stat Arb experiments", "/statarb#research"),
        ),
    ),
    (
        "Learn",
        (
            ("Concept explorer", "/explain"),
            ("Guided Demos", "/demos"),
            ("Teach Me This Session", "/demos#teach-session"),
            ("Learning progress", "/learning"),
            ("Interview mode", "/demos#demo=order&mode=interview"),
            ("Project defence", "/defence"),
        ),
    ),
    (
        "About",
        (
            ("How QuantLab works", "/how-it-works"),
            ("Assumptions & limitations", "/limitations"),
            ("Product tour", "/showcase"),
        ),
    ),
)
LABS = tuple(item for _, items in GROUPS for item in items)


def shell(path):
    groups = []
    for title, items in GROUPS:
        links = "".join(
            f'<a href="{escape(url)}"'
            + (' aria-current="page"' if url == path else "")
            + f">{escape(label)}</a>"
            for label, url in items
        )
        groups.append(
            f'<details class="ql-nav-group"><summary>{title}</summary>'
            f"<div>{links}</div></details>"
        )
    return (
        '<header class="ql-masthead"><a class="ql-wordmark" href="/home" '
        'aria-label="QuantLab home">'
        '<span aria-hidden="true">Q∕</span> QuantLab</a><span class="ql-brand-note">'
        "A quantitative finance laboratory</span>"
        f'<span class="ql-release">{VERSION} · LOCAL</span></header>'
        '<nav class="platform-nav ql-nav" aria-label="QuantLab labs">'
        '<a class="skip-content" href="#main-content">Skip to content</a>'
        '<a class="ql-home-link" href="/home">Home</a>' + "".join(groups) + "</nav>"
    )


def page(content, path):
    content = re.sub(r"QuantLab · Phase [0-9]+", f"QuantLab {VERSION}", content)
    content = content.replace("REAL TRANSACTIONS", "SIMULATED TRANSACTIONS")
    content = re.sub(r"PHASE [0-9]+ · ", "", content)
    content = re.sub(r"(QuantLab 1\.1\.0) only", r"\1", content)
    content = content.replace(
        "Later-phase domains are prepared only.",
        "Topics need eligible answer evidence before assessment.",
    )
    content = content.replace("PHASE 5 RESEARCH", "RECORDED RESEARCH")
    content = re.sub(r" Phase [0-9]+ only\.", "", content)
    editorial = path in PAGES
    assets = '<script src="/navigation.js" defer></script>'
    if not editorial:
        assets += (
            '<link rel="stylesheet" href="/explain.css">'
            '<script src="/explain.js" defer></script>'
            '<link rel="stylesheet" href="/demos.css"><script src="/demos.js" defer></script>'
        )
        if path != "/demos":
            assets += (
                '<link rel="stylesheet" href="/markets.css">'
                '<script src="/markets.js" defer></script>'
            )
    assets += (
        '<link rel="stylesheet" href="/product.css"><script src="/product.js" defer></script>'
    )
    content = content.replace("</head>", assets + "</head>")
    content = content.replace("<main>", '<main id="main-content" tabindex="-1">', 1)
    header = re.search(r"<header>(.*?)</header>", content, re.S)
    if header:
        # Keep genuine view controls and their labels; remove redundant lab-link bars.
        old = header.group(1)
        toolbar = '<div class="ql-lab-toolbar">' + old + "</div>" if "<select" in old else ""
        content = content[: header.start()] + shell(path) + toolbar + content[header.end() :]
    return content
