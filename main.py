from tkinter import ttk, Tk, Entry, StringVar, messagebox
from tkinter.messagebox import showerror, showwarning, showinfo
import tkinter.font as tkFont
from tkinter import *
import tkinter as tk
import random
from datetime import datetime, time
from tkcalendar import DateEntry
import subprocess
import sys
from fpdf import FPDF
import os

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
from Directory.malfunction_type import Malfunction_Type
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

    def is_valid_number(value):
        return value.isdigit() or value == ""
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
            
        # Получение данных типов неполадок
        self.malfunction_types = []
        self.db.cursor.execute("Select * from Malfunction_Type")
        result = self.db.cursor.fetchall()
        for mal_type in result:
            id_maltype = mal_type[0]
            name = mal_type[1]
            self.malfunction_types.append(Malfunction_Type(id_maltype, name))
            
            
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
        self.tabs = {}
        # Ноутбук с вкладками
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=True)

        # Вкладка Должности
        posts_columns = [
            ("Код", "code"),
            ("Название", "name")
        ]
        self.create_tab("Должности", posts_columns, self.posts)
        
        # Вкладка типов ламп
        lamp_types_columns = [
            ("Код", "code"),
            ("Название", "name")
        ]
        self.create_tab("Типы ламп", lamp_types_columns, self.lamp_types)
        
        # Вкладка типов неисправностей
        malfunction_types_columns = [
            ("Код", "code"),
            ("Название", "name")
        ]
        self.create_tab("Типы неисправностей", malfunction_types_columns, self.malfunction_types)
        
        # Вкладка локаций
        locations_columns = [
            ("Код", "code"),
            ("Название объекта", "name"),
            ("Адрес", "address")
        ]
        self.create_tab("Локации", locations_columns, self.locations)
        
         # Вкладка локаций
        vendors_columns = [
            ("Код", "code"),
            ("Модель аппарата", "name"),
            ("Описание", "description")
        ]
        self.create_tab("Модели аппаратов", vendors_columns, self.vendors)
        
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
        
        for child in self.notebook.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, ttk.Treeview):
                    widget.bind("<ButtonRelease-1>", self.open_edit_form)
                    
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=X, pady=10)
        
        actions = ["Добавить", "Редактировать", "Удалить"]
        for action in actions:
            if action == "Добавить":
                ttk.Button(control_frame, 
                           text=action, 
                           style="Primary.TButton",
                           command=lambda: self.open_add_form(self.notebook.index(self.notebook.select()))
                           ).pack(side=LEFT, padx=5)
            elif action == "Редактировать":
                ttk.Button(control_frame, 
                           text=action, 
                           style="Primary.TButton",
                           command=self.edit_selected
                           ).pack(side=LEFT, padx=5)
            elif action == "Удалить":
                ttk.Button(control_frame, 
                           text=action, 
                           style="Primary.TButton",
                           command=self.delete_row).pack(side=LEFT, padx=5)
            else:
                ttk.Button(control_frame, 
                           text=action, 
                           style="Primary.TButton"
                           ).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Отчеты", style="Primary.TButton", command=self.open_reports_window).pack(side=LEFT, padx=5)
        ttk.Button(control_frame, text="Печать заправки", style="Primary.TButton",
           command=self.print_selected_refill).pack(side=LEFT, padx=5)

    import tkinter.font as tkFont

    def open_add_form(self, current_tab_index):
        tab_name = self.notebook.tab(current_tab_index, "text")
        
        match tab_name:
            case "Должности":
                self.show_add_post_form()
            case "Типы ламп":
                self.show_add_lamp_type_form()
            case "Типы неисправностей":
                self.show_add_malfunctiontype_form()
            case "Локации":
                self.show_add_location_form()
            case "Модели аппаратов":
                self.show_add_vendor_form()
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
    def delete_row(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        
        def find_treeview(widget):
            if isinstance(widget, ttk.Treeview):
                return widget
            for child in widget.winfo_children():
                result = find_treeview(child)
                if result:
                    return result
            return None
        
        tree = find_treeview(current_tab)
        item_id = tree.focus()
        if not item_id: 
            showwarning("Внимание", "Выберите элемент для удаления")
            return
        
        values = tree.item(item_id)['values']
        if not messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            return 
        
        match(tab_name):
            case "Должности":
                try:
                    self.db.cursor.execute(f"delete from Post where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Должность успешно удалена!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить должность, которая фигурирует у сотрудников!")
            case "Типы ламп":
                try:
                    self.db.cursor.execute(f"delete from Lamp_type where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Тип лампы успешно удален!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить тип лампы, который фигурирует в лампах!")
            case "Типы неисправностей":
                showinfo("", "В разработке!")
            case "Локации":
                try:
                    self.db.cursor.execute(f"delete from location where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Локация успешно удалена!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить локацию, к которой уже привязан аппарат!") 
            case "Модели аппаратов":
                try:
                    self.db.cursor.execute(f"delete from Vendors where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Модель аппарата успешно удалена!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить уже использованную модель аппарата!")           
            case "Аппараты":
                try:
                    self.db.cursor.execute(f"delete from Vendor_usage where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Аппарат успешно удален!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить аппарат, который фигурирует в документах!")
            case "Лампы":
                try:
                    self.db.cursor.execute(f"delete from Lamps where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Лампа успешно удалена!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить лампу, которая используется в документах!")
            case "Сотрудники":
                try:
                    self.db.cursor.execute(f"delete from Employee where id={values[0]}")
                    self.db.connection.commit()
                    tree.delete(item_id)
                    messagebox.showinfo("Успешно!", "Сотрудник успешно удален!")
                except:
                    messagebox.showerror("Ошибка!", "Невозможно удалить сотрудника, который фигурирует в документах!")
            case "Заправки":
                pass
            case "Неполадки":
                pass
            case "Продажи":
                pass
        
    
    
    def edit_selected(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        
        def find_treeview(widget):
            if isinstance(widget, ttk.Treeview):
                return widget
            for child in widget.winfo_children():
                result = find_treeview(child)
                if result:
                    return result
            return None

        tree = find_treeview(current_tab)

        if tree is None:
            showerror("Ошибка", "Не найден виджет таблицы!")
            return

        item_id = tree.focus()
        if not item_id:
            showwarning("Внимание", "Выберите строку для редактирования")
            return
        
        values = tree.item(item_id)['values']
        match(tab_name):
            case "Аппараты":
                self.open_edit_vendor_form(values)
            case "Лампы":
                self.open_edit_lamp_form(values)
            case "Сотрудники":
                self.open_edit_employee_form(values)
            case "Заправки":
                self.open_edit_refill_form(values)
            case "Неполадки":
                self.open_edit_malfunction_form(values)
            case "Продажи":
                self.open_edit_sale_form(values)
    
    # Формы редактирования    
    def open_edit_vendor_form(self, values):
        form = Toplevel(self.root)
        form.title("Редактирование аппарата")
        form.geometry("400x300")
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Модель аппарата:").grid(row=0, column=0, sticky="w", pady=5)
        entry_vendor = ttk.Combobox(frame, state="readonly", values=[vendor.name for vendor in self.vendors])
        # Здесь можно попытаться установить исходное значение: из values[1] можно извлечь часть строки,
        # но лучше, если в базе и представлении у объекта Vendor присутствует метод __str__.
        entry_vendor.set(values[1])
        entry_vendor.grid(row=0, column=1, pady=5, sticky="ew")
        
        # Дата установки
        ttk.Label(frame, text="Дата установки (yyyy-MM-dd):").grid(row=1, column=0, sticky="w", pady=5)
        entry_install_date = DateEntry(frame, date_pattern="yyyy-MM-dd", locale="ru_RU", state="readonly", maxdate=datetime.now())
        entry_install_date.set_date(values[2])
        entry_install_date.grid(row=1, column=1, pady=5, sticky="ew")
        
        # Локация
        ttk.Label(frame, text="Локация:").grid(row=2, column=0, sticky="w", pady=5)
        entry_location = ttk.Combobox(frame, state="readonly", values=[loc.name for loc in self.locations])
        entry_location.set(values[3])
        entry_location.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Статус
        ttk.Label(frame, text="Статус:").grid(row=3, column=0, sticky="w", pady=5)
        entry_status = ttk.Combobox(frame, state="readonly", values=["Активен", "Неактивен", "В обслуживании"])
        entry_status.set(values[4])
        entry_status.grid(row=3, column=1, pady=5, sticky="ew")
        
        def update_vendor_usage():
            vendor_name = entry_vendor.get().strip()
            selected_vendor = next((v for v in self.vendors if v.name == vendor_name), None)
            install_date_new = entry_install_date.get()
            location_new = entry_location.get().strip()
            selected_location = next((loc for loc in self.locations if loc.name == location_new), None)
            status_new = entry_status.get().strip()
            code = values[0]  # идентификатор аппарата в эксплуатации
            query = (
                "UPDATE Vendor_usage SET id_vendor = {id_vendor}, Install_date = '{install_date}', "
                "id_location = {id_location}, Status = '{status}' WHERE id = {code}"
            ).format(id_vendor=selected_vendor.code if selected_vendor else 0,
                    install_date=install_date_new,
                    id_location=selected_location.code if selected_location else 0,
                    status=status_new,
                    code=code)
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Аппарат успешно обновлён!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.vendor_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при обновлении аппарата: {e}")
            form.destroy()
        
        ttk.Button(frame, text="Сохранить изменения", command=update_vendor_usage).grid(row=4, column=0, columnspan=2, pady=10)
        form.mainloop()
    
    def open_edit_lamp_form(self, values):
        # Ожидается, что values = [code, article, name, type, voltage, colorTemp, price, description]
        form = Toplevel(self.root)
        form.title("Редактирование лампы")
        form.geometry("400x450")
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Артикул:").grid(row=0, column=0, sticky="w", pady=5)
        entry_article = ttk.Entry(frame)
        entry_article.insert(0, values[1])
        entry_article.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Название:").grid(row=1, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(frame)
        entry_name.insert(0, values[2])
        entry_name.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Тип лампы:").grid(row=2, column=0, sticky="w", pady=5)
        entry_type = ttk.Combobox(frame, state="readonly", values=[lt.name for lt in self.lamp_types])
        entry_type.set(values[3])
        entry_type.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Вольтаж:").grid(row=3, column=0, sticky="w", pady=5)
        entry_voltage = ttk.Entry(frame)
        entry_voltage.insert(0, values[4])
        entry_voltage.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цветовая температура:").grid(row=4, column=0, sticky="w", pady=5)
        entry_colorTemp = ttk.Entry(frame)
        entry_colorTemp.insert(0, values[5])
        entry_colorTemp.grid(row=4, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цена:").grid(row=5, column=0, sticky="w", pady=5)
        entry_price = ttk.Entry(frame)
        entry_price.insert(0, values[6])
        entry_price.grid(row=5, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Описание:").grid(row=6, column=0, sticky="w", pady=5)
        text_description = Text(frame, width=25, height=5, wrap="word")
        text_description.insert("1.0", values[7])
        text_description.grid(row=6, column=1, pady=5, sticky="ew")
        
        def update_lamp():
            article_new = entry_article.get().strip()
            name_new = entry_name.get().strip()
            lamp_type_name = entry_type.get().strip()
            selected_lamp_type = next((lt for lt in self.lamp_types if lt.name == lamp_type_name), None)
            try:
                voltage_new = float(entry_voltage.get())
                colorTemp_new = float(entry_colorTemp.get())
                price_new = float(entry_price.get())
            except ValueError:
                showerror("Ошибка", "Введите корректное числовое значение для напряжения, цветовой температуры и цены")
                return
            description_new = text_description.get("1.0", END).strip()
            code = values[0]
            query = (
                "UPDATE Lamps SET article = '{article}', Name = '{name}', Voltage = {voltage}, "
                "ColorTemp = {colorTemp}, Price = {price}, Description = '{description}', id_type = {id_type} "
                "WHERE id = {code}"
            ).format(article=article_new, name=name_new, voltage=voltage_new,
                    colorTemp=colorTemp_new, price=price_new, description=description_new,
                    id_type=selected_lamp_type.code if selected_lamp_type else 0,
                    code=code)
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Лампа успешно обновлена!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.lamp_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при обновлении лампы: {e}")
            form.destroy()
        
        ttk.Button(frame, text="Сохранить изменения", command=update_lamp).grid(row=7, column=0, columnspan=2, pady=10)
        form.mainloop()

    
    def open_edit_employee_form(self, values):
        form = Toplevel(self.root)
        form.title("Редактирование сотрудника")
        form.geometry("400x500")
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
    
        ttk.Label(frame, text="ФИО:").grid(row=0, column=0, sticky="w", pady=5)
        entry_FIO = ttk.Entry(frame)
        entry_FIO.insert(0, values[1])
        entry_FIO.grid(row=0, column=1, pady=5, sticky="ew")
    
        ttk.Label(frame, text="Должность:").grid(row=1, column=0, sticky="w", pady=5)
        entry_post = ttk.Combobox(frame, state="readonly", values=[str(post) for post in self.posts])
        entry_post.set(values[2])
        entry_post.grid(row=1, column=1, pady=5, sticky="ew")
    
        ttk.Label(frame, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=2, column=0, sticky="w", pady=5)
        entry_birth_date = DateEntry(frame, date_pattern='yyyy-MM-dd', locale='ru_RU', state="readonly", maxdate=datetime.now())
        entry_birth_date.set_date(values[3])
        entry_birth_date.grid(row=2, column=1, pady=5, sticky="ew")
    
        ttk.Label(frame, text="ИНН:").grid(row=3, column=0, sticky="w", pady=5)
        entry_INN = ttk.Entry(frame)
        entry_INN.insert(0, values[4])
        entry_INN.grid(row=3, column=1, pady=5, sticky="ew")
    
        ttk.Label(frame, text="Телефон:").grid(row=4, column=0, sticky="w", pady=5)
        entry_phone = ttk.Entry(frame)
        entry_phone.insert(0, values[5])
        entry_phone.grid(row=4, column=1, pady=5, sticky="ew")
    
        ttk.Label(frame, text="Логин:").grid(row=5, column=0, sticky="w", pady=5)
        entry_login = ttk.Entry(frame)
        entry_login.insert(0, values[6])
        entry_login.grid(row=5, column=1, pady=5, sticky="ew")
    
        ttk.Label(frame, text="Пароль:").grid(row=6, column=0, sticky="w", pady=5)
        entry_password = ttk.Entry(frame, show="*")
        entry_password.insert(0, values[7])
        entry_password.grid(row=6, column=1, pady=5, sticky="ew")
    
        def update_employee():
            FIO_new = entry_FIO.get().strip()
            post_new = entry_post.get().strip()
            selected_post = next((post for post in self.posts if str(post) == post_new), None)
            birth_date_new = entry_birth_date.get()
            INN_new = entry_INN.get().strip()
            phone_new = entry_phone.get().strip()
            login_new = entry_login.get().strip()
            password_new = entry_password.get().strip()
            TAB = values[0]
            query = (
                "UPDATE Employee SET FIO = '{FIO}', id_post = {id_post}, BirthDate = '{birth_date}', "
                "INN = '{INN}', phoneNumber = '{phone}', login = '{login}', password = '{password}' "
                "WHERE id = {TAB}"
            ).format(FIO=FIO_new, id_post=selected_post.code if selected_post else 0,
                     birth_date=birth_date_new, INN=INN_new, phone=phone_new, login=login_new,
                     password=password_new, TAB=TAB)
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Сотрудник успешно обновлён!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.employee_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при обновлении сотрудника: {e}")
            form.destroy()
    
        ttk.Button(frame, text="Сохранить изменения", command=update_employee).grid(row=7, column=0, columnspan=2, pady=10)
        form.mainloop()
    
    def open_edit_refill_form(self, values):
        form = Toplevel(self.root)
        form.title("Редактирование заправки")
        form.geometry("600x700")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Сотрудник:").grid(row=0, column=0, sticky="w", pady=5)
        entry_employee = ttk.Combobox(frame, values=[str(emp) for emp in self.employees], width=50, state="readonly")
        entry_employee.set(values[1])
        entry_employee.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Аппарат:").grid(row=1, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Combobox(frame, values=[str(vu) for vu in self.vendor_usages], state="readonly")
        entry_vendor_usage.set(values[2])
        entry_vendor_usage.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата:").grid(row=2, column=0, sticky="w", pady=5)
        entry_date = DateEntry(frame, date_pattern='yyyy-MM-dd', locale='ru_RU', state="readonly")
        entry_date.set_date(values[3])
        entry_date.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Табличная часть (lamp_refills)
        ttk.Label(form, text="Список ламп", font=("Segoe UI", 10, "bold")).pack(pady=5)
        table_frame = ttk.Frame(form)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Код лампы", "Артикул", "Наименование", "Количество", "Цена")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(side="left", fill="both", expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Заполняем табличную часть из БД
        refill_id = values[0]
        self.db.cursor.execute(f"SELECT * FROM Lamps_Refills WHERE id_refill = {refill_id}")
        lamp_rows = self.db.cursor.fetchall()
        for row in lamp_rows:
            lamp = next((l for l in self.lamps if l.code == row[1]), None)
            if lamp:
                tree.insert("", END, values=(lamp.code, lamp.article, str(lamp), row[2], row[3]))
        
        ttk.Button(form, text="Добавить лампу", command=lambda: self.add_lamp_refill_row(tree)).pack(pady=5)
        ttk.Button(form, text="Удалить лампу", command=lambda: self.delete_lamp_refll_row(tree)).pack(pady=5)
        
        def save_changes():
            employee = next((emp for emp in self.employees if str(emp) == entry_employee.get()), None)
            vendor_usage = next((vu for vu in self.vendor_usages if str(vu) == entry_vendor_usage.get()), None)
            date_str = entry_date.get()
            
            try:
                # Обновляем refill
                update_query = f"""
                    UPDATE Refill SET id_employee = {employee.TAB},
                    id_vendor_usage = {vendor_usage.code}, date = '{date_str}' 
                    WHERE id = {refill_id}
                """
                self.db.cursor.execute(update_query)
                
                # Удаляем старые записи табличной части
                self.db.cursor.execute(f"DELETE FROM Lamps_Refills WHERE id_refill = {refill_id}")
                
                # Добавляем новые
                for child in tree.get_children():
                    row = tree.item(child)['values']
                    lamp_id = row[0]
                    quantity = int(row[3])
                    price = float(row[4])
                    self.db.cursor.execute(
                        f"""INSERT INTO Lamps_Refills (id_refill, id_lamp, quantity, price)
                        VALUES ({refill_id}, {lamp_id}, {quantity}, {price})"""
                    )
                self.db.connection.commit()
                showinfo("Успех", "Заправка успешно обновлена")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.refill_tab)
            except Exception as e:
                showerror("Ошибка", f"Не удалось обновить заправку: {e}")
            form.destroy()

        ttk.Button(form, text="Сохранить", command=save_changes).pack(pady=10)
    
    def open_edit_malfunction_form(self, values):
        # Предполагается, что values = [code, malfunction_type, employee, status, vendor_usage, reason, report_date, resolution_date]
        form = Toplevel(self.root)
        form.title("Редактирование неполадки")
        form.geometry("500x400")
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Тип неполадки:").grid(row=0, column=0, sticky="w", pady=5)
        entry_type = ttk.Combobox(frame, values=[malfunction_type for malfunction_type in self.malfunction_types])
        entry_type.insert(0, values[1])
        entry_type.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Мастер по ремонту:").grid(row=1, column=0, sticky="w", pady=5)
        entry_employee = ttk.Entry(frame)
        entry_employee.insert(0, values[2])
        entry_employee.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Статус:").grid(row=2, column=0, sticky="w", pady=5)
        entry_status = ttk.Entry(frame)
        entry_status.insert(0, values[3])
        entry_status.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Аппарат:").grid(row=3, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Entry(frame)
        entry_vendor_usage.insert(0, values[4])
        entry_vendor_usage.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Причина:").grid(row=4, column=0, sticky="w", pady=5)
        entry_reason = ttk.Entry(frame, width=40)
        entry_reason.insert(0, values[5])
        entry_reason.grid(row=4, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата возникновения (yyyy-MM-dd):").grid(row=5, column=0, sticky="w", pady=5)
        entry_report_date = DateEntry(frame, date_pattern="yyyy-MM-dd", locale="ru_RU", state="readonly", maxdate=datetime.now())
        entry_report_date.set_date(values[6])
        entry_report_date.grid(row=5, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата ремонта (yyyy-MM-dd):").grid(row=6, column=0, sticky="w", pady=5)
        entry_resolution_date = DateEntry(frame, date_pattern="yyyy-MM-dd", locale="ru_RU", state="readonly", maxdate=datetime.now())
        # Если значение пустое или "-", оставляем пустое
        if values[7] not in ("", "-"):
            entry_resolution_date.set_date(values[7])
        entry_resolution_date.grid(row=6, column=1, pady=5, sticky="ew")
        
        def update_malfunction():
            malfunction_type_new = entry_type.get().strip()
            employee_new = entry_employee.get().strip()
            status_new = entry_status.get().strip()
            vendor_usage_new = entry_vendor_usage.get().strip()
            reason_new = entry_reason.get().strip()
            report_date_new = entry_report_date.get()
            resolution_date_new = entry_resolution_date.get()
            code = values[0]
            query = (
                "UPDATE Malfunctions SET id_malfunctiontype = (SELECT id FROM Malfunction_Type WHERE Name = '{type}'), "
                "id_employee = (SELECT id FROM Employee WHERE FIO = '{employee}'), Status = '{status}', "
                "id_vendor_usage = (SELECT id FROM Vendor_usage WHERE id = {vendor_usage}), Reason = '{reason}', "
                "report_date = '{report_date}', resolution_date = '{resolution_date}' "
                "WHERE id = {code}"
            ).format(type=malfunction_type_new, employee=employee_new, status=status_new,
                    vendor_usage=code,  # Здесь может потребоваться преобразование,
                    reason=reason_new, report_date=report_date_new,
                    resolution_date=resolution_date_new, code=code)
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Неполадка успешно обновлена!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.malfunction_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при обновлении неполадки: {e}")
            form.destroy()
        
        ttk.Button(frame, text="Сохранить изменения", command=update_malfunction).grid(row=7, column=0, columnspan=2, pady=10)
        form.mainloop()

    def open_edit_sale_form(self, values):
        # values = [code, vendor_usage, lamp, price, date]
        form = Toplevel(self.root)
        form.title("Редактирование продажи")
        form.geometry("400x350")
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Аппарат:").grid(row=0, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Entry(frame)
        entry_vendor_usage.insert(0, values[1])
        entry_vendor_usage.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Лампа:").grid(row=1, column=0, sticky="w", pady=5)
        entry_lamp = ttk.Entry(frame)
        entry_lamp.insert(0, values[2])
        entry_lamp.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цена:").grid(row=2, column=0, sticky="w", pady=5)
        entry_price = ttk.Entry(frame)
        entry_price.insert(0, values[3])
        entry_price.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата (yyyy-MM-dd):").grid(row=3, column=0, sticky="w", pady=5)
        entry_date = DateEntry(frame, date_pattern="yyyy-MM-dd", locale="ru_RU", state="readonly", maxdate=datetime.now())
        entry_date.set_date(values[4])
        entry_date.grid(row=3, column=1, pady=5, sticky="ew")
        
        def update_sale():
            vendor_usage_new = entry_vendor_usage.get().strip()
            lamp_new = entry_lamp.get().strip()
            try:
                price_new = float(entry_price.get())
            except ValueError:
                showerror("Ошибка", "Введите корректное число для цены")
                return
            date_new = entry_date.get()
            code = values[0]
            query = (
                "UPDATE Sale SET id_vendor_usage = (SELECT id FROM Vendor_usage WHERE id = {vendor_usage}), "
                "id_lamp = (SELECT id FROM Lamps WHERE Name = '{lamp}'), price = {price}, date = '{date}' "
                "WHERE id = {code}"
            ).format(vendor_usage=code, lamp=lamp_new, price=price_new, date=date_new, code=code)
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Продажа успешно обновлена!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.sale_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при обновлении продажи: {e}")
            form.destroy()
        
        ttk.Button(frame, text="Сохранить изменения", command=update_sale).grid(row=4, column=0, columnspan=2, pady=10)
        form.mainloop()

    
    # Формы добавления
    
    # Форма для добавления должностей (Post)
    def show_add_post_form(self):
        form = Toplevel(self.root)
        form.title("Добавление должности")
        form.geometry("350x150")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Название должности:").grid(row=0, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(frame)
        entry_name.grid(row=0, column=1, pady=5, sticky="ew")

        def save_post():
            name = entry_name.get().strip()
            if not name:
                showwarning("Ошибка", "Введите название должности!")
                return
            query = f"INSERT INTO Post (Name) VALUES ('{name}')"
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Должность успешно добавлена!")
                self.fetch_data()
                self.refresh_widgets()
                # перейти на вкладку «Должности», если она у вас хранится в self.post_tab
                try:
                    self.notebook.select(self.post_tab)
                except:
                    pass
            except Exception as e:
                showerror("Ошибка", f"Не удалось добавить должность: {e}")
            form.destroy()

        ttk.Button(frame, text="Сохранить", command=save_post).grid(row=1, column=0, columnspan=2, pady=10)
        form.mainloop()
        
    # Форма для добавления Типов ламп (Lamp types)
    def show_add_lamp_type_form(self):
        form = Toplevel(self.root)
        form.title("Добавление типа лампы")
        form.geometry("350x150")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Название типа:").grid(row=0, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(frame)
        entry_name.grid(row=0, column=1, pady=5, sticky="ew")

        def save_lamp_type():
            name = entry_name.get().strip()
            if not name:
                showwarning("Ошибка", "Введите название типа лампы!")
                return
            query = f"INSERT INTO Lamp_Type (Name) VALUES ('{name}')"
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Тип лампы успешно добавлен!")
                self.fetch_data()
                self.refresh_widgets()
                try:
                    self.notebook.select(self.lamp_type_tab)
                except:
                    pass
            except Exception as e:
                showerror("Ошибка", f"Не удалось добавить тип лампы: {e}")
            form.destroy()

        ttk.Button(frame, text="Сохранить", command=save_lamp_type).grid(row=1, column=0, columnspan=2, pady=10)
        form.mainloop()
    # Форма для добавления Типа неисправности
    def show_add_malfunctiontype_form(self):
        showinfo("В разработке!", "Данная форма в разработке!")
        return
        
    # Форма для добавления Локации (Location)
    def show_add_location_form(self):
        form = Toplevel(self.root)
        form.title("Добавление локации")
        form.geometry("400x200")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Название объекта:").grid(row=0, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(frame)
        entry_name.grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Адрес:").grid(row=1, column=0, sticky="w", pady=5)
        entry_address = ttk.Entry(frame)
        entry_address.grid(row=1, column=1, pady=5, sticky="ew")

        def save_location():
            name = entry_name.get().strip()
            address = entry_address.get().strip()
            if not name or not address:
                showwarning("Ошибка", "Заполните оба поля!")
                return
            query = f"INSERT INTO Location (Name, Address) VALUES ('{name}', '{address}')"
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Локация успешно добавлена!")
                self.fetch_data()
                self.refresh_widgets()
                try:
                    self.notebook.select(self.location_tab)
                except:
                    pass
            except Exception as e:
                showerror("Ошибка", f"Не удалось добавить локацию: {e}")
            form.destroy()

        ttk.Button(frame, text="Сохранить", command=save_location).grid(row=2, column=0, columnspan=2, pady=10)
        form.mainloop()
    
    # Форма для добавления модели аппарата 
    def show_add_vendor_form(self):
        form = Toplevel(self.root)
        form.title("Добавление модели аппарата")
        form.geometry("400x250")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Модель аппарата:").grid(row=0, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(frame)
        entry_name.grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky="nw", pady=5)
        text_description = Text(frame, width=30, height=5, wrap="word")
        text_description.grid(row=1, column=1, pady=5, sticky="ew")
        text_description.configure(relief="solid", borderwidth=1, highlightthickness=0, padx=2, pady=2)

        def save_vendor():
            name = entry_name.get().strip()
            description = text_description.get("1.0", END).strip()
            if not name:
                showwarning("Ошибка", "Введите модель аппарата!")
                return
            if not description:
                showwarning("Ошибка", "Введите описание аппарата!")
                return
            query = f"INSERT INTO Vendors (Name, Description) VALUES ('{name}', '{description}')"
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Модель аппарата успешно добавлена!")
                self.fetch_data()
                self.refresh_widgets()
                try:
                    self.notebook.select(self.vendor_tab)
                except:
                    pass
            except Exception as e:
                showerror("Ошибка", f"Не удалось добавить модель аппарата: {e}")
            form.destroy()

        ttk.Button(frame, text="Сохранить", command=save_vendor).grid(row=2, column=0, columnspan=2, pady=10)
        form.mainloop()
        
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
                showerror("Ошибка!", "Выберите тип лампы!")
                return
            if entry_colorTemp.get() is "":
                showerror("Ошибка!", "Введите цветовую температуру!")
                return
            if entry_price.get() is "":
                showerror("Ошибка!", "Введите цену!")
                return
            if entry_voltage.get() is "":
                showerror("Ошибка!", "Введите напряжение!")
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
        form.geometry("600x700")
        
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
        ttk.Label(form, text="Список ламп", font=("Segoe UI", 10, "bold")).pack(pady=5)
        table_frame = ttk.Frame(form)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Код лампы", "Артикул", "Наименование","Количество", "Цена")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(side="left", fill="both", expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        
        ttk.Button(form, text="Добавить лампу", command=lambda: self.add_lamp_refill_row(tree)).pack(pady=5)
        def save_refill():
            # Получение основных данных
            emp_str = entry_employee.get().strip()
            vendor_usage_str = entry_vendor_usage.get()
            date_str = entry_date.get().strip()
            
            # Поиск соответствующих объектов по строковому представлению (так как в Combobox передаются строки)
            selected_employee = next((emp for emp in self.employees if str(emp) == emp_str), None)
            if not selected_employee:
                showwarning("Внимание", "Выберите сотрудника!")
                return
            selected_vendor_usage = next((vu for vu in self.vendor_usages if str(vu) == vendor_usage_str), None)
            if not selected_vendor_usage:
                showwarning("Внимание", "Выберите корректный аппарат!")
                return
            
            # Формирование SQL-запроса для вставки в таблицу Refill
            query_refill = (
                "INSERT INTO Refill (id_employee, id_vendor_usage, date) "
                f"VALUES ({selected_employee.TAB}, {selected_vendor_usage.code}, '{date_str}')"
            )
            try:
                self.db.cursor.execute(query_refill)
                self.db.connection.commit()
                # Получаем ID последней вставленной записи (если используется автоинкремент)
                refill_id = self.db.cursor.lastrowid
                if not tree.get_children():
                    showwarning("Внимание!", "Не добавлена ни одна лампа!")
                    return
                # Обработка табличной части: перебор строк в treeview
                for child in tree.get_children():
                    row = tree.item(child)['values']
                    # Предположим, что row имеет структуру:
                    # (id_lamp, article, наименование, quantity, price)
                    if not row:
                        showwarning("Внимание!", "Не выбрана ни одна лампа!")
                        return
                    lamp_id = row[0]
                    quantity = int(row[3])
                    price = float(row[4])
                    # Формируем запрос вставки для таблицы Lamps_Refills
                    query_lamp = (
                        "INSERT INTO Lamps_Refills (id_refill, id_lamp, quantity, price) "
                        f"VALUES ({refill_id}, {lamp_id}, {quantity}, {price})"
                    )
                    self.db.cursor.execute(query_lamp)
                    self.db.connection.commit()
                    showinfo("Успех", "Заправка и данные по лампам успешно добавлены!")
                    self.fetch_data()
                    self.refresh_widgets()
                    # При необходимости можно перейти на вкладку "Заправки"
                    self.notebook.select(self.refill_tab)
            except Exception as e:
                showerror("Ошибка", f"Ошибка при добавлении заправки: {e}")
        
            form.destroy()
        ttk.Button(form, text="Сохранить", command=save_refill).pack(pady=10)
        form.mainloop()


    # Форма для добавления неполадки
    def show_add_malfunction_form(self):
        form = Toplevel(self.root)
        form.title("Добавление неполадки")
        form.geometry("500x400")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Тип неполадки:").grid(row=0, column=0, sticky="w", pady=5)
        entry_type = ttk.Combobox(frame, values=[mal_type for mal_type in self.malfunction_types], state='readonly')
        entry_type.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Аппарат").grid(row=1, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Combobox(frame, values=[vu for vu in self.vendor_usages], width=30, state='readonly')
        entry_vendor_usage.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Таб.номер сотрудника (опционально):").grid(row=2, column=0, sticky="w", pady=5)
        entry_employee = ttk.Combobox(frame, values=[employee for employee in self.employees], state='readonly')
        entry_employee.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Статус:").grid(row=3, column=0, sticky="w", pady=5)
        entry_status = ttk.Combobox(frame, values=['Новая', 'В процессе', 'Решена'], state='readonly')
        entry_status.grid(row=3, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Причина:").grid(row=4, column=0, sticky="w", pady=5)
        entry_reason = ttk.Entry(frame)
        entry_reason.grid(row=4, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата возникновения (ГГГГ-ММ-ДД):").grid(row=5, column=0, sticky="w", pady=5)
        entry_report_date = DateEntry(frame, state='readonly')
        entry_report_date.grid(row=5, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата ремонта (ГГГГ-ММ-ДД, опционально):").grid(row=6, column=0, sticky="w", pady=5)
        entry_resolution_date = DateEntry(frame, state='readonly')
        entry_resolution_date.grid(row=6, column=1, pady=5, sticky="ew")
        def save_malfunction():
            # Получение значений из полей формы
            mal_type_str = entry_type.get()
            vendor_usage_str = entry_vendor_usage.get()
            employee_str = entry_employee.get()
            status = entry_status.get()
            reason = entry_reason.get()
            report_date = entry_report_date.get_date()
            resolution_date = entry_resolution_date.get_date()

            # Поиск объектов по строковому представлению
            selected_mal_type = next((mt for mt in self.malfunction_types if str(mt) == mal_type_str), None)
            selected_vendor = next((vu for vu in self.vendor_usages if str(vu) == vendor_usage_str), None)
            selected_employee = next((emp for emp in self.employees if str(emp) == employee_str), None)

            if not selected_mal_type or not selected_vendor:
                showwarning("Внимание", "Заполните обязательные поля: тип неполадки и аппарат.")
                return
            if status == "":
                showwarning("Ошибка!", "Не выбран статус неполадки!")
                return
            if resolution_date and resolution_date < report_date:
                showwarning("Ошибка!", "Дата и время ремонта должно быть позже даты возникновения!")
                return


            # Подготовка значений для запроса
            id_type = selected_mal_type.code
            id_vendor_usage = selected_vendor.code
            id_employee = f"{selected_employee.TAB}" if selected_employee else "NULL"
            report_date_str = report_date.strftime('%Y-%m-%d')
            resolution_date_str = f"'{resolution_date.strftime('%Y-%m-%d')}'" if resolution_date else "NULL"

            try:
                query = f"""
                    INSERT INTO Malfunctions
                    (id_malfunctiontype, id_vendor_usage, id_employee, Status, Reason, report_date, resolution_date)
                    VALUES ({id_type}, {id_vendor_usage}, {id_employee}, '{status}', '{reason}', '{report_date_str}', {resolution_date_str})
                """
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Неполадка успешно добавлена.")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.malfunction_tab)
                form.destroy()
            except Exception as e:
                showerror("Ошибка", f"Ошибка при добавлении неполадки: {e}")
            form.destroy()
        ttk.Button(form, text="Сохранить", command=save_malfunction).pack(pady=10)
        form.mainloop()


    # Форма для добавления продажи
    def show_add_sale_form(self):
        form = Toplevel(self.root)
        form.title("Добавление продажи")
        form.geometry("400x350")
        
        frame = ttk.Frame(form)
        frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame, text="Аппарат:").grid(row=0, column=0, sticky="w", pady=5)
        entry_vendor_usage = ttk.Combobox(frame, values=[vu for vu in self.vendor_usages])
        entry_vendor_usage.grid(row=0, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Лампа:").grid(row=1, column=0, sticky="w", pady=5)
        entry_lamp = ttk.Combobox(frame, values=[lamp for lamp in self.lamps])
        entry_lamp.grid(row=1, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цена:").grid(row=2, column=0, sticky="w", pady=5)
        entry_price = ttk.Entry(frame)
        entry_price.grid(row=2, column=1, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky="w", pady=5)
        entry_date = DateEntry(frame, state='readonly')
        entry_date.grid(row=3, column=1, pady=5, sticky="ew")
        def save_sale():
            # Извлечение значений из полей формы
            vendor_usage_str = entry_vendor_usage.get().strip()
            lamp_str = entry_lamp.get().strip()
            price_str = entry_price.get().strip()
            sale_date = entry_date.get_date()  # возвращает объект date

            # Проверка поля "Аппарат"
            if not vendor_usage_str:
                showerror("Ошибка!", "Не выбран аппарат!")
                return

            # Проверка поля "Лампа"
            if not lamp_str:
                showerror("Ошибка!", "Не выбрана лампа!")
                return

            # Проверка даты — дата продажи не должна быть позже текущей даты.
            current_date = datetime.now().date()
            if sale_date > current_date:
                showerror("Ошибка!", "Дата продажи не может быть позже текущей даты!")
                return

            # Проверка обязательных полей для цены
            if not price_str:
                showerror("Ошибка!", "Заполните поле 'Цена'!")
                return
            try:
                price = float(price_str)
            except ValueError:
                showerror("Ошибка!", "Цена должна быть числовым значением!")
                return

            # Поиск объектов по строковому представлению (предполагается, что в классах переопределён __str__)
            selected_vendor_usage = next((vu for vu in self.vendor_usages if str(vu) == vendor_usage_str), None)
            selected_lamp = next((lamp for lamp in self.lamps if str(lamp) == lamp_str), None)

            if not selected_vendor_usage:
                showerror("Ошибка!", "Не выбран аппарат!")
                return
            if not selected_lamp:
                showerror("Ошибка!", "Не выбрана лампа!")
                return

            # Формирование SQL-запроса для вставки продажи
            query = f"""
                INSERT INTO Sale (id_vendor_usage, id_lamp, price, date)
                VALUES ({selected_vendor_usage.code}, {selected_lamp.code}, {price}, '{sale_date.strftime('%Y-%m-%d')}')
            """
            try:
                self.db.cursor.execute(query)
                self.db.connection.commit()
                showinfo("Успех", "Продажа успешно добавлена!")
                self.fetch_data()
                self.refresh_widgets()
                self.notebook.select(self.sale_tab)
                form.destroy()
            except Exception as e:
                showerror("Ошибка", f"Ошибка при добавлении продажи: {e}")

        
        ttk.Button(form, text="Сохранить", command=save_sale).pack(pady=10)
        form.mainloop()

    def delete_lamp_refll_row(self, tree):
        selected = tree.selection()
        if not selected:
            showwarning("Внимание", "Выберите строку для удаления")
            return
        tree.delete(selected[0])
        
        
    def add_lamp_refill_row(self, tree):
        # Открываем небольшое окно для ввода одной строки для Lamp_Refills
        row_win = Toplevel(self.root)
        row_win.title("Добавить лампу")
        row_win.geometry("300x300")
        
        ttk.Label(row_win, text="Лампа").pack(pady=5)
        entry_id_lamp = ttk.Combobox(row_win, values=[lamp for lamp in self.lamps], width=30, state="readonly")
        entry_id_lamp.pack(pady=5)
        
        ttk.Label(row_win, text="Количество:").pack(pady=5)
        entry_quantity = ttk.Entry(row_win, width=30)
        entry_quantity.pack(pady=5)
        
        ttk.Label(row_win, text="Цена:").pack(pady=5)
        entry_price = ttk.Entry(row_win, width=30)
        entry_price.pack(pady=5)
        
        article=""
        code=0
        # Обработчик выбора лампы в комбобоксе
        def on_lamp_selected(event):
            nonlocal article, code
            # Получаем выбранное значение из комбобокса.
            # Если значения — объекты Lamp, то entry_id_lamp.get() вернёт строковое представление,
            # совпадающее с тем, что возвращает __str__.
            selected_str = entry_id_lamp.get()
            # Ищем лампу, у которой __str__ равен выбранной строке
            for lamp in self.lamps:
                if str(lamp) == selected_str:
                    # Записываем цену выбранной лампы в поле entry_price.
                    entry_price.delete(0, END)
                    entry_price.insert(0, str(lamp.price))
                    article=lamp.article
                    code=lamp.code
                    break

        # Привязываем событие выбора к обработчику
        entry_id_lamp.bind("<<ComboboxSelected>>", on_lamp_selected)
        
        
        def add_row():
            if code is None:
                showwarning("Ошибка!", "Сначала выберите лампу")
                return
            
            # Проверка на дублирование ламп из табличной части
            for iid in tree.get_children():
                existing_code = tree.item(iid)["values"][0]
                if existing_code == code:
                    showwarning("Ошибка!", "Выбранная лампа уже добавлена!")
                    return
            
            try:
                quantity = int(entry_quantity.get())
                # Дальнейшая обработка quantity
            except ValueError:
                showwarning("Ошибка!", "Количество должно быть целым числом!")
                return
            try:
                price = float(entry_price.get())
                # Дальнейшая обработка quantity
            except ValueError:
                showwarning("Ошибка!", "Цена должна быть дробным числом!")
                return
            row_values = (code, article, entry_id_lamp.get(), quantity, price)
            tree.insert("", END, values=row_values)
            row_win.destroy()
            
        ttk.Button(row_win, text="Добавить лампу", command=add_row).pack(pady=10)

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
        self.tabs[title] = {"container": frame}
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
        
    def print_selected_refill(self):
        # 1. Получаем текущую вкладку и её фрейм
        tab_id = self.notebook.select()
        title = self.notebook.tab(tab_id, "text")
        if "заправки" not in title.lower():
            showwarning("Внимание", "Печать доступна только на вкладке «Заправки»")
            return
        container = self.notebook.nametowidget(tab_id)

        # 2. Рекурсивно ищем в контейнере первый Treeview
        def find_tree(w):
            if isinstance(w, ttk.Treeview):
                return w
            for c in w.winfo_children():
                t = find_tree(c)
                if t: return t
            return None

        tree = find_tree(container)
        if not tree:
            showerror("Ошибка", "Не найдена таблица заправок")
            return

        # 3. Берём выделение
        sel = tree.selection()
        if not sel:
            showwarning("Внимание", "Сначала выберите запись заправки")
            return

        # 4. Пусть ID в первой колонке
        refill_id = tree.item(sel[0], "values")[0]

        # 5. Генерируем PDF
        self._generate_refill_pdf(refill_id)

    def _generate_refill_pdf(self, refill_id):
        # --- 1. Данные по заправке
        self.db.cursor.execute(f"""
            SELECT r.id, e.FIO, vu.id, v.Name, loc.Name, r.date
            FROM Refill r
            JOIN Employee e ON r.id_employee = e.id
            JOIN Vendor_usage vu ON r.id_vendor_usage = vu.id
            JOIN Vendors v ON vu.id_vendor = v.id
            JOIN Location loc ON vu.id_location = loc.id
            WHERE r.id = {refill_id}
        """)
        rid, fio, vu_id, vendor_name, loc_name, date = self.db.cursor.fetchone()

        self.db.cursor.execute(f"""
            SELECT l.Name, lr.quantity, lr.price, (lr.quantity * lr.price) AS total
            FROM Lamps_Refills lr
            JOIN Lamps l ON lr.id_lamp = l.id
            WHERE lr.id_refill = {refill_id}
        """)
        lamps = self.db.cursor.fetchall()

        # --- 2. PDF через FPDF (с Unicode‑шрифтами)
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()

        # Регистрация шрифтов (файлы рядом с main.py)
        pdf.add_font('DejaVu', '', 'fonts/DEJAVUSANS.TTF', uni=True)
        pdf.add_font('DejaVu', 'B', 'fonts/DEJAVUSANS-BOLD.TTF', uni=True)

        # Заголовок
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, f"ЗАПРАВКА №{rid}", ln=True, align="C")
        pdf.ln(5)

        # Инфо
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 8, f"Сотрудник: {fio}", ln=True)
        pdf.cell(0, 8, f"Автомат: №{vu_id} {vendor_name}, {loc_name}", ln=True)
        pdf.cell(0, 8, f"Дата заправки: {date}", ln=True)
        pdf.ln(5)

        # Таблица ламп
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(80, 8, "Лампа", border=1)
        pdf.cell(30, 8, "Кол-во", border=1, align="C")
        pdf.cell(30, 8, "Цена ед., руб.", border=1, align="C")
        pdf.cell(30, 8, "Сумма, руб.", border=1, ln=True)

        pdf.set_font('DejaVu', '', 12)
        total_all = 0
        for name, qty, price, total in lamps:
            pdf.cell(80, 8, name, border=1)
            pdf.cell(30, 8, str(qty), border=1, align="R")
            pdf.cell(30, 8, f"{price:.2f}", border=1, align="R")
            pdf.cell(30, 8, f"{total:.2f}", border=1, align="R", ln=True)
            total_all += total

        # Итог
        pdf.ln(5)
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(140, 8, "Общий итог:", border=0)
        pdf.cell(30, 8, f"{total_all:.2f}", border=1, align="R")
        pdf.ln(15)

        # Подпись
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 8, "Подпись: ____________________", ln=True)

        # --- 3. Сохранить и открыть
        fname = f"refill_{rid}.pdf"
        pdf.output(fname)
        try:
            if sys.platform.startswith("win"):
                os.startfile(fname)
            elif sys.platform == "darwin":
                subprocess.call(["open", fname])
            else:
                subprocess.call(["xdg-open", fname])
        except Exception:
            pass
    def open_reports_window(self):
        from report import ReportsWindow
        ReportsWindow(self.root)


if __name__ == "__main__":
    root = Tk()
    root.resizable(0, 0)
    root.iconbitmap("vendor.ico")
    app = MainApp(root)
    root.mainloop()