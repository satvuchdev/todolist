# 📝 ToDoList GUI (PySide6)

Простое приложение **ToDo-лист** с графическим интерфейсом на **PySide6**, использующее **SQLite** для хранения данных.  
Проект поддерживает пользователей, списки задач, категории, подзадачи, комментарии и профиль.  
Основано на консольной версии (`main.py`) и расширено интерфейсом (`gui.py`).

Автор: **satvuchdev**

---

## 🚀 Возможности

- 🔐 Регистрация и вход пользователей  
- 🗂️ Списки задач  
- ✅ Добавление и отметка задач как выполненных (двойным кликом)  
- 🗒️ Подзадачи и комментарии  
- 🏷️ Категории  
- 👤 Профиль пользователя и смена пароля  
- 💾 Хранение данных в SQLite (файл `todolist.db` создаётся автоматически)

---

## 🧩 Установка и запуск (РУССКИЙ)

### 1️⃣ Установи Python
Требуется **Python 3.9 или выше**.  
Проверь версию:
```bash
python --version
```

### 2️⃣ Установи зависимости
``` bash
pip install PySide6
```

### 3️⃣ Структура проекта
📦 todolist_app/
- ┣ 📜 main.py                # Бэкенд: база данных и логика
- ┣ 📜 gui_full_checkable.py  # Фронтенд: графический интерфейс PySide6
- ┗ 🗄️ todolist.db            # База SQLite (создаётся автоматически)

### 4️⃣ Запуск приложения
``` bash
python gui.py
```

### 5️⃣ Использование
- Введите email и пароль, чтобы войти, или зарегистрируйтесь.
- Вкладка Задачи — создание списков и задач, двойной клик отмечает задачу выполненной.
- Вкладка Категории — создание собственных категорий.
- Вкладка Профиль — изменение имени, email, пароля и выход из системы.
- Все изменения сохраняются автоматически в todolist.db.


# 📝 ToDoList GUI (PySide6)

A simple ToDo list application with a graphical interface written in PySide6, using SQLite for data storage.

The project supports users, task lists, categories, subtasks, comments, and profiles.

Based on the console version (`main.py`) and extended by the interface (`gui.py`).

Author: **satvuchdev**

---

## 🚀 Features

- 🔐 User Registration and Login
- 🗂️ Todo Lists
- ✅ Adding and Marking Tasks as Completed (Double-Click)
- 🗒️ Subtasks and Comments
- 🏷️ Categories
- 👤 User Profile and Password Change
- 💾 Data Storage in SQLite (the `todolist.db` file is created automatically)

---

## 🧩 Installation and Runtime (RUSSIAN)

### 1️⃣ Install Python
Requires **Python 3.9 or higher**.
Check the version:
```bash
python --version
```

### 2️⃣ Install dependencies
``` bash
pip install PySide6
```

### 3️⃣ Project structure
📦 todolist_app/
- ┣ 📜 main.py # Backend: database and logic
- ┣ 📜 gui_full_checkable.py # Frontend: PySide6 GUI
- ┗ 🗄️ todolist.db # SQLite database (created automatically)

### 4️⃣ Run the application
``` bash
python gui.py
```

### 5️⃣ Usage
- Enter your email and password to log in, or register.
- Tasks tab — create lists and tasks, double-click to mark a task as completed.
- Categories tab — create your own categories.
- Profile tab — change your name, email, password, and log out.
- All changes are saved automatically to todolist.db.
