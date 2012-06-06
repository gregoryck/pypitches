from flask import Flask

app = Flask(__name__)


@app.route('/pypitches/')
def hello_world():
    return "Hello pitches!"

if __name__ == "__main__":
    app.run()
