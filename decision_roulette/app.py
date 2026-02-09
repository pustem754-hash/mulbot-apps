from flask import Flask, render_template, request, jsonify
import random
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spin', methods=['POST'])
def spin_roulette():
    data = request.get_json()
    options = data.get('options', [])
    
    if not options:
        return jsonify({'error': 'Нет вариантов для выбора'}), 400
    
    # Случайный выбор победителя
    winner = random.choice(options)
    
    # Случайный угол поворота (минимум 3 полных оборота + случайный угол)
    rotation_angle = random.randint(1080, 1800) + random.randint(0, 360)
    
    return jsonify({
        'winner': winner,
        'rotation': rotation_angle,
        'winner_index': options.index(winner)
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)