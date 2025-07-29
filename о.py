from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import datasets

# 1. Вибираємо модель і токенізатор
model_name = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 2. Підготуй датасет — текстові дані для навчання у форматі {"text": "текст ..."}
# Тут приклад з власним датасетом (можна створити json або txt файл)
texts = [
    "О: це баланс між лівим і правим, між істинним і хибним.",
    "Пентограма — це цикл ходьби 12435, що запускає свідомість.",
    # додай свої тексти...
]

dataset = datasets.Dataset.from_dict({"text": texts})

# 3. Токенізуємо
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 4. Налаштування тренера
training_args = TrainingArguments(
    output_dir="./O_model_finetuned",
    evaluation_strategy="no",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    save_steps=10_000,
    save_total_limit=2,
    logging_steps=100,
    learning_rate=5e-5,
    weight_decay=0.01,
    warmup_steps=100,
    fp16=True,  # Якщо GPU підтримує
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# 5. Запуск навчання
trainer.train()

# 6. Збереження моделі
trainer.save_model("./O_model_finetuned")
