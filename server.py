
#!/usr/local/bin/python3

from flask import Flask, send_from_directory
from flask_restful import Api, Resource
from flask import request
from flask.json import jsonify
from flask_cache import Cache
from flask import Flask, session
from flask_session import Session
import aquatic_predict
import poultry_predict
import pig_predict


app = Flask(__name__)
api = Api(app)
sess = Session()

@app.route('/')
def index():
    return "Happy hacking!"

@app.route('/plot/<path:path>')
def send_js(path):
    return send_from_directory('plot', path)

@app.route('/api/pig', methods = ['post'])
def predict_pig():
    request_json = request.get_json()
    try:
        market = request_json['market']
        type_name = request_json['type_name']
        period = request_json['period']
        predict_days = request_json['predict_days']
    except:
        return jsonify({"Error": 'data not provided.'})
    result = pig_predict.predict(market_name=market, target_level=type_name, start=period, predict_days=predict_days)
    return jsonify(result)

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

if __name__ == '__main__':
    app.secret_key = 'hackntu948794crazy'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)

    app.run(host="0.0.0.0", port=9487, debug=True)
