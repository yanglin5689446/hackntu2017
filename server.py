
#!/usr/local/bin/python3

from flask import Flask, send_from_directory
from flask_restful import Api, Resource
from flask import request
from flask.json import jsonify
from flask_cache import Cache
from flask import Flask, session
from flask_session import Session
from flask_cors import CORS, cross_origin
import info
import aquatic_predict
import poultry_predict
import pig_predict


app = Flask(__name__)

@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp

@app.route('/')
def index():
    return "Happy hacking!"

@app.route('/plot/<path:path>')
def send_js(path):
    return send_from_directory('plot', path)
@app.route('/api/pig/info', methods = ['get'])
def pig_info():
    return jsonify(info.pig_info)

@app.route('/api/pig', methods = ['POST'])
def predict_pig():
    request_json = request.get_json()
    try:
        market = request_json['market']
        type_name = request_json['type_name']
        period = int(request_json['period'])
        predict_days = int(request_json['predict_days'])
    except:
        return jsonify({"Error": "data not provided."})
    result = pig_predict.predict(market_name=market, target_level=type_name, start=period, predict_days=predict_days)
    return jsonify(result)

@app.route('/api/poultry/info', methods = ['get'])
def poultry_info():
    return jsonify(info.poultry_info)

@app.route('/api/poultry', methods = ['post'])
def predict_poultry():
    request_json = request.get_json()
    try:
        type_name = request_json['type_name']
        period = request_json['period']
        predict_days = request_json['predict_days']
    except:
        return jsonify({"Error": 'data not provided.'})
    result = poultry_predict.predict(target=type_name, start=period, predict_days=predict_days)
    return jsonify(result)

@app.route('/api/aquatic/info', methods = ['get'])
def aquatic_info():
    return jsonify(info.aquatic_info)

@app.route('/api/aquatic', methods = ['post'])
def predict_aquatic():
    request_json = request.get_json()
    try:
        market = request_json['market']
        type_name = request_json['type_name']
        period = request_json['period']
        predict_days = request_json['predict_days']
    except:
        return jsonify({"Error": 'data not provided.'})
    result = aquatic_predict.predict(market_name=market, target=type_name, start=period, predict_days=predict_days)
    return jsonify(result)

@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp

if __name__ == '__main__':
    app.secret_key = 'hackntu948794crazy'

    app.run(host="0.0.0.0", port=9487, debug=True)
