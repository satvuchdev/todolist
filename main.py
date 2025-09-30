import sqlite3
import uuid
from datetime import datetime
import hashlib
from typing import Optional, List
import getpass
import sys

DB_FILENAME = "todolist.db"

def now_iso():
    return datetime.utcnow().isoformat(timespec='seconds')

def gen_id():
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class Database:
    """Простой слой доступа к sqlite."""
    def __init__(self, filename=DB_FILENAME):
        self.conn = sqlite3.connect(filename)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS languages (
            languageId TEXT PRIMARY KEY,
            code TEXT UNIQUE,
            name TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userId TEXT PRIMARY KEY,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT,
            preferredLanguageId TEXT,
            createdAt TEXT,
            lastLogin TEXT,
            FOREIGN KEY(preferredLanguageId) REFERENCES languages(languageId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS tasklists (
            listId TEXT PRIMARY KEY,
            title TEXT,
            createdAt TEXT,
            color TEXT,
            userId TEXT,
            FOREIGN KEY(userId) REFERENCES users(userId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            taskId TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            isCompleted INTEGER,
            dueDate TEXT,
            priority TEXT,
            createdAt TEXT,
            updatedAt TEXT,
            reminder TEXT,
            listId TEXT,
            FOREIGN KEY(listId) REFERENCES tasklists(listId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            categoryId TEXT PRIMARY KEY,
            name TEXT,
            color TEXT,
            userId TEXT,
            FOREIGN KEY(userId) REFERENCES users(userId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS task_categories (
            taskId TEXT,
            categoryId TEXT,
            PRIMARY KEY (taskId, categoryId),
            FOREIGN KEY(taskId) REFERENCES tasks(taskId),
            FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS subtasks (
            subTaskId TEXT PRIMARY KEY,
            title TEXT,
            isCompleted INTEGER,
            taskId TEXT,
            FOREIGN KEY(taskId) REFERENCES tasks(taskId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            commentId TEXT PRIMARY KEY,
            content TEXT,
            createdAt TEXT,
            authorId TEXT,
            taskId TEXT,
            FOREIGN KEY(authorId) REFERENCES users(userId),
            FOREIGN KEY(taskId) REFERENCES tasks(taskId)
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS shared_tasklists (
            sharedListId TEXT PRIMARY KEY,
            permissionLevel TEXT,
            sharedAt TEXT,
            userId TEXT,
            listId TEXT,
            FOREIGN KEY(userId) REFERENCES users(userId),
            FOREIGN KEY(listId) REFERENCES tasklists(listId)
        )
        """)
        self.conn.commit()

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur

    def query_one(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def query_all(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()



class Language:
    def __init__(self, db: Database, languageId: Optional[str]=None, code: str="en", name: str="English"):
        self.db = db
        self.languageId = languageId or gen_id()
        self.code = code
        self.name = name

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO languages(languageId, code, name) VALUES (?, ?, ?)
        """, (self.languageId, self.code, self.name))

    @staticmethod
    def get_by_code(db: Database, code: str) -> Optional['Language']:
        row = db.query_one("SELECT * FROM languages WHERE code=?", (code,))
        if row:
            return Language(db, row['languageId'], row['code'], row['name'])
        return None

class User:
    def __init__(self, db: Database, userId: Optional[str]=None, username: str="", email: str="", password_hash: str="", preferredLanguageId: Optional[str]=None, createdAt: Optional[str]=None, lastLogin: Optional[str]=None):
        self.db = db
        self.userId = userId or gen_id()
        self.username = username
        self.email = email
        self.password = password_hash
        self.preferredLanguageId = preferredLanguageId
        self.createdAt = createdAt or now_iso()
        self.lastLogin = lastLogin

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO users(userId, username, email, password, preferredLanguageId, createdAt, lastLogin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.userId, self.username, self.email, self.password, self.preferredLanguageId, self.createdAt, self.lastLogin))

    @staticmethod
    def register(db: Database, username: str, email: str, password: str, language_code: str = "en"):
        if db.query_one("SELECT 1 FROM users WHERE email=?", (email,)):
            raise ValueError("Пользователь с таким email уже существует.")
        lang = Language.get_by_code(db, language_code)
        if not lang:
            lang = Language(db, code=language_code, name=language_code)
            lang.save()
        u = User(db, username=username, email=email, password_hash=hash_password(password), preferredLanguageId=lang.languageId)
        u.save()
        return u

    @staticmethod
    def login(db: Database, email: str, password: str) -> Optional['User']:
        row = db.query_one("SELECT * FROM users WHERE email=?", (email,))
        if not row:
            return None
        if row['password'] != hash_password(password):
            return None
        user = User(db, row['userId'], row['username'], row['email'], row['password'], row['preferredLanguageId'], row['createdAt'], now_iso())
        user.save() 
        return user

    def logout(self):
        self.lastLogin = now_iso()
        self.save()

    def update_profile(self, username: Optional[str]=None, email: Optional[str]=None):
        if username:
            self.username = username
        if email:
            row = self.db.query_one("SELECT userId FROM users WHERE email=? AND userId<>?", (email, self.userId))
            if row:
                raise ValueError("Email уже используется другим пользователем.")
            self.email = email
        self.save()

    def change_password(self, old_password: str, new_password: str):
        if self.password != hash_password(old_password):
            raise ValueError("Старый пароль неверен.")
        self.password = hash_password(new_password)
        self.save()

    def get_tasklists(self) -> List['TaskList']:
        rows = self.db.query_all("SELECT * FROM tasklists WHERE userId=?", (self.userId,))
        return [TaskList.from_row(self.db, r) for r in rows]

class TaskList:
    def __init__(self, db: Database, listId: Optional[str]=None, title: str="", createdAt: Optional[str]=None, color: str="white", userId: Optional[str]=None):
        self.db = db
        self.listId = listId or gen_id()
        self.title = title
        self.createdAt = createdAt or now_iso()
        self.color = color
        self.userId = userId

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO tasklists(listId, title, createdAt, color, userId) VALUES (?, ?, ?, ?, ?)
        """, (self.listId, self.title, self.createdAt, self.color, self.userId))

    @staticmethod
    def create(db: Database, userId: str, title: str, color: str="white"):
        tl = TaskList(db, title=title, color=color, userId=userId)
        tl.save()
        return tl

    @staticmethod
    def from_row(db: Database, row):
        return TaskList(db, row['listId'], row['title'], row['createdAt'], row['color'], row['userId'])

    @staticmethod
    def get_by_id(db: Database, listId: str) -> Optional['TaskList']:
        row = db.query_one("SELECT * FROM tasklists WHERE listId=?", (listId,))
        if row:
            return TaskList.from_row(db, row)
        return None

    def delete(self):
        tasks = self.get_tasks()
        for t in tasks:
            t.delete()
        self.db.execute("DELETE FROM shared_tasklists WHERE listId=?", (self.listId,))
        self.db.execute("DELETE FROM tasklists WHERE listId=?", (self.listId,))

    def add_task(self, title: str, description: str = "", dueDate: Optional[str]=None, priority: str="Low"):
        t = Task(self.db, title=title, description=description, isCompleted=False, dueDate=dueDate, priority=priority, taskListId=self.listId)
        t.save()
        return t

    def get_tasks(self) -> List['Task']:
        rows = self.db.query_all("SELECT * FROM tasks WHERE listId=?", (self.listId,))
        return [Task.from_row(self.db, r) for r in rows]

    def share_with_user(self, userId: str, permissionLevel: str="Read"):
        st = SharedTaskList(self.db, permissionLevel=permissionLevel, sharedAt=now_iso(), userId=userId, listId=self.listId)
        st.save()
        return st

class Task:
    def __init__(self, db: Database, taskId: Optional[str]=None, title: str="", description: str="", isCompleted: bool=False, dueDate: Optional[str]=None, priority: str="Low", createdAt: Optional[str]=None, updatedAt: Optional[str]=None, reminder: Optional[str]=None, taskListId: Optional[str]=None):
        self.db = db
        self.taskId = taskId or gen_id()
        self.title = title
        self.description = description
        self.isCompleted = isCompleted
        self.dueDate = dueDate
        self.priority = priority
        self.createdAt = createdAt or now_iso()
        self.updatedAt = updatedAt or now_iso()
        self.reminder = reminder
        self.taskListId = taskListId

    def save(self):
        self.updatedAt = now_iso()
        self.db.execute("""
        INSERT OR REPLACE INTO tasks(taskId, title, description, isCompleted, dueDate, priority, createdAt, updatedAt, reminder, listId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.taskId, self.title, self.description, int(self.isCompleted), self.dueDate, self.priority, self.createdAt, self.updatedAt, self.reminder, self.taskListId))

    @staticmethod
    def from_row(db: Database, row):
        return Task(db, row['taskId'], row['title'], row['description'], bool(row['isCompleted']), row['dueDate'], row['priority'], row['createdAt'], row['updatedAt'], row['reminder'], row['listId'])

    @staticmethod
    def get_by_id(db: Database, taskId: str) -> Optional['Task']:
        row = db.query_one("SELECT * FROM tasks WHERE taskId=?", (taskId,))
        if row:
            return Task.from_row(db, row)
        return None

    def update_title(self, newTitle: str):
        self.title = newTitle
        self.save()

    def update_description(self, newDescription: str):
        self.description = newDescription
        self.save()

    def mark_as_completed(self):
        self.isCompleted = True
        self.save()

    def set_due_date(self, date_iso: str):
        self.dueDate = date_iso
        self.save()

    def set_priority(self, priority: str):
        self.priority = priority
        self.save()

    def add_reminder(self, date_iso: str):
        self.reminder = date_iso
        self.save()

    def delete(self):
        self.db.execute("DELETE FROM subtasks WHERE taskId=?", (self.taskId,))
        self.db.execute("DELETE FROM comments WHERE taskId=?", (self.taskId,))
        self.db.execute("DELETE FROM task_categories WHERE taskId=?", (self.taskId,))
        self.db.execute("DELETE FROM tasks WHERE taskId=?", (self.taskId,))

    def add_subtask(self, title: str):
        st = SubTask(self.db, title=title, isCompleted=False, taskId=self.taskId)
        st.save()
        return st

    def get_subtasks(self) -> List['SubTask']:
        rows = self.db.query_all("SELECT * FROM subtasks WHERE taskId=?", (self.taskId,))
        return [SubTask.from_row(self.db, r) for r in rows]

    def add_comment(self, authorId: str, content: str):
        c = Comment(self.db, content=content, createdAt=now_iso(), authorId=authorId, taskId=self.taskId)
        c.save()
        return c

    def get_comments(self) -> List['Comment']:
        rows = self.db.query_all("SELECT * FROM comments WHERE taskId=? ORDER BY createdAt ASC", (self.taskId,))
        return [Comment.from_row(self.db, r) for r in rows]

    def assign_category(self, categoryId: str):
        self.db.execute("INSERT OR IGNORE INTO task_categories(taskId, categoryId) VALUES (?, ?)", (self.taskId, categoryId))

    def unassign_category(self, categoryId: str):
        self.db.execute("DELETE FROM task_categories WHERE taskId=? AND categoryId=?", (self.taskId, categoryId))

    def get_categories(self) -> List['Category']:
        rows = self.db.query_all("""
        SELECT c.* FROM categories c
        JOIN task_categories tc ON c.categoryId = tc.categoryId
        WHERE tc.taskId=?
        """, (self.taskId,))
        return [Category.from_row(self.db, r) for r in rows]

class Category:
    def __init__(self, db: Database, categoryId: Optional[str]=None, name: str="", color: str="gray", userId: Optional[str]=None):
        self.db = db
        self.categoryId = categoryId or gen_id()
        self.name = name
        self.color = color
        self.userId = userId

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO categories(categoryId, name, color, userId) VALUES (?, ?, ?, ?)
        """, (self.categoryId, self.name, self.color, self.userId))

    @staticmethod
    def create(db: Database, userId: str, name: str, color: str="gray"):
        cat = Category(db, name=name, color=color, userId=userId)
        cat.save()
        return cat

    @staticmethod
    def from_row(db: Database, row):
        return Category(db, row['categoryId'], row['name'], row['color'], row['userId'])

    @staticmethod
    def get_by_id(db: Database, categoryId: str) -> Optional['Category']:
        row = db.query_one("SELECT * FROM categories WHERE categoryId=?", (categoryId,))
        if row:
            return Category.from_row(db, row)
        return None

class SubTask:
    def __init__(self, db: Database, subTaskId: Optional[str]=None, title: str="", isCompleted: bool=False, taskId: Optional[str]=None):
        self.db = db
        self.subTaskId = subTaskId or gen_id()
        self.title = title
        self.isCompleted = isCompleted
        self.taskId = taskId

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO subtasks(subTaskId, title, isCompleted, taskId) VALUES (?, ?, ?, ?)
        """, (self.subTaskId, self.title, int(self.isCompleted), self.taskId))

    @staticmethod
    def from_row(db: Database, row):
        return SubTask(db, row['subTaskId'], row['title'], bool(row['isCompleted']), row['taskId'])

    def mark_completed(self):
        self.isCompleted = True
        self.save()

class Comment:
    def __init__(self, db: Database, commentId: Optional[str]=None, content: str="", createdAt: Optional[str]=None, authorId: Optional[str]=None, taskId: Optional[str]=None):
        self.db = db
        self.commentId = commentId or gen_id()
        self.content = content
        self.createdAt = createdAt or now_iso()
        self.authorId = authorId
        self.taskId = taskId

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO comments(commentId, content, createdAt, authorId, taskId) VALUES (?, ?, ?, ?, ?)
        """, (self.commentId, self.content, self.createdAt, self.authorId, self.taskId))

    @staticmethod
    def from_row(db: Database, row):
        return Comment(db, row['commentId'], row['content'], row['createdAt'], row['authorId'], row['taskId'])

class SharedTaskList:
    def __init__(self, db: Database, sharedListId: Optional[str]=None, permissionLevel: str="Read", sharedAt: Optional[str]=None, userId: Optional[str]=None, listId: Optional[str]=None):
        self.db = db
        self.sharedListId = sharedListId or gen_id()
        self.permissionLevel = permissionLevel
        self.sharedAt = sharedAt or now_iso()
        self.userId = userId
        self.listId = listId

    def save(self):
        self.db.execute("""
        INSERT OR REPLACE INTO shared_tasklists(sharedListId, permissionLevel, sharedAt, userId, listId) VALUES (?, ?, ?, ?, ?)
        """, (self.sharedListId, self.permissionLevel, self.sharedAt, self.userId, self.listId))


class ConsoleApp:
    def __init__(self):
        self.db = Database()
        self.current_user: Optional[User] = None
        if not Language.get_by_code(self.db, "en"):
            Language(self.db, code="en", name="English").save()
        if not Language.get_by_code(self.db, "ru"):
            Language(self.db, code="ru", name="Русский").save()

    def run(self):
        print("=== Simple ToDoList (консольный) ===")
        while True:
            try:
                if not self.current_user:
                    self._unauth_menu()
                else:
                    self._auth_menu()
            except (KeyboardInterrupt, EOFError):
                print("\nВыход.")
                sys.exit(0)
            except Exception as e:
                print("Ошибка:", e)

    def _unauth_menu(self):
        print("\n1) Регистрация\n2) Вход\n3) Выход")
        choice = input("Выберите: ").strip()
        if choice == "1":
            self._register_flow()
        elif choice == "2":
            self._login_flow()
        elif choice == "3":
            print("Пока!")
            sys.exit(0)
        else:
            print("Неизвестный выбор.")

    def _register_flow(self):
        print("--- Регистрация ---")
        username = input("username: ").strip()
        email = input("email: ").strip()
        password = getpass.getpass("password: ")
        lang = input("language code (en/ru): ").strip() or "en"
        try:
            user = User.register(self.db, username, email, password, language_code=lang)
            print("Пользователь зарегистрирован. Войдите в систему.")
        except Exception as e:
            print("Не удалось зарегистрировать:", e)

    def _login_flow(self):
        print("--- Вход ---")
        email = input("email: ").strip()
        password = getpass.getpass("password: ")
        user = User.login(self.db, email, password)
        if user:
            self.current_user = user
            print(f"Привет, {user.username}!")
        else:
            print("Неверный email или пароль.")

    def _auth_menu(self):
        print(f"\n[Пользователь: {self.current_user.username}]")
        print("1) Мои списки\n2) Создать список\n3) Категории\n4) Профиль\n5) Выйти")
        choice = input("Выберите: ").strip()
        if choice == "1":
            self._lists_menu()
        elif choice == "2":
            self._create_list()
        elif choice == "3":
            self._categories_menu()
        elif choice == "4":
            self._profile_menu()
        elif choice == "5":
            self.current_user.logout()
            self.current_user = None
            print("Вы вышли.")
        else:
            print("Неизвестный выбор.")

    def _create_list(self):
        title = input("Название списка: ").strip()
        color = input("Цвет (произв.): ").strip() or "white"
        tl = TaskList.create(self.db, self.current_user.userId, title, color)
        print("Создан список:", tl.listId)

    def _lists_menu(self):
        lists = self.current_user.get_tasklists()
        if not lists:
            print("У вас пока нет списков.")
            return
        for idx, tl in enumerate(lists, start=1):
            print(f"{idx}) {tl.title} (id={tl.listId})")
        sel = input("Выберите номер списка для работы (или пусто): ").strip()
        if not sel:
            return
        try:
            idx = int(sel)-1
            tl = lists[idx]
            self._tasklist_menu(tl)
        except Exception as e:
            print("Неверный выбор:", e)

    def _tasklist_menu(self, tl: TaskList):
        while True:
            print(f"\n--- Список: {tl.title} ---")
            print("1) Показать задачи\n2) Добавить задачу\n3) Удалить список\n4) Поделиться списком\n5) Назад")
            choice = input("Выберите: ").strip()
            if choice == "1":
                self._show_tasks(tl)
            elif choice == "2":
                self._add_task_flow(tl)
            elif choice == "3":
                confirm = input("Удалить список? y/N: ").strip().lower()
                if confirm == "y":
                    tl.delete()
                    print("Список удалён.")
                    return
            elif choice == "4":
                self._share_list_flow(tl)
            elif choice == "5":
                return
            else:
                print("Неизвестный выбор.")

    def _show_tasks(self, tl: TaskList):
        tasks = tl.get_tasks()
        if not tasks:
            print("Задач нет.")
            return
        for idx, t in enumerate(tasks, start=1):
            status = "✓" if t.isCompleted else " "
            print(f"{idx}) [{status}] {t.title} (id={t.taskId}) priority={t.priority} due={t.dueDate}")
        sel = input("Выберите номер задачи для действий (или пусто): ").strip()
        if not sel:
            return
        try:
            idx = int(sel)-1
            task = tasks[idx]
            self._task_menu(task)
        except Exception as e:
            print("Неверный выбор:", e)

    def _add_task_flow(self, tl: TaskList):
        title = input("Название задачи: ").strip()
        desc = input("Описание (опц.): ").strip()
        due = input("dueDate (ISO, опц.): ").strip() or None
        priority = input("Приоритет (Low/Medium/High/Critical) [Low]: ").strip() or "Low"
        t = tl.add_task(title, description=desc, dueDate=due, priority=priority)
        print("Создана задача:", t.taskId)

    def _task_menu(self, task: Task):
        while True:
            print(f"\n--- Задача: {task.title} ---")
            print("1) Обновить заголовок\n2) Обновить описание\n3) Отметить как выполненную\n4) Добавить подзадачу\n5) Показать подзадачи\n6) Добавить комментарий\n7) Показать комментарии\n8) Назад")
            choice = input("Выберите: ").strip()
            if choice == "1":
                new = input("Новый заголовок: ").strip()
                task.update_title(new)
                print("Обновлено.")
            elif choice == "2":
                new = input("Новое описание: ").strip()
                task.update_description(new)
                print("Обновлено.")
            elif choice == "3":
                task.mark_as_completed()
                print("Отмечено выполненным.")
            elif choice == "4":
                title = input("Заголовок подзадачи: ").strip()
                st = task.add_subtask(title)
                print("Добавлена подзадача:", st.subTaskId)
            elif choice == "5":
                sts = task.get_subtasks()
                if not sts:
                    print("Нет подзадач.")
                for i, s in enumerate(sts, start=1):
                    print(f"{i}) [{'✓' if s.isCompleted else ' '}] {s.title} (id={s.subTaskId})")
                sub = input("Отметить подзадачу как выполненную (номер) или пусто: ").strip()
                if sub:
                    try:
                        num = int(sub)-1
                        sts[num].mark_completed()
                        print("Отмечено.")
                    except Exception as e:
                        print("Ошибка:", e)
            elif choice == "6":
                content = input("Комментарий: ").strip()
                c = task.add_comment(self.current_user.userId, content)
                print("Комментарий добавлен:", c.commentId)
            elif choice == "7":
                comms = task.get_comments()
                if not comms:
                    print("Комментариев нет.")
                for cm in comms:
                    author_row = self.db.query_one("SELECT username FROM users WHERE userId=?", (cm.authorId,))
                    author = author_row['username'] if author_row else "?"
                    print(f"- {cm.createdAt} {author}: {cm.content}")
            elif choice == "8":
                return
            else:
                print("Неизвестный выбор.")

    def _share_list_flow(self, tl: TaskList):
        email = input("Email пользователя, с кем делитесь: ").strip()
        row = self.db.query_one("SELECT userId FROM users WHERE email=?", (email,))
        if not row:
            print("Пользователь не найден.")
            return
        userId = row['userId']
        perm = input("Разрешение (Read/Write/Admin) [Read]: ").strip() or "Read"
        tl.share_with_user(userId, perm)
        print("Список расшарен.")

    def _categories_menu(self):
        while True:
            print("\n--- Категории ---")
            print("1) Показать мои категории\n2) Создать категорию\n3) Назад")
            choice = input("Выберите: ").strip()
            if choice == "1":
                rows = self.db.query_all("SELECT * FROM categories WHERE userId=?", (self.current_user.userId,))
                if not rows:
                    print("Категорий нет.")
                for r in rows:
                    print(f"- {r['name']} (id={r['categoryId']}) color={r['color']}")
            elif choice == "2":
                name = input("Название категории: ").strip()
                color = input("Цвет (опц.): ").strip() or "gray"
                cat = Category.create(self.db, self.current_user.userId, name, color)
                print("Создана категория:", cat.categoryId)
            elif choice == "3":
                return
            else:
                print("Неизвестный выбор.")

    def _profile_menu(self):
        while True:
            print("\n--- Профиль ---")
            print("1) Показать профиль\n2) Обновить профиль\n3) Поменять пароль\n4) Назад")
            choice = input("Выберите: ").strip()
            if choice == "1":
                print(f"username: {self.current_user.username}")
                print(f"email: {self.current_user.email}")
                print(f"createdAt: {self.current_user.createdAt}")
                print(f"lastLogin: {self.current_user.lastLogin}")
            elif choice == "2":
                username = input(f"username [{self.current_user.username}]: ").strip() or None
                email = input(f"email [{self.current_user.email}]: ").strip() or None
                try:
                    self.current_user.update_profile(username=username, email=email)
                    print("Обновлено.")
                except Exception as e:
                    print("Ошибка:", e)
            elif choice == "3":
                old = getpass.getpass("Старый пароль: ")
                new = getpass.getpass("Новый пароль: ")
                try:
                    self.current_user.change_password(old, new)
                    print("Пароль изменён.")
                except Exception as e:
                    print("Ошибка:", e)
            elif choice == "4":
                return
            else:
                print("Неизвестный выбор.")

if __name__ == "__main__":
    app = ConsoleApp()
    app.run()