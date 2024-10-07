import pytest
from unittest import mock

from presidio_anonymizer.entities import InvalidParamException
import hvac
from operators.vault import VaultEncrypt, VaultDecrypt


class TestVaultEncrypt:
    def test_given_valid_key_raises_no_exceptions(self):
        VaultEncrypt().validate(
            params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"}
        )

    def test_given_invalid_key_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, key must be a valid encryption key name.",
        ):
            VaultEncrypt().validate(
                params={"vault_url": "http://127.0.0.1:8200", "key": 1}
            )

    def test_given_valid_url_raises_no_exceptions(self):
        VaultEncrypt().validate(
            params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"}
        )

    def test_given_invalid_url_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, vault_url must be a valid URL.",
        ):
            VaultEncrypt().validate(
                params={"vault_url": "http:/127.0.0.1:8200", "key": "foobar"}
            )

    def test_vault_encrypt_and_result_is_returned(self):
        expected_vault_url = "http://127.0.0.1:8200"
        expected_vault_key = "key"
        expected_text = "text"
        expected_anonymized_text = "encrypted_text"
        with mock.patch.object(hvac, "Client"):
            expected_anonymized_text = "encrypted_text"
            fake_client = mock.MagicMock()
            fake_client.secrets.transit.encrypt_data.return_value = {
                "data": {"ciphertext": expected_anonymized_text}
            }
            hvac.Client.return_value = fake_client

            anonymized_text = VaultEncrypt().operate(
                text=expected_text,
                params={"vault_url": expected_vault_url, "key": expected_vault_key},
            )

            assert anonymized_text == expected_anonymized_text
            hvac.Client.assert_called_once_with(url=expected_vault_url)

    def test_vault_token_when_supplied_is_used(self):
        expected_vault_token = "secret-123"
        with mock.patch.object(hvac, "Client"):
            fake_client = mock.MagicMock()
            hvac.Client.return_value = fake_client

            VaultEncrypt().operate(
                text="", params={"vault_token": expected_vault_token}
            )

            assert fake_client.token == expected_vault_token


class TestVaultDecrypt:
    def test_given_valid_key_raises_no_exceptions(self):
        VaultDecrypt().validate(
            params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"}
        )

    def test_given_invalid_key_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, key must be a valid encryption key name.",
        ):
            VaultDecrypt().validate(
                params={"vault_url": "http://127.0.0.1:8200", "key": 1}
            )

    def test_given_valid_url_raises_no_exceptions(self):
        VaultDecrypt().validate(
            params={"vault_url": "http://127.0.0.1:8200", "key": "foobar"}
        )

    def test_given_invalid_url_raises_exceptions(self):
        with pytest.raises(
            InvalidParamException,
            match="Invalid input, vault_url must be a valid URL.",
        ):
            VaultDecrypt().validate(
                params={"vault_url": "http:/127.0.0.1:8200", "key": "foobar"}
            )

    def test_vault_decrypt_and_result_is_returned(self):
        expected_vault_url = "http://127.0.0.1:8200"
        expected_vault_key = "key"
        expected_deanonymized_text = "text"
        with mock.patch.object(hvac, "Client"):
            import base64

            fake_client = mock.MagicMock()
            fake_client.secrets.transit.decrypt_data.return_value = {
                "data": {
                    "plaintext": base64.urlsafe_b64encode(
                        expected_deanonymized_text.encode("utf8")
                    )
                }
            }
            hvac.Client.return_value = fake_client

            deanonymized_text = VaultDecrypt().operate(
                text="encrypted_text",
                params={"vault_url": expected_vault_url, "key": expected_vault_key},
            )

            assert deanonymized_text == expected_deanonymized_text
            hvac.Client.assert_called_once_with(url=expected_vault_url)

    def test_vault_token_when_supplied_is_used(self):
        expected_vault_token = "secret-123"
        expected_deanonymized_text = "text"
        with mock.patch.object(hvac, "Client"):
            import base64

            fake_client = mock.MagicMock()
            fake_client.secrets.transit.decrypt_data.return_value = {
                "data": {
                    "plaintext": base64.urlsafe_b64encode(
                        expected_deanonymized_text.encode("utf8")
                    )
                }
            }
            hvac.Client.return_value = fake_client

            VaultDecrypt().operate(
                text="encrypted_text", params={"vault_token": expected_vault_token}
            )

            assert fake_client.token == expected_vault_token
