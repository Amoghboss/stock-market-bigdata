#!/usr/bin/env bash
# =============================================================================
# Run All 7 Hadoop MapReduce Jobs on Cluster via Hadoop Streaming
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MAPREDUCE_DIR="${PROJECT_ROOT}/mapreduce"

# Locate Hadoop Streaming JAR
STREAMING_JAR=$(find "$HADOOP_HOME" -name "hadoop-streaming-*.jar" 2>/dev/null | head -n 1)

if [ -z "$STREAMING_JAR" ]; then
    echo "ERROR: hadoop-streaming jar not found under \$HADOOP_HOME ($HADOOP_HOME)"
    echo "Ensure Hadoop is properly installed and HADOOP_HOME is set."
    exit 1
fi

echo "Using Hadoop Streaming JAR: $STREAMING_JAR"

INPUT_HDFS="/stock_market/cleaned_data/cleaned_stock_data.csv"
OUTPUT_BASE_HDFS="/stock_market/processed_data"

# Ensure input file exists on HDFS
echo "Checking HDFS input dataset..."
if ! hdfs dfs -test -e "$INPUT_HDFS"; then
    echo "Input dataset not found at $INPUT_HDFS. Uploading now..."
    hdfs dfs -put -f "${PROJECT_ROOT}/datasets/cleaned/cleaned_stock_data.csv" "$INPUT_HDFS"
fi

# Array of jobs: (job_folder, job_name)
JOBS=(
    "average_price:Average Stock Price Analysis"
    "max_min_price:Maximum and Minimum Price Analysis"
    "trading_volume:Trading Volume Analysis"
    "daily_movement:Daily Stock Movement Analysis"
    "monthly_trends:Monthly Trend Analysis"
    "stock_ranking:Stock Performance Ranking"
    "volatility:Stock Volatility Analysis"
)

echo "================================================================="
echo " STARTING DISTRIBUTED MAPREDUCE ANALYTICS SUITE (7 JOBS)"
echo "================================================================="

for ITEM in "${JOBS[@]}"; do
    JOB_FOLDER="${ITEM%%:*}"
    JOB_NAME="${ITEM##*:}"

    JOB_DIR="${MAPREDUCE_DIR}/${JOB_FOLDER}"
    MAPPER="${JOB_DIR}/mapper.py"
    REDUCER="${JOB_DIR}/reducer.py"
    OUTPUT_HDFS="${OUTPUT_BASE_HDFS}/${JOB_FOLDER}"

    echo ""
    echo ">>> Running Job: ${JOB_NAME} (${JOB_FOLDER}) <<<"
    echo "Mapper:  $MAPPER"
    echo "Reducer: $REDUCER"
    echo "Output:  $OUTPUT_HDFS"

    # Remove existing output directory in HDFS
    hdfs dfs -rm -r -skipTrash "$OUTPUT_HDFS" 2>/dev/null || true

    START_TIME=$(date +%s)

    hadoop jar "$STREAMING_JAR" \
        -D mapreduce.job.name="StockAnalytics_${JOB_FOLDER}" \
        -D mapreduce.job.reduces=1 \
        -input "$INPUT_HDFS" \
        -output "$OUTPUT_HDFS" \
        -mapper "python3 mapper.py" \
        -reducer "python3 reducer.py" \
        -file "$MAPPER" \
        -file "$REDUCER"

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ">>> Job '${JOB_NAME}' completed in ${DURATION} seconds."

    # Download output to local reports folder
    LOCAL_OUT="${PROJECT_ROOT}/reports/mapreduce_outputs/${JOB_FOLDER}_output.txt"
    mkdir -p "$(dirname "$LOCAL_OUT")"
    hdfs dfs -cat "${OUTPUT_HDFS}/part-*" > "$LOCAL_OUT"
    echo "Results synced locally to: $LOCAL_OUT"
done

echo ""
echo "================================================================="
echo " ALL 7 HADOOP MAPREDUCE JOBS COMPLETED SUCCESSFULLY!"
echo "================================================================="
