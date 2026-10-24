from flask import Flask
from routes import web_bp, api_bp

app = Flask(__name__)

# Mendaftarkan Blueprint dari folder routes/
app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)