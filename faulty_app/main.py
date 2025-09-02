from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Try to load .env file
    app_name = os.getenv('APP_NAME')
    if not app_name:
        raise RuntimeError("Missing Application Name environment variable. Please set it in your .env file.")
    return 'Hello, this is the main endpoint!'

if __name__ == '__main__':
    app.run(debug=True)