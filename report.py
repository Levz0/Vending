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
            tree.heading(col, text=col, anchor="center",
                            command=lambda _col=col: self.treeview_sort_column(tree, _col, False))
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
        
    def treeview_sort_column(self, tv: ttk.Treeview, col: str, reverse: bool):
        """Сортирует данные в Treeview по колонке col."""
        # Получаем список (item_id, значение в столбце col)
        data = [(tv.set(k, col), k) for k in tv.get_children("")]
        try:
            # пытаемся конвертнуть в числа для числовой сортировки
            data = [(float(v), k) for v, k in data]
        except ValueError:
            # оставляем строки
            pass
        # собственно сортировка
        data.sort(reverse=reverse)
        # переставляем строки
        for index, (val, k) in enumerate(data):
            tv.move(k, '', index)
        # обновляем флаг направления сортировки
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))
    
    def generate_sales_report(self, start_date, end_date):
        title = "Отчет по реализованным лампам\nза период в разрезе автоматов"
        container = self.tabs[title]["container"]
        self.clear_container(container)

        lbl_info = ttk.Label(container, text="Отчет по реализованным лампам за период в разрезе автоматов", font=("Segoe UI", 12))
        lbl_info.pack(anchor="n", pady=5)

        # Определяем колонки: тип лампы, дата продажи, лампа, цена
        columns = ("тип лампы", "дата продажи", "лампа", "цена")
        tree = ttk.Treeview(container, columns=columns, show="tree headings")
        tree.heading("#0", text="Аппарат (код и название)")
        for col in columns:
            tree.heading(col, text=col, anchor="center")
            tree.column(col, anchor="center", stretch=True)
        tree.pack(fill=BOTH, expand=True, pady=5)

        query = f"""
        SELECT 
            vu.id,
            CONCAT(v.Name, ' ', loc.Name) AS аппарат,
            lt.Name AS тип_лампы,
            s.date AS дата_продажи,
            l.Name AS лампа,
            s.price AS цена
        FROM Sale s
        JOIN Vendor_usage vu ON s.id_vendor_usage = vu.id
        JOIN Vendors v ON vu.id_vendor = v.id
        JOIN Location loc ON vu.id_location = loc.id
        JOIN Lamps l ON s.id_lamp = l.id
        JOIN Lamp_Type lt ON l.id_type = lt.id
        WHERE s.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY vu.id, s.date
        """
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()

        grouped_data = {}
        for row in results:
            vendor_code, vendor_name = row[0], row[1]
            grouped_data.setdefault((vendor_code, vendor_name), []).append(row)

        overall_total = 0
        sort_states = {}

        def sort_by_column(tv, col):
            reverse = sort_states.get(col, False)
            for parent in tv.get_children():
                children = list(tv.get_children(parent))
                children.sort(key=lambda c: tv.set(c, col), reverse=reverse)
                for idx, child in enumerate(children):
                    tv.move(child, parent, idx)
            sort_states[col] = not reverse

        # Привязка сортировки
        for col in columns:
            tree.heading(col, command=lambda _col=col: sort_by_column(tree, _col))

        # Вставляем данные по каждому аппарату и добавляем подитог
        for (vendor_code, vendor_name), rows in grouped_data.items():
            parent_text = f"№{vendor_code} {vendor_name}"
            parent_id = tree.insert("", "end", text=parent_text, values=("", "", "", ""))
            tree.item(parent_id, open=True)

            group_total = 0
            for _, _, lamp_type, sale_date, lamp_name, price in rows:
                date_str = sale_date.strftime("%Y-%m-%d") if hasattr(sale_date, "strftime") else str(sale_date)
                tree.insert(parent_id, "end", text="",
                            values=(lamp_type, date_str, lamp_name, f"{price:.2f}"))
                group_total += price
                overall_total += price

            # Подитог по этому аппарату
            tree.insert(parent_id, "end", text="",
                values=("", "", "Итого по аппарату:", f"{group_total:.2f}"),
                tags=("subtotal",))

            tree.tag_configure("subtotal", background="#e0e0e0", font=("Segoe UI", 10, "bold"))
            
        # Общий итог
        lbl_total = ttk.Label(container, text=f"Общий итог по всем аппаратам: {overall_total:.2f}", font=("Segoe UI", 12, "bold"))
        lbl_total.pack(anchor="e", pady=5)

        self.auto_adjust_columns(tree)




    
    def generate_refills_report(self, start_date, end_date):
        title = "Отчет по заправкам\nаппаратов за период"
        container = self.tabs[title]["container"]
        self.clear_container(container)

        # Период
        lbl_period = ttk.Label(container, text=f"с {start_date} по {end_date}", font=("Segoe UI", 12))
        lbl_period.pack(anchor="n", pady=5)

        # Конфигурируем Treeview
        columns = ("инфо заправки", "лампа", "ед. цена", "количество", "сумма")
        tree = ttk.Treeview(container, columns=columns, show="tree headings")
        tree.heading("#0", text="аппарат (номер, имя, адрес)", anchor="w")
        tree.column("#0", anchor="w", width=250)

        # Словарь для запоминания направления сортировки по каждому столбцу
        sort_states = {}

        def sort_column(col, numeric):
            # Определяем текущее направление (True=asc, False=desc)
            asc = sort_states.get(col, True)
            sort_states[col] = not asc  # переключаем на следующий раз

            for parent in tree.get_children(""):
                children = tree.get_children(parent)
                normal = [c for c in children if "subtotal" not in tree.item(c, "tags")]
                subtotal = [c for c in children if "subtotal" in tree.item(c, "tags")]

                def key_func(item):
                    v = tree.set(item, col)
                    if numeric:
                        try:
                            return float(v)
                        except ValueError:
                            return 0.0
                    return v

                normal.sort(key=key_func, reverse=not asc)

                # Переставляем в дереве: сначала отсортированные, затем subtotal
                for idx, iid in enumerate(normal):
                    tree.move(iid, parent, idx)
                for iid in subtotal:
                    tree.move(iid, parent, "end")

        # Настраиваем заголовки с привязкой сортировки
        for col in columns:
            is_num = col in ("ед. цена", "количество", "сумма")
            tree.heading(col, text=col, anchor="center",
                        command=lambda c=col, n=is_num: sort_column(c, n))
            tree.column(col, anchor="center", stretch=True)

        tree.pack(fill=BOTH, expand=True, pady=5)

        # Получаем данные из БД
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
        raw = self.db.cursor.fetchall()

        # Группируем по аппарату
        grouped = {}
        for vid, apparatus_info, refill_id, refill_date, employee, lamp, unit_price, quantity, sum_total in raw:
            grouped.setdefault(vid, {
                "apparatus": f"№ {vid} {apparatus_info}",
                "rows": []
            })["rows"].append((refill_id, refill_date, employee, lamp, unit_price, quantity, sum_total))

        total_all = 0
        # Вставляем данные в дерево
        for vid, info in grouped.items():
            parent = tree.insert("", "end", text=info["apparatus"], values=("", "", "", "", ""))
            tree.item(parent, open=True)
            sum_group = 0

            for refill_id, refill_date, employee, lamp, unit_price, quantity, sum_total in info["rows"]:
                txt = f"№ {refill_id} от {refill_date.strftime('%d.%m.%Y')} ({employee})"
                tree.insert(parent, "end", text="",
                            values=(txt, lamp, unit_price, quantity, sum_total))
                sum_group += sum_total

            total_all += sum_group
            # Добавляем строку "Итого по аппарату"
            tree.insert(parent, "end", text="", 
                        values=("", "", "", "Итого по аппарату:", sum_group),
                        tags=("subtotal",))

        # Общий итог
        lbl_total = ttk.Label(container, text=f"Общий итог: {total_all:.2f}",
                            font=("Segoe UI", 12, "bold"))
        lbl_total.pack(anchor="e", pady=5)

        # Автоподгонка ширины колонок
        self.auto_adjust_columns(tree)

        # --- Локальная функция сортировки внутри каждой группы ---
    def sort_within_groups(col, numeric):
            """
            Для каждого родителя сортируем его потомков (кроме subtotal)
            по колонке col.
            """
            for parent in tree.get_children(""):
                children = tree.get_children(parent)
                # выделим нормальные строки и строку subtotal
                normal = [c for c in children if "subtotal" not in tree.item(c, "tags")]
                subtotal = [c for c in children if "subtotal" in tree.item(c, "tags")]

                # ключ сортировки
                def key_func(item):
                    val = tree.set(item, col)
                    if numeric:
                        try:
                            return float(val)
                        except ValueError:
                            return 0.0
                    return val

                # сама сортировка (только один раз, без смены направления)
                normal_sorted = sorted(normal, key=key_func)

                # переставим в порядке normal_sorted + subtotal
                for idx, iid in enumerate(normal_sorted):
                    tree.move(iid, parent, idx)
                for iid in subtotal:
                    tree.move(iid, parent, "end")




    
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
