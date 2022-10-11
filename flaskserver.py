from .flaskbase import app, complete_server_call
from .pindb import PINDb

@app.route('/get_pin', methods=['POST'])
def get_pin_route():
    return complete_server_call(PINDb.get_aes_key)

@app.route('/set_pin', methods=['POST'])
def set_pin_route():
    return complete_server_call(PINDb.set_pin)
