from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests (needed for Flutter Web or mobile)

@app.route('/')
def home():
    return jsonify({"message": "Hello from Flask API! 🎉"})

@app.route('/status')
def status():
    return jsonify({"status": "API is running", "code": 200})

if __name__ == '__main__':
    app.run(debug=True)