"""
Automated Unit Tests: HDFS Manager & Distributed File System Bridge
Gracefully skips cluster-dependent tests if Hadoop daemon is offline.
"""

import pytest
import os
import shutil
from hadoop.scripts.hdfs_manager import HdfsManager

def test_hdfs_manager_initialization():
    mgr = HdfsManager()
    assert hasattr(mgr, "is_hdfs_available")
    assert hasattr(mgr, "get_storage_info")

def test_hdfs_storage_info():
    mgr = HdfsManager()
    info = mgr.get_storage_info()
    assert "connected" in info
    assert "mode" in info

@pytest.mark.skipif(not HdfsManager().is_hdfs_available(), reason="Requires live active Hadoop HDFS cluster")
def test_hdfs_live_directory_listing():
    mgr = HdfsManager()
    dirs = mgr.list_directory("/stock_market")
    assert isinstance(dirs, list)
