import pytest
import json

from app import Server

@pytest.fixture()
def app():
    app = Server().app
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_analyze_csv_file(client):
    expected_response_id = {'value': ['1', '2', '3'], 'recognizer_results': [[], [], []]}

    response = client.post("/analyze", data={
        "file": open('./tests/analyzer_engine/sample_data.csv', 'rb'),
    })

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    # No PII in id
    assert data['id'] == expected_response_id
    # first row has no PII
    assert data['comments']['recognizer_results'][0] == []
    # second row has PII
    assert data['comments']['recognizer_results'][1][0]['entity_type'] == 'US_DRIVER_LICENSE'
    assert data['comments']['recognizer_results'][1][0]['start'] == 34
    assert data['comments']['recognizer_results'][1][0]['end'] == 42
