import tkinter as tk
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db
from tkinter.messagebox import showerror, showwarning, showinfo
import subprocess

# Подключаем Firebase с Realtime Database
cred = credentials.Certificate("vending_key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://vending-2c957-default-rtdb.firebaseio.com/"
})

def verifyClick():
    if username_entry.get() == "":
        showwarning(title="Предупреждение", message="Вы не ввели логин")
    elif password_entry.get() == "":
        showwarning(title="Предупреждение", message="Вы не ввели пароль")
    else:
        login()

def login():
    username = username_entry.get()
    password = password_entry.get()
    
    # Получаем всех пользователей из узла "users"
    users_ref = db.reference("/users")
    users = users_ref.get()
    
    if not users:
        messagebox.showerror("Ошибка", "Нет пользователей в базе данных!")
        return

    # Перебираем всех пользователей и ищем совпадение по логину и паролю
    for user_id, user_data in users.items():
        if user_id == username and user_data.get("password") == password:
            messagebox.showinfo("Успех", f"Добро пожаловать, {username}!")
            subprocess.Popen(["python", "main.py"])
            root.destroy()
            return

    messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

# Создаем окно авторизации в Tkinter
root = tk.Tk()
root.title("Авторизация")
root.geometry("400x300")          # Устанавливаем нормальный размер окна
root.configure(bg="lightyellow")       # Задаем жёлтый фон для всего окна

# Метка и поле ввода для имени пользователя
username_label = tk.Label(root, text="Имя пользователя:", bg="lightyellow", fg="red", font=("Helvetica", 12, "bold"))
username_label.pack(pady=10)
username_entry = tk.Entry(root, font=("Helvetica", 12))
username_entry.pack(pady=5)

# Метка и поле ввода для пароля
password_label = tk.Label(root, text="Пароль:", bg="lightyellow", fg="red", font=("Helvetica", 12, "bold"))
password_label.pack(pady=10)
password_entry = tk.Entry(root, show="*", font=("Helvetica", 12))
password_entry.pack(pady=5)

# Кнопка входа, оформленная в красных тонах с жёлтым текстом
login_button = tk.Button(root, text="Войти", command=verifyClick, bg="red", fg="lightyellow", font=("Helvetica", 12, "bold"), border=5)
login_button.pack(pady=20)

root.mainloop()
