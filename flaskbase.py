import time
import json
import os
from flask import Flask, request, jsonify
from . import server
from wallycore import hex_from_bytes, hex_to_bytes, AES_KEY_LEN_256, \
    AES_BLOCK_LEN

import logging
logging.basicConfig(level=logging.DEBUG)

b2h = hex_from_bytes
h2b = hex_to_bytes

# Time we will retain active sessions, in seconds.
# ie. maximum time allowed 'start_handshake' (which creates the session)
# and the get-/set-pin call, which utilises it.
SESSION_LIFETIME = 30

app = Flask(__name__)

sessions = {}

@app.route('/', methods=['GET'])
def alive():
    return ""

@app.route('/start_handshake', methods=['POST'])
def start_handshake_route():
    app.logger.debug('Number of sessions {}'.format(len(sessions)))

    # Create a new ephemeral server/session and get its signed pubkey
    e_ecdh_server = server.PINServerECDH()
    pubkey, sig = e_ecdh_server.get_signed_public_key()
    ske = b2h(pubkey)

    # Cache new session
    cleanup_expired_sessions()
    sessions[ske] = e_ecdh_server

    # Return response
    return jsonify({'ske': ske,
                    'sig': b2h(sig),
                    'pubkey': server.static_server_key.public_key.hex()})

def cleanup_expired_sessions():
    global sessions
    time_now = int(time.time())
    sessions = dict(filter(
        lambda s: time_now - s[1].time_started < SESSION_LIFETIME,
        sessions.items()))

def complete_server_call(pin_func):
    try:
        # Get request data
        udata = json.loads(request.data)
        ske = udata['ske']

        # Get associated session (ensuring not stale)
        cleanup_expired_sessions()
        e_ecdh_server = sessions[ske]

        # get/set pin and get response data
        encrypted_key, hmac = e_ecdh_server.call_with_payload(
                h2b(udata['cke']),
                h2b(udata['encrypted_data']),
                h2b(udata['hmac_encrypted_data']),
                pin_func)

        # Expecting to return an encrypted aes-key
        assert len(encrypted_key) == AES_KEY_LEN_256 + (2*AES_BLOCK_LEN)

        # Cleanup session
        del sessions[ske]
        cleanup_expired_sessions()

        # Return response
        return jsonify({'encrypted_key': b2h(encrypted_key),
                        'hmac': b2h(hmac)})

    except Exception as e:
        app.logger.error("Error: {} {}".format(type(e), e))
        app.logger.error("Request body: {}".format(request.data))
        raise e
