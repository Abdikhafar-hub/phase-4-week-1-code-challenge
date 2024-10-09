from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return '<h1>Code Challenge API</h1>'

# Route to get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(rules=('-hero_powers',)) for hero in heroes])

# Route to get a hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = db.session.get(Hero, id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404
    # Include hero_powers in the response
    return jsonify(hero.to_dict())

# Route to get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict(rules=('-hero_powers',)) for power in powers])

# Route to get a power by ID
@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def get_or_update_power(id):
    if request.method == 'GET':
        power = db.session.get(Power, id)
        if not power:
            return jsonify({'error': 'Power not found'}), 404
        return jsonify(power.to_dict(rules=('-hero_powers',)))
    
    if request.method == 'PATCH':
        power = db.session.get(Power, id)
        if not power:
            return jsonify({'error': 'Power not found'}), 404

        data = request.get_json()

        try:
            if 'description' in data:
                power.description = data['description']
            db.session.commit()
            return jsonify(power.to_dict()), 200
        except Exception as e:
            # Ensure consistent error format
            return jsonify({'errors': ["validation errors"]}), 400

# Route to create a HeroPower
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Validate strength value
    if data.get('strength') not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ["validation errors"]}), 400

    try:
        hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(hero_power)
        db.session.commit()
        return jsonify(hero_power.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Error handler for 404
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)
