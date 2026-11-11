"""Generate automated EDA reports for the sales dataset."""

import re
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


MINIMUM_VERSIONS = {
    "pandas": "2.0.0",
    "ydata-profiling": "4.6.0",
    "sweetviz": "2.3.0",
}


def is_version_supported(installed: str, minimum: str) -> bool:
    """Compare release numbers without requiring an extra versioning package."""
    version_match = re.fullmatch(r"(\d+(?:\.\d+)*)(.*)", installed)
    if version_match is None:
        return False

    installed_parts = tuple(int(part) for part in version_match.group(1).split("."))
    minimum_parts = tuple(int(part) for part in minimum.split("."))
    part_count = max(len(installed_parts), len(minimum_parts))
    installed_parts += (0,) * (part_count - len(installed_parts))
    minimum_parts += (0,) * (part_count - len(minimum_parts))

    is_prerelease = bool(
        re.match(
            r"[-.]?(?:a|b|rc|dev)",
            version_match.group(2),
            flags=re.IGNORECASE,
        )
    )
    return installed_parts > minimum_parts or (
        installed_parts == minimum_parts and not is_prerelease
    )


def verify_library_versions() -> bool:
    """Check that the required distributions are installed at supported versions."""
    for package, minimum in MINIMUM_VERSIONS.items():
        try:
            installed = version(package)
        except PackageNotFoundError:
            print(
                f"Required library '{package}' is not installed. "
                "Install dependencies using the commands in the setup instructions.",
                file=sys.stderr,
            )
            return False

        print(f"Found {package} {installed}.")
        if not is_version_supported(installed, minimum):
            print(
                f"{package} {minimum} or newer is required; found {installed}.",
                file=sys.stderr,
            )
            return False

    return True


def main() -> int:
    """Load the dataset and save YData Profiling and Sweetviz reports."""
    if not verify_library_versions():
        return 1

    try:
        import pandas as pd
        import sweetviz as sv
        from ydata_profiling import ProfileReport
    except ImportError as error:
        print(
            f"Could not import an EDA library: {error}. "
            "Check that the dependencies are installed in the active environment.",
            file=sys.stderr,
        )
        return 1

    script_directory = Path(__file__).resolve().parent
    data_path = script_directory / "sales_data.csv"

    try:
        sales_data = pd.read_csv(data_path)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        print(f"Could not load {data_path}: {error}", file=sys.stderr)
        return 1

    print(f"Loaded {len(sales_data):,} rows from {data_path}.")
    if "revenue" not in sales_data.columns:
        print(
            "The dataset must contain a 'revenue' column for the Sweetviz target.",
            file=sys.stderr,
        )
        return 1

    ydata_path = script_directory / "ydata_report.html"
    try:
        profile = ProfileReport(sales_data, minimal=True)
        profile.to_file(ydata_path)
    except (OSError, ValueError) as error:
        print(f"Could not create the YData Profiling report: {error}", file=sys.stderr)
        return 1
    print(f"YData Profiling report saved to {ydata_path}.")

    sweetviz_path = script_directory / "sweetviz_report.html"
    sweetviz_data = sales_data.copy()
    sweetviz_data = sweetviz_data.dropna(subset=["revenue"])
    if sweetviz_data.empty:
        print(
            "Cannot create the Sweetviz report: no rows have a non-missing revenue value.",
            file=sys.stderr,
        )
        return 1

    try:
        sweetviz_report = sv.analyze(sweetviz_data, target_feat="revenue")
        sweetviz_report.show_html(filepath=str(sweetviz_path), open_browser=False)
    except (OSError, ValueError, TypeError) as error:
        print(f"Could not create the Sweetviz report: {error}", file=sys.stderr)
        return 1
    print(f"Sweetviz report saved to {sweetviz_path}.")
    print("EDA report generation completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
