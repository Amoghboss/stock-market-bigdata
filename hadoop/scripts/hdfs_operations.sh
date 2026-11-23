#!/usr/bin/env bash
# =============================================================================
# HDFS File System Management Operations
# =============================================================================

function usage() {
    echo "Usage: $0 {init|upload|download|list|delete|status} [args]"
    echo ""
    echo "Commands:"
    echo "  init                    Create standard /stock_market HDFS directories"
    echo "  upload <local> <hdfs>   Upload local file or directory into HDFS"
    echo "  download <hdfs> <local> Download HDFS file to local file system"
    echo "  list [path]             List files in HDFS (defaults to /stock_market)"
    echo "  delete <hdfs_path>      Delete file or directory from HDFS"
    echo "  status                  Display HDFS cluster storage and health report"
    echo ""
    exit 1
}

ACTION=$1
ARG1=$2
ARG2=$3

case "$ACTION" in
    init)
        echo "Creating HDFS directory architecture..."
        hdfs dfs -mkdir -p /stock_market/raw_data
        hdfs dfs -mkdir -p /stock_market/cleaned_data
        hdfs dfs -mkdir -p /stock_market/processed_data
        hdfs dfs -mkdir -p /stock_market/analysis_results
        hdfs dfs -mkdir -p /stock_market/reports
        hdfs dfs -chmod -R 777 /stock_market
        echo "Created directories:"
        hdfs dfs -ls /stock_market
        ;;

    upload)
        if [ -z "$ARG1" ] || [ -z "$ARG2" ]; then
            echo "Error: Local path and HDFS destination path required."
            usage
        fi
        echo "Uploading $ARG1 to HDFS $ARG2..."
        hdfs dfs -put -f "$ARG1" "$ARG2"
        echo "Upload completed."
        ;;

    download)
        if [ -z "$ARG1" ] || [ -z "$ARG2" ]; then
            echo "Error: HDFS source path and local target path required."
            usage
        fi
        echo "Downloading HDFS $ARG1 to local $ARG2..."
        hdfs dfs -get -f "$ARG1" "$ARG2"
        echo "Download completed."
        ;;

    list)
        TARGET=${ARG1:-"/stock_market"}
        echo "Listing HDFS contents at: $TARGET"
        hdfs dfs -ls -R "$TARGET"
        ;;

    delete)
        if [ -z "$ARG1" ]; then
            echo "Error: HDFS target path required."
            usage
        fi
        echo "Deleting HDFS path: $ARG1"
        hdfs dfs -rm -r -skipTrash "$ARG1"
        echo "Deleted."
        ;;

    status)
        echo "=== HDFS Cluster Storage Report ==="
        hdfs dfsadmin -report
        echo ""
        echo "=== HDFS Disk Usage for /stock_market ==="
        hdfs dfs -du -h /stock_market
        ;;

    *)
        usage
        ;;
esac
