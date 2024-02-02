from flask import Flask, request, jsonify
from flask_cors import CORS
import zmq

TCSServer = Flask(__name__)

CORS(TCSServer, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://200.131.64.236:50350")

# Subscribe to multiple topics
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

poller = zmq.Poller()
poller.register(subscriber, zmq.POLLIN)

@TCSServer.route('/projection/telescope/position', methods=['GET'])
def get_telescope_position():
    message = {}
    socks = dict(poller.poll(50))
    if socks.get(subscriber) == zmq.POLLIN:        
        message = subscriber.recv_string()
        print(f"TCSPD: {message}")
    return message

if __name__ == '__main__':
    TCSServer.run(port=5000)

