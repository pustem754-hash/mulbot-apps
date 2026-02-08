let display = document.getElementById('result');
let currentInput = '';

function appendToDisplay(value) {
    currentInput += value;
    display.value = currentInput;
}

function clearDisplay() {
    currentInput = '';
    display.value = '';
}

function deleteLast() {
    currentInput = currentInput.slice(0, -1);
    display.value = currentInput;
}

async function calculate() {
    if (currentInput === '') return;
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                expression: currentInput
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            display.value = 'Ошибка';
            currentInput = '';
            setTimeout(() => {
                display.value = '';
            }, 2000);
        } else {
            display.value = data.result;
            currentInput = data.result.toString();
        }
    } catch (error) {
        display.value = 'Ошибка';
        currentInput = '';
        setTimeout(() => {
            display.value = '';
        }, 2000);
    }
}

// Поддержка клавиатуры
document.addEventListener('keydown', function(event) {
    const key = event.key;
    
    if (key >= '0' && key <= '9') {
        appendToDisplay(key);
    } else if (key === '+' || key === '-') {
        appendToDisplay(key);
    } else if (key === '*') {
        appendToDisplay('×');
    } else if (key === '/') {
        event.preventDefault();
        appendToDisplay('÷');
    } else if (key === '.') {
        appendToDisplay('.');
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    } else if (key === 'Backspace') {
        deleteLast();
    }
});