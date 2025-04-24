import torch
from main import MyModel

def chat_with_model(model_path):
    model = MyModel()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    print("Чат-бот готовий! Введіть 'exit', щоб завершити.")
    while True:
        user_input = input("Введіть дані (784 значення через кому): ")
        if user_input.lower() == 'exit':
            break
        try:
            data = torch.tensor([float(x) for x in user_input.split(',')]).view(1, -1)
            output = model(data)
            prediction = torch.argmax(output, dim=1).item()
            print(f"Модель передбачає: {prediction}")
        except Exception as e:
            print(f"Помилка: {e}")

if __name__ == "__main__":
    MODEL_PATH = "models/my_model.pth"
    chat_with_model(MODEL_PATH)