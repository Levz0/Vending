from tkinter import ttk, Tk
from tkinter.messagebox import showerror, showwarning, showinfo
import tkinter.font as tkFont
from tkinter import *
import random
from datetime import datetime, time
from tkcalendar import DateEntry


import os
import sys

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
        self.db.connect()
        
        # Получение данных должностей
        self.posts = []
        self.db.cursor.execute("Select * from Post")
        result = self.db.cursor.fetchall()
        for post in result:
            id_post = post[0]
            name = post[1]
            self.posts.append(Post(id_post, name))        
        
        # Получение данных типов ламп
        self.lamp_types = []
        self.db.cursor.execute("Select * from Lamp_Type")
        result = self.db.cursor.fetchall()
        for lamp_type in result:
            id_type = lamp_type[0]
            name = lamp_type[1]
            self.lamp_types.append(LampType(id_type, name))
            
        # Получение данных локаций
        self.locations = []
        self.db.cursor.execute("Select * from location")
        result = self.db.cursor.fetchall()
        for location in result:
            id_loc = location[0]
            name_object = location[1]
            address = location[2]
            self.locations.append(Location(id_loc, name_object, address))
            
        # Получение данных аппаратов   
        self.vendors = []
        self.db.cursor.execute("Select * from Vendors")
        result = self.db.cursor.fetchall()
        for vendor in result:
            id_vendor = vendor[0]
            name = vendor[1]
            description = vendor[2]
            self.vendors.append(Vendor(id_vendor, name, description))
            
        # Получение данных сотрудников
        self.employees = []
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
            location = Location(location[0],location[1], location[2])  
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
            vendor_usage = next((vu for vu in self.vendor_usages if vu.code == refill[2]), None)
            date = refill[3]
            self.refills.append(Refill(code, employee, vendor_usage, date))
            
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
            ("Аппарат", "vendor"),
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
            ("Дата ремонта", "resolution_date")
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
            if action == "Добавить":
                ttk.Button(control_frame, 
                        text=action, 
                        style="Primary.TButton",
                        command=lambda: self.open_add_form(self.notebook.index(self.notebook.select()))).pack(side=LEFT, padx=5)
            else:
                ttk.Button(control_frame, 
                        text=action, 
                   style="Primary.TButton").pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Отчеты", style="Primary.TButton", command=self.open_reports_window).pack(side=LEFT, padx=5)
    import tkinter.font as tkFont

    def open_add_form(self, current_tab_index):
        tab_name = self.notebook.tab(current_tab_index, "text")
        
        match tab_name:
            case "Аппараты":
                self.show_add_vendor_usage_form()
            case "Лампы":
                self.show_add_lamp_form()
            case "Сотрудники":
                self.show_add_employee_form()
            case "Заправки":
                self.show_add_refill_form()
            case "Неполадки":
                self.show_add_malfunction_form()  
            case "Продажи":
                self.show_add_sale_form()
            case _:
                print("Неизвестная вкладка для добавления")


    # Форма для добавления аппаратов (Vendor_usage)
    def show_add_vendor_usage_form(self):
        form = Toplevel(self.root)
        form.title("Добавление автомата (Vendor_usage)")
        form.geometry("430x350")
        frame = ttk.Frame(form)
        frame.grid(padx=10, pady=10)
        
        # Выбор модели аппарата
        ttk.Label(frame, text="Модель аппарата").grid(row=0, column=0, sticky="w", pady=5)
        entry_vendor = ttk.Combobox(frame, state="readonly", values=[vendor.name for vendor in self.vendors])
        entry_vendor.grid(row=0, column=1, pady=5, sticky="ew")
        
        # Выбор даты установки. Указываем формат ГГГГ-ММ-ДД для соответствия формату в БД.
        ttk.Label(frame, text="Дата установки (ГГГГ-ММ-ДД):").grid(row=1, column=0, sticky="w", pady=5)
        entry_install_date = DateEntry(frame,
                                    date_pattern='yyyy-MM-dd',
                                    locale='ru_RU', state="readonly", maxdate=datetime.now())
        entry_install_date.grid(row=1, column=1, pady=5, sticky="ew")
        
        # Выбор локации
        ttk.Label(frame, text="Локация:").grid(row=2, column=0, sticky="w", pady=5)
        entry_location = ttk.Combobox(frame, state="readonly", values=[loc.name for loc in self.locations])
        entry_location.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Выбор статуса
        ttk.Label(frame, text="Статус (Активен/Неактивен/В обслуживании):").grid(row=3, column=0, sticky="w", pady=5)
        entry_status = ttk.Combobox(frame, state="readonly", values=["Активен", "Неактивен", "В обслуживании"])
        entry_status.grid(row=3, column=1, pady=5, sticky="ew")
        
        def save_vendor_usage():
            # Получаем выбранное имя аппарата
            vendor_name = entry_vendor.get()
            # Ищем объект Vendor по имени
            selected_vendor = next((vendor for vendor in self.vendors if vendor.name == vendor_name), None)
            if not selected_vendor:
                print("Выберите корректную модель аппарата")
                return
            # Получаем дату установки
            install_date = entry_install_date.get()  # формат: yyyy-mm-dd
            # Получаем выбранное имя локации
            location_name = entry_location.get()
            # Ищем объект Location по имени
            selected_location = next((loc for loc in self.locations if loc.name == location_name), None)
            if not selected_location:
                print("Выберите корректную локацию")
                return

            # Получаем статус
            status = entry_status.get()
            
            # Формируем SQL-запрос для вставки записи в таблицу Vendor_usage.
            # Предполагается, что в таблице Vendor_usage столбцы:
            # id_vendor, Install_date, id_location, Status.
            query = (
                f"INSERT INTO Vendor_usage (id_vendor, Install_date, id_location, Status) "
                f"VALUES ({selected_vendor.code}, '{install_date}', {selected_location.code}, '{status}')"
            )
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()  # Фиксируем изменения в базе
                print("Запись успешно добавлена")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.vendor_tab)
                showinfo("Добавление данных", f"Аппарат {vendor_name} в {location_name} добавлен успешно!")
            except Exception as e:
                print("Ошибка при добавлении:", e)
            form.destroy()
        
        save_button = ttk.Button(frame, text="Сохранить", command=save_vendor_usage)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        form.mainloop()




    # Форма для добавления лампы
    def show_add_lamp_form(self):
        form = Toplevel(self.root)
        form.title("Добавление лампы")
        form.geometry("400x400")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Артикул:").grid(row=0, column=0, sticky="w", pady=5)
        entry_article = ttk.Entry(frame)
        entry_article.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Название:").grid(row=1, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(frame)
        entry_name.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Тип лампы ").grid(row=6, column=0, sticky="w", pady=5)
        entry_type = ttk.Combobox(frame, state="readonly", values=[lamp_type.name for lamp_type in self.lamp_types])        
        entry_type.grid(row=6, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Напряжение:").grid(row=2, column=0, sticky="w", pady=5)
        entry_voltage = ttk.Entry(frame)
        entry_voltage.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цветовая температура:").grid(row=3, column=0, sticky="w", pady=5)
        entry_colorTemp = ttk.Entry(frame)
        entry_colorTemp.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цена:").grid(row=4, column=0, sticky="w", pady=5)
        entry_price = ttk.Entry(frame)
        entry_price.grid(row=4, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Описание:").grid(row=5, column=0, sticky="w", pady=5)
        text_description = Text(frame, width=25, height=5, wrap="word")  # height=5 означает 5 строк текста
        text_description.grid(row=5, column=1, pady=6, sticky="ew")

        # Если нужно имитировать вид ttk.Entry:
        text_description.configure(
            relief="solid",  # Граница как у Entry
            borderwidth=1,
            highlightthickness=0,
            padx=2, pady=2
        )
        
        def save_lamp():
            article = entry_article.get().strip()
            name = entry_name.get().strip()
            lamp_type_name = entry_type.get().strip()
            selected_lamp_type = next((lt for lt in self.lamp_types if lt.name == lamp_type_name), None)
            if not selected_lamp_type:
                showerror("Ошибка", "Выберите корректный тип лампы")
                return
            try:
                voltage = float(entry_voltage.get())
                colorTemp = float(entry_colorTemp.get())
                price = float(entry_price.get())
            except ValueError:
                showerror("Ошибка", "Введите числовые значения для напряжения, цветовой температуры и цены")
                return
            description = text_description.get("1.0", END).strip()
            
            query = (
                "INSERT INTO Lamps (article, Name, Voltage, ColorTemp, Price, Description, id_type) "
                f"VALUES ('{article}', '{name}', {voltage}, {colorTemp}, {price}, '{description}', {selected_lamp_type.code})"
            )
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Лампа успешно добавлена!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.lamp_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при добавлении лампы: {e}")
            form.destroy()
                
        ttk.Button(form, text="Сохранить", command=save_lamp).pack(pady=10)
        form.mainloop()


    # Форма для добавления сотрудника
    def show_add_employee_form(self):
        form = Toplevel(self.root)
        form.title("Добавление сотрудника")
        form.geometry("400x400")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="ФИО:").grid(row=0, column=0, sticky="ew", pady=5)
        entry_FIO = ttk.Entry(frame)
        entry_FIO.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Должность:").grid(row=1, column=0, sticky="w", pady=5)
        entry_post = ttk.Combobox(frame, state="readonly", values=[post for post in self.posts])
        entry_post.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата рождения:").grid(row=2, column=0, sticky="w", pady=5)
        entry_birth_date = DateEntry(frame, 
                                       date_pattern = 'yyyy-MM-dd',
                                       locale = 'ru_RU', state = "readonly", maxdate = datetime.now())
        entry_birth_date.grid(row=2, column=1, pady=5, sticky="ew") 
        
        ttk.Label(frame, text="ИНН:").grid(row=3, column=0, sticky="w", pady=5)
        entry_INN = ttk.Entry(frame)
        entry_INN.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Телефон:").grid(row=4, column=0, sticky="w", pady=5)
        entry_phone = ttk.Entry(frame)
        entry_phone.grid(row=4, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Логин:").grid(row=5, column=0, sticky="w", pady=5)
        entry_login = ttk.Entry(frame)
        entry_login.grid(row=5, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Пароль:").grid(row=6, column=0, sticky="w", pady=5)
        entry_password = ttk.Entry(frame)
        entry_password.grid(row=6, column=1, pady=5, sticky="ew")
        
        def save_employee():
            FIO = entry_FIO.get().strip()
            post_name = entry_post.get().strip()
            # Ищем объект Post по строковому представлению
            selected_post = next((post for post in self.posts if str(post) == post_name), None)
            if not selected_post:
                print("Выберите корректную должность")
                return
            birth_date = entry_birth_date.get()  # в формате yyyy-MM-dd
            INN = entry_INN.get().strip()
            phone = entry_phone.get().strip()
            login = entry_login.get().strip()
            password = entry_password.get().strip()
            
            # Формируем SQL-запрос. Предполагается, что поле id (TAB) автоинкрементное.
            query = (
                "INSERT INTO Employee (FIO, id_post, BirthDate, INN, phoneNumber, login, password) "
                f"VALUES ('{FIO}', {selected_post.code}, '{birth_date}', '{INN}', '{phone}', '{login}', '{password}')"
            )
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                print("Сотрудник успешно добавлен")
                self.fetch_data()        # обновляем данные в памяти
                self.refresh_widgets()   # пересоздаем интерфейс
                self.notebook.select(self.employee_tab)
            except Exception as e:
                print("Ошибка при добавлении сотрудника:", e)
            form.destroy()
            
        ttk.Button(frame, text="Сохранить", command=save_employee).grid(row=7, column=0, columnspan=2, pady=10)

        form.mainloop()


    # Форма для добавления заправки (Refill) с табличной частью (Lamp_Refills)
    def show_add_refill_form(self):
        form = Toplevel(self.root)
        form.title("Добавление заправки")
        form.geometry("500x700")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Сотрудник:").grid(row=0, column=0, sticky="w", pady=5)
        entry_employee = ttk.Combobox(frame, values=[employee for employee in self.employees], width=50)
        entry_employee.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Аппарат:").grid(row=1, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Combobox(frame, values=[vendor_usage for vendor_usage in self.vendor_usages])
        entry_vendor_usage.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, sticky="w", pady=5)
        entry_date = DateEntry(frame,
                        date_pattern='yyyy-MM-dd ',
                        locale='ru_RU', state="readonly", maxdate=datetime.now())
        entry_date.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Табличная часть для Lamp_Refills
        ttk.Label(form, text="Табличная часть: данные для Lamp_Refills", font=("Segoe UI", 10, "bold")).pack(pady=5)
        table_frame = ttk.Frame(form)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("id_lamp", "quantity", "price")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(side="left", fill="both", expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        
        ttk.Button(form, text="Добавить строку в табличную часть", command=lambda: self.add_lamp_refill_row(tree)).pack(pady=5)
        
        ttk.Button(form, text="Сохранить", command=lambda: print("Сохранение заправки с табличной частью")).pack(pady=10)
        form.mainloop()


    # Форма для добавления неполадки
    def show_add_malfunction_form(self):
        form = Toplevel(self.root)
        form.title("Добавление неполадки")
        form.geometry("500x400")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="ID типа неполадки:").grid(row=0, column=0, sticky="w", pady=5)
        entry_type = ttk.Entry(frame)
        entry_type.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Код аппарата:").grid(row=1, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Entry(frame)
        entry_vendor_usage.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Таб.номер сотрудника (опционально):").grid(row=2, column=0, sticky="w", pady=5)
        entry_employee = ttk.Entry(frame)
        entry_employee.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Статус (Новая/В процессе/Решена):").grid(row=3, column=0, sticky="w", pady=5)
        entry_status = ttk.Entry(frame)
        entry_status.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Причина:").grid(row=4, column=0, sticky="w", pady=5)
        entry_reason = ttk.Entry(frame)
        entry_reason.grid(row=4, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата возникновения (ГГГГ-ММ-ДД):").grid(row=5, column=0, sticky="w", pady=5)
        entry_report_date = ttk.Entry(frame)
        entry_report_date.grid(row=5, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата ремонта (ГГГГ-ММ-ДД, опционально):").grid(row=6, column=0, sticky="w", pady=5)
        entry_resolution_date = ttk.Entry(frame)
        entry_resolution_date.grid(row=6, column=1, pady=5, sticky="ew")
        
        ttk.Button(form, text="Сохранить", command=lambda: print("Сохранение неполадки")).pack(pady=10)
        form.mainloop()


    # Форма для добавления продажи
    def show_add_sale_form(self):
        form = Toplevel(self.root)
        form.title("Добавление продажи")
        form.geometry("400x350")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Код аппарата (Vendor_usage):").grid(row=0, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Entry(frame)
        entry_vendor_usage.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Код лампы:").grid(row=1, column=0, sticky="w", pady=5)
        entry_lamp = ttk.Entry(frame)
        entry_lamp.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цена:").grid(row=2, column=0, sticky="w", pady=5)
        entry_price = ttk.Entry(frame)
        entry_price.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky="w", pady=5)
        entry_date = ttk.Entry(frame)
        entry_date.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Button(form, text="Сохранить", command=lambda: print("Сохранение продажи")).pack(pady=10)
        form.mainloop()


    def add_lamp_refill_row(self, tree):
        # Открываем небольшое окно для ввода одной строки для Lamp_Refills
        row_win = Toplevel(self.root)
        row_win.title("Добавить строку")
        row_win.geometry("300x300")
        
        ttk.Label(row_win, text="Код лампы:").pack(pady=5)
        entry_id_lamp = ttk.Entry(row_win)
        entry_id_lamp.pack(pady=5)
        
        ttk.Label(row_win, text="Количество:").pack(pady=5)
        entry_quantity = ttk.Entry(row_win)
        entry_quantity.pack(pady=5)
        
        ttk.Label(row_win, text="Цена:").pack(pady=5)
        entry_price = ttk.Entry(row_win)
        entry_price.pack(pady=5)
        
        def add_row():
            row_values = (entry_id_lamp.get(), entry_quantity.get(), entry_price.get())
            tree.insert("", END, values=row_values)
            row_win.destroy()
            
        ttk.Button(row_win, text="Добавить", command=add_row).pack(pady=10)

    def refresh_widgets(self):
        # Удаляем все виджеты из главного окна
        for widget in self.root.winfo_children():
            widget.destroy()
        # Пересоздаём виджеты
        self.create_widgets()
   
            
    def create_tab(self, title, columns, data):
        """
        columns - список кортежей вида (Заголовок, имя_свойства)
        data - список объектов
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        match(title):
            case "Аппараты":
                self.vendor_tab = frame
            case "Лампы":
                self.lamp_tab = frame
            case "Сотрудники":
                self.employee_tab = frame
            case "Заправки":
                self.refill_tab = frame
            case "Неполадки":
                self.malfunction_tab = frame
            case "Продажи":
                self.sale_tab = frame
            
        
        
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
    root.iconbitmap("vendor.ico")
    app = MainApp(root)
    root.mainloop()