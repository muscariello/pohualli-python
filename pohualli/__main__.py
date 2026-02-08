"""Module entry point.

Allows running the package with `python -m pohualli`.
"""

from .cli import main as _cli_main


def main() -> None:  # pragma: no cover (thin wrapper)
    _cli_main()


if __name__ == "__main__":  # pragma: no cover
    main()
