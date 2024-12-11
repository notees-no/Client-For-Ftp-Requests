import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, Text, Toplevel, Frame, Button, ttk, filedialog
from ftplib import FTP_TLS
import os
import traceback

class FTPClient:
    def __init__(self, master):
        self.master = master
        self.master.title("FTP Client")
        self.master.geometry("600x400")

        # Первая форма - авторизация
        self.login_frame = Frame(self.master)
        self.login_frame.pack(padx=10, pady=10)

        ttk.Label(self.login_frame, text="Логин:").grid(row=0, column=0)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        ttk.Label(self.login_frame, text="Пароль:").grid(row=1, column=0)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = ttk.Button(self.login_frame, text="Войти", command=self.login)
        self.login_button.grid(row=2, columnspan=2)

        # Вторая форма - отображение файлов
        self.file_frame = None
        self.current_directory = '/'
        self.previous_directory = []
        self.user_permissions = {}

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Логин и пароль не могут быть пустыми.")
            return

        try:
            self.ftp = FTP_TLS('127.0.0.1')  # Используем FTP_TLS
            self.ftp.login(user=username, passwd=password)  # Аутентификация
            self.ftp.prot_p()  # Устанавливаем защищенный режим передачи данных
            messagebox.showinfo("Успех", "Успешная авторизация!")
            self.user_permissions = self.get_user_permissions(username)  # Получаем права пользователя
            self.show_files()
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось подключиться. Проверьте логин и пароль.")

    def get_user_permissions(self, username):
        # Здесь вы можете определить права доступа для пользователей
        if username == "admin":
            return {
                "files": ["Read", "Write", "Append", "Delete", "Rename"],
                "directories": ["List", "Create", "Delete", "Rename"]
            }
        else:
            return {
                "files": ["Read", "Write", "Append", "Delete", "Rename"],
                "directories": ["List"]
            }

    def show_files(self):
        # Удаляем форму авторизации
        self.login_frame.pack_forget()

        # Создаем новую форму для отображения файлов
        self.file_frame = Frame(self.master)
        self.file_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(self.file_frame, text="Список файлов и директорий:").pack()

        self.file_listbox = Listbox(self.file_frame, width=80, height=20)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(self.file_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        self.file_listbox.bind('<Double-Button-1>', self.enter_directory)  # Двойной клик для входа в директорию
        self.file_listbox.bind('<Button-3>', self.show_file_options)  # Правый клик для опций файла

        # Кнопка "Назад"
        self.back_button = ttk.Button(self.file_frame, text="Назад", command=self.go_back)
        self.back_button.pack(pady=10)

        # Кнопка "Загрузить файл"
        self.upload_button = ttk.Button(self.file_frame, text="Загрузить файл", command=self.upload_file)
        self.upload_button.pack(pady=10)

        # Кнопка "Скачать файл"
        self.download_button = ttk.Button(self.file_frame, text="Скачать файл", command=self.download_file)
        self.download_button.pack(pady=10)

        # Кнопка "Обновить список"
        self.refresh_button = ttk.Button(self.file_frame, text="Обновить список", command=self.list_files)
        self.refresh_button.pack(pady=10)

        self.list_files()

        # Кнопка "Выйти"
        self.logout_button = ttk.Button(self.file_frame, text="Выйти", command=self.logout)
        self.logout_button.pack(pady=10)

    def list_files(self):
        try:
            self.ftp.set_pasv(False)
            files = self.ftp.nlst(self.current_directory)  # Получаем список файлов и директорий
            directories = []
            regular_files = []

            for file in files:
                full_path = os.path.join(self.current_directory, file)
                if self.is_directory(full_path):
                    directories.append(file)
                else:
                    regular_files.append(file)

            # Сортируем директории и файлы
            directories.sort()
            regular_files.sort()

            self.file_listbox.delete(0, tk.END)  # Очищаем список перед добавлением новых файлов
            for directory in directories:
                self.file_listbox.insert(tk.END, directory + "/")  # Добавляем слэш для обозначения директории
            for file in regular_files:
                self.file_listbox.insert(tk.END, file)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список файлов: {e}")

    def enter_directory(self, event):
        selected = self.file_listbox.get(self.file_listbox.curselection())
        if selected.endswith('/'):
            self.previous_directory.append(self.current_directory)  # Сохраняем текущую директорию
            directory_name = selected[:-1]  # Убираем слэш
            self.current_directory = os.path.join(self.current_directory, directory_name)
            self.list_files()

    def is_directory(self, name):
    # Проверка, является ли элемент директорией
        try:
            self.ftp.cwd(name)  # Пытаемся перейти в директорию
            self.ftp.cwd('..')  # Возвращаемся обратно
            return True
        except Exception as e:
            if "550" in str(e):
                return False  # Игнорируем ошибку 550
            raise  # Если это не ошибка 550, поднимаем исключение

    def go_back(self):
        if self.previous_directory:
            self.current_directory = self.previous_directory.pop()  # Возвращаемся к предыдущей директории
            self.list_files()

    def show_file_options(self, event):
        selected = self.file_listbox.get(self.file_listbox.curselection())
        if not selected.endswith('/'):
            self.open_file(selected)

    def open_file(self, filename):
        # Открытие файла для чтения
        try:
            with open(os.path.join(self.current_directory, filename), 'rb') as file:
                content = file.read().decode('utf-8', errors='ignore')  # Чтение файла
                self.show_file_content(filename, content)
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось открыть файл.")

    def show_file_content(self, filename, content):
        # Окно для отображения содержимого файла
        file_window = Toplevel(self.master)
        file_window.title(filename)
        text_area = Text(file_window, wrap='word')
        text_area.insert(tk.END, content)
        text_area.pack(expand=True, fill='both')
        text_area.config(state='disabled')  # Запрет редактирования

    def upload_file(self):
        # Загрузка файла на сервер
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.ftp.set_pasv(False)
                with open(file_path, 'rb') as file:
                    self.ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)
                messagebox.showinfo("Успех", "Файл успешно загружен!")
                self.list_files()  # Обновляем список файлов после загрузки
            except Exception:
                # Убираем вывод конкретной ошибки
               messagebox.showinfo("Информация", "Файл загружен. Нажмите `Обновить список`, чтобы он отобразился")

    def download_file(self):
        # Скачивание файла с сервера
        selected = self.file_listbox.get(self.file_listbox.curselection())
        if selected.endswith('/'):
            messagebox.showwarning("Предупреждение", "Выберите файл для скачивания.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=selected)
        if save_path:
            try:
                self.ftp.set_pasv(True)  # Устанавливаем пассивный режим
                with open(save_path, 'wb') as file:
                    self.ftp.retrbinary(f'RETR {selected}', file.write)
                messagebox.showinfo("Успех", "Файл успешно скачан!")
            except Exception:
                messagebox.showerror("Ошибка", "Не удалось скачать файл.")

    def logout(self):
        if hasattr(self, 'ftp'):
            try:
                self.ftp.quit()  # Закрываем соединение с FTP-сервером
            except Exception:
                pass  # Игнорируем ошибки при выходе
        self.show_login_frame()  # Возвращаемся к форме авторизации

    def show_login_frame(self):
        # Удаляем форму отображения файлов
        if self.file_frame:
            self.file_frame.pack_forget()

        # Возвращаемся к форме авторизации
        self.login_frame.pack(padx=10, pady=10)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def close(self):
        if hasattr(self, 'ftp'):
            try:
                self.ftp.quit()
            except Exception:
                pass  # Игнорируем ошибки при выходе
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClient(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()