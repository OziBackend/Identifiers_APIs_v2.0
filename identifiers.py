from flask import Flask
from routes import setup_routes

app = Flask(__name__)

# Configure your app here if needed

# Setup routes
setup_routes(app)

if __name__ == "__main__":
    app.run(host="172.16.0.94", port=9000, debug=True)
    # app.run(host="46.250.238.182", port=8007, debug=True)
