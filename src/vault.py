from text.text import text_analyzer, text_anonymizer
from presidio_anonymizer.entities import OperatorConfig
import base64
import hvac
import sys

VAULT_URL = "http://127.0.0.1:8200"


def base64ify(bytes_or_str):
    """Helper method to perform base64 encoding across Python 2.7 and Python 3.X"""
    if isinstance(bytes_or_str, str):
        input_bytes = bytes_or_str.encode('utf8')
    else:
        input_bytes = bytes_or_str

    output_bytes = base64.urlsafe_b64encode(input_bytes)
    return output_bytes.decode('ascii')


def vault_encrypt(text):
    print(f'plaintext is: {text} and {text.__class__}')
    print(f'b64 plaintext is: {base64.b64encode(text.encode())}')
    client = hvac.Client(url=VAULT_URL)

    encrypt_data_response = client.secrets.transit.encrypt_data(
        name='orders',
        plaintext=base64ify(text.encode()),
    )
    print(f"Response: {encrypt_data_response}")

    ciphertext = encrypt_data_response['data']['ciphertext']
    print(f'Encrypted plaintext ciphertext is: {ciphertext}')
    return ciphertext


vault_encrypt("PII")

# operators = {"DEFAULT": OperatorConfig("custom", {"lambda": vault_encrypt})}
# t = "Hi my name is Qwerty and I live in London. My number is 07440 123456."
# res = text_analyzer(t, "en")
# anon_res = text_anonymizer(t, res, operators)

# print(anon_res)
