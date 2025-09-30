## RUS Description
Простое консольное приложение для управления задачами, написанное на Python с использованием SQLite.

## 🚀 Возможности

- **🔐 Аутентификация** - регистрация и вход в систему
- **📝 Управление задачами** - создание, редактирование, отслеживание выполнения
- **📂 Организация** - списки задач, категории, приоритеты
- **👥 Совместная работа** - общий доступ к спискам с разными уровнями прав
- **💬 Комментарии** - обсуждение задач
- **⏰ Напоминания** - установка сроков выполнения
- **🔗 Подзадачи** - разбивка сложных задач на этапы

## 🛠 Что используется

- Python 3
- SQLite3
- SHA-256 для хеширования паролей
- UUID для генерации идентификаторов

## 📦 Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/satvuchdev/todolist.git

# Перейти в директорию проекта
cd todolist-console

# Запустить приложение
python main.py
```
## 💡 Как пользоваться
1. Зарегистрируйте нового пользователя или войдите в систему
2. Создайте списки задач для разных проектов
3. Добавляйте задачи с указанием приоритета и сроков
4. Организуйте задачи с помощью категорий
5. Делитесь списками с другими пользователями
6. Используйте подзадачи и комментарии для лучшей организации

## 🗃 Структура базы данных
- Приложение использует реляционную базу данных SQLite со следующими основными таблицами:
- **users** - пользователи системы
- **tasklists** - списки задач
- **tasks** - задачи
- **shared_tasklists** - общий доступ к спискам
- **categories** - категории задач
- **comments** - комментарии к задачам
- **subtasks** - подзадачи

## 👨💻 Автор
- **satvuchdev**

#

## ENG Description
A simple console application for task management, written in Python using SQLite.

## 🚀 Features

- **🔐 Authentication** - registration and login
- **📝 Task Management** - creation, editing, and tracking
- **📂 Organization** - task lists, categories, and priorities
- **👥 Collaboration** - sharing lists with different permission levels
- **💬 Comments** - task discussions
- **⏰ Reminders** - setting due dates
- **🔗 Subtasks** - breaking down complex tasks into steps

## 🛠 What's Used

- Python 3
- SQLite3
- SHA-256 for password hashing
- UUID for ID generation

## 📦 Installation and Run

```bash
git clone https://github.com/satvuchdev/todolist.git

cd todolist-console

python main.py
```
## 💡 How to use
1. Register a new user or log in
2. Create task lists for different projects
3. Add tasks with priority and due dates
4. Organize tasks using categories
5. Share lists with other users
6. Use subtasks and comments for better organization

## 🗃 Database structure
- The app uses a relational SQLite database with the following main tables:
- **users** - system users
- **tasklists** - task lists
- **tasks** - tasks
- **shared_tasklists** - shared lists
- **categories** - task categories
- **comments** - task comments
- **subtasks** - subtasks

## 👨💻 Author
- **satvuchdev**
