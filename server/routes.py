from server.helpers import (register_user, login_user, user_data, 
                            get_top_five_ing, list_all_users, 
                            add_recipe, all_recipes, search_recipes)
from flask import request,  jsonify 
from server import server
from functools import wraps
import jwt
from server import db
from server.models import Recipe, User


### Token auth
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, 
            server.config['SECRET_KEY'], 
            algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message' : "Token is invalid!"}), 401
        
        return f(current_user, *args, **kwargs)
    return  decorated    

### User routes
## Find user data
@server.route('/user/find')
def find_user_data():
    data = request.get_json()
    email = data["email"]

    return user_data(email)

## Create user
@server.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    result = register_user(data)

    return result

## Login user
@server.route('/login', methods=['GET'])
def login():
    result = login_user()

    return result

## List all users
@server.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    return list_all_users()

## Delete user
@server.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message' : 'The user has been deleted!'})

### Recipe routes
## Add new recipe
@server.route('/recipe', methods=['POST'])
@token_required
def add_new_recipe(current_user):
    data = request.get_json()
    result = add_recipe(current_user, data)

    return result

## List all recipes
@server.route('/recipe', methods=['GET'])
@token_required
def get_all_recipes(current_user):
    result = all_recipes()
    
    return result


## List user recipes 
@server.route('/recipe/<user_id>', methods=['GET'])
@token_required
def get_user_recipes(current_user, user_id):
    recipes = Recipe.query.filter_by(user_id=current_user.public_id).all()

    if not recipes:
        return jsonify({'message' : 'No recipes found!'})
    
    result = []

    for recipe in recipes:
        recipe_data = {}
        recipe_data['name'] = recipe.name
        recipe_data['preparation'] = recipe.preparation
        recipe_data['rating'] = recipe.rating
        recipe_data['num_of_ratings'] = recipe.num_of_ratings
        recipe_data['num_of_ingredients'] = recipe.num_of_ingredients
        recipe_data['ingredients'] = [ing.name for ing in recipe.ingredients]
        result.append(recipe_data)

    return jsonify({'Recipes' : result})

## Rate recipe
@server.route('/recipe/rate/<recipe_id>', methods=['PATCH'])
@token_required
def rate_recipe(current_user, recipe_id):
    if request.is_json:
        data = request.get_json()
        keys = list(data.keys())

        if 'rating' not in keys or 'user_id' not in keys or not recipe_id:
            return jsonify({'error': 'Unable to rate recipe'}), 400

        user_rating = int(data['rating'])
        if user_rating > 5 or user_rating < 1:
            return jsonify({'error': 'Rating out of range'}), 400

        
        recipe = db.session.query(Recipe).filter(
            Recipe.id == recipe_id).first()

        if current_user.public_id == data['user_id']:
            return jsonify({
                'error': 'Users cannot rate their own recipes'}),401

        recipe.rating = (
            (recipe.rating * recipe.num_of_ratings + user_rating) /
            (recipe.num_of_ratings + 1)
        )
        recipe.num_of_ratings += 1

        
        db.session.commit()

        return jsonify({'message': f'{recipe.name} rated succesfully'})
    else:
        return jsonify({'error': 'Unable to rate recipe'}), 400

## Search recipe 
@server.route('/recipe/search', methods=['GET'])
@token_required
def get_search_recipes(current_user):
    data = request.get_json()
    recipes = search_recipes(data)    
    result = [
        {
            'name': recipe.name,
            'preparation': recipe.preparation,
            'rating': recipe.rating,
            'num_of_ratings': recipe.num_of_ratings,
            'num_of_ingredients': recipe.num_of_ingredients,
            'ingredients': [ing.name for ing in recipe.ingredients]
        } for recipe in recipes]

    return jsonify({'message' : result})

###  Ingredients routes
## List top 5 ingredients
@server.route('/ingredients', methods=['GET'])
@token_required
def top_five_ing(current_user):
    result = get_top_five_ing()
    result = [ing.name for ing in result]

    return jsonify({'message' : result})
    


