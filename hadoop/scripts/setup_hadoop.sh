#!/usr/bin/env bash
# =============================================================================
# Setup Apache Hadoop 3.3.6 on Ubuntu / WSL2 (Pseudo-Distributed Mode)
# =============================================================================
set -e

echo "================================================================="
echo " HADOOP HDFS & YARN PSEUDO-DISTRIBUTED CLUSTER INSTALLER"
echo "================================================================="

# 1. Update packages and install Java OpenJDK 11
echo "[1/7] Updating apt repository and installing OpenJDK 11..."
sudo apt-get update -y
sudo apt-get install -y openjdk-11-jdk ssh pdsh rsync wget curl

# 2. Configure SSH localhost access (passwordless for Hadoop daemons)
echo "[2/7] Configuring passwordless SSH for localhost..."
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
fi
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys
ssh -o StrictHostKeyChecking=no localhost whoami || true

# 3. Download and extract Hadoop 3.3.6
HADOOP_VERSION="3.3.6"
INSTALL_DIR="/usr/local/hadoop"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "[3/7] Downloading Apache Hadoop ${HADOOP_VERSION}..."
    wget -q --show-progress "https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" \
      || wget -q --show-progress "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"

    echo "Extracting Hadoop to ${INSTALL_DIR}..."
    sudo tar -xzf "hadoop-${HADOOP_VERSION}.tar.gz" -C /usr/local/
    sudo mv "/usr/local/hadoop-${HADOOP_VERSION}" "$INSTALL_DIR"
    sudo chown -R "$USER:$USER" "$INSTALL_DIR"
    rm -f "hadoop-${HADOOP_VERSION}.tar.gz"
else
    echo "[3/7] Hadoop already installed at ${INSTALL_DIR}."
fi

# 4. Set Environment Variables
echo "[4/7] Setting environment variables in ~/.bashrc..."
JAVA_PATH=$(dirname $(dirname $(readlink -f $(which javac))))

grep -q "HADOOP_HOME" ~/.bashrc || cat << EOF >> ~/.bashrc

# --- Hadoop Environment Variables ---
export JAVA_HOME=${JAVA_PATH}
export HADOOP_HOME=${INSTALL_DIR}
export HADOOP_INSTALL=\${HADOOP_HOME}
export HADOOP_MAPRED_HOME=\${HADOOP_HOME}
export HADOOP_COMMON_HOME=\${HADOOP_HOME}
export HADOOP_HDFS_HOME=\${HADOOP_HOME}
export YARN_HOME=\${HADOOP_HOME}
export HADOOP_COMMON_LIB_NATIVE_DIR=\${HADOOP_HOME}/lib/native
export PATH=\${PATH}:\${HADOOP_HOME}/bin:\${HADOOP_HOME}/sbin
EOF

export JAVA_HOME=${JAVA_PATH}
export HADOOP_HOME=${INSTALL_DIR}
export PATH=${PATH}:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin

# Set JAVA_HOME in hadoop-env.sh
sed -i "s|# export JAVA_HOME=.*|export JAVA_HOME=${JAVA_PATH}|" "${HADOOP_HOME}/etc/hadoop/hadoop-env.sh"

# 5. Copy configuration files
echo "[5/7] Deploying custom Hadoop configuration files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/configuration"

cp -v "${CONFIG_DIR}/core-site.xml" "${HADOOP_HOME}/etc/hadoop/core-site.xml"
cp -v "${CONFIG_DIR}/hdfs-site.xml" "${HADOOP_HOME}/etc/hadoop/hdfs-site.xml"
cp -v "${CONFIG_DIR}/mapred-site.xml" "${HADOOP_HOME}/etc/hadoop/mapred-site.xml"
cp -v "${CONFIG_DIR}/yarn-site.xml" "${HADOOP_HOME}/etc/hadoop/yarn-site.xml"

# Create NameNode and DataNode directories
mkdir -p "${HOME}/hadoop_data/hdfs/namenode"
mkdir -p "${HOME}/hadoop_data/hdfs/datanode"

# 6. Format NameNode (only if not already formatted)
echo "[6/7] Formatting HDFS NameNode..."
if [ ! -d "${HOME}/hadoop_data/hdfs/namenode/current" ]; then
    hdfs namenode -format -force
fi

# 7. Start HDFS and YARN daemons
echo "[7/7] Starting HDFS & YARN services..."
start-dfs.sh
start-yarn.sh

echo "Waiting for NameNode to leave safe mode..."
hdfs dfsadmin -safemode wait || true

# Initialize Stock Market HDFS Directory Hierarchy
echo "Creating HDFS directory architecture for Stock Market Analytics..."
hdfs dfs -mkdir -p /stock_market/raw_data
hdfs dfs -mkdir -p /stock_market/cleaned_data
hdfs dfs -mkdir -p /stock_market/processed_data
hdfs dfs -mkdir -p /stock_market/analysis_results
hdfs dfs -mkdir -p /stock_market/reports
hdfs dfs -chmod -R 777 /stock_market

echo ""
echo "================================================================="
echo " HADOOP SETUP COMPLETED SUCCESSFULLY!"
echo "================================================================="
echo " NameNode Web UI: http://localhost:9870"
echo " YARN ResourceManager UI: http://localhost:8088"
echo " HDFS Directory Hierarchy:"
hdfs dfs -ls /stock_market
echo "================================================================="
