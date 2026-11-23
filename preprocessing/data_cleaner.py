"""
Stock Market Data Cleaning Module
==================================
Comprehensive data cleaning and validation for stock market datasets.
Handles missing values, duplicates, date standardization, price/volume
validation, outlier detection, and data type enforcement.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class StockDataCleaner:
    """End-to-end cleaner for stock market CSV data.

    Parameters
    ----------
    input_path : str | Path
        Path to the raw CSV file.
    output_path : str | Path, optional
        Default destination when saving cleaned data.
    """

    # Columns that must hold positive prices
    PRICE_COLS = ["Open", "High", "Low", "Close"]
    VOLUME_COL = "Volume"
    DATE_COL = "Date"

    # Common date formats to try during standardization
    _DATE_FORMATS = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%d %B %Y",
        "%Y%m%d",
    ]

    def __init__(self, input_path: str | Path, output_path: str | Path | None = None):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        self.df: pd.DataFrame = pd.read_csv(self.input_path)
        self._records_before: int = len(self.df)
        self._report: dict = {}

        # Normalize column names (strip whitespace, title-case)
        self.df.columns = [c.strip().title() for c in self.df.columns]

        logger.info(
            "Loaded %d records with columns: %s",
            self._records_before,
            list(self.df.columns),
        )

    # ------------------------------------------------------------------
    # Detection & validation helpers
    # ------------------------------------------------------------------

    def detect_missing_values(self) -> dict:
        """Return a dict of ``{column: missing_count}`` for every column
        that has at least one missing value."""
        counts = self.df.isnull().sum()
        missing = counts[counts > 0].to_dict()
        logger.info("Missing values detected: %s", missing)
        return missing

    def remove_duplicates(self) -> int:
        """Drop exact duplicate rows and return the number removed."""
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        removed = before - len(self.df)
        logger.info("Removed %d duplicate rows", removed)
        return removed

    def standardize_dates(self) -> None:
        """Convert the *Date* column to ``YYYY-MM-DD`` strings.

        Tries a list of common date formats and falls back to
        ``pd.to_datetime`` with ``infer_datetime_format``.
        """
        if self.DATE_COL not in self.df.columns:
            logger.warning("Column '%s' not found – skipping date standardization", self.DATE_COL)
            return

        raw = self.df[self.DATE_COL].astype(str).str.strip()
        parsed = pd.Series([pd.NaT] * len(raw), index=raw.index)

        for fmt in self._DATE_FORMATS:
            mask = parsed.isna()
            if not mask.any():
                break
            try:
                parsed[mask] = pd.to_datetime(raw[mask], format=fmt, errors="coerce")
            except Exception:
                continue

        # Fallback: let pandas infer remaining unparsed dates
        still_missing = parsed.isna()
        if still_missing.any():
            parsed[still_missing] = pd.to_datetime(raw[still_missing], errors="coerce")

        self.df[self.DATE_COL] = parsed.dt.strftime("%Y-%m-%d")
        failed = self.df[self.DATE_COL].isna().sum()
        if failed:
            logger.warning("%d dates could not be parsed and are set to NaT", failed)
        logger.info("Dates standardized to YYYY-MM-DD format")

    def validate_prices(self) -> list[dict]:
        """Validate OHLC price rules.

        Rules checked
        ~~~~~~~~~~~~~
        1. Open, High, Low, Close > 0
        2. High >= Low
        3. High >= Open  and  High >= Close
        4. Low  <= Open  and  Low  <= Close

        Returns a list of dicts, each containing the row index and the
        reason(s) it is invalid.
        """
        present_cols = [c for c in self.PRICE_COLS if c in self.df.columns]
        if not present_cols:
            logger.warning("No price columns found – skipping price validation")
            return []

        invalid_records: list[dict] = []

        for idx, row in self.df.iterrows():
            reasons: list[str] = []

            # Rule 1 – positive prices
            for col in present_cols:
                val = row.get(col)
                if pd.isna(val):
                    reasons.append(f"{col} is missing")
                elif val <= 0:
                    reasons.append(f"{col} <= 0 ({val})")

            # Rules 2-4 require all four columns
            if all(c in self.df.columns for c in self.PRICE_COLS):
                o, h, l, c = (row.get(x) for x in self.PRICE_COLS)
                if pd.notna(h) and pd.notna(l):
                    if h < l:
                        reasons.append(f"High ({h}) < Low ({l})")
                if pd.notna(h) and pd.notna(o) and h < o:
                    reasons.append(f"High ({h}) < Open ({o})")
                if pd.notna(h) and pd.notna(c) and h < c:
                    reasons.append(f"High ({h}) < Close ({c})")
                if pd.notna(l) and pd.notna(o) and l > o:
                    reasons.append(f"Low ({l}) > Open ({o})")
                if pd.notna(l) and pd.notna(c) and l > c:
                    reasons.append(f"Low ({l}) > Close ({c})")

            if reasons:
                invalid_records.append({"index": idx, "reasons": reasons})

        logger.info("Found %d records with invalid prices", len(invalid_records))
        return invalid_records

    def validate_volume(self) -> list[dict]:
        """Ensure the *Volume* column contains non-negative integers.

        Returns a list of dicts with the row index and reason.
        """
        if self.VOLUME_COL not in self.df.columns:
            logger.warning("Column '%s' not found – skipping volume validation", self.VOLUME_COL)
            return []

        invalid_records: list[dict] = []

        for idx, val in self.df[self.VOLUME_COL].items():
            reasons: list[str] = []
            if pd.isna(val):
                reasons.append("Volume is missing")
            else:
                try:
                    num = float(val)
                except (ValueError, TypeError):
                    reasons.append(f"Volume is not numeric ({val!r})")
                    invalid_records.append({"index": idx, "reasons": reasons})
                    continue
                if num < 0:
                    reasons.append(f"Volume is negative ({val})")
                if num != int(num):
                    reasons.append(f"Volume is not an integer ({val})")
            if reasons:
                invalid_records.append({"index": idx, "reasons": reasons})

        logger.info("Found %d records with invalid volume", len(invalid_records))
        return invalid_records

    # ------------------------------------------------------------------
    # Outlier detection
    # ------------------------------------------------------------------

    def detect_outliers(
        self,
        method: str = "iqr",
        columns: list[str] | None = None,
        iqr_factor: float = 1.5,
        z_threshold: float = 3.0,
    ) -> dict[str, list[int]]:
        """Detect outliers using either the IQR or Z-score method.

        Parameters
        ----------
        method : ``'iqr'`` | ``'zscore'``
        columns : list of column names to inspect (defaults to price columns).
        iqr_factor : multiplier for IQR fences (default 1.5).
        z_threshold : absolute Z-score threshold (default 3.0).

        Returns
        -------
        dict
            ``{column_name: [list_of_outlier_indices]}``
        """
        if columns is None:
            columns = [c for c in self.PRICE_COLS if c in self.df.columns]

        method = method.lower()
        if method not in ("iqr", "zscore"):
            raise ValueError(f"Unknown outlier method '{method}'. Use 'iqr' or 'zscore'.")

        outliers: dict[str, list[int]] = {}

        for col in columns:
            if col not in self.df.columns:
                logger.warning("Column '%s' not in DataFrame – skipping", col)
                continue

            series = pd.to_numeric(self.df[col], errors="coerce").dropna()

            if method == "iqr":
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - iqr_factor * iqr
                upper = q3 + iqr_factor * iqr
                mask = (series < lower) | (series > upper)
            else:  # zscore
                mean = series.mean()
                std = series.std()
                if std == 0:
                    mask = pd.Series(False, index=series.index)
                else:
                    z = ((series - mean) / std).abs()
                    mask = z > z_threshold

            idxs = series[mask].index.tolist()
            if idxs:
                outliers[col] = idxs

        total = sum(len(v) for v in outliers.values())
        logger.info("Detected %d outlier data-points across %d columns (%s method)", total, len(outliers), method)
        return outliers

    # ------------------------------------------------------------------
    # Type enforcement & imputation
    # ------------------------------------------------------------------

    def fix_data_types(self) -> None:
        """Coerce columns to canonical dtypes.

        * *Date* → ``datetime64`` then back to ``str`` (YYYY-MM-DD)
        * Price columns → ``float64``
        * *Volume* → ``Int64`` (nullable integer)
        """
        if self.DATE_COL in self.df.columns:
            self.df[self.DATE_COL] = pd.to_datetime(self.df[self.DATE_COL], errors="coerce")
            self.df[self.DATE_COL] = self.df[self.DATE_COL].dt.strftime("%Y-%m-%d")

        for col in self.PRICE_COLS:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").astype("float64")

        if self.VOLUME_COL in self.df.columns:
            self.df[self.VOLUME_COL] = pd.to_numeric(self.df[self.VOLUME_COL], errors="coerce")
            # Round first to handle floats like 1000.0, then use nullable int
            self.df[self.VOLUME_COL] = self.df[self.VOLUME_COL].round(0).astype("Int64")

        logger.info("Data types fixed")

    # ------------------------------------------------------------------
    # Fill / impute missing values
    # ------------------------------------------------------------------

    def fill_missing_values(self, strategy: str = "ffill") -> int:
        """Fill missing values using the chosen *strategy*.

        Strategies: ``'ffill'`` (forward fill), ``'bfill'`` (back fill),
        ``'mean'``, ``'median'``, ``'drop'``.

        Returns the number of values filled (or rows dropped).
        """
        before_null = int(self.df.isnull().sum().sum())

        if strategy == "drop":
            self.df.dropna(inplace=True)
            self.df.reset_index(drop=True, inplace=True)
        elif strategy == "ffill":
            self.df = self.df.ffill().bfill()
        elif strategy == "bfill":
            self.df = self.df.bfill().ffill()
        elif strategy == "mean":
            numeric = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric] = self.df[numeric].fillna(self.df[numeric].mean())
        elif strategy == "median":
            numeric = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric] = self.df[numeric].fillna(self.df[numeric].median())
        else:
            raise ValueError(f"Unknown fill strategy '{strategy}'")

        after_null = int(self.df.isnull().sum().sum())
        filled = before_null - after_null
        logger.info("Filled/dropped %d missing values using '%s'", filled, strategy)
        return filled

    # ------------------------------------------------------------------
    # Composite pipeline
    # ------------------------------------------------------------------

    def clean_all(self, fill_strategy: str = "ffill") -> dict:
        """Execute the full cleaning pipeline and return a summary report.

        Steps (in order):
        1. Detect missing values
        2. Remove duplicates
        3. Standardize dates
        4. Fix data types
        5. Fill missing values
        6. Validate prices
        7. Validate volume
        8. Detect outliers (IQR)
        """
        logger.info("=" * 60)
        logger.info("Starting full cleaning pipeline")
        logger.info("=" * 60)

        missing = self.detect_missing_values()
        duplicates_removed = self.remove_duplicates()
        self.standardize_dates()
        self.fix_data_types()
        filled = self.fill_missing_values(strategy=fill_strategy)
        invalid_prices = self.validate_prices()
        invalid_volumes = self.validate_volume()
        outliers = self.detect_outliers(method="iqr")

        self._report = {
            "records_before": self._records_before,
            "records_after": len(self.df),
            "missing_values_found": missing,
            "total_missing_values": sum(missing.values()) if missing else 0,
            "missing_values_filled": filled,
            "duplicates_removed": duplicates_removed,
            "invalid_prices": len(invalid_prices),
            "invalid_price_details": invalid_prices,
            "invalid_volumes": len(invalid_volumes),
            "invalid_volume_details": invalid_volumes,
            "outliers_found": {col: len(idxs) for col, idxs in outliers.items()},
            "total_outliers": sum(len(v) for v in outliers.values()),
        }

        logger.info("Cleaning pipeline complete")
        return self._report

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    def save_cleaned_data(self, path: str | Path | None = None) -> Path:
        """Save the cleaned DataFrame to CSV.

        Parameters
        ----------
        path : str | Path, optional
            Destination file path.  Falls back to *output_path* given at
            construction time, or ``<input_stem>_cleaned.csv``.

        Returns
        -------
        Path
            The path the file was written to.
        """
        if path is None:
            path = self.output_path
        if path is None:
            path = self.input_path.with_name(self.input_path.stem + "_cleaned.csv")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_csv(path, index=False)
        logger.info("Cleaned data saved to %s (%d records)", path, len(self.df))
        return path

    def generate_report(self) -> dict:
        """Return the last cleaning report, or build one on the fly."""
        if self._report:
            return self._report

        missing = self.detect_missing_values()
        invalid_prices = self.validate_prices()
        invalid_volumes = self.validate_volume()
        outliers = self.detect_outliers(method="iqr")

        return {
            "records_before": self._records_before,
            "records_after": len(self.df),
            "missing_values_found": missing,
            "total_missing_values": sum(missing.values()) if missing else 0,
            "duplicates_removed": self._records_before - len(self.df),
            "invalid_prices": len(invalid_prices),
            "invalid_volumes": len(invalid_volumes),
            "outliers_found": {col: len(idxs) for col, idxs in outliers.items()},
            "total_outliers": sum(len(v) for v in outliers.values()),
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"StockDataCleaner(input='{self.input_path}', "
            f"records={len(self.df)}, columns={list(self.df.columns)})"
        )
