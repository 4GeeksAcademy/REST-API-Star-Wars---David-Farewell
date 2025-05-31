"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Error handler
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Sitemap
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.filter_by(user_id=1).all()
    return jsonify([fav.serialize() for fav in favorites]), 200

# Characters
@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    return jsonify([char.serialize() for char in characters]), 200

@app.route('/people/<int:id>', methods=['GET'])
def get_person(id):
    character = Character.query.get(id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(character.serialize()), 200

@app.route('/favorite/people/<int:id>', methods=['POST'])
def add_favorite_character(id):
    exists = Favorite.query.filter_by(user_id=1, character_id=id).first()
    if exists:
        return jsonify({"message": "Character already in favorites"}), 400

    favorite = Favorite(user_id=1, character_id=id, planet_id=None)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Planets
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:id>', methods=['GET'])
def get_planet(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/favorite/planet/<int:id>', methods=['POST'])
def add_favorite_planet(id):
    exists = Favorite.query.filter_by(user_id=1, planet_id=id).first()
    if exists:
        return jsonify({"message": "Planet already in favorites"}), 400

    favorite = Favorite(user_id=1, planet_id=id, character_id=None)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201

# Main
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
