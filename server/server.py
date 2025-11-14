from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    app.config["DATA FILE"] = os.path.join(base_dir, "data.json")

    from server.routes.upload_route import bp as upload_bp
    from server.routes.data_route import bp as data_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(data_bp)

    return app

if __name__ =="__main__":
    app = create_app()
    app.run(host="0.0.0.0", port = 5000, debug = True)


