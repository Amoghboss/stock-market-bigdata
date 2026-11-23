"""
Configuration for Stock Market Big Data Analytics Dashboard.
"""
import os

# Project root is one level up from backend/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """Base configuration."""

    # --- Flask ---
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY = os.environ.get("SECRET_KEY", "stock-market-bigdata-secret-key-change-in-prod")

    # --- Database ---
    IS_VERCEL = os.environ.get("VERCEL") == "1"
    DATABASE_DIR = "/tmp" if IS_VERCEL else os.path.join(PROJECT_ROOT, "data")
    DATABASE_PATH = os.path.join(DATABASE_DIR, "analytics.db")

    # --- Data directories ---
    RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "datasets", "raw")
    CLEANED_DATA_DIR = os.path.join(PROJECT_ROOT, "datasets", "cleaned")
    PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "datasets", "cleaned")
    REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
    MAPREDUCE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "mapreduce_outputs")
    EXPORTS_DIR = "/tmp/exports" if IS_VERCEL else os.path.join(PROJECT_ROOT, "reports", "exports")

    # --- HDFS (optional – used when a real Hadoop cluster is available) ---
    HDFS_NAMENODE = os.environ.get("HDFS_NAMENODE", "http://localhost:9870")
    HDFS_USER = os.environ.get("HDFS_USER", "hadoop")
    HDFS_DATA_PATH = os.environ.get("HDFS_DATA_PATH", "/user/hadoop/stock_data")
    HDFS_OUTPUT_PATH = os.environ.get("HDFS_OUTPUT_PATH", "/user/hadoop/stock_output")

    # --- MapReduce ---
    MAPREDUCE_JAR = os.environ.get(
        "MAPREDUCE_JAR",
        os.path.join(PROJECT_ROOT, "mapreduce", "stock_analytics.jar"),
    )

    # --- Supported CSV columns ---
    CSV_DATE_COL = "Date"
    CSV_OPEN_COL = "Open"
    CSV_HIGH_COL = "High"
    CSV_LOW_COL = "Low"
    CSV_CLOSE_COL = "Close"
    CSV_ADJ_CLOSE_COL = "Adj Close"
    CSV_VOLUME_COL = "Volume"

    @classmethod
    def ensure_dirs(cls):
        """Create all required directories if they don't exist."""
        for d in (
            cls.DATABASE_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.REPORTS_DIR,
            cls.MAPREDUCE_OUTPUT_DIR,
            cls.EXPORTS_DIR,
        ):
            os.makedirs(d, exist_ok=True)
