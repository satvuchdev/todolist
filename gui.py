# gui_full_checkable.py
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QTextEdit, QMessageBox, QTabWidget, QInputDialog
)
from PySide6.QtCore import Qt
import sys
from main import Database, User, TaskList, Task, Category


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.user = None
        self.setWindowTitle("ToDoList (PySide6)")
        self.setGeometry(300, 200, 400, 300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Добро пожаловать!", alignment=Qt.AlignCenter))

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Войти")
        self.register_btn = QPushButton("Регистрация")

        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)

    def login(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        user = User.login(self.db, email, password)
        if user:
            self.hide()
            self.todo = MainApp(self.db, user)
            self.todo.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный email или пароль.")

    def register(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        username = email.split("@")[0]
        try:
            User.register(self.db, username, email, password, "ru")
            QMessageBox.information(self, "OK", "Регистрация успешна.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))


class MainApp(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user

        self.setWindowTitle(f"ToDoList — {user.username}")
        self.setGeometry(200, 150, 700, 500)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладки
        self.tasks_tab = TasksTab(db, user)
        self.categories_tab = CategoriesTab(db, user)
        self.profile_tab = ProfileTab(db, user, self)

        tabs.addTab(self.tasks_tab, "Задачи")
        tabs.addTab(self.categories_tab, "Категории")
        tabs.addTab(self.profile_tab, "Профиль")


class TasksTab(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self.current_list = None

        layout = QHBoxLayout(self)

        # Списки задач
        self.list_widget = QListWidget()
        self.load_lists()
        layout.addWidget(self.list_widget, 1)

        # Правая панель
        right = QVBoxLayout()

        self.task_list = QListWidget()
        self.task_title = QLineEdit()
        self.task_title.setPlaceholderText("Название задачи...")
        self.task_desc = QTextEdit()
        self.task_desc.setPlaceholderText("Описание...")
        self.add_task_btn = QPushButton("Добавить задачу")
        self.add_list_btn = QPushButton("Создать список")
        self.show_subtasks_btn = QPushButton("Показать подзадачи")
        self.show_comments_btn = QPushButton("Показать комментарии")

        right.addWidget(QLabel("Задачи"))
        right.addWidget(self.task_list)
        right.addWidget(self.task_title)
        right.addWidget(self.task_desc)
        right.addWidget(self.add_task_btn)
        right.addWidget(self.add_list_btn)
        right.addWidget(self.show_subtasks_btn)
        right.addWidget(self.show_comments_btn)

        layout.addLayout(right, 2)

        # События
        self.list_widget.itemSelectionChanged.connect(self.load_tasks)
        self.add_task_btn.clicked.connect(self.add_task)
        self.add_list_btn.clicked.connect(self.add_list)
        self.show_subtasks_btn.clicked.connect(self.show_subtasks)
        self.show_comments_btn.clicked.connect(self.show_comments)
        self.task_list.itemDoubleClicked.connect(self.toggle_task_done)

    def load_lists(self):
        self.list_widget.clear()
        for l in self.user.get_tasklists():
            self.list_widget.addItem(l.title)

    def load_tasks(self):
        self.task_list.clear()
        current = self.list_widget.currentRow()
        if current < 0:
            return
        self.current_list = self.user.get_tasklists()[current]
        for t in self.current_list.get_tasks():
            status = "✓ " if t.isCompleted else "• "
            self.task_list.addItem(status + t.title)

    def add_task(self):
        if not self.current_list:
            QMessageBox.warning(self, "Ошибка", "Выберите список.")
            return
        title = self.task_title.text().strip()
        if not title:
            return
        desc = self.task_desc.toPlainText().strip()
        self.current_list.add_task(title, description=desc)
        self.load_tasks()
        self.task_title.clear()
        self.task_desc.clear()

    def add_list(self):
        name, ok = QInputDialog.getText(self, "Новый список", "Название списка:")
        if ok and name.strip():
            TaskList.create(self.db, self.user.userId, name.strip())
            self.load_lists()

    def show_subtasks(self):
        row = self.task_list.currentRow()
        if row < 0:
            return
        task = self.current_list.get_tasks()[row]
        subs = task.get_subtasks()
        if not subs:
            QMessageBox.information(self, "Подзадачи", "Нет подзадач.")
            return
        msg = "\n".join([("✓ " if s.isCompleted else "• ") + s.title for s in subs])
        QMessageBox.information(self, "Подзадачи", msg)

    def show_comments(self):
        row = self.task_list.currentRow()
        if row < 0:
            return
        task = self.current_list.get_tasks()[row]
        comments = task.get_comments()
        if not comments:
            QMessageBox.information(self, "Комментарии", "Нет комментариев.")
            return
        msg = "\n".join([f"{c.createdAt}: {c.content}" for c in comments])
        QMessageBox.information(self, "Комментарии", msg)

    def toggle_task_done(self, item):
        row = self.task_list.row(item)
        if row < 0 or not self.current_list:
            return
        task = self.current_list.get_tasks()[row]
        task.isCompleted = not task.isCompleted
        task.save()
        self.load_tasks()


class CategoriesTab(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.add_btn = QPushButton("Создать категорию")

        layout.addWidget(QLabel("Мои категории"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.add_btn)

        self.add_btn.clicked.connect(self.add_category)
        self.load_categories()

    def load_categories(self):
        self.list_widget.clear()
        rows = self.db.query_all("SELECT * FROM categories WHERE userId=?", (self.user.userId,))
        for r in rows:
            self.list_widget.addItem(f"{r['name']} ({r['color']})")

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Новая категория", "Название категории:")
        if ok and name.strip():
            color, ok2 = QInputDialog.getText(self, "Цвет", "Введите цвет (напр. red):")
            if ok2:
                Category.create(self.db, self.user.userId, name.strip(), color.strip() or "gray")
                self.load_categories()


class ProfileTab(QWidget):
    def __init__(self, db, user, parent_window):
        super().__init__()
        self.db = db
        self.user = user
        self.parent_window = parent_window

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Профиль"))
        self.username = QLineEdit(user.username)
        self.email = QLineEdit(user.email)
        self.save_btn = QPushButton("Сохранить изменения")
        self.change_pass_btn = QPushButton("Сменить пароль")
        self.logout_btn = QPushButton("Выйти")

        layout.addWidget(QLabel("Имя пользователя"))
        layout.addWidget(self.username)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.change_pass_btn)
        layout.addWidget(self.logout_btn)

        self.save_btn.clicked.connect(self.save_profile)
        self.change_pass_btn.clicked.connect(self.change_password)
        self.logout_btn.clicked.connect(self.logout)

    def save_profile(self):
        try:
            self.user.update_profile(username=self.username.text(), email=self.email.text())
            QMessageBox.information(self, "OK", "Профиль обновлён.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def change_password(self):
        old, ok1 = QInputDialog.getText(self, "Пароль", "Введите старый пароль:", QLineEdit.Password)
        if not ok1:
            return
        new, ok2 = QInputDialog.getText(self, "Пароль", "Введите новый пароль:", QLineEdit.Password)
        if ok2:
            try:
                self.user.change_password(old, new)
                QMessageBox.information(self, "OK", "Пароль изменён.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def logout(self):
        self.user.logout()
        self.parent_window.close()
        login = LoginWindow()
        login.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())
