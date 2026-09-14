"""Phase 9 explanations from allowlisted, current public portfolio risk facts."""

from quantlab.tutor.context import PublicContext

# Each lesson is (intuition, mathematics, common mistake, interview question).
LESSONS = {
    "covariance": (
        (
            "Covariance asks whether two returns tend to be above or below their own averages"
            " together."
        ),
        "Sample cov(A,B)=sum((A_i-meanA)(B_i-meanB))/(n-1). Units are return squared.",
        "Covariance and correlation are the same number.",
        "Why centre both return series before measuring their co-movement?",
    ),
    "correlation": (
        "Correlation removes the scale of the two assets' movements.",
        "rho=cov(A,B)/(sigmaA*sigmaB). It is undefined when either standard deviation is zero.",
        "Historical correlation is a permanent property of two assets.",
        "How would you stress diversification without claiming correlations always rise?",
    ),
    "covariance_matrices": (
        "The diagonal stores individual variances; the off-diagonal entries store co-movement.",
        "Sigma_ij=cov(R_i,R_j); Sigma_ij=Sigma_ji.",
        "A covariance matrix may use unsynchronised observation rows.",
        "What does every entry of your covariance matrix encode?",
    ),
    "portfolio_variance": (
        "Risk depends on both the sizes of positions and how their returns move together.",
        "Variance=w^T Sigma w=sum(w_i² Sigma_ii)+2 sum_{i<j}(w_i w_j Sigma_ij).",
        "Portfolio variance is just the average asset variance.",
        "Explain where the cross-asset terms come from.",
    ),
    "diversification": (
        (
            "Holding different assets can reduce risk when their movements do not fully "
            "reinforce one another."
        ),
        "For two equal-volatility, half-weight assets: sigma_p²=sigma²(1+rho)/2.",
        "More position names always means a safer portfolio.",
        "Can both assets be volatile while their combination is less volatile than either?",
    ),
    "var": (
        "VaR is a loss threshold under stated assumptions. Worse losses remain possible.",
        "VaR_alpha=inf{x:F_loss(x)>=alpha}. Loss is minus P&L.",
        "VaR is the maximum possible loss.",
        "Why must a risk manager look beyond 95% VaR?",
    ),
    "expected_shortfall": (
        (
            "Expected Shortfall measures the average severity of the worst tail, not just "
            "where it begins."
        ),
        (
            "ES_alpha=(1/(1-alpha))*integral_alpha^1 VaR_u du; discrete samples use a "
            "fractional boundary atom."
        ),
        "Average the best 5% of profits to calculate loss Expected Shortfall.",
        "How can portfolios share a VaR threshold but have different Expected Shortfall?",
    ),
    "tail_risk": (
        "Rare outcomes can dominate losses even when everyday movements appear modest.",
        (
            "At confidence alpha, tail probability is 1-alpha; N*(1-alpha) is effective tail "
            "sample size."
        ),
        "A thousand simulated paths guarantees a thousand independent crisis observations.",
        "What does a small tail sample fail to tell you?",
    ),
    "stress_testing": (
        (
            "A stress test asks what this actual portfolio would do in a specified difficult "
            "situation."
        ),
        (
            "Scenario P&L=repriced model changes+stock changes+cash carry-explicit "
            "liquidation cost."
        ),
        "Stress P&L has already been realised in the account.",
        "How would you stress a supposedly diversified portfolio?",
    ),
    "concentration": (
        (
            "A large share in one instrument can leave the book dependent on a narrow source "
            "of value."
        ),
        (
            "Value share_i=abs(V_i)/sum(abs(V)); HHI=sum(share_i²). Delta concentration is a "
            "separate measure."
        ),
        "Low estimated volatility proves a portfolio is diversified.",
        "Why can option-premium concentration understate risk concentration?",
    ),
    "risk_contribution": (
        (
            "An exposure can add risk or offset other exposures; contribution depends on the "
            "whole portfolio."
        ),
        (
            "Marginal volatility=(Sigma w)_i/sigma_p; component=w_i*(Sigma w)_i/sigma_p, when"
            " sigma_p>0."
        ),
        "Risk contribution is always positive and stable near zero variance.",
        "What does a negative component risk contribution mean?",
    ),
    "delta_normal": (
        "Delta-normal risk treats options as if their current stock sensitivity stayed fixed.",
        (
            "Approximate P&L=sum(delta_i*S_i*return_i); apply normal moments to that linear "
            "exposure."
        ),
        "Delta neutrality removes gamma, vega and all possible loss.",
        "Why can delta-normal VaR fail for an options portfolio?",
    ),
    "full_revaluation": (
        "Full revaluation runs the pricing model again at each hypothetical future state.",
        "Option P&L=q*m*(BSM(new inputs)-BSM(current inputs)); quote/model basis is frozen.",
        "Full model repricing gives an exact prediction of market liquidation proceeds.",
        "What model risk survives full revaluation?",
    ),
    "scenario_analysis": (
        "A scenario changes explicit inputs and reveals which held positions drive the result.",
        (
            "Taylor P&L=delta*dS+0.5*gamma*dS²+vega*dvol+theta*dt+rho*dr; "
            "residual=full-approximate."
        ),
        "Force Greek terms to equal full repricing by hiding the residual.",
        "Why can a larger shock increase Greek approximation error?",
    ),
    "model_risk": (
        "The reported number changes when the model, sample or assumptions change.",
        (
            "Risk is conditional on exposure, distribution, covariance, horizon, confidence "
            "and valuation model."
        ),
        "More decimal places imply a more accurate forecast.",
        "What would make your Monte Carlo VaR misleading despite reproducibility?",
    ),
    "minimum_variance": (
        (
            "Choose weights that minimise estimated variability while respecting an explicit "
            "budget and constraints."
        ),
        "Minimise w^T Sigma w subject to sum(w)=1 and stated bounds.",
        "The minimum-variance portfolio is guaranteed to be safest in the future.",
        "Why can an unconstrained cash-inclusive minimum-variance solution be all cash?",
    ),
    "portfolio_optimisation": (
        (
            "Optimisation makes the trade-off and constraints explicit; it does not discover "
            "certain future returns."
        ),
        "Minimise (lambda/2)*w^T Sigma w-mu^T w, with lambda>0 and budget/weight constraints.",
        "An optimiser's expected returns are facts about the future.",
        "How can uncertain expected returns destabilise an allocation?",
    ),
    "positive_semidefinite": (
        "A valid covariance matrix cannot imply negative variance for any portfolio direction.",
        (
            "w^T Sigma w>=0 for every real w; a symmetric matrix is PSD when all eigenvalues "
            "are nonnegative."
        ),
        "Silently replace any invalid covariance matrix with one that passes.",
        "What changes when a covariance matrix is singular?",
    ),
    "correlated_simulation": (
        (
            "Transform independent random shocks so their joint movement follows the chosen "
            "covariance."
        ),
        (
            "If Sigma=L L^T and Z has identity covariance, LZ has covariance Sigma; Cholesky "
            "needs positive definiteness."
        ),
        "Simulate each asset independently while claiming nonzero correlation.",
        "How would you verify your correlated draws statistically?",
    ),
}


def risk_context(state, source):
    r = state["report"]
    p = r["portfolio"]
    m = r["monte_carlo"]["full"]
    f = {
        "equity": p["equity"],
        "pnl": p["pnl"],
        "gross": p["gross"],
        "delta": p["greeks"]["delta"],
        "gamma": p["greeks"]["gamma"],
        "vega": p["greeks"]["vega"],
        "var": m["var"],
        "es": m["es"],
        "confidence": m["confidence"],
        "horizon": r["settings"]["days"],
        "sample_n": m["n"],
        "correlation": r["correlation"][0][1],
        "variance": r["parametric"]["decomposition"]["variance"],
        "cross_variance": r["parametric"]["decomposition"]["cross_total"],
        "concentration": p["largest_position_share"],
        "scenario_pnl": None,
        "scenario_residual": None,
        "optimisation_variance": None,
    }
    if state.get("scenario"):
        f["scenario_pnl"] = state["scenario"]["full_pnl"]
        f["scenario_residual"] = state["scenario"]["residual"]
    if state.get("optimisation"):
        f["optimisation_variance"] = state["optimisation"]["variance"]
    return PublicContext(source, "risk", state["revision"], state["revision"], f)


def risk_relevance(context):
    keys = list(LESSONS)
    if context.facts["optimisation_variance"] is None:
        keys = [k for k in keys if k not in ("minimum_variance", "portfolio_optimisation")]
    return [(k, 100 if k == "var" else 70 if k == "expected_shortfall" else 40) for k in keys]


def risk_question(concept, context, difficulty=1):
    from quantlab.tutor.questions import Question, describe

    intuition, maths, mistake, interview = LESSONS[concept]
    prompt = (
        f"For this portfolio's {concept.replace('_', ' ')}, which interpretation is defensible?"
    )
    expected = "mechanism"
    options = (("mechanism", intuition), ("mistake", mistake))
    level = 1
    answer_type = "choice"
    tolerance = "0"
    f = context.facts
    if difficulty == 2 and concept in (
        "var",
        "tail_risk",
        "portfolio_variance",
        "scenario_analysis",
        "concentration",
    ):
        prompt, value = {
            "var": (
                (
                    "At this confidence, what fraction of model outcomes lies beyond the VaR "
                    "threshold?"
                ),
                1 - f["confidence"],
            ),
            "tail_risk": (
                "How many effective observations belong to this run's worst tail?",
                f["sample_n"] * (1 - f["confidence"]),
            ),
            "portfolio_variance": (
                "What is volatility in GBP from this displayed linear portfolio variance?",
                f["variance"] ** 0.5,
            ),
            "scenario_analysis": (
                "What is the full-minus-Greek residual in the selected scenario?",
                f["scenario_residual"],
            ),
            "concentration": (
                "Express the largest absolute marked-value share as a percentage.",
                100 * f["concentration"],
            ),
        }[concept]
        if value is not None:
            expected = str(value)
            options = ()
            level = 2
            answer_type = "number"
            tolerance = "0.00001"
    elif difficulty >= 3:
        prompt = interview + " Select both defensible statements."
        options = (
            ("mechanism", intuition),
            ("limits", "The conclusion depends on stated model and data assumptions"),
            ("mistake", mistake),
            ("future", "The next actual market move is already known"),
        )
        expected = ("mechanism", "limits")
        level = min(4, difficulty)
        answer_type = "choices"
    return Question(
        concept,
        level,
        prompt,
        answer_type,
        expected,
        options,
        ("Separate an observed position from a hypothetical future outcome.", intuition),
        intuition,
        maths,
        describe(context),
        interview,
        concept + ": incorrect risk claim",
        tolerance,
        ("risk",),
    )
