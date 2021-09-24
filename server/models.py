from server import db

recipe_ing = db.Table(
    'recipe_ing',
    db.Column('recipe_id', db.ForeignKey('recipe.id'),
              primary_key=True),
    db.Column('ingredient_id', db.ForeignKey('ingredient.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(50), unique = True)
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(200))
    email = db.Column(db.String(50))
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')


class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    preparation = db.Column(db.String())
    rating = db.Column(db.Float(), default=0)
    num_of_ratings = db.Column(db.Integer(), default=0)
    user_id = db.Column(db.ForeignKey('user.public_id'))
    num_of_ingredients = db.Column(db.Integer())
    ingredients = db.relationship('Ingredient', secondary=recipe_ing,
                                  back_populates='recipes', lazy='dynamic')


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    recipes = db.relationship('Recipe', secondary=recipe_ing,
                              back_populates='ingredients', lazy='dynamic')