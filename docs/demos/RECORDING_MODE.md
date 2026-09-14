# Recording and showcase preparation

This phase prepares reproducible moments; it does **not** record videos, make GIFs, install
capture software, publish marketing assets or redesign the final recruiter README.

1. Open Demos and choose a flagship in Quick mode for a concise outline.
2. Use **Recording mode** to hide catalogue/development navigation and unrelated controls.
3. Optionally enable **Larger text**. The environment badge, simulation truth, assumptions,
   limitations and production differences remain visible.
4. Under **Named capture states & script export**, select a stable name and explicitly enter
   showcase capture. This can reveal later results and disables learning credit for the demo.
5. Export the Markdown script and the chosen demo path. Use Restart to restore the engine's
   declared seed, book, accounts and parameters. Restart does not erase prior answer exposure.

Examples:

| Demo | Named states |
|---|---|
| Order execution | `order-before-submit`, `order-after-multifill` |
| Getting picked off | `picked-off-before-fill`, `picked-off-after-event` |
| Delta hedge | `delta-before-hedge`, `delta-after-hedge`, `delta-after-volatility-shock` |
| VaR / ES | `var-vs-es-tail` |
| Correlation / residual | `correlation-vs-residual` |
| Winner's curse | `winner-before-test`, `winner-after-test` |
| Synthetic prices | `synthetic-before-event`, `synthetic-after-event` |
| Historical evidence | `historical-before-order`, `historical-after-paper-fill` |

Hindsight is a separate control after the completed walkthrough. A capture jump does not silently
reveal latent truth or a hidden scenario's configuration. Keep observer captions on any later
recording of private signal/markout evidence.

The eight reproducible outlines are in [scripts](scripts). Rebuild them with
`venv/bin/python scripts/phase14_evidence.py`. Scripts report actual engine values and a result
digest, and separate public observations from any explicit observer discussion. They are outlines,
not final external videos or a polished voiceover.
