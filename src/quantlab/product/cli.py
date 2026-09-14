"""Release launcher. Financial model/replay version remains unchanged."""

import argparse

from quantlab import __version__ as core_version
from quantlab.product import VERSION


def main(argv=None):
    parser = argparse.ArgumentParser(description="QuantLab — local finance laboratory")
    parser.add_argument("command", nargs="?", choices=["serve"], default="serve")
    parser.add_argument(
        "--version",
        action="version",
        version=f"QuantLab {VERSION} (financial replay core {core_version})",
    )
    _, remaining = parser.parse_known_args(argv)
    from quantlab.trading.server import main as serve

    serve(remaining)


if __name__ == "__main__":
    main()
