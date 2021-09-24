import clearbit
import os
from pyhunter import PyHunter
from server.models import User, Ingredient, Recipe
from server import db
from sqlalchemy import func, or_, exc
from flask import request,  jsonify,  make_response
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from server import server

clearbit.key = os.environ.get('CLEARBIT_KEY')
hunter = PyHunter(os.environ.get('HUNTER_KEY'))

def user_data(email):  
    email = email
    try:
        response = clearbit.Person.find(email=email)
    except:
        return jsonify({'message' : "User not found"}),404

    return jsonify({
        'first_name': response['name']['givenName'],
        'last_name': response['name']['familyName']
    })

def register_user(data):
    if '@' not in data["email"] or '.' not in data["email"]:
        return jsonify({'message' : 'Invalid email'}), 401

    check_email = hunter.email_verifier(data["email"])

    if check_email['result'] == 'undeliverable':
        return jsonify({'message2' : 'Invalid email'}), 401

    hashed_password = generate_password_hash(data["password"],
     method='sha256')

    new_user = User(public_id=str(uuid.uuid4()),
                    username=data['username'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    password=hashed_password,
                    email=data['email'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'New user created!'})

def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401,
         {'WWW-Authenticate' : 'Bsic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401,
         {'WWW-Authenticate' : 'Bsic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 
        'exp' : datetime.datetime.utcnow() + 
        datetime.timedelta(minutes=30)}, 
        server.config['SECRET_KEY'])

        return jsonify({'token' : token})

    return make_response('Could not verify', 401,
         {'WWW-Authenticate' : 'Bsic realm="Login required!"'})

def list_all_users():
    users = User.query.all()
    result = []

    for user in users:
        user_data={}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        user_data['password'] = user.password
        user_data['email'] = user.email
        result.append(user_data)

    return jsonify({"user" : result})

def add_recipe(current_user, data):
    ingredient_list = []

    if 'ingredients' in list(data.keys()):
        for ing in data['ingredients']:            
            instance = db.session.query(Ingredient).filter(
                Ingredient.name == ing).first()
            if instance:
                ingredient_list.append(instance)
            else:
                ingredient_list.append(add_ingredient(ing))

    new_recipe = Recipe(
        name=data['name'],
        preparation=data['preparation'],
        ingredients=ingredient_list,
        user_id=current_user.public_id,
        num_of_ingredients=len(ingredient_list)
        )
    db.session.add(new_recipe)
    db.session.commit()

    db.session.add(new_recipe)
    db.session.commit()

    return jsonify({'message' : "Recipe created!"})

def all_recipes():
    recipes = db.session.query(Recipe).all()

    result = []

    for recipe in recipes:
        recipe_data = {}
        recipe_data['name'] = recipe.name
        recipe_data['id'] = recipe.id
        recipe_data['preparation'] = recipe.preparation
        recipe_data['rating'] = recipe.rating
        recipe_data['num_of_ratings'] = recipe.num_of_ratings
        recipe_data['num_of_ingredients'] = recipe.num_of_ingredients
        recipe_data['ingredients'] = [ing.name for ing in recipe.ingredients]
        result.append(recipe_data)

    return jsonify({'Recipes' : result})

def add_ingredient(name):
    new_ingredient = Ingredient(name=name)

    db.session.add(new_ingredient)
    db.session.commit()

    return new_ingredient

def get_top_five_ing():
    most_used_ing = db.session \
        .query(Ingredient) \
        .join(Ingredient.recipes) \
        .group_by(Ingredient.id) \
        .order_by(func.count().desc()) \
        .limit(5) \
        .all()

    return most_used_ing

def search_recipes(args):
    arr = []
    keys = list(args.keys())

    if 'name' in keys:
        arr.append(Recipe.name.contains(args['name']))
    if 'text' in keys:
        arr.append(Recipe.preparation.contains(args['text']))
    if 'ingredients' in keys:
        arr.append(or_(
            *[Ingredient.name.contains(ingredient)
              for ingredient in args['ingredients'].split(',')]
        ))

    try:
        recipes = db.session.query(Recipe).join(Recipe.ingredients).filter(
            or_(*arr)).all()
    except exc.SQLAlchemyError:
        return jsonify({'message' : 'Internal server error'}), 500

    return recipes