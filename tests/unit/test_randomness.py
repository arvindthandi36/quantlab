import os
import random
import subprocess
import sys

import pytest

from quantlab.randomness import RandomStreams


def test_seeded_named_streams_reproduce_and_restart_explicitly():
    streams = RandomStreams(42)
    first, second = streams.create("noise"), streams.create("noise")
    assert [first.random() for _ in range(20)] == [second.random() for _ in range(20)]
    assert streams.create("noise").random() == RandomStreams(42).create("noise").random()


def test_streams_do_not_depend_on_creation_order_or_other_draws():
    streams = RandomStreams(42)
    noise, latent = streams.create("noise"), streams.create("latent")
    expected_latent = streams.create("latent")
    for _ in range(100):
        noise.random()
    assert [latent.random() for _ in range(20)] == [expected_latent.random() for _ in range(20)]
    assert streams.create("noise").getstate() != streams.create("latent").getstate()
    assert streams.create("noise").getstate() != RandomStreams(43).create("noise").getstate()


def test_no_mutation_of_global_random_state():
    before = random.getstate()
    RandomStreams(1).create("test").random()
    assert random.getstate() == before


def test_streams_do_not_depend_on_process_hash_salt():
    script = (
        "from quantlab.randomness import RandomStreams; "
        "rng = RandomStreams(42).create('noise'); "
        "print([rng.random() for _ in range(5)])"
    )
    outputs = [
        subprocess.check_output(
            [sys.executable, "-c", script],
            env={**os.environ, "PYTHONHASHSEED": salt},
            text=True,
        )
        for salt in ("1", "999")
    ]
    assert outputs[0] == outputs[1]


@pytest.mark.parametrize("seed", [True, 1.5, "42", None])
def test_invalid_seed_type(seed):
    with pytest.raises(TypeError):
        RandomStreams(seed)


def test_invalid_seed_value_and_stream_names():
    with pytest.raises(ValueError):
        RandomStreams(-1)
    for name in ("", " noise", "noise "):
        with pytest.raises(ValueError):
            RandomStreams(1).create(name)
    with pytest.raises(TypeError):
        RandomStreams(1).create(2)
