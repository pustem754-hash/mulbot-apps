from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# Файл для хранения заметок
NOTES_FILE = 'notes.json'

def load_notes():
    """Загружает заметки из файла"""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_notes(notes):
    """Сохраняет заметки в файл"""
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Главная страница"""
    notes = load_notes()
    return render_template('index.html', notes=notes)

@app.route('/add_note', methods=['POST'])
def add_note():
    """Добавляет новую заметку"""
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({'success': False, 'message': 'Заполните все поля!'})
    
    notes = load_notes()
    
    # Создаем новую заметку
    new_note = {
        'id': len(notes) + 1,
        'title': title,
        'content': content,
        'created_at': datetime.now().strftime('%d.%m.%Y %H:%M')
    }
    
    notes.append(new_note)
    save_notes(notes)
    
    return jsonify({
        'success': True, 
        'message': 'Заметка добавлена!',
        'note': new_note
    })

@app.route('/delete_note/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Удаляет заметку по ID"""
    notes = load_notes()
    notes = [note for note in notes if note['id'] != note_id]
    save_notes(notes)
    
    return jsonify({'success': True, 'message': 'Заметка удалена!'})

@app.route('/edit_note/<int:note_id>', methods=['PUT'])
def edit_note(note_id):
    """Редактирует заметку по ID"""
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({'success': False, 'message': 'Заполните все поля!'})
    
    notes = load_notes()
    
    for note in notes:
        if note['id'] == note_id:
            note['title'] = title
            note['content'] = content
            note['updated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M')
            break
    
    save_notes(notes)
    return jsonify({'success': True, 'message': 'Заметка обновлена!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)