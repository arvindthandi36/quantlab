import pytest

from quantlab.market.events import EventKind, EventQueue


def test_clock_jumps_chronologically_and_ties_follow_scheduling_order():
    queue = EventQueue()
    later = queue.schedule(20, EventKind.NOISE)
    first = queue.schedule(10, EventKind.LIQUIDITY)
    second = queue.schedule(10, EventKind.LATENT)
    assert queue.now_us == 0
    assert queue.peek() == first
    assert queue.pop() == first
    assert queue.now_us == 10
    third = queue.schedule(10, EventKind.NOISE)
    assert [queue.pop(), queue.pop(), queue.pop()] == [second, third, later]
    assert queue.now_us == 20
    assert queue.peek() is None
    with pytest.raises(IndexError, match="empty"):
        queue.pop()


@pytest.mark.parametrize("time", [True, 1.5, "1", None])
def test_clock_rejects_noninteger_time(time):
    with pytest.raises(TypeError):
        EventQueue().schedule(time, EventKind.NOISE)


def test_no_backwards_time_or_silently_skipped_events():
    queue = EventQueue()
    with pytest.raises(ValueError):
        queue.schedule(-1, EventKind.NOISE)
    with pytest.raises(TypeError):
        queue.schedule(0, "noise")
    event = queue.schedule(5, EventKind.NOISE)
    assert event.sequence == 1  # Invalid attempts do not consume IDs.
    queue.advance_to(4)
    with pytest.raises(ValueError, match="pending"):
        queue.advance_to(5)
    queue.pop()
    with pytest.raises(ValueError, match="past"):
        queue.schedule(4, EventKind.NOISE)
    with pytest.raises(ValueError, match="past"):
        queue.advance_to(4)
    queue.advance_to(10)
    assert queue.now_us == 10
