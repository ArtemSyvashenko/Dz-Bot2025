# 📦 Посібник із запуску Telegram-бота

## 🛍 Кроки для запуску

### 1. Клонуйте репозиторій

```bash
git clone https://github.com/your-username/your-bot.git
cd your-bot
```

### 2. Перевірте встановлення Python (3.10+)

```bash
python --version
```

### 3. Встановіть залежності

```bash
pip install -r requirements.txt
```

### 4. Створіть файл `config.py`

```python
TOKEN = "токен_вашого_бота"
SUBJECTS = ["math", "eng", "phys", "hist"]
```

### 5. Створіть папку `data/` та додайте JSON-файли з даними предметів

Наприклад `math.json`:

```json
{
  "main": 0,
  "adds": [],
  "done": false,
  "chat_id": null
}
```

### 6. Запустіть бота

```bash
python main.py
```
