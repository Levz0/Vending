from tkinter import ttk, Tk
import tkinter.font as tkFont
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

# Импорт классов
from Directory.post import Post
from Directory.LampType import LampType
from Directory.employee import Employee
from Directory.Lamp import Lamp
from Directory.vendor import Vendor
from Directory.vendor_usage import Vendor_usage
from Directory.Location import Location

from Documents.Refill import Refill
from Documents.Malfunction import Malfunction
from Documents.Sale import Sale

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
            self.db.cursor.execute(f"SELECT * FROM Post WHERE id = {employee[2]}")   
            post = self.db.cursor.fetchone()
            post = Post(post[0], post[1])
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
            self.db.cursor.execute(f"SELECT * FROM Lamp_Type WHERE id = {lamp[7]}")   
            lamp_type = self.db.cursor.fetchone()
            lamp_type = LampType(lamp_type[0], lamp_type[1])
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
            self.db.cursor.execute(f"SELECT * FROM Vendors WHERE id = {vendor_usages[1]}")   
            vendor = self.db.cursor.fetchone()   
            vendor = Vendor(vendor[0], vendor[1], vendor[2])
            install_date = vendor_usages[2]
            self.db.cursor.execute(f"SELECT * FROM Location WHERE id = {vendor_usages[3]}")   
            location = self.db.cursor.fetchone()
            location = Location(location[0],location[1])  
            status = vendor_usages[4]
            self.vendor_usages.append(Vendor_usage(code, vendor, install_date, location, status))

        # Получение данных заправок  
        self.refills = []
        self.db.cursor.execute("Select * from Refill")
        result = self.db.cursor.fetchall()    
        for refill in result:
            code = refill[0]
            self.db.cursor.execute(f"SELECT * from Employee WHERE id = {refill[1] }")   
            employee = self.db.cursor.fetchone()
            employee = Employee(employee[0], employee[1], employee[2], employee[3], employee[4], employee[5], employee[6], employee[7])
            self.db.cursor.execute(f"Select * from Vendors where id = (Select id_vendor from Vendor_usage where id = {refill[2]})")   
            vendor = self.db.cursor.fetchone()
            vendor = Vendor(vendor[0], vendor[1], vendor[2])    
            date = refill[3]
            self.refills.append(Refill(code, employee, vendor, date))
            
        # Получение данных неполадок  
        self.malfunctions = []
        self.db.cursor.execute("SELECT * FROM Malfunctions")
        result = self.db.cursor.fetchall()    
        for malfunction in result:
            code = malfunction[0]
            self.db.cursor.execute(f"SELECT Name FROM Malfunction_Type WHERE id = {malfunction[1] }") 
            malfunction_type = self.db.cursor.fetchone()[0]    
            self.db.cursor.execute(f"SELECT Name FROM Vendors WHERE id = (SELECT id_vendor FROM Vendor_usage WHERE id = {malfunction[2]})")   
            vendor_usage = self.db.cursor.fetchone()[0]
            
            # Проверяем, существует ли id_employee
            if malfunction[3] is not None:
                self.db.cursor.execute(f"SELECT * FROM Employee WHERE id = {malfunction[3]}")
                emp_data = self.db.cursor.fetchone()
                if emp_data:
                    employee = Employee(emp_data[0], emp_data[1], emp_data[2], emp_data[3], emp_data[4], emp_data[5], emp_data[6], emp_data[7])
                else:
                    employee = "-"
            else:
                employee = "-"

            status = malfunction[4]
            reason = malfunction[5]
            report_date = malfunction[6]
            resolution_date = malfunction[7]
            if (resolution_date is None):
                resolution_date = "-"
            self.malfunctions.append(Malfunction(code, malfunction_type, vendor_usage, employee, status, reason, report_date, resolution_date))

             # Получение данных продаж
        self.sales = []
        self.db.cursor.execute("SELECT * FROM Sale")
        result = self.db.cursor.fetchall()
        for sale in result:
            code = sale[0]
            # Получаем вендор использования (аппарат) по id_vendor_usage
            self.db.cursor.execute(
                f"SELECT Name FROM Vendors WHERE id = (SELECT id_vendor FROM Vendor_usage WHERE id = {sale[1]})"
            )
            vendor_usage = self.db.cursor.fetchone()[0]
            # Получаем лампу по id_lamp
            self.db.cursor.execute(f"SELECT Name FROM Lamps WHERE id = {sale[2]}")
            lamp = self.db.cursor.fetchone()[0]
            price = sale[3]
            date = sale[4]
            self.sales.append(Sale(code, vendor_usage, lamp, price, date))
            
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
            ("Номер заправки", "code"),
            ("ФИО сотрудника", "employee"),
            ("Аппарат", "vendor_usage"),
            ("Дата", "date")
        ]
        self.create_tab("Заправки", refill_columns, self.refills)
        
        # Вкладка "Неполадки"
        malfunction_columns = [
            ("Номер неполадки", "code"),
            ("Тип неполадки", "malfunction_type"),
            ("Мастер по ремонту", "employee"),
            ("Статус", "status"),
            ("Аппарат", "vendor_usage"),
            ("Причина возникновения", "reason"),
            ("Дата возникновения", "report_date"),
            ("Дата починки", "resolution_date")
        ]
        self.create_tab("Неполадки", malfunction_columns, self.malfunctions)
        
        # Вкладка "Продажи" - новая вкладка
        sale_columns = [
            ("Номер продажи", "code"),
            ("Аппарат", "vendor_usage"),
            ("Лампа", "lamp"),
            ("Цена", "price"),
            ("Дата", "date")
        ]
        self.create_tab("Продажи", sale_columns, self.sales)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=X, pady=10)
        
        actions = ["Добавить", "Редактировать", "Удалить", "Обновить"]
        for action in actions:
            ttk.Button(control_frame, 
                       text=action, 
                       style="Primary.TButton").pack(side=LEFT, padx=5)
            
        ttk.Button(control_frame, text="Отчеты", style="Primary.TButton", command=self.open_reports_window).pack(side=LEFT, padx=5)

    import tkinter.font as tkFont

    def create_tab(self, title, columns, data):
        """
        columns - список кортежей вида (Заголовок, имя_свойства)
        data - список объектов
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        
        # Фрейм для таблицы и скроллбаров
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Создаем горизонтальный и вертикальный скроллбары
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Извлекаем только заголовки для Treeview
        col_headers = [col[0] for col in columns]
        tree = ttk.Treeview(tree_frame, columns=col_headers, show='headings', height=15,
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        vsb.pack(side=RIGHT, fill="y")
        hsb.pack(side=BOTTOM, fill="x")
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Настройка колонок (начальная настройка, ширина будет скорректирована)
        for header, attr in columns:
            tree.heading(header, text=header, anchor=CENTER)
            tree.column(header, width=150, anchor=CENTER)
        
        # Заполнение данными
        for item in data:
            row = []
            for header, attr in columns:
                value = getattr(item, attr, "")
                if not isinstance(value, (str, int, float)):
                    value = str(value)
                row.append(value)
            tree.insert('', END, values=row)
        
        # Автоматическая регулировка ширины столбцов по содержимому
        # Создаем объект шрифта, соответствующий используемому шрифту
        tree_font = tkFont.Font(font=FONT)
        for col in col_headers:
            # Начинаем с ширины заголовка
            max_width = tree_font.measure(col)
            # Перебираем все строки в столбце
            for item in tree.get_children():
                cell_text = tree.set(item, col)
                cell_width = tree_font.measure(cell_text)
                if cell_width > max_width:
                    max_width = cell_width
            # Добавляем небольшой отступ (например, 10 пикселей)
            tree.column(col, width=max_width + 10)

    def open_reports_window(self):
        from report import ReportsWindow
        ReportsWindow(self.root)

if __name__ == "__main__":
    root = Tk()
    root.resizable(0, 0)
    app = MainApp(root)
    root.mainloop()