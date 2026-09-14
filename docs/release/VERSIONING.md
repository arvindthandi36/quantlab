# Product 1.1.0 and financial replay core 1.0.0

1.0.0 already represented the completed financial core. **1.1.0** is the additive explainability,
market-environment, guided-demo and final-product release. The installed package metadata, `quantlab
--version`, common application header and launch message identify 1.1.0.

The approved `quantlab.__version__` remains **1.0.0**: existing financial journals and verifiers use
it as their exact compatibility key. Changing it just for a new navigation bar would reject
approved replay records despite identical calculations. The new product launcher lives in
`quantlab.product.cli`, with an explicit product VERSION; pyproject and tests check they agree.

This does not weaken version gates or relabel old records. Python/NumPy/SciPy requirements and
all outcome/fingerprint comparisons continue to apply. No journal migration is performed.
The legacy `python -m quantlab --version` reports the financial core version; use the supported
`quantlab --version` for the release version. Both serve entry points launch the same application.

A future financial-rule change must update the financial model/replay contract and tests explicitly.
[Original replay policy](replay_policy.md). The 1.1.0 source is published at
[arvindthandi36/quantlab](https://github.com/arvindthandi36/quantlab). Repository publication
does not itself imply a release tag or a GitHub Release.
