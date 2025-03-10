from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='activity', cascade='all, delete-orphan')
    campers = association_proxy('signups', 'camper', creator=lambda camper_obj: Signup(camper=camper_obj))
    serialize_rules = ('-signups.activity',)

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='camper', cascade='all, delete-orphan')
    activities = association_proxy('signups', 'activity', creator=lambda activity_obj: Signup(activity=activity_obj))
    serialize_rules = ('-signups',)

    @validates('name')
    def validate_name(self, _, name):
        if not name or len(name) < 1:
            raise ValueError('Camper should have a name.')
        return name
    
    @validates('age')
    def validate_age(self, _, age):
        if not 8 <= age <= 18:
            raise ValueError("Camper's age must be between 8 and 18.")
        return age
        
    def __repr__(self):
        return f'<Camper id: {self.id}, name: {self.name}, age: {self.age}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))

    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')

    serialize_rules = ('-activity.signups', '-camper.signups',)
    
    @validates('time')
    def validate_time(self, _, time):
        if time not in range(24):
            raise ValueError('Time can only be between 0 and 23.')
        return time
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
