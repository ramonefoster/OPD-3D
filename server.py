from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import zmq
from utils.conversions import hms_to_hours, dms_to_degrees
import json

TCSServer = Flask(__name__, template_folder='templates')
CORS(TCSServer, resources={r"/projection/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:8888", "http://localhost:8888", "*"]}})

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://200.131.64.236:50350")

# Subscribe to multiple topics
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

poller = zmq.Poller()
poller.register(subscriber, zmq.POLLIN)

global message
message = {}

@TCSServer.route('/projection/telescope/position', methods=['GET'])
def get_telescope_position():    
    global message
    socks = dict(poller.poll(100))
    if socks.get(subscriber) == zmq.POLLIN:
        message = subscriber.recv_string()
        message = json.loads(message)
        message["hourAngle"] = hms_to_hours(message["hourAngle"])
        message["declination"] = dms_to_degrees(message["declination"].replace(",", ""))
        print(f"TCSPD: {message['hourAngle'], message['declination']}")
    return message

@TCSServer.route('/')
def home():    
    return render_template('index.html')

if __name__ == '__main__':
    TCSServer.run(port=8888, debug=False)