"""Fail at the numerical boundary rather than returning a misleading finite summary."""

from functools import wraps


def checked(function):
    """Reject overflow, undefined operations and division by zero; allow underflow.

    Underflow of a very small tail to zero is a disclosed precision limitation.
    This does not catch accounting/invariant failures or repair invalid inputs.
    """

    @wraps(function)
    def run(*args, **kwargs):
        import numpy as np

        try:
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                return function(*args, **kwargs)
        except (FloatingPointError, OverflowError, ZeroDivisionError) as exc:
            raise ValueError(
                f"{function.__name__}: input magnitude exceeds reliable numerical precision; "
                "no estimate returned. Reduce the scale or inspect the inputs."
            ) from exc

    return run
