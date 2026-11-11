"""Launch D-Tale for interactive exploration of the sales dataset."""

import sys
import webbrowser
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


MINIMUM_VERSIONS = {
    "pandas": (2, 0, 0),
    "dtale": (3, 10, 0),
}


def version_is_supported(installed: str, minimum: tuple[int, ...]) -> bool:
    """Return whether an installed release meets the required minimum."""
    release = installed.split("+", maxsplit=1)[0].split(".", maxsplit=3)
    try:
        installed_parts = tuple(int(part) for part in release[:3])
    except ValueError:
        return False

    installed_parts += (0,) * (len(minimum) - len(installed_parts))
    return installed_parts[: len(minimum)] >= minimum


def verify_versions() -> bool:
    """Check that pandas and D-Tale are installed at compatible versions."""
    for package, minimum in MINIMUM_VERSIONS.items():
        try:
            installed = version(package)
        except PackageNotFoundError:
            print(
                f"Required package '{package}' is not installed. "
                "Install dependencies in the active environment first.",
                file=sys.stderr,
            )
            return False

        print(f"Found {package} {installed}.")
        if not version_is_supported(installed, minimum):
            minimum_text = ".".join(str(part) for part in minimum)
            print(
                f"{package} {minimum_text} or newer is required; found {installed}.",
                file=sys.stderr,
            )
            return False

    return True


def main() -> int:
    """Load the sales CSV and open the D-Tale interface."""
    if not verify_versions():
        return 1

    try:
        import dtale
        import pandas as pd
    except ImportError as error:
        print(f"Could not import a required library: {error}", file=sys.stderr)
        return 1

    data_path = Path(__file__).resolve().with_name("sales_data.csv")
    try:
        sales_data = pd.read_csv(data_path)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        print(f"Could not load {data_path}: {error}", file=sys.stderr)
        return 1

    print(f"Loaded {len(sales_data):,} rows from {data_path}.")
    try:
        instance = dtale.show(sales_data, open_browser=False)
        # build_main_url returns a URL in IDE/IPython frontends as well.
        url = instance.build_main_url()
        if not url:
            print("D-Tale did not return an interface URL.", file=sys.stderr)
            return 1
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(f"Could not launch the D-Tale interface: {error}", file=sys.stderr)
        return 1

    try:
        browser_opened = webbrowser.open(url)
    except (OSError, webbrowser.Error) as error:
        print(f"Could not open a browser automatically: {error}", file=sys.stderr)
        browser_opened = False

    if browser_opened:
        print("D-Tale launched successfully in your browser.")
    else:
        print("D-Tale is running; open the URL below in your browser.")
    print(f"Open this URL in your browser: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
