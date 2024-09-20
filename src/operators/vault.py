import base64
from typing import Dict
from urllib.parse import urlparse

import hvac
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Operator, OperatorType


class VaultEncrypt(Operator):
    def _base64ify(self, bytes_or_str):
        if isinstance(bytes_or_str, str):
            input_bytes = bytes_or_str.encode('utf8')
        else:
            input_bytes = bytes_or_str

        output_bytes = base64.urlsafe_b64encode(input_bytes)
        return output_bytes.decode('ascii')

    def operate(self, text: str, params: Dict = None) -> str:
        vault_url = params.get("vault_url")
        key = params.get("key")

        client = hvac.Client(url=vault_url)
        if params.get("vault_token"):
            client.token = params.get("vault_token")
        encrypt_data_response = client.secrets.transit.encrypt_data(
            name=key,
            plaintext=self._base64ify(text),
        )
        ciphertext = encrypt_data_response['data']['ciphertext']

        return ciphertext

    def validate(self, params: Dict = None) -> None:
        vault_url = params.get("vault_url")
        if isinstance(vault_url, str):
            result = urlparse(vault_url)
            if result.scheme and result.netloc:
                pass
            else:
                raise InvalidParamException(f"Invalid input, vault_url must be a valid URL.")
        else:
            raise InvalidParamException(f"Invalid input, vault_url must be a string.")

        key = params.get("key")
        if isinstance(key, str) and key:
            pass
        else:
            raise InvalidParamException(f"Invalid input, key must be a valid encryption key name.")

    def operator_name(self) -> str:
        return "vault_encrypt"

    def operator_type(self) -> OperatorType:
        return OperatorType.Anonymize



class VaultDecrypt(Operator):
    def operate(self, text: str, params: Dict = None) -> str:
        vault_url = params.get("vault_url")
        key = params.get("key")

        client = hvac.Client(url=vault_url)
        if params.get("vault_token"):
            client.token = params.get("vault_token")
        decrypt_data_response = client.secrets.transit.decrypt_data(
            name=key,
            ciphertext=text,
        )
        encodedtext = decrypt_data_response['data']['plaintext']
        plaintext = base64.b64decode(encodedtext).decode('utf8')

        return plaintext

    def validate(self, params: Dict = None) -> None:
        vault_url = params.get("vault_url")
        if isinstance(vault_url, str):
            result = urlparse(vault_url)
            if result.scheme and result.netloc:
                pass
            else:
                raise InvalidParamException(f"Invalid input, vault_url must be a valid URL.")
        else:
            raise InvalidParamException(f"Invalid input, vault_url must be a string.")

        key = params.get("key")
        if isinstance(key, str) and key:
            pass
        else:
            raise InvalidParamException(f"Invalid input, key must be a valid encryption key name.")

    def operator_name(self) -> str:
        return "vault_decrypt"

    def operator_type(self) -> OperatorType:
        return OperatorType.Deanonymize
