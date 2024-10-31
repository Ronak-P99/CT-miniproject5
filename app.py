from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class CustomerSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class OrderSchema(ma.Schema):
    id = fields.String(dump_only=True)
    date = fields.Date(required=True)
    customer_id = fields.String(required=True)

    class Meta:
        fields = ("id", "date", "customer_id")

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


class CustomerAccountSchema(ma.Schema):
    id = fields.String(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer_id = fields.String(required=True)

    class Meta:
        fields = ("id", "username", "password", "customer_id")

customer_account_schema = CustomerAccountSchema()
customers_account_schema = CustomerAccountSchema(many=True)

class ProductSchema(ma.Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))

# One-To-One

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

@app.route('/customers', methods=['GET'])
def get_customer():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def get_one_customer(id):
    customer = Customer.query.get(id)
    return customer_schema.jsonify(customer)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()

    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"}), 200

@app.route('/customers_account', methods=['GET'])
def get_customer_account():
    customers_account = CustomerAccount.query.all()
    return customers_account_schema.jsonify(customers_account)

@app.route('/customers_account/<int:id>', methods=['GET'])
def get_one_customer_account(id):
    customer_account = CustomerAccount.query.get(id)
    return customer_account_schema.jsonify(customer_account)

@app.route('/customers_account', methods=['POST'])
def add_customer_account():
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer_account = CustomerAccount(username=customer_account_data['username'], customer_id=customer_account_data['customer_id'], password=customer_account_data['password'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message": "New customer account added successfully"}), 201

@app.route('/customers_account/<int:id>', methods=['PUT'])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer_account.username = customer_account_data['username']
    customer_account.password = customer_account_data['password']
    db.session.commit()

    return jsonify({"message": "Customer Account details updated successfully"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_one_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()

    return jsonify({"message": "Product details updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product removed successfully"}), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return orders_schema.jsonify(orders)

@app.route('/orders/<int:id>', methods=['GET'])
def get_one_order(id):
    order = Order.query.get(id)
    return order_schema.jsonify(order)

@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(date=order_data['date'], customer_id=order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "New Order added successfully"}), 201

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get_or_404(id)
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    order.date = order_data['date']
    db.session.commit()

    return jsonify({"message": "Order details updated successfully"}), 200


# Initialize the database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
