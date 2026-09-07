from datetime import datetime
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Создаем само приложение Flask
app = Flask(__name__)

# Подключаем локальную базу данных SQLite, она сама создаст файл site.db в папке проекта
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)


# Описываем структуру таблицы для наших задач (модель данных)
class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)  # Уникальный номер задачи (айдишник)
  content = db.Column(
      db.String(200), nullable=False
  )  # Текст задачи (обязательный, до 200 символов)
  date_created = db.Column(
      db.DateTime, default=datetime.utcnow
  )  # Дата и время создания записи

  def __repr__(self):
    return "<Task %r>" % self.id


# Главная страница: тут смотрим список задач и добавляем новые
@app.route("/", methods=["POST", "GET"])
def index():
  # Если пользователь отправил форму (нажал кнопку "Add Task")
  if request.method == "POST":
    task_content = request.form["content"]  # Забираем текст из формы
    new_task = Todo(content=task_content)  # Создаем объект задачи

    try:
      db.session.add(new_task)  # Добавляем в сессию бд
      db.session.commit()  # Сохраняем изменения в базе
      return redirect("/")  # Перенаправляем обратно на главную
    except:
      return "There was an issue adding your task"
  else:
    # Если это просто заход на страницу (GET): достаем все задачи из базы по дате
    tasks = Todo.query.order_by(Todo.date_created).all()
    # Передаем список задач в HTML-шаблон index.html
    return render_template("index.html", tasks=tasks)


# Удаление задачи по её уникальному ID
@app.route("/delete/<int:id>")
def delete(id):
  task_to_delete = Todo.query.get_or_404(
      id
  )  # Ищем задачу или кидаем 404, если её нет

  try:
    db.session.delete(task_to_delete)  # Удаляем из базы
    db.session.commit()  # Подтверждаем удаление
    return redirect("/")
  except:
    return "There was a problem deleting that task"


# Страница редактирования (обновления) задачи
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
  task = Todo.query.get_or_404(id)  # Находим нужную задачу

  if request.method == "POST":
    task.content = request.form["content"]  # Меняем текст на новый из формы
    try:
      db.session.commit()  # Сохраняем отредактированное
      return redirect("/")
    except:
      return "There was an issue updating your task"
  else:
    # Открываем форму обновления и передаем туда текущую задачу
    return render_template("update.html", task=task)


# Запуск локального сервера разработки
if __name__ == "__main__":
  with app.app_context():
    db.create_all()  # Создаем таблицы в БД перед стартом, если их еще не было
  app.run(
      debug=True
  )  # Стартуем сервер с автоперезагрузкой при изменении кода (debug режим)
