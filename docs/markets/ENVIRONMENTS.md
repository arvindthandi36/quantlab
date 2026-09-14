# Market environment contract

Phase 13 adds environments around the approved 1.0.0 engines. An environment provides
public observations, executable actions, a clock, provenance, capabilities and a
verified journal. It need not invent the same internal market mechanism everywhere.

| Environment | What is real? | Execution | What QuantLab knows |
|---|---|---|---|
| Synthetic | Your instructions and the recorded simulation events | Existing price/time-priority exchange | The controlled generating process; hidden truth stays private during decisions |
| Historical | User-supplied recorded observations, subject to their provenance | Explicit next-close paper rule | The revealed observations; no true value or real-market causal explanation |
| Scenario | Your actions within a deliberately configured synthetic model | Existing stock, multi-asset or option engine | Configuration and synthetic truth; hidden scenario details require ended-session reveal |

The same local application serves all three. Historical options are unavailable in
this phase; no model-generated option chain is presented as historical. Compatible
paired historical series can use the existing causal regression/signal APIs. Historical
risk uses only revealed returns through the existing portfolio revaluation and tail APIs.

Historical timestamps mean **bar end / availability time**. An instruction submitted
at observation t cannot fill until a later observation. Market orders use the next
revealed close plus fixed adverse tick slippage, limited by a shared participation
budget. The remainder cancels. Limit orders use the same price only when it satisfies
the limit and may remain for later observations. High/low never determines fills.
This is a paper convention, not reconstructed exchange priority.

Provenance records source, instrument, timezone, frequency, units, adjustment status,
corporate-action handling, fields and transformations. Raw and adjusted inputs cannot
be mixed. Full dataset hashes and complete journals are available only after completion;
live evidence uses the published prefix. Replay requires the original dataset hash.

Hidden scenario public projections omit names, seeds, process types, scheduled shocks
and private intensity/regime configuration. Publicly visible consequences are allowed.
Revealing configuration is a separate ended-session action and never feeds a live quiz.

Rewind is read-only verified replay. Restart creates a fresh account/session and warns
that prior knowledge cannot be erased; it is never the same live decision state.
Phase 14's polished teaching/replay catalogue is not part of this build.
