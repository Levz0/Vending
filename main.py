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
from entities.post import Post
from entities.LampType import LampType
from entities.employee import Employee
from entities.Lamp import Lamp
from entities.vendor import Vendor
from entities.vendor_usage import Vendor_usage


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vending Master Pro")
        self.root.geometry("1280x720")
        self.configure_styles()
        self.generate_data()
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

    def generate_data(self):
        # Генерация данных для сотрудников
        self.employees = []
        for i in range(1, 6):
            FIO = f"Сотрудник {i}"
            post = Post(random.choice(["Менеджер", "Техник", "Администратор"]))
            birthDate = (datetime.now() - timedelta(days=365*random.randint(25,50))).strftime("%Y-%m-%d")
            INN = f"{random.randint(1000000000, 9999999999)}"
            phoneNumber = f"+7 900 123456{i}"
            login = f"user{i}"
            password = f"pass{i}"
            self.employees.append(Employee(FIO, post, birthDate, INN, phoneNumber, login, password))
        
        # Генерация данных для ламп
        self.lamps = []
        lamp_types = [LampType("LED"), LampType("Галогенная"), LampType("Люминесцентная")]
        for i in range(1, 6):
            name = f"Лампа {i}"
            lamp_type = random.choice(lamp_types)
            voltage = random.choice([110, 220])
            colorTemp = random.choice(["Тёплый", "Нейтральный", "Холодный"])
            price = random.randint(100, 500)
            description = f"Описание лампы {i}"
            self.lamps.append(Lamp(name, lamp_type, voltage, colorTemp, price, description))
        
        # Генерация данных для аппаратов (используем Vendor_usage)
        self.vendor_usages = []
        vendors = [Vendor(f"V-{i:03d}", f"Вендор {i}", "Описание") for i in range(1, 4)]
        locations = ["Локация 1", "Локация 2", "Локация 3"]
        for i in range(1, 6):
            code = f"APP-{i:03d}"
            vendor = random.choice(vendors)
            install_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            location = random.choice(locations)
            status = random.choice(["Активен", "Неактивен", "В обслуживании"])
            self.vendor_usages.append(Vendor_usage(code, vendor, install_date, location, status))

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
            ("ФИО", "FIO"),
            ("Должность", "post"),
            ("Дата рождения", "birthDate"),
            ("ИНН", "INN"),
            ("Телефон", "phoneNumber"),
            ("Логин", "login"),
            ("Пароль", "password")
        ]
        self.create_tab("Сотрудники", employee_columns, self.employees)

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