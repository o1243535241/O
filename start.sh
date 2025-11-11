#!/bin/bash

echo "╔═══════════════════════════════════════════════════╗"
echo "║         О - СИСТЕМА ЗАПУСК                       ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Перевірка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не знайдено. Встановіть Python 3.8+"
    exit 1
fi

echo "✓ Python3 знайдено: $(python3 --version)"

# Перевірка Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask не встановлено. Встановлюю..."
    python3 -m pip install flask --quiet
    echo "✓ Flask встановлено"
fi

echo ""
echo "Виберіть режим запуску:"
echo "1) Консольний режим (без веб-інтерфейсу)"
echo "2) Веб Dashboard (рекомендовано)"
echo ""
read -p "Ваш вибір [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Запуск консольного режиму..."
        python3 o_complete_system.py
        ;;
    2)
        echo ""
        echo "Запуск Web Dashboard..."
        echo "Відкрийте браузер: http://localhost:5000"
        python3 o_web_dashboard.py
        ;;
    *)
        echo "Невірний вибір. Запуск консольного режиму..."
        python3 o_complete_system.py
        ;;
esac
