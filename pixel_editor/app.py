from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageDraw
import io
import base64
import json

app = Flask(__name__)

# Палитра цветов
PALETTE = {
    'black': '#000000',
    'white': '#FFFFFF',
    'red': '#FF0000',
    'blue': '#0000FF',
    'green': '#00FF00',
    'yellow': '#FFFF00',
    'orange': '#FFA500',
    'pink': '#FFC0CB',
    'purple': '#800080',
    'brown': '#8B4513',
    'gray': '#808080',
    'cyan': '#00FFFF',
    'lime': '#32CD32',
    'maroon': '#800000',
    'turquoise': '#40E0D0',
    'gold': '#FFD700'
}

@app.route('/')
def index():
    return render_template('index.html', palette=PALETTE)

@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        grid_data = request.json['grid']
        
        # Создаем изображение 32x32
        img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        
        for y in range(32):
            for x in range(32):
                color = grid_data[y][x]
                if color and color != 'transparent':
                    # Конвертируем hex в RGB
                    hex_color = color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    img.putpixel((x, y), rgb + (255,))
        
        # Увеличиваем изображение в 10 раз для лучшего качества
        img = img.resize((320, 320), Image.NEAREST)
        
        # Сохраняем в буфер
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='pixel_art.png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)