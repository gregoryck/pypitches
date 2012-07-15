from flask import Flask, request, session, url_for, render_template, flash, send_from_directory, jsonify
import load
import traceback
from os.path import join
from model import start_postgres, GameDir


app = Flask(__name__)
Session = None

@app.route('/pypitches/status')
def status():
    return render_template("status.html")

@app.route('/pypitches/controls')
def controls():
    return render_template("controls.html")

@app.route('/pypitches/load', methods=['POST'])
def load():
    gamedir_id = request.form['gamedir_id']

@app.route('/pypitches/_gamedata')
def gamedirs():
    start = int(request.args['iDisplayStart'])
    length = int(request.args['iDisplayLength'])
    columns = int(request.args['iColumns'])
    echo = int(request.args['sEcho'])
    print start, length, columns, echo
    try:
        query = Session.query(GameDir.path, GameDir.url, GameDir.downloaded_time, GameDir.loaded_time, GameDir.date_scheduled)
        count = query.count()
        rows = [fmt_row(row, ident, ident, str, str, str) for row in query.all()]
        return jsonify({
                    'iTotalRecords': count,
                    'iTotalDisplayRecords': count,
                    'sEcho': echo,
                    'aaData': rows,
                    'DT_RowClass': 'any_row',
                })
    except:
        print traceback.format_exc()
        return "<pre>{0}</pre>".format(traceback.format_exc())

def ident(x):
    return x


def fmt_row(row, *types):
    return [ ty(col) for ty, col in zip(types, row)]


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

def run(db='pypitches', user='pypitches', password=None):
    global Session  
    Session = start_postgres(db, user, password)
    app.run()

if __name__ == "__main__":
    run()
