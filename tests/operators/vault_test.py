import pytest
from unittest import mock

from presidio_anonymizer.entities import InvalidParamException
import hvac
from operators.vault import VaultEncrypt, VaultDecrypt


class TestVaultEncrypt:
    def test_given_valid_key_raises_no_exceptions(self):
        VaultEncrypt().validate(params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"})

    def test_given_invalid_key_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, key must be a valid encryption key name.",
        ):
            VaultEncrypt().validate(params={"vault_url": "http://127.0.0.1:8200", "key": 1})

    def test_given_valid_url_raises_no_exceptions(self):
        VaultEncrypt().validate(params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"})

    def test_given_invalid_url_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, vault_url must be a valid URL.",
        ):
            VaultEncrypt().validate(params={"vault_url": "http:/127.0.0.1:8200", "key": "foobar"})

    def test_vault_encrypt_and_result_is_returned(self):
        with mock.patch.object(hvac, "Client"):
            expected_anonymized_text = "encrypted_text"
            fake_client = mock.MagicMock()
            fake_client.secrets.transit.encrypt_data.return_value = {"data": {"ciphertext": expected_anonymized_text}}
            hvac.Client.return_value = fake_client

            anonymized_text = VaultEncrypt().operate(text="text", params={"key": "key"})

            assert anonymized_text == expected_anonymized_text


class TestVaultDecrypt:
    def test_given_valid_key_raises_no_exceptions(self):
        VaultDecrypt().validate(params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"})

    def test_given_invalid_key_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, key must be a valid encryption key name.",
        ):
            VaultDecrypt().validate(params={"vault_url": "http://127.0.0.1:8200", "key": 1})

    def test_given_valid_url_raises_no_exceptions(self):
        VaultDecrypt().validate(params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"})

    def test_given_invalid_url_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, vault_url must be a valid URL.",
        ):
            VaultDecrypt().validate(params={"vault_url": "http:/127.0.0.1:8200", "key": "foobar"})

    def test_vault_decrypt_and_result_is_returned(self):
        with mock.patch.object(hvac, "Client"):
            import base64
            expected_deanonymized_text = "text"
            fake_client = mock.MagicMock()
            fake_client.secrets.transit.decrypt_data.return_value = {"data": {"plaintext": base64.urlsafe_b64encode(expected_deanonymized_text.encode('utf8'))}}
            hvac.Client.return_value = fake_client

            deanonymized_text = VaultDecrypt().operate(text="text", params={"key": "key"})

            assert deanonymized_text == expected_deanonymized_text
