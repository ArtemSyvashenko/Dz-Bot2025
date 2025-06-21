Як запустити бота
Клонуйте репозиторій:

bash
Копіювати
Редагувати
git clone https://github.com/<your-username>/<your-bot-repo>.git
cd <folder-name>
Переконайтесь, що встановлено Python 3.10+:

bash
Копіювати
Редагувати
python --version
Встановіть залежності:

bash
Копіювати
Редагувати
pip install -r requirements.txt
Створіть файл config.py:

python
Копіювати
Редагувати
TOKEN = "токен_вашого_бота"
SUBJECTS = ["math", "eng", "phys", "hist"]
Створіть папку data/ і додайте JSON-файли з предметами, наприклад math.json:

json
Копіювати
Редагувати
{
  "main": 0,
  "adds": [],
  "done": false,
  "chat_id": null
}
Запустіть бота:

bash
Копіювати
Редагувати
python main.py