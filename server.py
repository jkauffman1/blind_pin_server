import time
from hmac import compare_digest
import os
import functools
from .lib import decrypt, encrypt, E_ECDH, ECKeyPair
from wallycore import ec_private_key_verify, ec_sig_from_bytes, sha256, \
    hmac_sha256, EC_FLAG_ECDSA


STATIC_SERVER_PRIVATE_KEY_FILE = 'server_private_key.key'

class PersistentKey(ECKeyPair):

    def __init__(self, filename=STATIC_SERVER_PRIVATE_KEY_FILE):

        try:
            with open(filename, 'r') as f:
                private_key_hex = f.read()
                private_key = bytes.fromhex(private_key_hex)
                ECKeyPair.__init__(private_key)
        except FileNotFoundError:
            app.logger.info(f'Private key file "{filename}" not found, generating new master key')
            ECKeyPair.__init__()
            with open(filename, 'w') as f:
                f.write(self.private_key.hex())

        app.logger.info('Server master public key = {self.public_key.hex()}')

    def sign(self, msg):
        hashed = sha256(msg)
        return ec_sig_from_bytes(self.private_key, hashed, EC_FLAG_ECDSA)

    @functools.lru_cache(maxsize=None)
    def hmac_sha256(self, key):
        return hmac_sha256(self.private_key, key)

static_server_key = None

class PINServerECDH(E_ECDH):

    def __init__(self):
        if static_server_key is None:
            static_server_key = PersistentKey()

        super().__init__()
        self.time_started = int(time.time())

    def get_signed_public_key(self):
        return self.public_key, static_server_key.sign(self.public_key)

    # Decrypt the received payload (ie. aes-key)
    def decrypt_request_payload(self, cke, encrypted, hmac):
        # Verify hmac received
        hmac_calculated = hmac_sha256(self.request_hmac_key, cke + encrypted)
        assert compare_digest(hmac, hmac_calculated)

        # Return decrypted data
        return decrypt(self.request_encryption_key, encrypted)

    def encrypt_response_payload(self, payload):
        encrypted = encrypt(self.response_encryption_key, payload)
        hmac = hmac_sha256(self.response_hmac_key, encrypted)
        return encrypted, hmac

    # Function to deal with wrapper ecdh encryption.
    # Calls passed function with unwrapped payload, and wraps response before
    # returning.  Separates payload handler func from wrapper encryption.
    def call_with_payload(self, cke, encrypted, hmac, func):
        self.generate_shared_secrets(cke)
        payload = self.decrypt_request_payload(cke, encrypted, hmac)

        # Call the passed function with the decrypted payload
        response = func(cke, payload, static_server_key.hmac_sha256(b'pin_data'))

        encrypted, hmac = self.encrypt_response_payload(response)
        return encrypted, hmac
