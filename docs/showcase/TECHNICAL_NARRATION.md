# Technical walkthrough outline · 3–5 minutes

**0:00–0:35 — Architecture.** “An action becomes an event; the clock orders events deterministically.
The interface submits commands, while Python owns matching and accounting.” Show the system page.

**0:35–1:10 — Matching and accounting.** Submit the order demo. Explain cheaper asks then FIFO,
partial fills, actual VWAP and fees. Point to buyer/seller/trade conservation and independent
cash/position reconciliation. A replay must agree at each transition, not just at its final P&L.

**1:10–1:45 — Information and price.** Show synthetic price formation. Latent value is not a public
price. Ordinary participants have public information; the informed trader gets a noisy signal.
Orders—not direct stochastic output—produce transaction prices. Discuss allowed ended hindsight.

**1:45–2:30 — Options and risk.** A contract multiplier scales price and Greeks. Stock orders hedge
current delta through the existing book. Gamma changes the hedge; vega remains. Risk reads actual
positions with explicit covariance and stress assumptions. Equal VaR need not mean equal ES.

**2:30–3:10 — Stat Arb.** Past-only fitting, residual, prior-window z-score, signal, sequential
execution. Explain leg risk and why high correlation does not prove a stable residual. Show failure.

**3:10–3:50 — Research discipline.** Register variants, separate development and evaluation, use
common random numbers when valid, retain failures and show uncertainty. The selected Gaussian
control's positive evaluation is still not proof of alpha. Reproducibility is not model validity.

**3:50–4:30 — Teaching and limitations.** Open Explain on the selected point. The central registry
provides definitions; actual inputs provide evidence. Demo viewing cannot earn mastery. State
three unrealistic assumptions and how a real deployment would require different validation.

Do not memorise sentences. Use the [defence questions](PROJECT_DEFENCE.md) to test understanding.
