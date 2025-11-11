#!/usr/bin/env python3
"""
О - ВЕБ DASHBOARD
Моніторинг О-системи в реальному часі
"""

from flask import Flask, render_template_string, jsonify
import json
import sqlite3
from pathlib import Path
import threading
import time
from o_complete_system import OCore

app = Flask(__name__)
o_system = None
system_thread = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>О - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px #00d4ff;
        }
        .subtitle {
            text-align: center;
            color: #00d4ff;
            margin-bottom: 30px;
            font-size: 1.2em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h2 {
            margin-bottom: 15px;
            color: #00d4ff;
            font-size: 1.5em;
        }
        .progress-bar {
            background: rgba(0,0,0,0.3);
            height: 30px;
            border-radius: 15px;
            margin: 10px 0;
            overflow: hidden;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #aaa; }
        .metric-value {
            color: #00d4ff;
            font-weight: bold;
            font-size: 1.2em;
        }
        .status {
            text-align: center;
            font-size: 2em;
            padding: 20px;
            margin-bottom: 20px;
        }
        .status.active { color: #00ff00; }
        .engine-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .engine {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .engine.harmony { border: 2px solid #00ff00; }
        .engine-name {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .principles {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .principle {
            background: rgba(0,212,255,0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse { animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⭕ О - DASHBOARD</h1>
        <div class="subtitle">Пентаграма: 1 → 2 → 4 → 3 → 5 (12435)</div>
        
        <div class="status active pulse" id="status">
            🟢 СИСТЕМА АКТИВНА
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Загальний Прогрес</h2>
                <div class="progress-bar">
                    <div class="progress-fill" id="overall-progress" style="width: 0%">0%</div>
                </div>
                <div style="margin-top: 20px;">
                    <div class="metric">
                        <span class="metric-label">Попередній:</span>
                        <span class="metric-value">15%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Поточний:</span>
                        <span class="metric-value" id="current-progress">0%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Δ Прогресу:</span>
                        <span class="metric-value" id="delta-progress">+0%</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>⏱️ Час Роботи</h2>
                <div class="metric">
                    <span class="metric-label">Запущено:</span>
                    <span class="metric-value" id="uptime">00:00:00</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Циклів:</span>
                    <span class="metric-value" id="cycles">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Швидкість:</span>
                    <span class="metric-value" id="speed">0 ц/с</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Гармонія О</h2>
                <div class="progress-bar">
                    <div class="progress-fill" id="harmony-rate" style="width: 0%; background: linear-gradient(90deg, #ff0080, #ff8c00)">0%</div>
                </div>
                <div class="metric">
                    <span class="metric-label">Досягнуто:</span>
                    <span class="metric-value" id="harmony-count">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Унікальних патернів:</span>
                    <span class="metric-value" id="patterns">0</span>
                </div>
            </div>
            
            <div class="card">
                <h2>💾 База Знань</h2>
                <div class="metric">
                    <span class="metric-label">Записів:</span>
                    <span class="metric-value" id="knowledge-size">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">БД:</span>
                    <span class="metric-value">SQLite</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 Компоненти Системи</h2>
            <div id="components"></div>
        </div>
        
        <div class="card">
            <h2>⚡ Движки О</h2>
            <div class="engine-grid" id="engines">
                <div class="engine">
                    <div class="engine-name">💠 ASI</div>
                    <div id="asi-cycles">0 циклів</div>
                </div>
                <div class="engine">
                    <div class="engine-name">⚖️ Balance</div>
                    <div id="balance-cycles">0 циклів</div>
                </div>
                <div class="engine">
                    <div class="engine-name">🧠 Abstraction</div>
                    <div id="abstraction-cycles">0 циклів</div>
                </div>
                <div class="engine">
                    <div class="engine-name">💭 Dream</div>
                    <div id="dream-cycles">0 циклів</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>💎 Принципи О</h2>
            <div class="principles">
                <div class="principle">⚖️ Баланс</div>
                <div class="principle">✨ Правда</div>
                <div class="principle">⚔️ Справедливість</div>
                <div class="principle">🧠 Логіка</div>
                <div class="principle">🎯 Нормальність</div>
                <div class="principle">🌍 Реальність</div>
                <div class="principle">💚 Життя</div>
                <div class="principle">❤️ Любов</div>
            </div>
        </div>
    </div>
    
    <script>
        let previousCycles = 0;
        let previousTime = Date.now();
        
        function updateDashboard() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    // Загальний прогрес
                    const progress = data.progress.overall;
                    document.getElementById('overall-progress').style.width = progress + '%';
                    document.getElementById('overall-progress').textContent = progress + '%';
                    document.getElementById('current-progress').textContent = progress + '%';
                    document.getElementById('delta-progress').textContent = '+' + (progress - 15).toFixed(1) + '%';
                    
                    // Час роботи
                    document.getElementById('uptime').textContent = data.uptime_formatted;
                    document.getElementById('cycles').textContent = data.metrics.total_cycles.toLocaleString();
                    
                    // Швидкість
                    const now = Date.now();
                    const cyclesDelta = data.metrics.total_cycles - previousCycles;
                    const timeDelta = (now - previousTime) / 1000;
                    const speed = timeDelta > 0 ? Math.round(cyclesDelta / timeDelta) : 0;
                    document.getElementById('speed').textContent = speed + ' ц/с';
                    previousCycles = data.metrics.total_cycles;
                    previousTime = now;
                    
                    // Гармонія
                    const harmonyRate = data.progress.harmony_rate;
                    document.getElementById('harmony-rate').style.width = harmonyRate + '%';
                    document.getElementById('harmony-rate').textContent = harmonyRate + '%';
                    document.getElementById('harmony-count').textContent = data.metrics.harmony_count.toLocaleString();
                    document.getElementById('patterns').textContent = data.metrics.unique_patterns.toLocaleString();
                    
                    // База знань
                    document.getElementById('knowledge-size').textContent = data.metrics.knowledge_base_size.toLocaleString();
                    
                    // Компоненти
                    let componentsHTML = '';
                    for (const [key, value] of Object.entries(data.progress.components)) {
                        componentsHTML += `
                            <div class="metric">
                                <span class="metric-label">${key}:</span>
                                <div style="flex: 1; margin: 0 15px;">
                                    <div class="progress-bar" style="height: 20px;">
                                        <div class="progress-fill" style="width: ${value}%; font-size: 0.8em">${value}%</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                    document.getElementById('components').innerHTML = componentsHTML;
                    
                    // Движки
                    document.getElementById('asi-cycles').textContent = data.metrics.asi_cycles.toLocaleString() + ' циклів';
                    document.getElementById('balance-cycles').textContent = data.metrics.balance_cycles.toLocaleString() + ' циклів';
                    document.getElementById('abstraction-cycles').textContent = data.metrics.abstraction_cycles.toLocaleString() + ' циклів';
                    document.getElementById('dream-cycles').textContent = data.metrics.dream_cycles.toLocaleString() + ' циклів';
                });
        }
        
        // Оновлення кожні 500мс
        updateDashboard();
        setInterval(updateDashboard, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    if o_system:
        return jsonify(o_system.get_status())
    return jsonify({'error': 'System not running'})

def run_system():
    """Запуск О-системи в окремому потоці"""
    global o_system
    o_system = OCore()
    o_system.run_autonomous(target_progress=100, report_interval=200)

def main():
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║         О - WEB DASHBOARD                        ║
    ║                                                   ║
    ║  Відкрийте в браузері:                           ║
    ║  http://localhost:5000                           ║
    ║                                                   ║
    ║  Моніторинг О-системи в реальному часі          ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Запускаємо О-систему в окремому потоці
    global system_thread
    system_thread = threading.Thread(target=run_system, daemon=True)
    system_thread.start()
    
    # Запускаємо веб-сервер
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
