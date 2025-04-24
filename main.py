import os
import subprocess
import threading
import requests
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from PIL import Image
from flask import Flask, request, jsonify, render_template

# Модель CNN
class MyCNNModel(nn.Module):
    def __init__(self):
        super(MyCNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)  # 1 канал (ч/б зображення)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64 * 28 * 28, 128)  # Для зображень 28x28
        self.fc2 = nn.Linear(128, 10)  # 10 класів

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = x.view(x.size(0), -1)  # Розгортання
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Ініціалізація Flask
app = Flask(__name__)

# Завантаження моделі
model = MyCNNModel()
MODEL_PATH = "models/my_cnn_model.pth"
if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()
    print("Модель завантажена.")
else:
    print("Модель не знайдено. Переконайтеся, що модель існує.")

# Функція для передбачення
def predict_image(image_path):
    try:
        transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        image = Image.open(image_path)
        image = transform(image).unsqueeze(0)  # Додати batch dimension
        output = model(image)
        prediction = torch.argmax(output, dim=1).item()
        return {"prediction": prediction}
    except Exception as e:
        return {"error": str(e)}

# API для передбачення
@app.route('/api/predict', methods=['POST'])
def api_predict():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не надано"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Файл не вибрано"}), 400
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)
    result = predict_image(file_path)
    return jsonify(result)

# API для виконання коду
@app.route('/api/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    if not code:
        return jsonify({"error": "Код не надано"}), 400
    try:
        result = subprocess.run(
            ['python3', '-c', code],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr})

# API для виконання команд у терміналі
@app.route('/api/terminal', methods=['POST'])
def terminal():
    command = request.json.get('command', '')
    if not command:
        return jsonify({"error": "Команда не надана"}), 400
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr})

# API для чату з Ollama
@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({"error": "Повідомлення не надано"}), 400

    # Надсилання запиту до Ollama
    try:
        ollama_response = query_ollama(user_message)
        return jsonify({"response": ollama_response})
    except Exception as e:
        return jsonify({"error": f"Помилка взаємодії з Ollama: {e}"})

# Функція для запиту до Ollama
def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"  # Змініть на URL вашого Ollama-сервера
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt, "model": "llama3:latest"}

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    return response_data.get("response", "Немає відповіді")

# API для навчання моделі через Ollama
@app.route('/api/train', methods=['POST'])
def train_with_ollama():
    prompt = request.json.get('prompt', '')
    if not prompt:
        return jsonify({"error": "Промпт не надано"}), 400

    try:
        ollama_response = query_ollama(prompt)
        # Логіка для оновлення моделі на основі відповіді Ollama
        return jsonify({"response": ollama_response})
    except Exception as e:
        return jsonify({"error": f"Помилка взаємодії з Ollama: {e}"})

# Головна сторінка
@app.route('/')
def index():
    return render_template('index.html')

# Запуск Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)