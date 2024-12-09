import sqlite3
import hashlib
import json
import os
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from openpyxl import Workbook
import subprocess


class BookstoreApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Книжный магазин")
        self.geometry("1000x700")
        self.center_window(1000, 700)

        self.iconbitmap("book.ico")

        self.user_file = "users.json"
        self.conn = sqlite3.connect("bookstore.db")
        self.create_tables()

        self.user = None
        self.show_login_screen()

    def create_tables(self):
        """Создает таблицы базы данных, если они не существуют."""
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            availability TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def center_window(self, width, height):
        """Центрирует окно."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # -------------------- ЛОГИН/РЕГИСТРАЦИЯ --------------------

    def show_login_screen(self):
        """Отображает экран авторизации."""
        self.clear_screen()
        self.geometry("400x250")
        self.center_window(400, 250)

        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=50, padx=50)

        ctk.CTkLabel(self.login_frame, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        self.login_entry = ctk.CTkEntry(self.login_frame)
        self.login_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.login_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ctk.CTkButton(self.login_frame, text="Войти", command=self.login)
        self.login_button.grid(row=2, column=0, padx=5, pady=10)

        self.register_button = ctk.CTkButton(self.login_frame, text="Регистрация", command=self.show_register_screen)
        self.register_button.grid(row=2, column=1, padx=5, pady=10)

    def show_register_screen(self):
        """Отображает экран регистрации."""
        self.clear_screen()
        self.geometry("400x250")
        self.center_window(400, 250)

        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.pack(pady=50, padx=50)

        ctk.CTkLabel(self.register_frame, text="Логин:").grid(row=0, column=0, padx=5, pady=5)
        self.register_login_entry = ctk.CTkEntry(self.register_frame)
        self.register_login_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.register_frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5)
        self.register_password_entry = ctk.CTkEntry(self.register_frame, show="*")
        self.register_password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.register_button = ctk.CTkButton(self.register_frame, text="Зарегистрироваться", command=self.register)
        self.register_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.back_button = ctk.CTkButton(self.register_frame, text="Назад", command=self.show_login_screen)
        self.back_button.grid(row=3, column=0, columnspan=2, pady=5)

    def login(self):
        """Авторизация пользователя."""
        username = self.login_entry.get()
        password = self.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if not os.path.exists(self.user_file):
            messagebox.showerror("Ошибка", "Пользователь не найден!")
            return

        with open(self.user_file, "r") as file:
            users = json.load(file)

        if username in users and users[username] == hashed_password:
            self.user = username
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def register(self):
        """Регистрация нового пользователя."""
        username = self.register_login_entry.get()
        password = self.register_password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        users = {}
        if os.path.exists(self.user_file):
            with open(self.user_file, "r") as file:
                users = json.load(file)

        if username in users:
            messagebox.showerror("Ошибка", "Пользователь уже существует!")
            return

        users[username] = hashed_password
        with open(self.user_file, "w") as file:
            json.dump(users, file)

        messagebox.showinfo("Успех", "Регистрация завершена!")
        self.show_login_screen()

    # -------------------- ОСНОВНОЙ ЭКРАН --------------------

    def show_main_screen(self):
        """Отображает основной экран приложения."""
        self.clear_screen()
        self.geometry("1000x700")
        self.center_window(1000, 700)
        self.setup_ui()

    def clear_screen(self):
        """Очищает экран."""
        for widget in self.winfo_children():
            widget.destroy()

    def setup_ui(self):
        """Создает интерфейс приложения."""
        # Фрейм для добавления/обновления книг
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(self.form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.book_name_entry = ctk.CTkEntry(self.form_frame)
        self.book_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.form_frame, text="Цена:").grid(row=0, column=2, padx=5, pady=5)
        self.book_price_entry = ctk.CTkEntry(self.form_frame)
        self.book_price_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(self.form_frame, text="Наличие:").grid(row=0, column=4, padx=5, pady=5)
        self.availability_var = ctk.StringVar(value="Нет в наличии")
        self.book_availability_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.availability_var,
                                                        values=["Нет в наличии", "На складе", "Есть в магазине"])
        self.book_availability_menu.grid(row=0, column=5, padx=5, pady=5)

        self.add_button = ctk.CTkButton(self.form_frame, text="Добавить", command=self.add_book)
        self.add_button.grid(row=0, column=6, padx=5, pady=5)

        self.update_button = ctk.CTkButton(self.form_frame, text="Обновить", command=self.update_book)
        self.update_button.grid(row=0, column=7, padx=5, pady=5)

        # Таблица
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, pady=10)

        self.table = ttk.Treeview(self.table_frame, columns=("id", "name", "price", "availability"), show="headings")
        self.table.heading("id", text="ID")
        self.table.heading("name", text="Название")
        self.table.heading("price", text="Цена")
        self.table.heading("availability", text="Наличие")
        self.table.bind("<Double-1>", self.load_book_to_form)
        self.table.pack(fill="both", expand=True)

        self.load_books()

        # Кнопки фильтров
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(pady=10, fill="x")

        self.filter_price_button = ctk.CTkButton(self.filter_frame, text="Цена >= 1000", command=self.filter_by_price)
        self.filter_price_button.grid(row=0, column=0, padx=10, pady=5)

        self.delete_button = ctk.CTkButton(self.filter_frame, text="Удалить книги с ценой < 50", command=self.delete_books_below_50)
        self.delete_button.grid(row=0, column=1, padx=10, pady=5)

        self.export_button = ctk.CTkButton(self.filter_frame, text="Экспорт в Excel", command=self.export_to_excel)
        self.export_button.grid(row=0, column=2, padx=10, pady=5)

    # -------------------- ДЕЙСТВИЯ С ДАННЫМИ --------------------

    def load_books(self):
        """Загружает данные из базы в таблицу."""
        for row in self.table.get_children():
            self.table.delete(row)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()

        for book in books:
            self.table.insert("", "end", values=book)

    def load_book_to_form(self, event):
        """Загружает данные книги в форму при двойном клике."""
        selected_item = self.table.selection()[0]
        book = self.table.item(selected_item)["values"]

        self.book_name_entry.delete(0, "end")
        self.book_name_entry.insert(0, book[1])

        self.book_price_entry.delete(0, "end")
        self.book_price_entry.insert(0, book[2])

        self.availability_var.set(book[3])
        self.current_book_id = book[0]

    def add_book(self):
        """Добавляет новую книгу."""
        name = self.book_name_entry.get()
        price = self.book_price_entry.get()
        availability = self.availability_var.get()

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO books (name, price, availability) VALUES (?, ?, ?)",
                       (name, price, availability))
        self.conn.commit()
        self.load_books()

    def update_book(self):
        """Обновляет данные книги."""
        name = self.book_name_entry.get()
        price = self.book_price_entry.get()
        availability = self.availability_var.get()

        cursor = self.conn.cursor()
        cursor.execute("UPDATE books SET name = ?, price = ?, availability = ? WHERE id = ?",
                       (name, price, availability, self.current_book_id))
        self.conn.commit()
        self.load_books()

    def filter_by_price(self):
        """Фильтрует книги с ценой >= 1000."""
        for row in self.table.get_children():
            self.table.delete(row)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE price >= 1000")
        books = cursor.fetchall()

        for book in books:
            self.table.insert("", "end", values=book)

    def delete_books_below_50(self):
        """Удаляет книги с ценой < 50."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM books WHERE price < 50")
        self.conn.commit()
        self.load_books()

    def export_to_excel(self):
        """Экспортирует данные в Excel."""
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if filename:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM books")
            books = cursor.fetchall()

            workbook = Workbook()
            sheet = workbook.active
            sheet.append(["ID", "Название", "Цена", "Наличие"])

            for book in books:
                sheet.append(book)

            workbook.save(filename)
            subprocess.run(["open" if os.name == "posix" else "start", filename], check=True, shell=True)
            messagebox.showinfo("Успех", "Данные экспортированы в Excel!")


if __name__ == "__main__":
    app = BookstoreApp()
    app.mainloop()
