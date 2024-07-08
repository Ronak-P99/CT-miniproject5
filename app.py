from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Mario101299@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    age = fields.String(required=True)

    class Meta:
        fields = ("name", "age", "id")


class WorkoutSessionsSchema(ma.Schema):
    session_id = fields.Int(dump_only=True)
    member_id = fields.Int(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)
    

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_schema = WorkoutSessionsSchema()
workouts_schema = WorkoutSessionsSchema(many=True)

class Members(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.String(10))
    workouts = db.relationship('WorkoutSessions', backref='Members')

class WorkoutSessions(db.Model):
    __tablename__ = 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(255), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))

'''# One-To-One

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

# Many-To-Many

order_product = db.Table('Order_Product',
        db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key = True),
        db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))
'''
@app.route('/members', methods=['GET'])
def get_members():
    members = Members.query.all()
    return members_schema.jsonify(members)

@app.route('/members/<int:id>', methods=['GET'])
def get_one_member(id):
    member = Members.query.get(id)
    return member_schema.jsonify(member)

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Members(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Members.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.name = member_data['name']
    member.age = member_data['age']

    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Members.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()

@app.route('/workoutsessions', methods=['GET'])
def get_workouts():
    workouts = WorkoutSessions.query.all()
    return workouts_schema.jsonify(workouts)

@app.route('/workoutsessions/<int:id>', methods=['GET'])
def get_one_workout(id):
    workout = WorkoutSessions.query.get(id)
    return workout_schema.jsonify(workout)

@app.route('/workoutsessions', methods=['POST'])
def add_workouts():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_workout = WorkoutSessions(member_id=workout_data['member_id'], session_date=workout_data['session_date'], session_time=workout_data['session_time'], activity=workout_data['activity'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"message": "New workout added successfully"}), 201

@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_workouts(id):
    workout = WorkoutSessions.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    workout.session_date = workout_data['session_date']
    workout.session_time = workout_data['session_time']
    workout.activity = workout_data['activity']

    db.session.commit()
    return jsonify({"message": "Workout details updated successfully"}), 200

# Initialize the database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
