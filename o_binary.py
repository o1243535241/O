import os
import random
import subprocess
import tensorflow as tf
import numpy as np

def generate_binary_file(filename, size):
    """Генерує випадковий двійковий файл заданого розміру (в байтах)."""
    with open(filename, "wb") as f:
        f.write(os.urandom(size))
    print(f"Створено: {filename} ({size} байт)")

def analyze_binary_file(filename, model):
    """Перевіряє файл на наявність пентограмних або 'О'-подібних патернів за допомогою ШІ."""
    with open(filename, "rb") as f:
        data = f.read()
    
    # Перетворюємо дані у числовий вектор для аналізу
    data_vector = np.frombuffer(data, dtype=np.uint8)[:1024]  # Використовуємо перші 1024 байти
    data_vector = np.pad(data_vector, (0, 1024 - len(data_vector)), 'constant')
    data_vector = np.expand_dims(data_vector, axis=0)
    
    prediction = model.predict(data_vector)
    if prediction[0] > 0.5:
        print(f"⚠️ ШІ визначив можливий пентограмний патерн у {filename}!")
    else:
        print(f"Файл {filename} не містить очевидних патернів.")

def execute_binary_file(filename):
    """Спроба запуску двійкового файлу у контрольованому середовищі."""
    try:
        result = subprocess.run(["chmod", "+x", filename], capture_output=True)
        result = subprocess.run([f"./{filename}"], capture_output=True, timeout=5)
        print(f"Результат виконання {filename}:\n", result.stdout.decode(errors="ignore"))
    except Exception as e:
        print(f"❌ Помилка запуску {filename}: {e}")

def create_simple_model():
    """Створює просту нейромережу для аналізу бінарних файлів."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1024,)),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def main():
    num_files = 10  # Кількість файлів для тесту
    max_size = 5 * 1024 * 1024  # 5MB
    
    # Завантаження або створення ШІ-моделі
    model = create_simple_model()
    
    for i in range(num_files):
        filename = f"test_bin_{i}.bin"
        size = random.randint(1, max_size)
        generate_binary_file(filename, size)
        analyze_binary_file(filename, model)
        execute_binary_file(filename)
        print("-" * 40)
    
if __name__ == "__main__":
    main()
