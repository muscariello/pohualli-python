"""Module entry point.

Allows running the package with `python -m pohualli` and supports
packaged launchers (e.g. Briefcase) that may invoke the top-level
module instead of the configured `main_module`.
"""

from .desktop_app import main as _desktop_main


def main() -> None:  # pragma: no cover (thin wrapper)
    _desktop_main()


if __name__ == "__main__":  # pragma: no cover
    main()
