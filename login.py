import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, db
import subprocess

# Стилизация приложения
BG_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#1877f2"
HOVER_COLOR = "#166fe5"
TEXT_COLOR = "#1c1e21"
ENTRY_BG = "#ffffff"
FONT = ("Segoe UI", 10)

# Подключаем Firebase
cred = credentials.Certificate("vending_key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://vending-2c957-default-rtdb.firebaseio.com/"
})

def verifyClick():
    if not username_entry.get():
        messagebox.showwarning("Ошибка!", "Не введен логин!")
        return
    if not password_entry.get():
        messagebox.showwarning("Ошибка!", "Ошибка! Не введен пароль!")
        return
    login()

def login():
    username = username_entry.get()
    password = password_entry.get()
    
    try:
        users_ref = db.reference("/users")
        users = users_ref.get()
        
        if not users:
            messagebox.showerror("Ошибка", "База данных пользователей пуста")
            return

        # Проверка существования пользователя
        if username not in users:
            messagebox.showerror("Ошибка", "Ошибка! Такого пользователя не существует!")
            return
            
        # Проверка пароля
        if users[username].get("password") != password:
            messagebox.showerror("Ошибка", "Ошибка! Неверный пароль!")
            return

        # Успешная авторизация
        messagebox.showinfo("Успешный вход", f"Добро пожаловать, {username}!")
        root.destroy()
        subprocess.Popen(["python", "main.py"])
            
    except Exception as e:
        messagebox.showerror("Ошибка соединения", f"Ошибка подключения к базе данных: {str(e)}")
# Создание главного окна
root = tk.Tk()
root.title("Авторизация")
root.geometry("400x500")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

# Центрирование окна
root.eval('tk::PlaceWindow . center')

# Основной контейнер
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(pady=40, padx=40, fill='both', expand=True)

# Заголовок
header = tk.Label(main_frame, 
                text="Авторизация в системе",
                font=("Segoe UI Semibold", 18),
                bg=BG_COLOR,
                fg=TEXT_COLOR)
header.pack(pady=(0, 30))

# Поле ввода логина
username_frame = tk.Frame(main_frame, bg=BG_COLOR)
username_frame.pack(fill='x', pady=5)

tk.Label(username_frame, 
        text="Логин",
        font=FONT,
        bg=BG_COLOR,
        fg=TEXT_COLOR).pack(anchor='w')

username_entry = ttk.Entry(username_frame, 
                          font=FONT, 
                          style='Custom.TEntry')
username_entry.pack(fill='x', pady=5)

# Поле ввода пароля
password_frame = tk.Frame(main_frame, bg=BG_COLOR)
password_frame.pack(fill='x', pady=5)

tk.Label(password_frame, 
        text="Пароль",
        font=FONT,
        bg=BG_COLOR,
        fg=TEXT_COLOR).pack(anchor='w')

password_entry = ttk.Entry(password_frame, 
                          font=FONT, 
                          show="•",
                          style='Custom.TEntry')
password_entry.pack(fill='x', pady=5)

# Стиль для кнопок и полей ввода
style = ttk.Style()
style.theme_use('clam')

style.configure('Custom.TEntry',
                fieldbackground=ENTRY_BG,
                borderwidth=2,
                relief="flat",
                padding=5)

style.configure('Primary.TButton',
                font=FONT,
                background=PRIMARY_COLOR,
                foreground='white',
                borderwidth=0,
                focuscolor=PRIMARY_COLOR,
                padding=10)

style.map('Primary.TButton',
          background=[('active', HOVER_COLOR), ('disabled', '#dddfe2')])

# Кнопка входа
login_btn = ttk.Button(main_frame, 
                      text="Войти", 
                      style='Primary.TButton',
                      command=verifyClick)
login_btn.pack(fill='x', pady=20)

# Обработка Enter
root.bind('<Return>', lambda event: verifyClick())

root.mainloop()