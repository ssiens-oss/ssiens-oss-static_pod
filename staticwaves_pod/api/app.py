from flask import Flask
from api.routes import api
from api.config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
