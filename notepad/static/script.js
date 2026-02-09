// Глобальные переменные
let editingNoteId = null;
let allNotes = [];

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Загружаем все заметки в массив для поиска
    loadNotesFromPage();
    
    // Обработчик формы
    document.getElementById('noteForm').addEventListener('submit', handleFormSubmit);
    
    // Обработчик поиска
    document.getElementById('searchInput').addEventListener('input', handleSearch);
    
    // Обработчик отмены редактирования
    document.getElementById('cancelEdit').addEventListener('click', cancelEdit);
});

// Загружает заметки со страницы в массив
function loadNotesFromPage() {
    const noteCards = document.querySelectorAll('.note-card');
    allNotes = Array.from(noteCards).map(card => {
        return {
            id: parseInt(card.dataset.id),
            title: card.querySelector('.note-title').textContent,
            content: card.querySelector('.note-content').textContent,
            element: card
        };
    });
}

// Обработка отправки формы
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const title = document.getElementById('noteTitle').value.trim();
    const content = document.getElementById('noteContent').value.trim();
    
    if (!title || !content) {
        showNotification('Пожалуйста, заполните все поля!', 'error');
        return;
    }
    
    if (editingNoteId) {
        await updateNote(editingNoteId, title, content);
    } else {
        await addNote(title, content);
    }
}

// Добавление новой заметки
async function addNote(title, content) {
    try {
        const response = await fetch('/add_note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            clearForm();
            addNoteToPage(data.note);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Ошибка при добавлении заметки!', 'error');
    }
}

// Обновление заметки
async function updateNote(noteId, title, content) {
    try {
        const response = await fetch(`/edit_note/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            updateNoteOnPage(noteId, title, content);
            cancelEdit();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Ошибка при обновлении заметки!', 'error');
    }
}

// Удаление заметки
async function deleteNote(noteId) {
    if (!confirm('Вы уверены, что хотите удалить эту заметку?')) {
        return;
    }
    
    try {
        const response = await fetch(`/delete_note/${noteId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            removeNoteFromPage(noteId);
        } else {
            showNotification('Ошибка при удалении заметки!', 'error');
        }
    } catch (error) {
        showNotification('Ошибка при удалении заметки!', 'error');
    }
}

// Начало редактирования заметки
function editNote(noteId) {
    const noteCard = document.querySelector(`[data-id="${noteId}"]`);
    const title = noteCard.querySelector('.note-title').textContent;
    const content = noteCard.querySelector('.note-content').textContent;
    
    // Заполняем форму данными заметки
    document.getElementById('noteTitle').value = title;
    document.getElementById('noteContent').value = content;
    
    // Переключаем в режим редактирования
    editingNoteId = noteId;
    document.getElementById('submitText').textContent = 'Сохранить изменения';
    document.getElementById('cancelEdit').style.display = 'inline-block';
    
    // Подсвечиваем редактируемую заметку
    document.querySelectorAll('.note-card').forEach(card => {
        card.classList.remove('editing');
    });
    noteCard.classList.add('editing');
    
    // Прокручиваем к форме
    document.querySelector('.add-note-section').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// Отмена редактирования
function cancelEdit() {
    editingNoteId = null;
    clearForm();
    document.getElementById('submitText').textContent = 'Добавить заметку';
    document.getElementById('cancelEdit').style.display = 'none';
    
    // Убираем подсветку
    document.querySelectorAll('.note-card').forEach(card => {
        card.classList.remove('editing');
    });
}

// Очистка формы
function clearForm() {
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').value = '';
}

// Добавление заметки на страницу
function addNoteToPage(note) {
    const notesList = document.getElementById('notesList');
    
    // Удаляем сообщение о пустом состоянии, если оно есть
    const emptyState = notesList.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Создаем HTML для новой заметки
    const noteHTML = `
        <div class="note-card" data-id="${note.id}">
            <div class="note-header">
                <h3 class="note-title">${note.title}</h3>
                <div class="note-actions">
                    <button onclick="editNote(${note.id})" class="btn-icon edit-btn" title="Редактировать">
                        ✏️
                    </button>
                    <button onclick="deleteNote(${note.id})" class="btn-icon delete-btn" title="Удалить">
                        🗑️
                    </button>
                </div>
            </div>
            <p class="note-content">${note.content}</p>
            <div class="note-date">
                Создано: ${note.created_at}
            </div>
        </div>
    `;
    
    // Добавляем в начало списка
    notesList.insertAdjacentHTML('afterbegin', noteHTML);
    
    // Обновляем массив заметок
    loadNotesFromPage();
    updateNotesCount();
}

// Обновление заметки на странице
function updateNoteOnPage(noteId, title, content) {
    const noteCard = document.querySelector(`[data-id="${noteId}"]`);
    noteCard.querySelector('.note-title').textContent = title;
    noteCard.querySelector('.note-content').textContent = content;
    
    // Обновляем дату изменения
    const dateDiv = noteCard.querySelector('.note-date');
    const now = new Date();
    const dateStr = `${now.getDate().toString().padStart(2, '0')}.${(now.getMonth()+1).toString().padStart(2, '0')}.${now.getFullYear()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    if (dateDiv.innerHTML.includes('Обновлено:')) {
        dateDiv.innerHTML = dateDiv.innerHTML.replace(/Обновлено: .*$/, `Обновлено: ${dateStr}`);
    } else {
        dateDiv.innerHTML += `<br>Обновлено: ${dateStr}`;
    }
    
    // Обновляем массив заметок
    loadNotesFromPage();
}

// Удаление заметки со страницы
function removeNoteFromPage(noteId) {
    const noteCard = document.querySelector(`[data-id="${noteId}"]`);
    noteCard.style.animation = 'fadeOut 0.3s ease';
    
    setTimeout(() => {
        noteCard.remove();
        
        // Проверяем, остались ли заметки
        const remainingNotes = document.querySelectorAll('.note-card');
        if (remainingNotes.length === 0) {
            document.getElementById('notesList').innerHTML = `
                <div class="empty-state">
                    <p>📝 У вас пока нет заметок</p>
                    <p>Создайте свою первую заметку!</p>
                </div>
            `;
        }
        
        // Обновляем массив заметок и счетчик
        loadNotesFromPage();
        updateNotesCount();
        
        // Если удаляли редактируемую заметку, отменяем редактирование
        if (editingNoteId === noteId) {
            cancelEdit();
        }
    }, 300);
}

// Поиск заметок
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    allNotes.forEach(note => {
        const titleMatch = note.title.toLowerCase().includes(searchTerm);
        const contentMatch = note.content.toLowerCase().includes(searchTerm);
        
        if (titleMatch || contentMatch || searchTerm === '') {
            note.element.style.display = 'block';
        } else {
            note.element.style.display = 'none';
        }
    });
    
    updateNotesCount();
}

// Обновление счетчика заметок
function updateNotesCount() {
    const visibleNotes = document.querySelectorAll('.note-card[style=""], .note-card:not([style])');
    document.getElementById('notesCount').textContent = visibleNotes.length;
}

// Показ уведомлений
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// CSS анимация для удаления
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-100%); }
    }
`;
document.head.appendChild(style);