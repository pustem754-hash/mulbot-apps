class RouletteApp {
    constructor() {
        this.options = this.loadOptions();
        this.colors = [
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7',
            '#dda0dd', '#98d8c8', '#ffaaa5', '#ff7675', '#a29bfe',
            '#fd79a8', '#fdcb6e'
        ];
        this.canvas = document.getElementById('wheel');
        this.ctx = this.canvas.getContext('2d');
        this.isSpinning = false;
        
        this.initEventListeners();
        this.updateUI();
        this.drawWheel();
    }

    initEventListeners() {
        document.getElementById('addBtn').addEventListener('click', () => this.addOption());
        document.getElementById('optionInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addOption();
        });
        document.getElementById('spinBtn').addEventListener('click', () => this.spinWheel());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());
        document.getElementById('closeModal').addEventListener('click', () => this.closeModal());
        
        // Закрытие модального окна по клику вне его
        document.getElementById('resultModal').addEventListener('click', (e) => {
            if (e.target.id === 'resultModal') this.closeModal();
        });
    }

    addOption() {
        const input = document.getElementById('optionInput');
        const option = input.value.trim();
        
        if (!option) {
            this.showNotification('Введите вариант!', 'error');
            return;
        }
        
        if (this.options.length >= 12) {
            this.showNotification('Максимум 12 вариантов!', 'error');
            return;
        }
        
        if (this.options.includes(option)) {
            this.showNotification('Этот вариант уже добавлен!', 'error');
            return;
        }
        
        this.options.push(option);
        input.value = '';
        this.saveOptions();
        this.updateUI();
        this.drawWheel();
        this.showNotification('Вариант добавлен! 🎉');
    }

    removeOption(index) {
        this.options.splice(index, 1);
        this.saveOptions();
        this.updateUI();
        this.drawWheel();
    }

    clearAll() {
        if (this.options.length === 0) return;
        
        if (confirm('Удалить все варианты?')) {
            this.options = [];
            this.saveOptions();
            this.updateUI();
            this.drawWheel();
            this.showNotification('Все варианты удалены! 🗑️');
        }
    }

    updateUI() {
        const optionsList = document.getElementById('optionsList');
        const optionCount = document.getElementById('optionCount');
        const spinBtn = document.getElementById('spinBtn');
        
        // Обновляем счетчик
        optionCount.textContent = this.options.length;
        
        // Обновляем кнопку вращения
        spinBtn.disabled = this.options.length < 2 || this.isSpinning;
        
        // Обновляем список
        optionsList.innerHTML = '';
        this.options.forEach((option, index) => {
            const li = document.createElement('li');
            li.className = 'option-item';
            li.style.borderLeftColor = this.colors[index % this.colors.length];
            
            li.innerHTML = `
                <span class="option-text">${option}</span>
                <button class="remove-btn" onclick="app.removeOption(${index})">
                    ✕
                </button>
            `;
            
            optionsList.appendChild(li);
        });
    }

    drawWheel() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = 140;
        
        // Очищаем canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.options.length === 0) {
            // Рисуем пустое колесо
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            this.ctx.fillStyle = '#ecf0f1';
            this.ctx.fill();
            this.ctx.strokeStyle = '#bdc3c7';
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
            
            // Текст
            this.ctx.fillStyle = '#95a5a6';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('Добавьте варианты', centerX, centerY - 10);
            this.ctx.fillText('для начала!', centerX, centerY + 15);
            return;
        }
        
        const anglePerSegment = (2 * Math.PI) / this.options.length;
        
        // Рисуем сегменты
        this.options.forEach((option, index) => {
            const startAngle = index * anglePerSegment;
            const endAngle = startAngle + anglePerSegment;
            
            // Рисуем сегмент
            this.ctx.beginPath();
            this.ctx.arc(centerX, centerY, radius, startAngle, endAngle);
            this.ctx.lineTo(centerX, centerY);
            this.ctx.fillStyle = this.colors[index % this.colors.length];
            this.ctx.fill();
            this.ctx.strokeStyle = '#fff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Добавляем текст
            const textAngle = startAngle + anglePerSegment / 2;
            const textX = centerX + Math.cos(textAngle) * (radius * 0.7);
            const textY = centerY + Math.sin(textAngle) * (radius * 0.7);
            
            this.ctx.save();
            this.ctx.translate(textX, textY);
            this.ctx.rotate(textAngle + Math.PI / 2);
            this.ctx.fillStyle = '#fff';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(option, 0, 0);
            this.ctx.restore();
        });
        
        // Рисуем центральный круг
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.fill();
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
    }

    async spinWheel() {
        if (this.isSpinning || this.options.length < 2) return;
        
        this.isSpinning = true;
        document.getElementById('spinBtn').disabled = true;
        
        try {
            const response = await fetch('/spin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ options: this.options })
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.showNotification(data.error, 'error');
                return;
            }
            
            // Анимация вращения
            this.canvas.style.transform = `rotate(${data.rotation}deg)`;
            
            // Показываем результат через 4 секунды
            setTimeout(() => {
                this.showWinner(data.winner);
                this.isSpinning = false;
                document.getElementById('spinBtn').disabled = false;
            }, 4000);
            
        } catch (error) {
            console.error('Ошибка при вращении:', error);
            this.showNotification('Ошибка сервера!', 'error');
            this.isSpinning = false;
            document.getElementById('spinBtn').disabled = false;
        }
    }

    showWinner(winner) {
        document.getElementById('winnerText').textContent = winner;
        document.getElementById('resultModal').style.display = 'block';
    }

    closeModal() {
        document.getElementById('resultModal').style.display = 'none';
    }

    showNotification(message, type = 'success') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            z-index: 1001;
            animation: slideInRight 0.3s ease;
            max-width: 300px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        `;
        
        notification.style.background = type === 'error' 
            ? 'linear-gradient(45deg, #e74c3c, #c0392b)' 
            : 'linear-gradient(45deg, #2ecc71, #27ae60)';
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Удаляем через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    saveOptions() {
        localStorage.setItem('rouletteOptions', JSON.stringify(this.options));
    }

    loadOptions() {
        const saved = localStorage.getItem('rouletteOptions');
        return saved ? JSON.parse(saved) : [];
    }
}

// Добавляем CSS для анимаций уведомлений
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Инициализируем приложение
const app = new RouletteApp();