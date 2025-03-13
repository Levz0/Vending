from tkinter import ttk, Tk
from tkinter import *
import random
from datetime import datetime

# Импорт классов (предполагается, что файлы находятся в соседней папке)
from entities.post import Post
from entities.LampType import LampType
from entities.employee import Employee
from entities.Lamp import Lamp


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vending Management System")
        self.root.geometry("1200x600")
        
        # Генерация тестовых данных
        self.generate_data()
        
        # Создание интерфейса
        self.create_widgets()

    def generate_data(self):
        # Создаем случайные данные
        self.posts = [Post("Менеджер"), Post("Техник"), Post("Оператор")]
        self.lamp_types = [LampType("Светодиодная"), LampType("Люминесцентная")]
        
        # Сотрудники
        self.employees = [
            Employee(
                FIO=f"Иванов Иван {i}",
                post=random.choice(self.posts),
                birthDate=f"199{random.randint(0,9)}-0{random.randint(1,9)}-{random.randint(10,28)}",
                INN=random.randint(100000000000, 999999999999),
                phoneNumber=f"+7{random.randint(9000000000, 9999999999)}",
                login=f"user{i}",
                password="12345"
            ) for i in range(1, 6)
        ]
        
        # Лампы
        self.lamps = [
            Lamp(
                name=f"Лампа-{i}",
                LampType=random.choice(self.lamp_types).name,
                voltage=random.choice([220, 110]),
                colorTemp=random.randint(3000, 6500),
                price=round(random.uniform(100, 1000), 2),
                description=f"Описание лампы {i}"
            ) for i in range(1, 6)
        ]
        
        # Аппараты
        self.apparatuses = [
            {
                "code": f"VM-{i:03d}",
                "location": random.choice(["ТЦ 'МЕГА'", "Вокзал", "Офис"]),
                "install_date": datetime.now().strftime("%Y-%m-%d"),
                "status": random.choice(["Активен", "Неактивен"])
            } for i in range(1, 6)
        ]

    def create_widgets(self):
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)  # Делаем notebook атрибутом класса
        self.notebook.pack(fill=BOTH, expand=True)

        # Вкладка для аппаратов
        frame_app = ttk.Frame(self.notebook)
        self.create_table(frame_app, "Аппараты", 
                         ["Код", "Локация", "Дата установки", "Статус"],
                         [{
                             "Код": app["code"],
                             "Локация": app["location"],
                             "Дата установки": app["install_date"],
                             "Статус": app["status"]
                         } for app in self.apparatuses])
        self.notebook.add(frame_app, text="Аппараты")

        # Вкладка для ламп
        frame_lamps = ttk.Frame(self.notebook)
        self.create_table(frame_lamps, "Лампы", 
                         ["Название", "Тип", "Вольтаж", "Цена"],
                         [{
                             "Название": lamp.name,
                             "Тип": lamp.type,
                             "Вольтаж": lamp.voltage,
                             "Цена": lamp.price
                         } for lamp in self.lamps])
        self.notebook.add(frame_lamps, text="Лампы")

        # Вкладка для сотрудников
        frame_emp = ttk.Frame(self.notebook)
        self.create_table(frame_emp, "Сотрудники", 
                         ["ФИО", "Должность", "Телефон", "ИНН"],
                         [{
                             "ФИО": emp.FIO,
                             "Должность": emp.post,
                             "Телефон": emp.phoneNumber,
                             "ИНН": emp.INN
                         } for emp in self.employees])
        self.notebook.add(frame_emp, text="Сотрудники")

    def create_table(self, parent, title, columns, data):
        # Заголовок
        label = Label(parent, text=title, font=('Arial', 14, 'bold'))
        label.pack(pady=10)

        # Таблица
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        # Настройка столбцов
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=CENTER)
        
        # Добавление данных
        for item in data:
            tree.insert('', END, values=[item[col] for col in columns])
        
        # Скроллбар
        scroll = ttk.Scrollbar(parent, orient=VERTICAL, command=tree.yview)
        tree.configure(yscroll=scroll.set)
        scroll.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True)



if __name__ == "__main__":
    root = Tk()
    app = MainApp(root)
    root.mainloop()