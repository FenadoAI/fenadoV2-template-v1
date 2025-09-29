"""FastAPI server endpoint smoke tests."""

import requests

BASE_URL = "http://localhost:8000/api"


def test_root_endpoint():
    response = requests.get(f"{BASE_URL}/")
    response.raise_for_status()
    assert response.json() == {"message": "Hello World"}


def test_chat_endpoint():
    payload = {"message": "What is 2+2?", "agent_type": "chat"}
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    response.raise_for_status()
    data = response.json()
    assert data["success"] is True
    assert "4" in data["response"]


def test_search_endpoint():
    payload = {"query": "capital of Japan", "max_results": 3}
    response = requests.post(f"{BASE_URL}/search", json=payload)
    response.raise_for_status()
    data = response.json()
    assert data["success"] is True
    assert "Tokyo" in data["summary"].lower()


def test_capabilities_endpoint():
    response = requests.get(f"{BASE_URL}/agents/capabilities")
    response.raise_for_status()
    data = response.json()
    assert data["success"] is True
    assert "search_agent" in data["capabilities"]
    assert "chat_agent" in data["capabilities"]
