"""Bound visual replay retention without truncating or changing financial evidence."""

from quantlab.research.codec import canonical


class ReplayFrames(list):
    """An explicit serialized-size budget; Python object overhead is additional."""

    def __init__(self, values=(), *, byte_limit=64_000_000):
        super().__init__()
        self.byte_limit = byte_limit
        self.serialized_bytes = 0
        for value in values:
            self.append(value)

    def append(self, value):
        size = len(canonical(value).encode())
        if self.serialized_bytes + size > self.byte_limit:
            raise ValueError(
                "Visual replay exceeds the 64 MB frame budget. No frames were truncated. "
                "Verify this journal through the Python replay API without frame capture; "
                "the current application session is unchanged."
            )
        super().append(value)
        self.serialized_bytes += size
