#!/usr/bin/env python3
"""
Automated Financial & Big Data Analytical Report Generator
Produces structured CSV analytical summaries and multi-page professional PDF reports.
"""

import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Path resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analytics.stock_analyzer import StockAnalyzer

class ReportGenerator:
    """Generates analytical reports in CSV and PDF formats."""

    def __init__(self, analyzer: StockAnalyzer):
        self.analyzer = analyzer

    def generate_csv_report(self, output_path=None):
        """Generate comprehensive CSV summary report for all equities."""
        if output_path is None:
            output_path = PROJECT_ROOT / "reports" / "stock_market_analytics_report.csv"
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        symbols = [s["Symbol"] for s in self.analyzer.get_symbols()]
        rows = [self.analyzer.get_stock_summary(sym) for sym in symbols]

        df_rep = pd.DataFrame(rows)
        df_rep.to_csv(output_path, index=False)
        return str(output_path)

    def generate_pdf_report(self, output_path=None):
        """Generate professional multi-page PDF analytical report."""
        if output_path is None:
            output_path = PROJECT_ROOT / "reports" / "stock_market_analytics_report.pdf"
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            from fpdf import FPDF
        except ImportError:
            raise ImportError("fpdf2 is required for PDF generation. Run 'pip install fpdf2'.")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Document Header
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(24, 43, 73)
        pdf.cell(0, 10, "Stock Market Big Data & Trend Analysis Report", ln=True, align="C")

        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 110, 125)
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Hadoop HDFS & MapReduce Engine", ln=True, align="C")
        pdf.ln(6)

        # Overview Section
        stats = self.analyzer.get_overall_statistics()
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "1. Executive Portfolio Summary", ln=True)
        pdf.set_draw_color(203, 213, 225)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        summary_lines = [
            f"Total Equities Analyzed: {stats['total_stocks']}",
            f"Historical Trading Records Processed: {stats['total_records']:,}",
            f"Observation Window: {stats['date_range']}",
            f"Average Market Valuation: Rs. {stats['average_market_price']:.2f}",
            f"Total Cumulative Volume: {stats['total_market_volume']:,} shares",
            f"Top Performing Equity: {stats['highest_performer']['symbol']} ({stats['highest_performer']['return']})",
            f"Lowest Performing Equity: {stats['lowest_performer']['symbol']} ({stats['lowest_performer']['return']})",
            f"Hadoop Processing Status: {stats['last_processing_status']}"
        ]
        for line in summary_lines:
            pdf.cell(0, 6, f"  * {line}", ln=True)
        pdf.ln(6)

        # Performance Table
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "2. Equity Performance & Volatility Analysis", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        # Table Header
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(28, 8, "Symbol", border=1, fill=True)
        pdf.cell(24, 8, "Initial", border=1, fill=True, align="R")
        pdf.cell(24, 8, "Latest", border=1, fill=True, align="R")
        pdf.cell(24, 8, "High", border=1, fill=True, align="R")
        pdf.cell(24, 8, "Low", border=1, fill=True, align="R")
        pdf.cell(28, 8, "Return (%)", border=1, fill=True, align="R")
        pdf.cell(38, 8, "Ann. Volatility", border=1, fill=True, align="R")
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        symbols = [s["Symbol"] for s in self.analyzer.get_symbols()]
        for sym in symbols:
            s = self.analyzer.get_stock_summary(sym)
            ret_val = s.get("percentage_return", 0)
            ret_str = f"{ret_val:+.2f}%"

            pdf.cell(28, 7, str(s["symbol"]), border=1)
            pdf.cell(24, 7, f"{s['initial_price']:.1f}", border=1, align="R")
            pdf.cell(24, 7, f"{s['latest_close']:.1f}", border=1, align="R")
            pdf.cell(24, 7, f"{s['highest_price']:.1f}", border=1, align="R")
            pdf.cell(24, 7, f"{s['lowest_price']:.1f}", border=1, align="R")

            # Color return
            if ret_val >= 0:
                pdf.set_text_color(22, 101, 52)
            else:
                pdf.set_text_color(185, 28, 28)
            pdf.cell(28, 7, ret_str, border=1, align="R")
            pdf.set_text_color(15, 23, 42)

            pdf.cell(38, 7, f"{s['annualized_volatility']:.2f}%", border=1, align="R")
            pdf.ln()

        pdf.ln(6)

        # Technical Indicators & Methodology Notice
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "3. Big Data Processing & Analytical Methodology", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(71, 85, 105)
        method_text = (
            "This report is generated by executing 7 MapReduce jobs across historical stock market data "
            "stored in Apache Hadoop HDFS. Technical indicators including Simple Moving Averages (SMA-20, SMA-50), "
            "Exponential Moving Averages (EMA-20), Relative Strength Index (RSI-14, Wilder's smoothing), Moving Average "
            "Convergence Divergence (MACD 12/26/9), and 20-day Bollinger Bands are computed strictly for trend "
            "characterization and research. Notice: Technical indicators reflect historical price relationships and do not "
            "constitute investment advice or guarantee future performance."
        )
        pdf.multi_cell(0, 5, method_text)

        pdf.output(str(output_path))
        return str(output_path)

    def generate_stock_comparison(self, symbols, output_path=None):
        """Export tabular comparison of selected equities to CSV."""
        if output_path is None:
            output_path = PROJECT_ROOT / "reports" / "stock_comparison.csv"
        else:
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        rows = [self.analyzer.get_stock_summary(s) for s in symbols]
        df_comp = pd.DataFrame(rows)
        df_comp.to_csv(output_path, index=False)
        return str(output_path)

if __name__ == "__main__":
    cleaned_file = PROJECT_ROOT / "datasets" / "cleaned" / "cleaned_stock_data.csv"
    if not cleaned_file.exists():
        cleaned_file = PROJECT_ROOT / "datasets" / "raw" / "nse_stock_data.csv"
    analyzer = StockAnalyzer(cleaned_file)
    gen = ReportGenerator(analyzer)
    print("CSV Report:", gen.generate_csv_report())
    print("PDF Report:", gen.generate_pdf_report())
