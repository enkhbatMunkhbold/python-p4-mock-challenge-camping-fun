#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, session
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)
db.init_app(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict() for camper in Camper.query.all()]
        return make_response( campers, 200 )
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')

        try:
            new_camper = Camper(
                name = name,
                age = age
            )

            db.session.add(new_camper)
            db.session.commit()
            return make_response( new_camper.to_dict(), 201) 
        
        except ValueError:
            return make_response({ 'errors': ['validation errors']}, 400 )

api.add_resource(Campers, '/campers', endpoint='campers')

class CampersByID(Resource):
    def get(self, id):
        # camper = db.session.get(Camper, id)
        camper = Camper.query.filter(Camper.id == id).first()

        if not camper:
            return make_response( jsonify({ 'error': 'Camper not found' }), 404 )
        return make_response( camper.to_dict(rules=('-signups.camper',)), 200)

    def patch(self, id):
        
        camper = Camper.query.filter(Camper.id == id).first()

        if camper == None:
            return make_response( {'error': 'Camper not found'}, 404 )
        
        try:        
            setattr(camper, 'name', request.get_json()['name'])
            setattr(camper, 'age', request.get_json()['age'])

            db.session.add(camper)
            db.session.commit()

            return make_response( camper.to_dict(), 202 )
        except ValueError:
            return make_response( {'errors': ['validation errors']}, 400 )

    
api.add_resource(CampersByID, '/campers/<int:id>', endpoint='<int:id>')

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(rules=('-signups',)) for activity in Activity.query.all()]
        return make_response( activities, 200 )

api.add_resource(Activities, '/activities', endpoint='activities')

class ActivitiesByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if not activity:
            return make_response({'error': 'Activity not found'}, 404)
        
        db.session.delete(activity)
        db.session.commit()

        return make_response({ 'message': 'activity successfully deleted.'}, 204)
    
api.add_resource(ActivitiesByID, '/activities/<int:id>', endpoint='<int:id')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            new_signup = Signup(
            camper_id = data.get('camper_id'),
            activity_id = data.get('activity_id'),
            time = data.get('time')
            )

            db.session.add(new_signup)
            db.session.commit()

            return make_response( new_signup.to_dict(), 201 )
        except ValueError:
            return make_response( {'errors': ['validation errors']}, 400 )        

api.add_resource(Signups, '/signups', endpoint='signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
