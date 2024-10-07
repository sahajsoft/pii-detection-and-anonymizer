import pytest
import json
from unittest import mock

import hvac
from app import Server


@pytest.fixture()
def app():
    app = Server().app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_analyze_non_existent(client):
    response = client.post(
        "/analyze",
        data={
            "language": "en",
        },
    )

    assert response.status_code == 500


def test_analyze_invalid_csv(client):
    response = client.post(
        "/analyze",
        data={
            "file": open("./tests/sample_data/invalid.csv", "rb"),
        },
    )

    assert response.status_code == 500


def test_analyze_pii_csv(client):
    expected_response_id = {
        "value": ["1", "2", "3"],
        "recognizer_results": [[], [], []],
    }

    response = client.post(
        "/analyze",
        data={
            "file": open("./tests/sample_data/sample_data.csv", "rb"),
            "language": "en",
        },
    )

    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    # No PII in id
    assert data["id"] == expected_response_id
    # first row has no PII
    assert data["comments"]["recognizer_results"][0] == []
    # second row has PII
    assert (
        data["comments"]["recognizer_results"][1][0]["entity_type"]
        == "US_DRIVER_LICENSE"
    )
    assert data["comments"]["recognizer_results"][1][0]["start"] == 34
    assert data["comments"]["recognizer_results"][1][0]["end"] == 42


def test_anonymize_csv_pii(client):
    analyze_response = client.post(
        "/analyze",
        data={
            "file": open("./tests/sample_data/sample_data.csv", "rb"),
            "language": "en",
        },
    )

    assert analyze_response.status_code == 200
    analyzer_results = analyze_response.get_data(as_text=True)

    anonymizer_response = client.post(
        "/anonymize", data={"analyzer_results": analyzer_results}
    )

    assert anonymizer_response.status_code == 200
    anonymizer_data = anonymizer_response.get_data(as_text=True)
    expected_anonymized_data = open(
        "./tests/sample_data/anonymized_data.csv", "r"
    ).read()
    assert anonymizer_data.replace("\r", "") == expected_anonymized_data


def test_vault_anonymize_csv_pii(client):
    analyze_response = client.post(
        "/analyze",
        data={
            "file": open("./tests/sample_data/sample_data.csv", "rb"),
            "language": "en",
        },
    )

    assert analyze_response.status_code == 200
    analyzer_results = analyze_response.get_data(as_text=True)

    with mock.patch.object(hvac, "Client"):
        expected_anonymized_text = "encrypted_text"
        fake_client = mock.MagicMock()
        fake_client.secrets.transit.encrypt_data.return_value = {
            "data": {"ciphertext": expected_anonymized_text}
        }
        hvac.Client.return_value = fake_client

        anonymizer_response = client.post(
            "/anonymize",
            data={
                "vault_config": '{"url": "http://127.0.0.1:8200", "key": "foobar"}',
                "analyzer_results": analyzer_results,
            },
        )

        assert anonymizer_response.status_code == 200
        anonymizer_data = anonymizer_response.get_data(as_text=True)
        expected_anonymized_data = open(
            "./tests/sample_data/vault_encrypted.csv", "r"
        ).read()
        assert anonymizer_data.replace("\r", "") == expected_anonymized_data
