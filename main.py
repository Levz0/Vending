from tkinter import ttk, Tk
from tkinter import *
import random
from datetime import datetime

# Импорт классов (предполагается, что файлы находятся в соседней папке)
from entities.post import Post
from entities.LampType import LampType
from entities.employee import Employee
from entities.Lamp import Lamp
from entities.vendor import Vendor
from entities.vendor_usage import Vendor_usage

# Стилизация приложения
BG_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#1877f2"
HOVER_COLOR = "#166fe5"
TEXT_COLOR = "#1c1e21"
ENTRY_BG = "#ffffff"
FONT = ("Segoe UI", 10)


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vending Management System")
        self.root.geometry("1200x600")
        
        # Генерация тестовых данных
        self.generate_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        #Создание кнопок
        self.create_buttons()

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
                colorTemp=random.randint(2000, 6500),
                price=round(random.uniform(100, 1000), 2),
                description=f"Описание лампы {i}"
            ) for i in range(1, 6)
        ]
        
        # Аппараты
        self.vendors = [
            Vendor(
                code=i,
                name=random.choice(["LightVend Pro", "BulbBox 24/7", "LumaSphere Auto", "BrightSpot Express", "EcoLamp Vend"]),
                description=random.choice([
                    "Компактный и надежный помощник, готовый работать круглосуточно, чтобы удовлетворить ваши потребности в любое время суток.",
                    "Современный дизайн и интуитивно понятный интерфейс делают использование простым и удобным для каждого.",
                    "Автономный и энергоэффективный, этот аппарат идеально подходит для мест с высокой проходимостью.",
                    "Быстрая выдача и широкий ассортимент — всё, что нужно для вашего комфорта.",
                    "Надежный и долговечный, этот аппарат станет вашим незаменимым спутником в повседневной жизни."
                ])
            ) for i in range (1, 6)
        ]
        # Аппараты_в_использовании
        self.apparatuses = [
            Vendor_usage(
                code=i,
                vendor = random.choice(self.vendors),
                location= random.choice(["ТЦ 'МЕГА'", "Вокзал", "Офис"]),
                install_date= datetime.now().strftime("%Y-%m-%d"),
                status= random.choice(["Активен", "Неактивен", "В обслуживании"])
            ) for i in range(1, 6)
        ]

    def create_widgets(self):
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)  # Делаем notebook атрибутом класса
        self.notebook.pack(fill=BOTH, expand=True)

        # Вкладка для аппаратов
        frame_app = ttk.Frame(self.notebook)
        self.create_table(frame_app, "Аппараты", 
                         ["Код", "Название", "Локация","Дата установки", "Статус"],
                         [{
                             "Код": app.code,
                             "Название": app.vendor.name,
                             "Локация": app.location,
                             "Дата установки": app.install_date,
                             "Статус": app.status
                         } for app in self.apparatuses])
        self.notebook.add(frame_app, text="Аппараты")

        # Вкладка для ламп
        frame_lamps = ttk.Frame(self.notebook)
        self.create_table(frame_lamps, "Лампы", 
                         ["Название", "Тип", "Вольтаж", "Цветовая температура", "Цена", "Описание"],
                         [{
                             "Название": lamp.name,
                             "Тип": lamp.type,
                             "Вольтаж": lamp.voltage,
                             "Цветовая температура": lamp.colorTemp,
                             "Цена": lamp.price,
                             "Описание": lamp.description
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
        
    def create_buttons(self):
        # Создаем фрейм для кнопок
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, fill=X, padx=20)

        # Стиль для ttk виджетов
        style = ttk.Style()
        style.theme_use('clam')

        # Конфигурация стиля для кнопок
        style.configure('Primary.TButton', 
                        font=FONT,
                        background=PRIMARY_COLOR,
                        foreground='white',
                        borderwidth=0,
                        padding=10,
                        focuscolor=PRIMARY_COLOR)

        style.map('Primary.TButton',
                background=[('active', HOVER_COLOR), ('disabled', '#dddfe2')],
                foreground=[('disabled', '#606770')])

        # Кнопка "Добавить" с правильным стилем
        b_add = ttk.Button(
            button_frame,
            text="Добавить",
            style='Primary.TButton'
        )
        b_add.pack(side=LEFT, padx=5)

        # Можно добавить другие кнопки аналогично
        b_edit = ttk.Button(
            button_frame,
            text="Редактировать",
            style='Primary.TButton'
        )
        b_edit.pack(side=LEFT, padx=5)



if __name__ == "__main__":
    root = Tk()
    app = MainApp(root)
    root.mainloop()