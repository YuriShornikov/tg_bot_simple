import telebot
import psycopg2
from token_tg import token

bot = telebot.TeleBot(token)

# Подключение к базе данных PostgreSQL и создание таблицы, при отсутствии
conn = psycopg2.connect(database="tg", user="postgres", password="1234", host="localhost", port="5432")
cur = conn.cursor()
cur.execute("""
  CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task TEXT
  );
""")
conn.commit()
cur.close()

# Код чат бота
@bot.message_handler(content_types=['text'])
def start(message):
  if message.text == "/add":
    bot.send_message(message.from_user.id, "Напишите задачу")
    bot.register_next_step_handler(message, add_task)
  elif message.text == "/tsk":
    list_task(message)
  else:
    bot.send_message(message.chat.id, 
    "Привет! Я бот-помощник. Используй команду /add, чтобы добавить задачу, и /tsk, чтобы посмотреть список задач.")

# функция добавления задачи
def add_task(message):
  task = message.text
  try:
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
    conn.commit()
    cur.close()
    bot.send_message(message.from_user.id, "Задача принята и записана")
  except Exception as e:
    bot.send_message(message.from_user.id, "Произошла ошибка")

# функция вывода задач
def list_task(message):
  try:
    cur = conn.cursor()
    cur.execute("SELECT task FROM tasks")
    tasks = cur.fetchall()
    cur.close()
    if tasks:
      task_list = '\n'.join([task[0] for task in tasks])
      bot.send_message(message.from_user.id, f'Ваши задачи:\n{task_list}')
    else:
      bot.send_message(message.from_user.id, 'У вас нет ни одной задачи.')
  except Exception as e:
    bot.send_message(message.from_user.id, 'Произошла ошибка при получении списка задач.')


bot.polling(none_stop=True, interval=1)