import sqlite3
import datetime
import uuid

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('todo.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                userId TEXT PRIMYAR KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT,
                createdAt TEXT,
                lastLogin TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasklists (
                listId TEXT PRIMARY KEY,
                title TEXT,
                createdAt TEXT,
                userId TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                taskId TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                isCompleted BOOLEAN,
                dueDate TEXT,
                priority TEXT,
                createdAt TEXT,
                listId TEXT
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetch(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

db = Database()

class User:
    def __init__(self):
        self.userId = ""
        self.username = ""
        self.email = ""
    
    def register(self, username, email, password):
        userId = str(uuid.uuid4())
        createdAt = datetime.datetime.now().isoformat()
        
        query = '''INSERT INTO users (userId, username, email, password, createdAt, lastLogin)
                   VALUES (?, ?, ?, ?, ?, ?)'''
        try:
            db.execute(query, (userId, username, email, password, createdAt, createdAt))
            return True
        except:
            return False
    
    def login(self, email, password):
        query = "SELECT * FROM users WHERE email = ? AND password = ?"
        result = db.fetch(query, (email, password))
        
        if result:
            user_data = result[0]
            self.userId = user_data[0]
            self.username = user_data[1]
            self.email = user_data[2]
            
            db.execute("UPDATE users SET lastLogin = ? WHERE userId = ?", 
                     (datetime.datetime.now().isoformat(), self.userId))
            return True
        return False

class TaskList:
    def __init__(self, userId=""):
        self.listId = ""
        self.title = ""
        self.userId = userId
    
    def create(self, title, userId):
        self.listId = str(uuid.uuid4())
        self.title = title
        self.userId = userId
        
        query = "INSERT INTO tasklists (listId, title, createdAt, userId) VALUES (?, ?, ?, ?)"
        db.execute(query, (self.listId, title, datetime.datetime.now().isoformat(), userId))
    
    def get_tasks(self):
        query = "SELECT * FROM tasks WHERE listId = ?"
        return db.fetch(query, (self.listId,))
    
    def delete_task(self, taskId):
        db.execute("DELETE FROM tasks WHERE taskId = ?", (taskId,))

class Task:
    def __init__(self):
        self.taskId = ""
        self.title = ""
        self.description = ""
        self.isCompleted = False
        self.priority = "Medium"
    
    def create(self, title, description, listId, priority="Medium"):
        self.taskId = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.listId = listId
        self.priority = priority
        
        query = '''INSERT INTO tasks (taskId, title, description, isCompleted, priority, createdAt, listId)
                   VALUES (?, ?, ?, ?, ?, ?, ?)'''
        db.execute(query, (self.taskId, title, description, False, priority, 
                         datetime.datetime.now().isoformat(), listId))
    
    def mark_completed(self, taskId):
        db.execute("UPDATE tasks SET isCompleted = ? WHERE taskId = ?", (True, taskId))
    
    def update_title(self, taskId, newTitle):
        db.execute("UPDATE tasks SET title = ? WHERE taskId = ?", (newTitle, taskId))


current_user = User()
task_lists = []

def get_user_lists(userId):
    query = "SELECT * FROM tasklists WHERE userId = ?"
    return db.fetch(query, (userId,))

def get_list_tasks(listId):
    query = "SELECT * FROM tasks WHERE listId = ?"
    return db.fetch(query, (listId,))