import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from ftplib import FTP
import os
import logging
import json

# Настройка логирования
# logging.basicConfig(filename='ftp_client.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernFTPClient:
    CONFIG_FILE = 'ftp_config.json'

    def __init__(self):
        self.ftp_connection = None
        self.current_directory = '/'
        self.login_window_instance = None
        self.main_window_instance = None
        self.load_config()  # Загружаем конфигурацию
        self.login_window()

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.last_ip = config.get('ip', '')
                self.last_port = config.get('port', '')
        else:
            self.last_ip = ''
            self.last_port = ''

    def save_config(self, ip, port):
        config = {
            'ip': ip,
            'port': port
        }
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def login_window(self):
        if self.login_window_instance is None:  # Проверяем, существует ли окно
            self.login_window_instance = ctk.CTk()  # Создаем окно входа
            self.login_window_instance.title("Вход")
            self.login_window_instance.geometry("700x600")

            ctk.CTkLabel(self.login_window_instance, text="FTP Клиент", font=("Roboto", 24)).pack(pady=20)

            ctk.CTkLabel(self.login_window_instance, text="IP-адрес:").pack()
            self.ip_entry = ctk.CTkEntry(self.login_window_instance, placeholder_text="Введите IP-адрес")
            self.ip_entry.pack(pady=10)
            self.ip_entry.insert(0, self.last_ip)  # Заполняем поле IP

            ctk.CTkLabel(self.login_window_instance, text="Порт:").pack()
            self.port_entry = ctk.CTkEntry(self.login_window_instance, placeholder_text="Введите порт", validate="key")
            self.port_entry.pack(pady=10)
            self.port_entry.insert(0, self.last_port)  # Заполняем поле порта

            ctk.CTkLabel(self.login_window_instance, text="Логин:").pack()
            self.username_entry = ctk.CTkEntry(self.login_window_instance, placeholder_text="Введите логин")
            self.username_entry.pack(pady=10)

            ctk.CTkLabel(self.login_window_instance, text="Пароль:").pack()
            self.password_entry = ctk.CTkEntry(self.login_window_instance, show="*", placeholder_text="Введите пароль")
            self.password_entry.pack(pady=10)

            login_btn = ctk.CTkButton(self.login_window_instance, text="Войти", command=self.login)
            login_btn.pack(pady=20)

        self.login_window_instance.deiconify()  # Показываем окно входа

    def login(self):
        ip_address = self.ip_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            self.ftp_connection = FTP()
            self.ftp_connection.connect(ip_address, int(port))  # Используем введенные IP и порт
            self.ftp_connection.login(user=username, passwd=password)

            logging.info(f"Успешное подключение к FTP-серверу с логином {username}")

            self.save_config(ip_address, port)  # Сохраняем IP и порт
            self.login_window_instance.withdraw()  # Скрываем окно входа
            self.main_window()  # Переходим к основному окну

        except Exception as e:
            logging.error(f"Не удалось подключиться к FTP-серверу: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")

    def main_window(self):
        if self.main_window_instance is None:  # Проверяем, существует ли основное окно
            self.main_window_instance = ctk.CTk()  # Создаем основное окно
            self.main_window_instance.title("FTP Клиент")
            self.main_window_instance.geometry("1200x600")

            # Создаем отдельный фрейм для отображения текущей директории
            self.path_frame = ctk.CTkFrame(self.main_window_instance)
            self.path_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))

            # Label для отображения текущей директории
            self.current_dir_label = ctk.CTkLabel(self.path_frame, text=f"Текущая директория: {self.current_directory}")
            self.current_dir_label.pack(pady=5)

            self.dir_frame = ctk.CTkFrame(self.main_window_instance, width=200)
            self.dir_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            self.dir_frame.grid_propagate(False)

            self.dir_label = ctk.CTkLabel(self.dir_frame, text="Директории")
            self.dir_label.pack(pady=10)

            # Создаем фрейм для Listbox и Scrollbar
            self.dir_listbox_frame = ctk.CTkFrame(self.dir_frame)
            self.dir_listbox_frame.pack(fill=tk.BOTH, expand=True)

            self.dir_listbox = tk.Listbox(self.dir_listbox_frame, bg="#2E2E2E", fg="#FFFFFF", font=("Roboto", 12), selectbackground="#4A4A4A", selectforeground="#FFFFFF")
            self.dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.scrollbar = tk.Scrollbar(self.dir_listbox_frame, command=self.dir_listbox.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.dir_listbox.config(yscrollcommand=self.scrollbar.set)

            self.file_frame = ctk.CTkFrame(self.main_window_instance, width=500)
            self.file_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
            self.file_frame.grid_propagate(False)

            self.file_label = ctk.CTkLabel(self.file_frame, text="Файлы")
            self.file_label.pack(pady=10)

            # Создаем фрейм для Listbox и Scrollbar для файлов
            self.file_listbox_frame = ctk.CTkFrame(self.file_frame)
            self.file_listbox_frame.pack(fill=tk.BOTH, expand=True)

            self.file_listbox = tk.Listbox(self.file_listbox_frame, bg="#2E2E2E", fg="#FFFFFF", font=("Roboto", 12), selectbackground="#4A4A4A", selectforeground="#FFFFFF")
            self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.file_scrollbar = tk.Scrollbar(self.file_listbox_frame, command=self.file_listbox.yview)
            self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.file_listbox.config(yscrollcommand=self.file_scrollbar.set)

            self.control_frame = ctk.CTkFrame(self.main_window_instance)
            self.control_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

            buttons = [
                ("Загрузить", self.upload_file),
                ("Скачать", self.download_file),
                ("Создать папку", self.create_directory),
                ("Удалить", self.delete_item),
                ("Войти", self.enter_directory),
                ("Назад", self.back_directory),
                ("Выход", self.exit)
            ]

            for text, command in buttons:
                btn = ctk.CTkButton(self.control_frame, text=text, command=command)
                btn.pack(side=tk.LEFT, padx=5)

            self.refresh_list()
            self.main_window_instance.protocol("WM_DELETE_WINDOW", self.exit)

        self.main_window_instance.deiconify()  # Показываем основное окно
        self.main_window_instance.mainloop()  # Запускаем главный цикл для основного окна

    def refresh_list(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        try:
            self.file_listbox.delete(0, tk.END)
            self.dir_listbox.delete(0, tk.END)

            items = self.ftp_connection.nlst(self.current_directory)

            for item in items:
                try:
                    self.ftp_connection.cwd(os.path.join(self.current_directory, item))
                    self.dir_listbox.insert(tk.END, item)  # Добавляем директорию в Listbox
                    self.ftp_connection.cwd('..')
                except Exception:
                    self.file_listbox.insert(tk.END, item)  # Добавляем файл в Listbox

            self.current_dir_label.configure(text=f"Текущая директория: {self.current_directory}")  # Обновляем текст

        except Exception as e:
            logging.error(f"Не удалось обновить список: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось обновить список: {str(e)}")

    def upload_file(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        try:
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                self.ftp_connection.storbinary(f'STOR {filename}', file)

            logging.info(f"Файл {filename} успешно загружен")
            self.refresh_list()

        except Exception as e:
            logging.error(f"Не удалось загрузить файл: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def download_file(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_file_index = self.file_listbox.curselection()
        if not selected_file_index:
            messagebox.showwarning("Внимание", "Выберите файл для скачивания")
            return

        selected_file = self.file_listbox.get(selected_file_index)
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=selected_file)
        if not save_path:
            return

        try:
            with open(save_path, 'wb') as file:
                self.ftp_connection.retrbinary(f'RETR {selected_file}', file.write)

            logging.info(f"Файл {selected_file} успешно скачан")

        except Exception as e:
            logging.error(f"Не удалось скачать файл: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось скачать файл: {str(e)}")

    def create_directory(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        new_dir_name = simpledialog.askstring("Создание директории", "Введите имя новой директории")
        if not new_dir_name:
            return

        try:
            if new_dir_name in self.ftp_connection.nlst(self.current_directory):
                messagebox.showerror("Ошибка", "Директория с таким же именем уже существует")
                return

            self.ftp_connection.mkd(os.path.join(self.current_directory, new_dir_name))

            logging.info(f"Директория {new_dir_name} успешно создана")
            self.refresh_list()

        except Exception as e:
            logging.error(f"Не удалось создать директорию: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать директорию: {str(e)}")

    def delete_item(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_file_index = self.file_listbox.curselection()
        selected_dir_index = self.dir_listbox.curselection()

        if not selected_file_index and not selected_dir_index:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления")
            return

        # Если выбран файл
        if selected_file_index:
            selected_file = self.file_listbox.get(selected_file_index)
            try:
                self.ftp_connection.delete(os.path.join(self.current_directory, selected_file))
                logging.info(f"Файл {selected_file} успешно удален")
            except Exception as e:
                logging.error(f"Не удалось удалить файл: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось удалить файл: {str(e)}")

        # Если выбран каталог
        if selected_dir_index:
            selected_dir = self.dir_listbox.get(selected_dir_index)
            try:
                self.ftp_connection.rmd(os.path.join(self.current_directory, selected_dir))
                logging.info(f"Директория {selected_dir} успешно удалена")
            except Exception as e:
                logging.error(f"Не удалось удалить директорию: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось удалить директорию: {str(e)}")

        self.refresh_list()

    def enter_directory(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_dir_index = self.dir_listbox.curselection()
        if not selected_dir_index:
            messagebox.showwarning("Внимание", "Выберите директорию для входа")
            return

        selected_dir = self.dir_listbox.get(selected_dir_index)
        try:
            self.ftp_connection.cwd(os.path.join(self.current_directory, selected_dir))
            self.current_directory = os.path.join(self.current_directory, selected_dir)
            self.refresh_list()
            self.current_dir_label.configure(text=f"Текущая директория: {self.current_directory}")  # Обновляем текст

        except Exception as e:
            logging.error(f"Не удалось войти в директорию: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось войти в директорию: {str(e)}")

    def back_directory(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        try:
            self.ftp_connection.cwd('..')
            self.current_directory = os.path.dirname(self.current_directory)
            self.refresh_list()
            self.current_dir_label.configure(text=f"Текущая директория: {self.current_directory}")  # Обновляем текст

        except Exception as e:
            logging.error(f"Не удалось выйти из директории: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось выйти из директории: {str(e)}")

    def exit(self):
        if self.ftp_connection:
            try:
                self.ftp_connection.quit()
                logging.info("Соединение с FTP-сервером закрыто")
            except Exception as e:
                logging.error(f"Ошибка при выходе из FTP: {str(e)}")

        # Скрываем текущее окно
        self.main_window_instance.withdraw()  # Скрываем основное окно
        self.login_window()  # Переходим к окну входа

def main():
    app = ModernFTPClient()
    app.login_window_instance.mainloop()  # запускаем главный цикл для окна входа

if __name__ == "__main__":
    main()