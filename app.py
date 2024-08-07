from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user

#variavel que vai receber uma instancia da classe flask
app = Flask(__name__)
app.config['SECRET_KEY'] = "minha_chave"

#configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

#concta o banco ao app
login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)


#modelagem

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=True)  #nullable= deixa obrigatorio, nao pode prosseguir sem.


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


#autenticação
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()  #filter para filtrar.

    if user:
        if data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully"})
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401

    return jsonify({"message": "Logged in successfully"})



@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logout successfolly"})


#add produtos
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json
    #if uma condição para que seja necessario ter o name e o data,caso contrario nao vai prosseguir
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 200
    return jsonify({"message": "invalid product data"}), 400


#delete produtos
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        # Reordenar IDs
        product = Product.query.order_by(product_id).all()
        for index, product in enumerate(product):
            Product.id = index + 1
        db.session.commit()

        return jsonify({"message": "Product deleted successfully"}), 200
    return jsonify({"message": "product not found"}), 404


@app.route('/api/products/<int:product_id>', methods=["GET"])
@login_required
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404


@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json
    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    db.session.commit()  #necessario para a mudança ser adicionada ao banco de dados

    return jsonify({'message': 'Product update sucessfully'})


@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        }
        product_list.append(product_data)
    return jsonify(product_list)


#definir uma rota raiz (pagina inicial) e a função que sera executada, quando requisitado
@app.route("/")
#definar uma funçao def(definição)
def hello_world():
    return "Hello World"


#visibilidade
if __name__ == "__main__":
    app.run(debug=True)
