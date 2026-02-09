from flask import Flask, render_template

app = Flask(__name__)

# Данные меню
menu_data = {
    'coffee': [
        {'name': 'Эспрессо', 'price': '150₽', 'description': 'Классический итальянский кофе'},
        {'name': 'Американо', 'price': '180₽', 'description': 'Эспрессо с горячей водой'},
        {'name': 'Капучино', 'price': '220₽', 'description': 'Эспрессо с молочной пеной'},
        {'name': 'Латте', 'price': '250₽', 'description': 'Эспрессо с молоком и легкой пенкой'},
        {'name': 'Мокко', 'price': '280₽', 'description': 'Кофе с шоколадом и взбитыми сливками'}
    ],
    'desserts': [
        {'name': 'Круассан', 'price': '120₽', 'description': 'Свежий французский круассан'},
        {'name': 'Чизкейк', 'price': '180₽', 'description': 'Нежный чизкейк с ягодами'},
        {'name': 'Тирамису', 'price': '200₽', 'description': 'Классический итальянский десерт'},
        {'name': 'Маффин', 'price': '90₽', 'description': 'Домашний маффин с начинкой'}
    ]
}

@app.route('/')
def home():
    return render_template('index.html', menu=menu_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)