let options = [];
let isSpinning = false;

// Цвета для секторов рулетки
const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
    '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
    '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
];

function addOption() {
    const input = document.getElementById('optionInput');
    const option = input.value.trim();
    
    if (option && !options.includes(option) && options.length < 12) {
        options.push(option);
        input.value = '';
        updateOptionsDisplay();
        updateSpinButton();
        drawWheel();
    }
}

function removeOption(index) {
    options.splice(index, 1);
    updateOptionsDisplay();
    updateSpinButton();
    drawWheel();
}

function clearOptions() {
    options = [];
    updateOptionsDisplay();
    updateSpinButton();
    drawWheel();
    hideResult();
}

function updateOptionsDisplay() {
    const container = document.getElementById('optionsList');
    container.innerHTML = '';
    
    options.forEach((option, index) => {
        const tag = document.createElement('div');
        tag.className = 'option-tag';
        tag.innerHTML = `
            <span>${option}</span>
            <button class="remove-option" onclick="removeOption(${index})">×</button>
        `;
        container.appendChild(tag);
    });
}

function updateSpinButton() {
    const spinBtn = document.getElementById('spinBtn');
    spinBtn.disabled = options.length < 2 || isSpinning;
}

function drawWheel() {
    const canvas = document.getElementById('rouletteWheel');
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 140;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (options.length === 0) {
        // Рисуем пустое колесо
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.fillStyle = '#f0f0f0';
        ctx.fill();
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 3;
        ctx.stroke();
        
        ctx.fillStyle = '#999';
        ctx.font = '18px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Добавьте варианты', centerX, centerY);
        return;
    }
    
    const anglePerSection = (2 * Math.PI) / options.length;
    
    options.forEach((option, index) => {
        const startAngle = index * anglePerSection;
        const endAngle = startAngle + anglePerSection;
        
        // Рисуем сектор
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.closePath();
        ctx.fillStyle = colors[index % colors.length];
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Добавляем текст
        const textAngle = startAngle + anglePerSection / 2;
        const textX = centerX + Math.cos(textAngle) * (radius * 0.7);
        const textY = centerY + Math.sin(textAngle) * (radius * 0.7);
        
        ctx.save();
        ctx.translate(textX, textY);
        ctx.rotate(textAngle);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 2;
        ctx.fillText(option.length > 10 ? option.substring(0, 8) + '...' : option, 0, 5);
        ctx.restore();
    });
    
    // Рисуем центральный круг
    ctx.beginPath();
    ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
    ctx.fillStyle = '#333';
    ctx.fill();
}

async function spinRoulette() {
    if (isSpinning || options.length < 2) return;
    
    isSpinning = true;
    updateSpinButton();
    hideResult();
    
    try {
        const response = await fetch('/spin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ options: options })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Анимация вращения
        const wheel = document.getElementById('rouletteWheel');
        const finalRotation = data.rotation;
        
        wheel.style.transform = `rotate(${finalRotation}deg)`;
        
        // Показываем результат через 3 секунды (время анимации)
        setTimeout(() => {
            showResult(data.winner);
            isSpinning = false;
            updateSpinButton();
        }, 3000);
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при вращении рулетки');
        isSpinning = false;
        updateSpinButton();
    }
}

function showResult(winner) {
    const resultDiv = document.getElementById('result');
    const winnerText = document.getElementById('winnerText');
    
    winnerText.textContent = winner;
    resultDiv.classList.remove('hidden');
    
    setTimeout(() => {
        resultDiv.classList.add('show');
        resultDiv.classList.add('bounce');
    }, 100);
}

function hideResult() {
    const resultDiv = document.getElementById('result');
    resultDiv.classList.remove('show', 'bounce');
    resultDiv.classList.add('hidden');
}

// Обработчик Enter для поля ввода
document.getElementById('optionInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addOption();
    }
});

// Инициализация
drawWheel();