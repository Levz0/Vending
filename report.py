# report.py
from tkinter import Toplevel, BOTH, END, W, font
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

    def auto_adjust_columns(self, tree):
        default_font = font.nametofont("TkDefaultFont")
        for col in tree["columns"]:
            max_width = default_font.measure(tree.heading(col)["text"])
            for item in tree.get_children():
                cell_text = tree.set(item, col)
                max_width = max(max_width, default_font.measure(cell_text))
            tree.column(col, width=max_width + 10, stretch=True)


    def clear_container(self, container):
        for widget in container.winfo_children():
            widget.destroy()
    
    def generate_malfunctions_report(self, start_date, end_date):
        title = "Отчет о неполадках\nаппаратов за период"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)
        
        # Таблица с колонками: код аппарата, id сотрудника, аппарат, тип неполадки, дата возникновния, дата ремонта, причина возникновения
        columns = ("код", "сотрудник", "аппарат", "тип неполадки", "дата возникновния", "дата ремонта", "причина возникновения")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            # Убираем фиксированную ширину, оставляя возможность растягивания
            tree.column(col, anchor="center", stretch=True)
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        # Запрос с добавленным полем m.id_employee
        query = f"""
        SELECT vu.id as код, e.FIO, CONCAT(v.Name, l.Address) as аппарат, 
               mt.Name as `тип неполадки`, m.report_date, m.resolution_date, m.Reason
        FROM Malfunctions m
        Left JOIN Vendor_usage vu ON m.id_vendor_usage = vu.id
        Left JOIN Vendors v ON vu.id_vendor = v.id
        Left JOIN location l ON vu.id_location = l.id
        Left JOIN Malfunction_Type mt ON m.id_malfunctiontype = mt.id
        Left JOIN Employee e ON m.id_employee = e.id
        WHERE m.report_date BETWEEN '{start_date}' AND '{end_date}'
        Order by m.report_date DESC
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        for row in results:
            row = list(row)
            cleaned_row = ["-" if item is None else item for item in row]
            tree.insert("", END, values=cleaned_row)
        
        # Автоматически подгоняем ширину столбцов
        self.auto_adjust_columns(tree)
    
    def generate_sales_report(self, start_date, end_date):
        title = "Отчет по реализованным лампам\nза период в разрезе автоматов"
        container = self.tabs[title]["container"]
        self.clear_container(container)

        lbl_info = ttk.Label(container, text="Отчет по реализованным лампам за период в разрезе автоматов", font=("Segoe UI", 12))
        lbl_info.pack(anchor="n", pady=5)

        # Первый столбец (#0) – для иерархии (здесь будет объединён код и название аппарата)
        columns = ("тип лампы", "лампа", "цена", "количество", "выручка")
        tree = ttk.Treeview(container, columns=columns, show="tree headings")
        tree.heading("#0", text="Аппарат (код и название)")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=True)
        tree.pack(fill=BOTH, expand=True, pady=5)

        query = f"""
        SELECT CONCAT('Аппарат № ', vu.id), CONCAT(v.Name, ' ', loc.Name) as аппарат, lt.Name as `тип лампы`, l.Name as лампа, s.price as цена, 
            COUNT(*) as количество, SUM(s.price) as выручка
        FROM Sale s
        JOIN Vendor_usage vu ON s.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Lamps l ON s.id_lamp = l.id
        JOIN Lamp_Type lt ON l.id_type = lt.id
        JOIN Location loc ON vu.id_location = loc.id
        WHERE s.date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY v.Name, l.Name, s.price
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()

        # Группируем по названию аппарата, сохраняя код аппарата из первой записи
        grouped_data = {}
        for row in results:
            vendor_code = row[0]      # Код аппарата
            vendor_name = row[1]      # Название аппарата
            if vendor_name not in grouped_data:
                grouped_data[vendor_name] = {"code": vendor_code, "rows": []}
            grouped_data[vendor_name]["rows"].append(row)

        total = 0
        for vendor_name, data in grouped_data.items():
            # Родительский узел: объединяем код и название аппарата
            parent_text = f"{data['code']} {vendor_name}"
            parent_id = tree.insert("", END, text=parent_text, values=("", "", "", "", ""))
            tree.item(parent_id, open=True)  # Узел сразу раскрыт

            for row in data["rows"]:
                # В дочерних узлах первый столбец оставляем пустым, остальные – данные по лампе
                tree.insert(parent_id, END, text="",
                            values=(row[2], row[3], row[4], row[5], row[6]))
                total += row[6]

        lbl_total = ttk.Label(container, text=f"Итого: {total:.2f}", font=("Segoe UI", 12, "bold"))
        lbl_total.pack(anchor="e", pady=5)

        self.auto_adjust_columns(tree)


    
    def generate_refills_report(self, start_date, end_date):
        title = "Отчет по заправкам\nаппаратов за период"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)
        
        # Определяем столбцы: первая колонка (#0) будет для аппарата, остальные — для данных заправки и ламп
        columns = ("инфо заправки", "лампа", "ед. цена", "количество", "сумма")
        tree = ttk.Treeview(container, columns=columns, show="tree headings")
        tree.heading("#0", text="аппарат (номер, имя, адрес)")
        tree.column("#0", anchor="w", width=250)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=True)
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        query = f"""
        SELECT 
            vu.id AS vendor_usage_id,
            CONCAT(v.Name, ' ', loc.Name) AS apparatus_info,
            r.id AS refill_id,
            r.date AS refill_date,
            e.FIO AS employee,
            l.Name AS lamp,
            lr.price AS unit_price,
            lr.quantity AS quantity,
            (lr.price * lr.quantity) AS sum_total
        FROM Refill r
        JOIN Lamps_Refills lr ON r.id = lr.id_refill
        JOIN Vendor_usage vu ON r.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Location loc ON vu.id_location = loc.id
        JOIN Employee e ON r.id_employee = e.id
        JOIN Lamps l ON lr.id_lamp = l.id
        WHERE r.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY vu.id, r.date, r.id, l.Name
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        
        current_app = None
        app_node = ""
        
        for row in results:
            vendor_usage_id = row[0]
            apparatus_info = row[1]
            refill_id = row[2]
            refill_date = row[3]
            employee = row[4]
            lamp = row[5]
            unit_price = row[6]
            quantity = row[7]
            sum_total = row[8]
            
            # Если сменился аппарат, создаем новый родительский узел
            if vendor_usage_id != current_app:
                app_text = f"№ {vendor_usage_id} {apparatus_info}"
                app_node = tree.insert("", END, text=app_text, values=("", "", "", "", ""))
                tree.item(app_node, open=True)
                current_app = vendor_usage_id
            
            # Форматируем данные заправки, чтобы вывести их в отдельном столбце
            formatted_date = refill_date.strftime("%d.%m.%Y") if hasattr(refill_date, "strftime") else refill_date
            refill_text = f"№ {refill_id} от {formatted_date} ({employee})"
            
            # Добавляем строку с данными по лампе, при этом заправка – часть данных, а не отдельный узел
            tree.insert(app_node, END, text="", values=(refill_text, lamp, unit_price, quantity, sum_total))
        
        self.auto_adjust_columns(tree)




    
    def generate_lamps_report(self, start_date, end_date):
        title = "Проданные типы ламп\nпо аппаратам"
        container = self.tabs[title]["container"]
        self.clear_container(container)
        
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)
        
        columns = ("тип лампы", "количество", "выручка")
        tree = ttk.Treeview(container, columns=columns, show="tree headings")
        tree.heading("#0", text="аппарат (номер, имя, адрес)")
        tree.column("#0", anchor="w", width=200)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=True)
        tree.pack(fill=BOTH, expand=True, pady=5)
        
        query = f"""
        SELECT 
            vu.id,
            CONCAT("Аппарат № ", vu.id, " ", v.Name , " ", loc.Name) as аппарат, 
            lt.Name as `тип лампы`, 
            Count(*) as количество,
            SUM(s.price) as выручка
        FROM Sale s
        JOIN Vendor_usage vu ON s.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Lamps l ON s.id_lamp = l.id
        JOIN Lamp_Type lt ON l.id_type = lt.id
        JOIN Location loc ON vu.id_location = loc.id
        GROUP BY аппарат, lt.Name
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        
        grouped_data = {}
        for row in results:
            vendor_usage_id = row[0]
            apparatus = row[1]
            lamp_type = row[2]
            quantity = row[3]
            revenue = row[4]
            if vendor_usage_id not in grouped_data:
                grouped_data[vendor_usage_id] = {
                    "apparatus": apparatus,
                    "details": []
                }
            grouped_data[vendor_usage_id]["details"].append((lamp_type, quantity, revenue))
            
        for vendor_usage_id, data in grouped_data.items():
            parent_id = tree.insert("", END, text=data["apparatus"], values=("", "", ""))
            tree.item(parent_id, open=True)
            for detail in data["details"]:
                lamp_type, quantity, revenue = detail
                tree.insert(parent_id, END, text="", values=(lamp_type, quantity, revenue))
        
        self.auto_adjust_columns(tree)
