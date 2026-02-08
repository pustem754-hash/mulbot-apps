let display = document.getElementById('display');
let result = document.getElementById('result');
let currentExpression = '';
let lastResult = '0';

function updateDisplay() {
    display.value = currentExpression;
    result.textContent = lastResult;
}

function appendNumber(num) {
    currentExpression += num;
    updateDisplay();
}

function appendOperator(op) {
    if (op === '^') {
        currentExpression += '**';
    } else {
        currentExpression += op;
    }
    updateDisplay();
}

function appendFunction(func) {
    currentExpression += func;
    updateDisplay();
}

function appendConstant(constant) {
    currentExpression += constant;
    updateDisplay();
}

function clearAll() {
    currentExpression = '';
    lastResult = '0';
    updateDisplay();
}

function clearEntry() {
    currentExpression = '';
    updateDisplay();
}

function deleteLast() {
    currentExpression = currentExpression.slice(0, -1);
    updateDisplay();
}

function calculate() {
    if (!currentExpression) return;
    
    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            expression: currentExpression
        })
    })
    .then(response => response.json())
    .then(data => {
        lastResult = data.result;
        updateDisplay();
        
        // Если результат не содержит ошибку, заменяем выражение результатом
        if (!data.result.startsWith('Ошибка')) {
            currentExpression = data.result;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        lastResult = 'Ошибка соединения';
        updateDisplay();
    });
}

// Обработка клавиатуры
document.addEventListener('keydown', function(event) {
    const key = event.key;
    
    if (key >= '0' && key <= '9') {
        appendNumber(key);
    } else if (key === '.') {
        appendNumber('.');
    } else if (key === '+') {
        appendOperator('+');
    } else if (key === '-') {
        appendOperator('-');
    } else if (key === '*') {
        appendOperator('*');
    } else if (key === '/') {
        event.preventDefault();
        appendOperator('/');
    } else if (key === '(') {
        appendOperator('(');
    } else if (key === ')') {
        appendOperator(')');
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Escape') {
        clearAll();
    } else if (key === 'Backspace') {
        event.preventDefault();
        deleteLast();
    }
});

// Инициализация
updateDisplay();