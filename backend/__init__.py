from flask import *
from flask_cors import CORS
from api import api
from flasgger import Swagger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SWAGGER"] = {
    "openapi": "3.0.2",
    "title": "Free 5GC DNS API",
    "version": "0.9.1",
    "hide_top_bar": True
}

Swagger(app)

app.register_blueprint(api, url_prefix='/api')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5534, debug=True)
