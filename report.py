# report.py
from tkinter import Toplevel, BOTH, END, W
from tkinter import ttk
from tkcalendar import DateEntry  # Виджет выбора даты
from datetime import datetime
from db import DataBase  # Ваш класс подключения к БД (pymysql)

class ReportsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = Toplevel(self.parent)
        self.window.title("Формирование отчетов")
        self.window.geometry("1200x700")
        
        # Подключаемся к БД
        self.db = DataBase("127.0.0.1", "root", "", "Vending")
        self.db.connect()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Создаем Notebook для вкладок отчетов
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Словарь для хранения вкладок и их компонентов
        self.tabs = {}
        
        # Каждый элемент: (название вкладки, функция формирования отчета, требуется ли выбор периода)
        # Период требуется только для отчетов "Отчет о неполадках..." и "Отчет по заправкам..."
        reports = [
            ("Отчет о неполадках\nаппаратов за период", self.generate_malfunctions_report, True),
            ("Отчет по реализованным лампам\nза период в разрезе автоматов", self.generate_sales_report, True),
            ("Отчет по заправкам\nаппаратов за период", self.generate_refills_report, True),
            ("Проданные типы ламп\nпо аппаратам", self.generate_lamps_report, False)
        ]
        
        for title, report_func, period_required in reports:
            frame = ttk.Frame(self.notebook)
            frame.pack(fill=BOTH, expand=True)
            self.notebook.add(frame, text=title)
            self.tabs[title] = {}
            
            # Гибкое размещение внутри вкладки
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(4, weight=1)
            
            row = 0
            # Дата создания отчета – в правом верхнем углу
            creation_date = datetime.now().strftime("%Y-%m-%d")
            lbl_date = ttk.Label(frame, text=f"Дата создания отчета: {creation_date}")
            lbl_date.grid(row=row, column=0, sticky="e", padx=10, pady=5)
            row += 1
            
            # Заголовок отчета по центру
            if "неполадках" in title.lower():
                header_text = "Неполадки аппаратов за период"
            elif "реализованным" in title.lower():
                header_text = "Реализованные лампы каждого аппарата за период"
            elif "заправкам" in title.lower():
                header_text = "Заправки аппаратов за период"
            else:
                header_text = "Проданные типы ламп по аппаратам"
            lbl_header = ttk.Label(frame, text=header_text, font=("Segoe UI", 16, "bold"))
            lbl_header.grid(row=row, column=0, sticky="n", padx=10, pady=5)
            row += 1
            
            # Если требуется выбор периода, создаем поля DateEntry
            if period_required:
                period_frame = ttk.Frame(frame)
                period_frame.grid(row=row, column=0, pady=5)
                lbl_start = ttk.Label(period_frame, text="Период: с")
                lbl_start.pack(side="left", padx=5)
                entry_start = DateEntry(period_frame, width=12, date_pattern="yyyy-mm-dd")
                entry_start.pack(side="left", padx=5)
                lbl_to = ttk.Label(period_frame, text="по")
                lbl_to.pack(side="left", padx=5)
                entry_end = DateEntry(period_frame, width=12, date_pattern="yyyy-mm-dd")
                entry_end.pack(side="left", padx=5)
                self.tabs[title]["entry_start"] = entry_start
                self.tabs[title]["entry_end"] = entry_end
            row += 1
            
            # Кнопка формирования отчета
            btn_generate = ttk.Button(frame, text="Сформировать отчет", 
                                      command=lambda es=self.tabs[title].get("entry_start"),
                                                     ee=self.tabs[title].get("entry_end"),
                                                     func=report_func: func(es.get() if es else "", ee.get() if ee else ""))
            btn_generate.grid(row=row, column=0, pady=10)
            row += 1
            
            # Контейнер для вывода отчета – здесь будет размещена таблица с данными
            container = ttk.Frame(frame)
            container.grid(row=row, column=0, sticky="nsew", padx=10, pady=10)
            frame.rowconfigure(row, weight=1)
            self.tabs[title]["container"] = container
    
    def clear_container(self, container):
        for widget in container.winfo_children():
            widget.destroy()
    
    def generate_malfunctions_report(self, start_date, end_date):
        title = "Отчет о неполадках\nаппаратов за период"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)
        
        # Таблица с колонками: аппарат, дата поломки, дата починки, причина возникновения
        columns = ("аппарат", "дата поломки", "дата починки", "причина возникновения")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        # Выполняем SQL-запрос для получения данных отчета по неполадкам
        query = f"""
        SELECT v.Name as аппарат, m.report_date, m.resolution_date, m.Reason
        FROM Malfunctions m
        JOIN Vendor_usage vu ON m.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        WHERE m.report_date BETWEEN '{start_date}' AND '{end_date}'
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        for row in results:
            tree.insert("", END, values=row)
    
    def generate_sales_report(self, start_date, end_date):
        title = "Отчет по реализованным лампам\nза период в разрезе автоматов"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        # Этот отчет не требует выбора периода, поэтому просто формируем заголовок
        lbl_info = ttk.Label(container, text="Отчет по реализованным лампам за период в разрезе автоматов", font=("Segoe UI", 12))
        lbl_info.pack(anchor="n", pady=5)
        
        # Таблица с колонками: аппарат, лампа, цена, количество, выручка
        columns = ("аппарат", "лампа", "цена", "количество", "выручка")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        # Запрос для отчета по продажам
        query = f"""
        SELECT v.Name as аппарат, l.Name as лампа, s.price as цена, COUNT(*) as количество, SUM(s.price) as выручка
        FROM Sale s
        JOIN Vendor_usage vu ON s.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Lamps l ON s.id_lamp = l.id
        WHERE s.date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY v.Name, l.Name, s.price
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        total = 0
        for row in results:
            tree.insert("", END, values=row)
            total += row[4]
        lbl_total = ttk.Label(container, text=f"Итого: {total:.2f}", font=("Segoe UI", 12, "bold"))
        lbl_total.pack(anchor="e", pady=5)
    
    def generate_refills_report(self, start_date, end_date):
        title = "Отчет по заправкам\nаппаратов за период"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)
        
        # Таблица с колонками: аппарат, лампа, ед. цена, количество, сумма
        columns = ("аппарат", "лампа", "ед. цена", "количество", "сумма")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        query = f"""
        SELECT v.Name as аппарат, l.Name as лампа, lr.price as `ед_цена`, lr.quantity as количество, (lr.price * lr.quantity) as сумма
        FROM Refill r
        JOIN Lamps_Refills lr ON r.id = lr.id_refill
        JOIN Vendor_usage vu ON r.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Lamps l ON lr.id_lamp = l.id
        WHERE r.date BETWEEN '{start_date}' AND '{end_date}'
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        for row in results:
            tree.insert("", END, values=row)
    
    def generate_lamps_report(self, start_date, end_date):
        title = "Проданные типы ламп\nпо аппаратам"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)
        
        # Таблица с колонками: аппарат, тип лампы, выручка
        columns = ("аппарат", "тип лампы", "выручка")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        query = f"""
        SELECT v.Name as аппарат, lt.Name as `тип лампы`, SUM(s.price) as выручка
        FROM Sale s
        JOIN Vendor_usage vu ON s.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Lamps l ON s.id_lamp = l.id
        JOIN Lamp_Type lt ON l.id_type = lt.id
        GROUP BY v.Name, lt.Name
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        for row in results:
            tree.insert("", END, values=row)
