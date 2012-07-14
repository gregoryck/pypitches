from flask import Flask, request, session, url_for, render_template, flash, send_from_directory, jsonify
from pypitches import load
import traceback
from os.path import join

app = Flask(__name__)


@app.route('/pypitches/status')
def status():
    return render_template("status.html")

@app.route('/pypitches/controls')
def controls():
    return render_template("controls.html")

@app.route('/pypitches/load', methods=['POST'])
def load():
    gamedir_id = request.form['gamedir_id']

@app.route('/pypitches/_gamedirs')
def gamedirs():
    return jsonify({'gamedirs': [{'Path': 'test',
                                  'URL' : 'test2',
                                 }]
                  })

@app.route('/static/<filename>')
def send_foo(filename):
    print "hi!", filename
    print app.root_path
    try:
        return send_from_directory(join(app.root_path, 'static'), filename)
    except:
        print "hey!"
        traceback.print_exc()
        raise


if __name__ == "__main__":
    app.run()
