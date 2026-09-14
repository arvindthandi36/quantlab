# Model-risk dependency map

Read arrows as “this assumption affects these outputs,” not proof that the output predicts reality. The central [assumptions register](../../ASSUMPTIONS.md) defines each model's scope.

```mermaid
flowchart TD
    L[Latent shocks and trader arrival assumptions] --> O[Submitted orders]
    I[Noisy signal and prior assumptions] --> O
    Q[Public quote and inventory rules] --> O
    O --> E[FIFO execution and finite depth]
    E --> A[Exact cash and inventory ledgers]
    E --> M[Later reference and role-specific markouts]
    R[Public mark and funding conventions] --> A
    V[BSM volatility, rates, expiry and exercise assumptions] --> P[Option model prices and Greeks]
    P --> D[Finite dealer quotes]
    D --> A
    P --> H[Discrete stock hedge decisions]
    H --> E
    A --> X[Actual portfolio exposure]
    P --> X
    C[Return distribution, covariance and time assumptions] --> T[Conditional VaR and ES]
    X --> T
    V --> T
    C --> W[Constrained allocation studies]
    S[Chosen stress and liquidity assumptions] --> F[Hypothetical full-repricing P&L]
    X --> F
    V --> F
    G[Synthetic asset relationship and structural-break assumptions] --> Y[Published multi-asset prices]
    Y --> B[Causal OLS and past-window normalisation]
    B --> Z[Stat Arb signals and two-leg orders]
    Z --> E
    A --> N[Whole-session research outcomes]
    K[Seed design, selection, sample and independence assumptions] --> U[Intervals and comparison claims]
    N --> U
    M --> U
    X --> J[Allowlisted public tutor context]
    U --> J
```

An accounting identity can hold perfectly while the model feeding the mark or risk forecast is wrong. For example, the cash paid for an option is exact; tomorrow's option value under fixed IV is conditional. Likewise a reproducible Stat Arb backtest can be causally correct and still fail when its fitted relationship changes.
