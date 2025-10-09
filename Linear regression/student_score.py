import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import webbrowser
import os

# Загрузка данных
df = pd.read_csv('student_scores.csv')

# Подготовка данных
X = df[['Hours']]
y = df['Scores']

# Разделение данных
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание и обучение модели
model = LinearRegression()
model.fit(X_train, y_train)

# Предсказания
y_pred = model.predict(X_test)

# Вычисление метрик
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
slope = model.coef_[0]
intercept = model.intercept_

# Вывод результатов в консоль
print("=" * 50)
print("РЕЗУЛЬТАТЫ ЛИНЕЙНОЙ РЕГРЕССИИ")
print("=" * 50)
print(f"R² Score: {r2:.4f}")
print(f"MSE: {mse:.2f}")
print(f"Коэффициент (наклон): {slope:.4f}")
print(f"Пересечение: {intercept:.4f}")
print(f"Уравнение: y = {slope:.2f}x + {intercept:.2f}")
print("=" * 50)

# Подготовка данных для HTML
data_points = []
for _, row in df.iterrows():
    data_points.append(f"{{hours: {row['Hours']}, score: {row['Scores']}}}")
data_js = ",\n            ".join(data_points)

# Подготовка таблицы данных
table_rows = ""
for idx, row in df.iterrows():
    table_rows += f"""
                <tr>
                    <td>{idx + 1}</td>
                    <td>{row['Hours']}</td>
                    <td>{row['Scores']}</td>
                </tr>"""

# Генерация HTML
html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Scores - Linear Regression Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        canvas {{
            max-width: 100%;
            height: auto;
        }}

        .metrics-panel {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .metric-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
        }}

        .metric-title {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        .metric-description {{
            font-size: 0.85em;
            color: #999;
            margin-top: 10px;
        }}

        .info-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-top: 20px;
        }}

        .info-card h3 {{
            color: #333;
            margin-bottom: 15px;
        }}

        .info-card p {{
            color: #666;
            line-height: 1.6;
        }}

        /* Калькулятор предсказаний */
        .predictor-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        .predictor-card h3 {{
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            color: #666;
            margin-bottom: 8px;
            font-weight: 600;
        }}

        .form-group input {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}

        .form-group input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .predict-btn {{
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .predict-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .predict-btn:active {{
            transform: translateY(0);
        }}

        .result-box {{
            margin-top: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
            text-align: center;
            display: none;
        }}

        .result-box.show {{
            display: block;
            animation: slideIn 0.3s ease;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .result-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}

        .result-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}

        /* Таблица данных */
        .data-table-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-top: 20px;
        }}

        .data-table-card h3 {{
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .table-wrapper {{
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            color: #333;
        }}

        tr:hover {{
            background-color: #f5f5f5;
        }}

        tr:nth-child(even) {{
            background-color: #fafafa;
        }}

        tr:nth-child(even):hover {{
            background-color: #f0f0f0;
        }}

        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .stat-box {{
            padding: 15px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
            text-align: center;
        }}

        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}

        @media (max-width: 1024px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}

            .metrics-panel {{
                grid-template-columns: repeat(2, 1fr);
                display: grid;
            }}
        }}

        @media (max-width: 768px) {{
            .metrics-panel {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Student Performance Analysis Report</h1>
        
        <div class="dashboard">
            <div class="chart-container">
                <canvas id="regressionChart"></canvas>
            </div>
            
            <div class="metrics-panel">
                <div class="metric-card">
                    <div class="metric-title">R² Score (Точность)</div>
                    <div class="metric-value">{r2:.4f}</div>
                    <div class="metric-description">Коэффициент детерминации показывает, насколько хорошо модель описывает данные</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">MSE (Средняя квадратичная ошибка)</div>
                    <div class="metric-value">{mse:.2f}</div>
                    <div class="metric-description">Средняя квадратичная ошибка предсказаний модели</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Уравнение</div>
                    <div class="metric-value" style="font-size: 1.5em;">y = {slope:.2f}x + {intercept:.2f}</div>
                    <div class="metric-description">Линейное уравнение регрессии</div>
                </div>
            </div>
        </div>

        <!-- Калькулятор предсказаний -->
        <div class="predictor-card">
            <h3>🎯 Предсказать свою оценку</h3>
            <div class="form-group">
                <label for="hoursInput">Сколько часов вы планируете заниматься?</label>
                <input type="number" id="hoursInput" placeholder="Введите количество часов (например, 7.5)" step="0.1" min="0" max="20">
            </div>
            <button class="predict-btn" onclick="predictScore()">🔮 Предсказать оценку</button>
            <div class="result-box" id="resultBox">
                <div class="result-label">Предсказанная оценка:</div>
                <div class="result-value" id="predictedScore">--</div>
            </div>
        </div>

        <!-- Таблица данных -->
        <div class="data-table-card">
            <h3>📋 Данные для обучения модели</h3>
            <div class="stats-summary">
                <div class="stat-box">
                    <div class="stat-label">Всего записей</div>
                    <div class="stat-value">{len(df)}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Мин. часов</div>
                    <div class="stat-value">{df['Hours'].min():.1f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Макс. часов</div>
                    <div class="stat-value">{df['Hours'].max():.1f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Средняя оценка</div>
                    <div class="stat-value">{df['Scores'].mean():.1f}</div>
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Часы обучения</th>
                            <th>Оценка</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="info-card">
            <h3>ℹ️ Информация о данных</h3>
            <p>Всего точек данных: <strong>{len(df)}</strong></p>
            <p>Данные для обучения: <strong>{len(X_train)}</strong> | Данные для тестирования: <strong>{len(X_test)}</strong></p>
            <p>Чтобы добавить новые данные, отредактируйте файл <strong>student_scores.csv</strong> и запустите скрипт снова.</p>
        </div>
    </div>

    <script>
        // Данные из CSV
        let data = [
            {data_js}
        ];

        let canvas = document.getElementById('regressionChart');
        let ctx = canvas.getContext('2d');

        function resizeCanvas() {{
            const container = canvas.parentElement;
            canvas.width = container.clientWidth - 60;
            canvas.height = 500;
        }}

        // Параметры модели из Python
        const slope = {slope};
        const intercept = {intercept};

        // Функция предсказания оценки
        function predictScore() {{
            const hoursInput = document.getElementById('hoursInput');
            const hours = parseFloat(hoursInput.value);
            
            if (isNaN(hours) || hours < 0) {{
                alert('⚠️ Пожалуйста, введите корректное количество часов (не менее 0)');
                return;
            }}
            
            if (hours > 20) {{
                alert('⚠️ Введенное значение слишком большое. Обычно студенты занимаются не более 20 часов в день.');
                return;
            }}
            
            // Вычисление предсказания по формуле линейной регрессии
            const predictedScore = slope * hours + intercept;
            
            // Ограничение оценки в разумных пределах (0-100)
            const finalScore = Math.max(0, Math.min(100, predictedScore));
            
            // Отображение результата
            const resultBox = document.getElementById('resultBox');
            const scoreElement = document.getElementById('predictedScore');
            
            scoreElement.textContent = finalScore.toFixed(2);
            resultBox.classList.add('show');
            
            // Добавление эмодзи в зависимости от оценки
            let emoji = '';
            if (finalScore >= 90) emoji = '🌟';
            else if (finalScore >= 75) emoji = '👍';
            else if (finalScore >= 60) emoji = '✅';
            else emoji = '📚';
            
            scoreElement.textContent = emoji + ' ' + finalScore.toFixed(2);
        }}

        // Обработка Enter в поле ввода
        document.getElementById('hoursInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                predictScore();
            }}
        }});

        // Функция для отрисовки графика
        function drawChart() {{
            resizeCanvas();
            
            const width = canvas.width;
            const height = canvas.height;
            const padding = 50;
            
            // Очистка canvas
            ctx.clearRect(0, 0, width, height);
            
            // Определение масштаба
            const maxX = Math.max(...data.map(p => p.hours)) + 0.5;
            const maxY = Math.max(...data.map(p => p.score)) + 5;
            const minX = Math.min(...data.map(p => p.hours)) - 0.5;
            const minY = Math.min(...data.map(p => p.score)) - 5;
            
            const scaleX = (width - 2 * padding) / (maxX - minX);
            const scaleY = (height - 2 * padding) / (maxY - minY);
            
            // Функция для преобразования координат
            const toCanvasX = (x) => padding + (x - minX) * scaleX;
            const toCanvasY = (y) => height - padding - (y - minY) * scaleY;
            
            // Рисование осей
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(padding, height - padding);
            ctx.lineTo(width - padding, height - padding);
            ctx.moveTo(padding, padding);
            ctx.lineTo(padding, height - padding);
            ctx.stroke();
            
            // Метки осей
            ctx.fillStyle = '#333';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Hours (Часы обучения)', width / 2, height - 10);
            ctx.save();
            ctx.translate(15, height / 2);
            ctx.rotate(-Math.PI / 2);
            ctx.fillText('Scores (Оценки)', 0, 0);
            ctx.restore();
            
            // Рисование линии регрессии
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 4;
            ctx.setLineDash([]);
            ctx.beginPath();
            const startX = minX;
            const startY = slope * startX + intercept;
            const endX = maxX;
            const endY = slope * endX + intercept;
            ctx.moveTo(toCanvasX(startX), toCanvasY(startY));
            ctx.lineTo(toCanvasX(endX), toCanvasY(endY));
            ctx.stroke();
            
            // Рисование точек данных
            data.forEach(point => {{
                ctx.fillStyle = '#667eea';
                ctx.beginPath();
                ctx.arc(toCanvasX(point.hours), toCanvasY(point.score), 7, 0, 2 * Math.PI);
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
            }});
            
            // Подписи делений на оси X
            ctx.fillStyle = '#666';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            for (let i = 0; i <= 10; i += 1) {{
                if (i >= Math.floor(minX) && i <= Math.ceil(maxX)) {{
                    ctx.fillText(i, toCanvasX(i), height - padding + 20);
                }}
            }}
            
            // Подписи делений на оси Y
            ctx.textAlign = 'right';
            for (let i = 0; i <= 100; i += 10) {{
                if (i >= Math.floor(minY) && i <= Math.ceil(maxY)) {{
                    ctx.fillText(i, padding - 10, toCanvasY(i) + 5);
                }}
            }}
        }}

        // Инициализация
        window.addEventListener('resize', drawChart);
        drawChart();
    </script>
</body>
</html>"""

# Сохранение HTML файла
html_filename = 'regression_report.html'
with open(html_filename, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ HTML отчет создан: {html_filename}")
print("🌐 Открываю отчет в браузере...")

# Открытие HTML файла в браузере
webbrowser.open('file://' + os.path.realpath(html_filename))

print("\n💡 Для обновления данных:")
print("   1. Отредактируйте файл student_scores.csv")
print("   2. Запустите этот скрипт снова")
print("=" * 50)