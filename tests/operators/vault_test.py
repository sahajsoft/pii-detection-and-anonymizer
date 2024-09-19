import pytest

from presidio_anonymizer.entities import InvalidParamException
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
