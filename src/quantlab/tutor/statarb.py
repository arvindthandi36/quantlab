"""Stat-arb teaching grounded in detached current public facts."""

from quantlab.tutor.context import PublicContext

# intuition, mathematics, common mistake, project-defence question
LESSONS = {
    "covariance": (
        "Covariance measures whether two changes tend to move together, retaining their units.",
        "cov(X,Y)=sum((X-meanX)(Y-meanY))/(n-1)",
        "Positive covariance guarantees profitable convergence.",
        "Why do covariance units matter?",
    ),
    "correlation": (
        "Correlation measures linear co-movement, not a stable tradable spread.",
        "rho=cov(X,Y)/(sdX*sdY)",
        "Price correlation 0.95 is enough to justify a pairs trade.",
        "Why is correlation different from cointegration?",
    ),
    "regression": (
        "OLS chooses the line with the smallest total squared vertical errors.",
        "Minimise sum((Y-alpha-beta*X)^2). The live fit ends before this observation.",
        "High R² establishes future profitability.",
        "Why does QuantLab fit on past rows using a stable least-squares solver?",
    ),
    "alpha": (
        "The intercept shifts the fitted price relationship up or down.",
        "alpha_hat=meanY-beta_hat*meanX, in GBP per Y unit",
        "A regression intercept is trading alpha.",
        "Why is this alpha not evidence of investment skill?",
    ),
    "beta": (
        "Beta estimates how Y changes with X under this particular fitted model.",
        "beta_hat=cov(X,Y)/var(X), in X units per Y unit for a unit hedge",
        "Beta is a permanent exact market hedge.",
        "Why can a fitted beta change after deployment?",
    ),
    "residual": (
        "A residual is the amount by which Y differs from its fitted relationship to X.",
        "residual=Y-alpha-beta*X",
        "Y-X is always the right residual.",
        "Why use residuals instead of raw price differences?",
    ),
    "r_squared": (
        "R² describes how much sample variation the fitted line accounts for.",
        "R²=1-SSE/SST; undefined for a constant Y",
        "A high R² promises profitable trading.",
        "How can unrelated wandering prices have a high R²?",
    ),
    "hedge_ratio": (
        (
            "A unit hedge offsets a fitted relationship; whole-unit rounding "
            "leaves residual exposure."
        ),
        "Long spread: qY>0 and qX approximately -beta*qY",
        "A regression hedge is automatically dollar-neutral.",
        "Which units and price scales enter the hedge?",
    ),
    "z_score": (
        "A z-score compares today's residual with its past mean and standard deviation.",
        "z=(spread-current_past_mean)/past_sd; t is excluded from normalisation",
        "z=2.5 guarantees the spread will fall.",
        "Why is a z-score not a convergence probability?",
    ),
    "mean_reversion": (
        (
            "Under the model, deviations tend to shrink on average but "
            "individual paths can worsen."
        ),
        "s[t]=mu+phi*(s[t-1]-mu)+sigma*Z[t], |phi|<1",
        "Every deviation must reverse before the stop.",
        "Why can a mean-reverting strategy still lose money?",
    ),
    "stationarity": (
        (
            "Stable statistical behaviour concerns the distribution through "
            "time, not whether a chart looks flat."
        ),
        "Weak stationarity: constant mean/variance and lag-dependent covariance",
        "A flat-looking price proves stationarity.",
        "Which changing assumptions would undermine a stationary-spread model?",
    ),
    "unit_root": (
        "A unit-root process carries shocks forward rather than pulling them back.",
        "s[t]=s[t-1]+epsilon[t] when phi=1; variance grows with time",
        "The descriptive AR(1) fit supplies a valid ADF p-value.",
        "What can our limited AR diagnostic establish, and what can it not establish?",
    ),
    "cointegration": (
        "Wandering individual prices can share a stationary linear combination.",
        "If X is I(1), Y=alpha+beta*X+s and s is I(0), their residual is stationary",
        "Cointegration guarantees positive net trading P&L.",
        "What evidence beyond correlation supports a stable residual?",
    ),
    "look_ahead": (
        "A historical decision must use only information already available then.",
        "fit_end<=t; normalisation rows [t-W,t); current row only forms current residual",
        "Full-sample beta is legitimate for trades early in that sample.",
        "How do future-data mutation tests protect QuantLab's signals?",
    ),
    "walk_forward": (
        "Fit on a past window, freeze the model for an unseen block, then move forward.",
        "fit [t-W,t); deploy [t,t+B)",
        "Walk-forward refitting guarantees better performance.",
        "Why is walk-forward closer to deployment than a full-sample fit?",
    ),
    "parameter_instability": (
        "A relationship estimated in one period can change or disappear later.",
        "Compare alpha_hat and beta_hat across past fitting windows",
        "An old fit is a law of nature.",
        "What happens if the relationship structurally breaks?",
    ),
    "leg_risk": (
        "The first fill creates real exposure while the other leg remains unfilled.",
        "Unit-hedge imbalance in GBP=abs(qX+beta*qY)*X",
        "Two submitted orders imply two completed fills.",
        "What happens when the hedge leg only partially fills?",
    ),
    "dollar_neutrality": (
        "Equal long and short marked pounds remove net marked value, not every risk factor.",
        "Dollar net=qX*X+qY*Y; factor net=sum(qi*Pi*loading_i)",
        "Dollar-neutral and market-neutral mean the same thing.",
        "Can a dollar-neutral pair retain common-factor exposure?",
    ),
    "factor_neutrality": (
        "Factor neutrality offsets exposure to a specified factor and model.",
        "Factor exposure=sum(qi*Pi*estimated_loading_i)",
        "Neutral to one fitted factor means neutral to every market risk.",
        "Which factor is actually being hedged in this example?",
    ),
    "multiple_testing": (
        (
            "Searching many candidates creates more opportunities for "
            "impressive results by chance."
        ),
        "For m independent size-a tests, P(at least one false rejection)=1-(1-a)^m",
        "Report only the best of twenty tried pairs.",
        "What must you know about all tried candidates before trusting the winner?",
    ),
    "data_snooping": (
        (
            "Repeatedly using the test outcome to improve choices turns the "
            "test into development data."
        ),
        "Selection sees training only; persist choices before claiming evaluation access",
        "An evaluation seed remains untouched after repeated inspection.",
        "Why can high in-sample performance disappear out of sample?",
    ),
    "transaction_costs": (
        "Both legs pay executable spreads and fees; frequent trading can consume small edges.",
        "net P&L=marked movement-signed execution shortfall-fees",
        "Compute pair P&L at mid and ignore the second leg's costs.",
        "How do costs change a high-turnover strategy?",
    ),
}


def statarb_context(state, source):
    s, m = state["signal"], state["metrics"]
    return PublicContext(
        source,
        "statarb",
        state["revision"],
        state["t"] * 1_000_000,
        dict(
            t=state["t"],
            alpha=s.get("fit", {}).get("alpha"),
            beta=s.get("fit", {}).get("beta"),
            r_squared=s.get("fit", {}).get("r_squared"),
            fit_end=s.get("fit", {}).get("end"),
            spread=s.get("spread"),
            mean=s.get("mean"),
            sd=s.get("sd"),
            z=s.get("z"),
            correlation=s.get("price_correlation"),
            pnl=m["net_pnl"],
            gross=state["exposure"]["gross"],
            net=state["exposure"]["net"],
            imbalance=state["exposure"]["imbalance"],
            costs=m["costs"],
            factor_exposure=state["risk"]["factor_exposure"],
        ),
    )


def statarb_relevance(context):
    return [
        (
            k,
            100
            if k == "leg_risk" and context.facts["imbalance"] > 1
            else 90
            if k == "z_score" and context.facts["z"] is not None
            else 40,
        )
        for k in LESSONS
    ]


def statarb_question(concept, context, difficulty=1):
    from quantlab.tutor.questions import Question, describe

    intuition, maths, mistake, interview = LESSONS[concept]
    prompt = (
        f"For this observed {concept.replace('_', ' ')} example, which statement is defensible?"
    )
    options, expected, kind, level = (
        (("mechanism", intuition), ("mistake", mistake)),
        "mechanism",
        "choice",
        1,
    )
    f = context.facts
    if difficulty == 2 and concept in ("z_score", "beta", "alpha", "leg_risk"):
        value = {
            "z_score": f["z"],
            "beta": f["beta"],
            "alpha": f["alpha"],
            "leg_risk": f["imbalance"],
        }[concept]
        if value is not None:
            prompt = {
                "z_score": (
                    "Using the displayed spread, past mean and SD, calculate the z-score."
                ),
                "beta": "What is the estimated number of X units per Y unit before rounding?",
                "alpha": "What is this model's intercept in GBP?",
                "leg_risk": "What is the currently displayed unit-hedge imbalance in GBP?",
            }[concept]
            options, expected, kind, level = (), str(value), "number", 2
    elif difficulty >= 3:
        prompt = interview + " Select both defensible statements."
        options = (
            ("mechanism", intuition),
            (
                "limits",
                "The result depends on the data, execution and stated model assumptions",
            ),
            ("mistake", mistake),
            ("future", "Future convergence is known at this decision time"),
        )
        expected, kind, level = ("mechanism", "limits"), "choices", min(4, difficulty)
    return Question(
        concept,
        level,
        prompt,
        kind,
        expected,
        options,
        ("Use only the observations available at this event.", intuition),
        intuition,
        maths,
        describe(context),
        interview,
        concept + ": unsupported stat-arb inference",
        "0.001",
        ("statarb",),
    )
