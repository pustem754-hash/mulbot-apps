class PixelEditor {
    constructor() {
        this.grid = Array(32).fill().map(() => Array(32).fill('transparent'));
        this.currentTool = 'pencil';
        this.currentColor = '#000000';
        this.isDrawing = false;
        
        this.initCanvas();
        this.initEventListeners();
    }
    
    initCanvas() {
        const canvas = document.getElementById('canvas');
        canvas.innerHTML = '';
        
        for (let y = 0; y < 32; y++) {
            for (let x = 0; x < 32; x++) {
                const pixel = document.createElement('div');
                pixel.className = 'pixel';
                pixel.dataset.x = x;
                pixel.dataset.y = y;
                
                pixel.addEventListener('mousedown', (e) => this.startDrawing(e));
                pixel.addEventListener('mouseenter', (e) => this.draw(e));
                pixel.addEventListener('mouseup', () => this.stopDrawing());
                
                canvas.appendChild(pixel);
            }
        }
        
        // Предотвращаем перетаскивание
        canvas.addEventListener('dragstart', e => e.preventDefault());
        canvas.addEventListener('selectstart', e => e.preventDefault());
    }
    
    initEventListeners() {
        // Инструменты
        document.querySelectorAll('.tool').forEach(tool => {
            tool.addEventListener('click', (e) => {
                document.querySelectorAll('.tool').forEach(t => t.classList.remove('active'));
                tool.classList.add('active');
                this.currentTool = tool.dataset.tool;
            });
        });
        
        // Палитра
        document.querySelectorAll('.color-item').forEach(colorItem => {
            colorItem.addEventListener('click', (e) => {
                document.querySelectorAll('.color-item').forEach(c => c.classList.remove('selected'));
                colorItem.classList.add('selected');
                this.currentColor = colorItem.dataset.color;
                document.getElementById('selected-color').style.backgroundColor = this.currentColor;
            });
        });
        
        // Первый цвет по умолчанию
        document.querySelector('.color-item').classList.add('selected');
        
        // Кнопки действий
        document.getElementById('clear').addEventListener('click', () => this.clearCanvas());
        document.getElementById('download').addEventListener('click', () => this.downloadImage());
        
        // Глобальные события мыши
        document.addEventListener('mouseup', () => this.stopDrawing());
        document.addEventListener('mouseleave', () => this.stopDrawing());
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        this.draw(e);
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const x = parseInt(e.target.dataset.x);
        const y = parseInt(e.target.dataset.y);
        
        if (x === undefined || y === undefined) return;
        
        if (this.currentTool === 'pencil') {
            this.grid[y][x] = this.currentColor;
            e.target.style.backgroundColor = this.currentColor;
        } else if (this.currentTool === 'eraser') {
            this.grid[y][x] = 'transparent';
            e.target.style.backgroundColor = 'white';
        }
    }
    
    stopDrawing() {
        this.isDrawing = false;
    }
    
    clearCanvas() {
        if (confirm('Вы уверены, что хотите очистить холст?')) {
            this.grid = Array(32).fill().map(() => Array(32).fill('transparent'));
            document.querySelectorAll('.pixel').forEach(pixel => {
                pixel.style.backgroundColor = 'white';
            });
        }
    }
    
    async downloadImage() {
        try {
            const response = await fetch('/save_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    grid: this.grid
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'pixel_art.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                alert('Ошибка при сохранении изображения');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка при сохранении изображения');
        }
    }
}

// Инициализация редактора
document.addEventListener('DOMContentLoaded', () => {
    new PixelEditor();
});