#!/usr/bin/env bash
# =============================================================================
# Cleanly Shutdown All Hadoop Services
# =============================================================================

echo "Stopping Hadoop YARN daemons..."
stop-yarn.sh || true

echo "Stopping Hadoop HDFS daemons..."
stop-dfs.sh || true

echo "Checking remaining Java processes..."
jps

echo "Hadoop daemons stopped successfully."
