from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QTextEdit, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt
import sys
from main import *

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user = User()
        self.setWindowTitle("ToDo List")
        self.setGeometry(400, 200, 400, 300)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ToDo List", alignment=Qt.AlignCenter))
        
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
        if self.current_user.login(self.email.text(), self.password.text()):
            self.hide()
            MainApp(self.current_user).show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный email или пароль")

    def register(self):
        email = self.email.text()
        username = email.split("@")[0]
        if self.current_user.register(username, email, self.password.text()):
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
        else:
            QMessageBox.warning(self, "Ошибка", "Регистрация не удалась")

class MainApp(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"ToDo — {user.username}")
        self.setGeometry(200, 150, 700, 500)
        
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        tabs.addTab(TasksTab(user), "Задачи")
        tabs.addTab(ProfileTab(user, self), "Профиль")

class TasksTab(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.current_list_id = None
        
        layout = QHBoxLayout(self)
        
        left_panel = QVBoxLayout()
        self.lists_list = QListWidget()
        self.new_list_input = QLineEdit()
        self.new_list_input.setPlaceholderText("Новый список")
        self.add_list_btn = QPushButton("Добавить список")
        
        left_panel.addWidget(QLabel("Списки:"))
        left_panel.addWidget(self.lists_list)
        left_panel.addWidget(self.new_list_input)
        left_panel.addWidget(self.add_list_btn)
        
        right_panel = QVBoxLayout()
        self.tasks_list = QListWidget()
        self.task_title = QLineEdit()
        self.task_title.setPlaceholderText("Новая задача")
        self.add_task_btn = QPushButton("Добавить задачу")
        
        right_panel.addWidget(QLabel("Задачи:"))
        right_panel.addWidget(self.tasks_list)
        right_panel.addWidget(self.task_title)
        right_panel.addWidget(self.add_task_btn)
        
        layout.addLayout(left_panel)
        layout.addLayout(right_panel)
        
        self.add_list_btn.clicked.connect(self.add_list)
        self.add_task_btn.clicked.connect(self.add_task)
        self.lists_list.itemClicked.connect(self.load_tasks)
        self.tasks_list.itemDoubleClicked.connect(self.complete_task)
        
        self.load_lists()

    def load_lists(self):
        self.lists_list.clear()
        for list_item in get_user_lists(self.user.userId):
            self.lists_list.addItem(list_item[1])

    def load_tasks(self):
        selected = self.lists_list.currentItem()
        if selected:
            list_title = selected.text()
            for list_item in get_user_lists(self.user.userId):
                if list_item[1] == list_title:
                    self.current_list_id = list_item[0]
                    break
            
            self.tasks_list.clear()
            for task in get_list_tasks(self.current_list_id):
                status = "✓" if task[3] else "○"
                self.tasks_list.addItem(f"{status} {task[1]}")

    def add_list(self):
        title = self.new_list_input.text()
        if title:
            TaskList(self.user.userId).create(title, self.user.userId)
            self.new_list_input.clear()
            self.load_lists()

    def add_task(self):
        if self.current_list_id and self.task_title.text():
            Task().create(self.task_title.text(), "", self.current_list_id)
            self.task_title.clear()
            self.load_tasks()

    def complete_task(self):
        selected = self.tasks_list.currentItem()
        if selected and self.current_list_id:
            task_text = selected.text()
            task_title = task_text[2:]
            for task in get_list_tasks(self.current_list_id):
                if task[1] == task_title:
                    Task().mark_completed(task[0])
                    break
            self.load_tasks()

class ProfileTab(QWidget):
    def __init__(self, user, parent_window):
        super().__init__()
        self.user = user
        self.parent_window = parent_window
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Пользователь: {user.username}"))
        layout.addWidget(QLabel(f"Email: {user.email}"))
        
        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

    def logout(self):
        self.parent_window.close()
        LoginWindow().show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())