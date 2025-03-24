from tkinter import ttk, Tk
from tkinter import *
import random
from datetime import datetime, timedelta

# Цветовая схема
BG_COLOR = "#f8f9fa"
PRIMARY_COLOR = "#007bff"
SECONDARY_COLOR = "#6c757d"
HOVER_COLOR = "#0056b3"
TEXT_COLOR = "#212529"
FONT = ("Segoe UI", 10)
TABLE_HEADER_STYLE = {"background": PRIMARY_COLOR, "foreground": "white"}

# Импорт классов (предположим, что эти импорты нужны для других частей проекта)
from Directory.post import Post
from Directory.LampType import LampType
from Directory.employee import Employee
from Directory.Lamp import Lamp
from Directory.vendor import Vendor
from Directory.vendor_usage import Vendor_usage
from Documents.Refill import Refill
from db import DataBase

class MainApp:
    def __init__(self, root):
        self.host = "127.0.0.1"
        self.user = "root"
        self.password = ""
        self.database = "Vending"
        self.db = DataBase(self.host, self.user, self.password, self.database)
        self.root = root
        self.root.title("Vending Master Pro")
        self.root.geometry("1280x720")
        self.configure_styles()
        self.fetch_data()
        self.create_widgets()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Общие настройки стилей
        style.configure(".", background=BG_COLOR, font=FONT)
        style.configure("TNotebook", background=BG_COLOR)
        style.configure("TNotebook.Tab", 
                      background=SECONDARY_COLOR,
                      foreground="white",
                      padding=[15, 5],
                      font=FONT)
        style.map("TNotebook.Tab", 
                 background=[("selected", PRIMARY_COLOR)],
                 foreground=[("selected", "white")])
        
        # Стиль для кнопок
        style.configure("Primary.TButton", 
                       background=PRIMARY_COLOR,
                       foreground="white",
                       borderwidth=0,
                       padding=10)
        style.map("Primary.TButton",
                 background=[("active", HOVER_COLOR), ("disabled", "#ced4da")])
        
        # Стиль для таблиц
        style.configure("Treeview.Heading", **TABLE_HEADER_STYLE)
        style.configure("Treeview", 
                       rowheight=30,
                       background="#ffffff",
                       fieldbackground="#ffffff")

    def fetch_data(self):
        # Получение данных сотрудников
        self.employees = []
        self.db.connect()
        self.db.cursor.execute("Select * from Employee")
        result = self.db.cursor.fetchall()
        for employee in result:
            TAB = employee[0]
            FIO = employee[1]
            self.db.cursor.execute(f"SELECT Name FROM Post WHERE id = {employee[2]}")   
            post = self.db.cursor.fetchone()[0]
            birthDate = employee[3]
            INN = employee[4]
            phoneNumber = employee[5]
            login = employee[6]
            password = employee[7]
            self.employees.append(Employee(TAB, FIO, post, birthDate, INN, phoneNumber, login, password))
        
         # Получение данных ламп
        self.lamps = []
        self.db.cursor.execute("Select * from Lamps")
        result = self.db.cursor.fetchall()
        for lamp in result:
            code = lamp[0]
            article = lamp[1]
            name = lamp[2]
            self.db.cursor.execute(f"SELECT Name FROM Lamp_Type WHERE id = {lamp[7]}")   
            lamp_type = self.db.cursor.fetchone()[0]            
            voltage = lamp[3]
            colorTemp = lamp[4]
            price = lamp[5]
            description = lamp[6]
            self.lamps.append(Lamp(code, article, name, lamp_type, voltage, colorTemp, price, description))
        
        # Получение данных аппаратов в эксплуатации
        self.vendor_usages = []
        self.db.cursor.execute("Select * from Vendor_usage")
        result = self.db.cursor.fetchall()
        for vendor_usages in result:
            code = vendor_usages[0]
            self.db.cursor.execute(f"SELECT Name FROM Vendors WHERE id = {vendor_usages[1]}")   
            vendor = self.db.cursor.fetchone()[0]   
            install_date = vendor_usages[2]
            self.db.cursor.execute(f"SELECT Name FROM Location WHERE id = {vendor_usages[3]}")   
            location = self.db.cursor.fetchone()[0]   
            status = vendor_usages[4]
            self.vendor_usages.append(Vendor_usage(code, vendor, install_date, location, status))


        # Получение данных заправок  
        self.refills = []
        self.db.cursor.execute("Select * from Refill")
        result = self.db.cursor.fetchall()    
        for refill in result:
            code = refill[0]
            self.db.cursor.execute(f"SELECT FIO FROM Employee WHERE id = {refill[1]}")   
            employee = self.db.cursor.fetchone()[0]  
            self.db.cursor.execute(f"Select Name from Vendors where id = (Select id_vendor from Vendor_usage where id = {refill[2]})")   
            vendor = self.db.cursor.fetchone()[0]    
            date = refill[3]
            self.refills.append(Refill(code, employee, vendor, date))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Ноутбук с вкладками
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)

        # Вкладка "Аппараты" (на основе Vendor_usage)
        apparatus_columns = [
            ("Код", "code"),
            ("Вендор", "vendor"),
            ("Дата установки", "install_date"),
            ("Локация", "location"),
            ("Статус", "status")
        ]
        self.create_tab("Аппараты", apparatus_columns, self.vendor_usages)
        
        # Вкладка "Лампы"
        lamp_columns = [
            ("Код", "code"),
            ("Артикул", "article"),
            ("Название", "name"),
            ("Тип", "type"),
            ("Вольтаж", "voltage"),
            ("Цветовая температура", "colorTemp"),
            ("Цена", "price"),
            ("Описание", "description")
        ]
        self.create_tab("Лампы", lamp_columns, self.lamps)
        
        # Вкладка "Сотрудники"
        employee_columns = [
            ("Табельный номер", "TAB"),
            ("ФИО", "FIO"),
            ("Должность", "post"),
            ("Дата рождения", "birthDate"),
            ("ИНН", "INN"),
            ("Телефон", "phoneNumber"),
            ("Логин", "login"),
            ("Пароль", "password")
        ]
        self.create_tab("Сотрудники", employee_columns, self.employees)


        # Вкладка "Заправки"
        refill_columns = [
            ("Код", "code"),
            ("ФИО сотрудника", "employee"),
            ("Аппарат", "vendor_usage"),
            ("Дата", "date")
        ]
        self.create_tab("Заправки", refill_columns, self.refills)
        
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=X, pady=10)
        
        actions = ["Добавить", "Редактировать", "Удалить", "Обновить", "Экспорт"]
        for action in actions:
            ttk.Button(control_frame, 
                       text=action, 
                       style="Primary.TButton").pack(side=LEFT, padx=5)

    def create_tab(self, title, columns, data):
        """
        columns - список кортежей вида (Заголовок, имя_свойства)
        data - список объектов
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        
        # Таблица
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Извлекаем только заголовки для Treeview
        col_headers = [col[0] for col in columns]
        tree = ttk.Treeview(tree_frame, columns=col_headers, show='headings', height=15)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        # Настройка колонок
        for header, attr in columns:
            tree.heading(header, text=header, anchor=CENTER)
            tree.column(header, width=150, anchor=CENTER)
        
        # Заполнение данными
        for item in data:
            row = []
            for header, attr in columns:
                value = getattr(item, attr, "")
                # Если значение является объектом, выводим его строковое представление
                if not isinstance(value, (str, int, float)):
                    value = str(value)
                row.append(value)
            tree.insert('', END, values=row)
        
        vsb.pack(side=RIGHT, fill="y")
        tree.pack(side=LEFT, fill=BOTH, expand=True)


if __name__ == "__main__":
    root = Tk()
    app = MainApp(root)
    root.mainloop()