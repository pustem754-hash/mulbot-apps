import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file
import qrcode
from PIL import Image
import json
from datetime import datetime

app = Flask(__name__)

# Конфигурация
UPLOAD_FOLDER = 'static/qr_codes'
STATS_FILE = 'stats.json'

# Создаем папку для QR кодов
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_stats():
    """Загружает статистику из файла"""
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'total_qr_codes': 0}

def save_stats(stats):
    """Сохраняет статистику в файл"""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

def increment_qr_count():
    """Увеличивает счетчик QR кодов"""
    stats = load_stats()
    stats['total_qr_codes'] += 1
    save_stats(stats)
    return stats['total_qr_codes']

@app.route('/')
def index():
    """Главная страница"""
    stats = load_stats()
    return render_template('index.html', total_qr_codes=stats['total_qr_codes'])

@app.route('/generate', methods=['POST'])
def generate_qr():
    """Генерирует QR код"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Текст не может быть пустым'}), 400
        
        # Создаем QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Конвертируем в base64 для отображения
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        # Сохраняем файл для скачивания
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'qr_code_{timestamp}.png'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        img.save(filepath)
        
        # Увеличиваем счетчик
        total_count = increment_qr_count()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'filename': filename,
            'total_count': total_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_qr(filename):
    """Скачивает QR код"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Файл не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Возвращает текущую статистику"""
    stats = load_stats()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)