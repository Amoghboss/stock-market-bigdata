"""
Automated Integration Tests: Flask REST API Endpoints
"""

import pytest
import json
from pathlib import Path
from backend.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_api_overview(client):
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "total_stocks" in data["data"]

def test_api_stocks(client):
    res = client.get("/api/stocks")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0

def test_api_stock_data(client):
    res = client.get("/api/stock/RELIANCE")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["symbol"] == "RELIANCE"

def test_api_compare(client):
    res = client.get("/api/compare?symbols=RELIANCE,TCS")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "RELIANCE" in data["symbols"]

def test_api_performers(client):
    res = client.get("/api/performers")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["top_performers"]) > 0

def test_api_mapreduce_status(client):
    res = client.get("/api/mapreduce/status")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["jobs"]) == 7

def test_api_hdfs_info(client):
    res = client.get("/api/hdfs/info")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
