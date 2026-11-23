#!/usr/bin/env python3
"""
HDFS Manager Module
Provides an interface for executing HDFS commands from Python.
Supports direct Linux hadoop execution as well as WSL2 invocation from Windows.
"""

import os
import sys
import subprocess
import shutil
import logging

logger = logging.getLogger(__name__)

class HdfsManager:
    """Manages HDFS operations via Hadoop CLI commands."""

    def __init__(self, wsl_mode=None):
        # Auto-detect if running on Windows and should delegate to WSL
        if wsl_mode is None:
            self.wsl_mode = (os.name == "nt" and shutil.which("wsl") is not None)
        else:
            self.wsl_mode = wsl_mode

        self.hadoop_cmd = "hadoop"
        self.hdfs_cmd = "hdfs"

    def _exec(self, cmd_args):
        """Execute a CLI command either directly or through WSL."""
        if self.wsl_mode:
            full_cmd = ["wsl"] + cmd_args
        else:
            full_cmd = cmd_args

        try:
            res = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return res.returncode == 0, res.stdout, res.stderr
        except Exception as e:
            logger.error("Command execution failed: %s (%s)", cmd_args, e)
            return False, "", str(e)

    def is_hdfs_available(self):
        """Check if HDFS service is reachable."""
        success, out, _ = self._exec([self.hdfs_cmd, "dfsadmin", "-safemode", "get"])
        return success

    def create_directory(self, hdfs_path):
        """Create directory structure in HDFS."""
        success, out, err = self._exec([self.hdfs_cmd, "dfs", "-mkdir", "-p", hdfs_path])
        return success

    def upload_file(self, local_path, hdfs_path):
        """Upload a local file into HDFS."""
        # Convert Windows path to WSL path if needed
        target_local = local_path
        if self.wsl_mode and ":" in str(local_path):
            drive, rest = str(local_path).split(":", 1)
            target_local = f"/mnt/{drive.lower()}" + rest.replace("\\", "/")

        success, out, err = self._exec([self.hdfs_cmd, "dfs", "-put", "-f", target_local, hdfs_path])
        return success, err

    def download_file(self, hdfs_path, local_path):
        """Download a file from HDFS to local file system."""
        target_local = local_path
        if self.wsl_mode and ":" in str(local_path):
            drive, rest = str(local_path).split(":", 1)
            target_local = f"/mnt/{drive.lower()}" + rest.replace("\\", "/")

        success, out, err = self._exec([self.hdfs_cmd, "dfs", "-get", "-f", hdfs_path, target_local])
        return success, err

    def list_directory(self, hdfs_path="/stock_market"):
        """List files and folders in HDFS."""
        success, out, err = self._exec([self.hdfs_cmd, "dfs", "-ls", hdfs_path])
        if not success:
            return []
        items = []
        for line in out.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 8:
                items.append({
                    "permissions": parts[0],
                    "replication": parts[1],
                    "owner": parts[2],
                    "group": parts[3],
                    "size": parts[4],
                    "date": parts[5] + " " + parts[6],
                    "path": parts[7]
                })
        return items

    def delete_file(self, hdfs_path):
        """Delete file or directory from HDFS."""
        success, out, err = self._exec([self.hdfs_cmd, "dfs", "-rm", "-r", "-skipTrash", hdfs_path])
        return success

    def file_exists(self, hdfs_path):
        """Check if file exists on HDFS."""
        success, _, _ = self._exec([self.hdfs_cmd, "dfs", "-test", "-e", hdfs_path])
        return success

    def get_storage_info(self):
        """Retrieve HDFS cluster storage report."""
        available = self.is_hdfs_available()
        if not available:
            return {
                "connected": False,
                "mode": "Demonstration / Local Fallback",
                "cluster_status": "Offline / Not Configured",
                "total_capacity": "N/A",
                "used_capacity": "N/A",
                "remaining_capacity": "N/A",
                "active_nodes": 0
            }

        success, out, _ = self._exec([self.hdfs_cmd, "dfsadmin", "-report"])
        return {
            "connected": True,
            "mode": "Live Hadoop Cluster",
            "cluster_status": "Healthy / In Service",
            "raw_report": out[:500] if success else "Error querying cluster"
        }

if __name__ == "__main__":
    mgr = HdfsManager()
    print("HDFS Available:", mgr.is_hdfs_available())
    print("Storage Info:", mgr.get_storage_info())
