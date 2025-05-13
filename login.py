import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, db
from db import DataBase
import subprocess
import sys
# Стилизация приложения
BG_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#1877f2"
HOVER_COLOR = "#166fe5"
TEXT_COLOR = "#1c1e21"
ENTRY_BG = "#ffffff"
FONT = ("Segoe UI", 10)

class Login(Frame):
    def __init__(self, root):
        super().__init__(root)  # Инициализация родительского класса Frame
        self.host = "127.0.0.1"
        self.user = "root"
        self.password = ""
        self.database = "Vending"
        self.db = DataBase(self.host, self.user, self.password, self.database)
        self.root = root        
        self.main_frame = tk.Frame(root, bg=BG_COLOR)
        self.main_frame.pack(fill='both', expand=True)  # Добавляем фрейм в окно
        self.build()

    def verifyClick(self):
        if not self.username_entry.get():
            messagebox.showwarning("Ошибка!", "Не введен логин!")
            return
        if not self.password_entry.get():
            messagebox.showwarning("Ошибка!", "Не введен пароль!")
            return
        self.login()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        try:
            self.db.connect()
            query = "Select login, password from Employee where login = %s"
            
            self.db.cursor.execute(query, (username,))
            
            user_data = self.db.cursor.fetchone()
            
            if not user_data:
                messagebox.showerror("Ошибка", "Пользователь не найден")
                return

            stored_login, stored_password = user_data
            if stored_password != password:
                messagebox.showerror("Ошибка", "Неверный пароль")
                return

            messagebox.showinfo("Успешно", f"Добро пожаловать, {username}!")
            self.root.destroy()
            from main import MainApp

            new_root = Tk()
            new_root.resizable(0, 0)
            new_root.iconbitmap("vendor.ico")
            MainApp(new_root)
            new_root.mainloop()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {str(e)}")
        finally:
            if hasattr(self.db, 'connection') and self.db.connection:
                self.db.connection.close()
                

    def build(self):
        # Заголовок
        header = tk.Label(
            self.main_frame,
            text="Авторизация в системе",
            font=("Segoe UI Semibold", 18),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        header.pack(pady=(30, 20))

        # Контейнер для полей ввода
        input_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        input_frame.pack(padx=40, pady=10, fill='x')

        # Поле логина
        username_frame = tk.Frame(input_frame, bg=BG_COLOR)
        username_frame.pack(fill='x', pady=5)
        
        tk.Label(username_frame, 
                text="Логин",
                font=FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR).pack(anchor='w')
        
        self.username_entry = ttk.Entry(
            username_frame, 
            font=FONT, 
            style='Custom.TEntry'
        )
        self.username_entry.pack(fill='x', pady=5)

        # Поле пароля
        password_frame = tk.Frame(input_frame, bg=BG_COLOR)
        password_frame.pack(fill='x', pady=5)
        
        tk.Label(password_frame, 
                text="Пароль",
                font=FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR).pack(anchor='w')
        
        self.password_entry = ttk.Entry(
            password_frame, 
            font=FONT, 
            show="•",
            style='Custom.TEntry'
        )
        self.password_entry.pack(fill='x', pady=5)

        # Стилизация
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TEntry', fieldbackground=ENTRY_BG, borderwidth=2, relief="flat", padding=5)
        style.configure('Primary.TButton', font=FONT, background=PRIMARY_COLOR, foreground='white', borderwidth=0, padding=10)
        style.map('Primary.TButton', background=[('active', HOVER_COLOR)])

        # Кнопка входа
        login_btn = ttk.Button(
            input_frame,
            text="Войти", 
            style='Primary.TButton',
            command=self.verifyClick
        )
        login_btn.pack(fill='x', pady=20)

        # Обработка Enter
        self.root.bind('<Return>', lambda e: self.verifyClick())

# Инициализация главного окна
root = Tk()
root.title("Авторизация")
root.geometry("400x500")
root.configure(bg=BG_COLOR)
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')  # Центрирование

app = Login(root)
root.mainloop()