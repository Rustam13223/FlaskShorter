from flask import Flask, jsonify, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

from datetime import datetime, timedelta


app = Flask(__name__)
dburi = 'sqlite:///./data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = dburi
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(20), unique=True, nullable=False)
    full = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return "\n" + self.short + "\n" + self.full + "\n"


b_ips = {}
tracks = {}

def gTime():
    return datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")

@app.route("/", methods=["GET"])
def index():
    ip = request.remote_addr
    time = gTime()

    if ip in b_ips.keys():
        if time < b_ips[ip]:
            return abort(404)
        else:
            del b_ips[ip]

    if ip not in tracks.keys():
        tracks[ip] = [0, gTime()]
    elif tracks[ip][0] >= 2:
        b_ips[ip] = time + timedelta(minutes=1)
        del tracks[ip]
    elif time == tracks[ip][1]:
        tracks[ip][0] += 1
    else:
        del tracks[ip]

    return render_template("index.html")

@app.route("/new/", methods=["POST"])
def createShort():
    print(request.json)
    if not request.json:
        return jsonify({"Error":"no json found"})
    if "shot" not in request.json:
        return jsonify({"Error":"Короткая ссылка не найдена"})
    if "url" not in request.json:
        return jsonify({"Error":"Ссылка не найдена"})

    shot = request.json["shot"]
    url = request.json["url"]

    if Link.query.filter_by(short=shot).first() == None:
        newLink = Link(short=shot, full=url)
        db.session.add(newLink)
        db.session.commit()
        return jsonify({"Status":"OK"})
    else:
        return jsonify({"Error":"Данная короткая ссылка уже используется"})

@app.route("/<shot>/", methods=["GET"])
def redir(shot):
    res = Link.query.filter_by(short=shot).first()
    if res != None:
        return redirect(res.full)
    else:
        return jsonify({"Error":"bad url"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
