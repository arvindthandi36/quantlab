"""One supported local application, with all labs served by the same process."""

import argparse

from quantlab import __version__


def main():
    parser = argparse.ArgumentParser(
        description="QuantLab local quantitative learning platform"
    )
    parser.add_argument("command", nargs="?", choices=["serve"], default="serve")
    parser.add_argument("--version", action="version", version=f"QuantLab {__version__}")
    args, remaining = parser.parse_known_args()
    from quantlab.trading.server import main as serve

    serve(remaining)


if __name__ == "__main__":
    main()
