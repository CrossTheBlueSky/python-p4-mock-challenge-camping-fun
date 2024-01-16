#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=["GET", "POST"])
def campers():
    if request.method == "GET":
        campers = [camper.to_dict(rules=('-signups',)) for camper in Camper.query.all()]
        return campers

    if request.method == "POST":
        data = request.json
        try:
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(), 200)
        
        except:
            print("fail")
            return make_response({"errors" : ["validation errors"]}, 400)

@app.route('/campers/<int:id>', methods=["GET", "PATCH", "POST"])
def camper_by_id(id):
    selected_camper = Camper.query.filter(Camper.id == id).first() or None

    if selected_camper == None:
        return make_response({"error" : "Camper not found"}, 404)

    if request.method == "GET":
        return make_response(selected_camper.to_dict(), 200)
    if request.method == "PATCH":
        try:
            for attr in request.json:
                setattr(selected_camper , attr, request.json.get(attr))
            db.session.add(selected_camper)
            db.session.commit()
            return make_response(selected_camper.to_dict(), 202)
        except:
            return make_response({"errors" : ["validation errors"]}, 400)



@app.route("/activities")
def activities():

    activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]
    
    return activities

@app.route("/activities/<int:id>", methods=["DELETE"])
def activities_by_id(id):
    selected_activity = Activity.query.filter(Activity.id == id).first() or None
    if selected_activity == None:
        return make_response({"error" : "Activity not found"}, 404)
    db.session.delete(selected_activity)
    db.session.commit()
    return make_response({"message" : "activity deleted successfully"}, 204)

@app.route("/signups", methods=["POST"])
def signups():
    if request.method == "POST":
        data = request.json
        sel_camper = Camper.query.filter(Camper.id == data['camper_id']).first()
        sel_activity = Activity.query.filter(Activity.id == data['activity_id']).first()
        try:
            new_signup = Signup(
                time = data['time'],
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                camper = sel_camper,
                activity = sel_activity

            )

            db.session.add(new_signup)
            db.session.commit()

            return make_response(new_signup.to_dict(), 200)
        except:
            return make_response({"errors" : ["validation errors"]}, 400)
        
if __name__ == '__main__':
    app.run(port=5555, debug=True)
