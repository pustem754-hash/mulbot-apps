from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spin', methods=['POST'])
def spin():
    data = request.get_json()
    options = data.get('options', [])
    
    if len(options) < 2:
        return jsonify({'error': 'Минимум 2 варианта для вращения'}), 400
    
    # Генерируем случайный угол поворота
    base_rotation = random.randint(1440, 2520)  # 4-7 полных оборотов
    
    # Выбираем победителя
    winner_index = random.randint(0, len(options) - 1)
    winner = options[winner_index]
    
    # Рассчитываем угол для остановки на победителе
    sector_angle = 360 / len(options)
    target_angle = 360 - (winner_index * sector_angle + sector_angle / 2)
    final_rotation = base_rotation + target_angle
    
    return jsonify({
        'rotation': final_rotation,
        'winner': winner,
        'winner_index': winner_index
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)