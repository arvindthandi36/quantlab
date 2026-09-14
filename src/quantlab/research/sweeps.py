"""One-dimensional designs reusable for any JSON-configured simulation adapter."""

from quantlab.research.codec import canonical, plain
from quantlab.research.models import ExperimentSpec, Variant


def sweep_spec(
    *,
    question,
    hypothesis,
    seeds,
    adapter,
    base_configuration,
    parameter: tuple[str, ...],
    values: tuple,
    **options,
) -> ExperimentSpec:
    if not parameter or any(not isinstance(p, str) or not p for p in parameter):
        raise ValueError("parameter must identify a nested configuration field")
    if not values or len({canonical(v) for v in values}) != len(values):
        raise ValueError("sweep values must be nonempty and unique")
    variants = []
    for value in values:
        configuration = plain(base_configuration)
        target = configuration
        for key in parameter[:-1]:
            if key not in target or not isinstance(target[key], dict):
                raise ValueError("unknown sweep parameter path")
            target = target[key]
        if parameter[-1] not in target:
            raise ValueError("unknown sweep parameter")
        target[parameter[-1]] = plain(value)
        adapter.validate(configuration)
        variants.append(Variant(".".join(parameter) + "=" + str(value), configuration))
    keys = [adapter.environment_key(v.configuration) for v in variants]
    paired = all(key == keys[0] for key in keys)
    return ExperimentSpec(
        question, hypothesis, seeds, tuple(variants), adapter.name, paired=paired, **options
    )
