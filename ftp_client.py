import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from ftplib import FTP
import os
import logging

# Настройка логирования
# logging.basicConfig(filename='ftp_client.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernFTPClient:
    def __init__(self):
        self.ftp_connection = None
        self.current_directory = '/'
        self.login_window_instance = None
        self.main_window_instance = None
        self.login_window()

    def login_window(self):
        self.login_window_instance = ctk.CTk()  # Создаем окно входа
        self.login_window_instance.title("Вход")
        self.login_window_instance.geometry("700x600")

        ctk.CTkLabel(self.login_window_instance, text="FTP Клиент", font=("Roboto", 24)).pack(pady=20)

        ctk.CTkLabel(self.login_window_instance, text="IP-адрес:").pack()
        self.ip_entry = ctk.CTkEntry(self.login_window_instance, placeholder_text="Введите IP-адрес")
        self.ip_entry.pack(pady=10)

        ctk.CTkLabel(self.login_window_instance, text="Порт:").pack()
        self.port_entry = ctk.CTkEntry(self.login_window_instance, placeholder_text="Введите порт", validate="key")
        self.port_entry.pack(pady=10)

        ctk.CTkLabel(self.login_window_instance, text="Логин:").pack()
        self.username_entry = ctk.CTkEntry(self.login_window_instance, placeholder_text="Введите логин")
        self.username_entry.pack(pady=10)

        ctk.CTkLabel(self.login_window_instance, text="Пароль:").pack()
        self.password_entry = ctk.CTkEntry(self.login_window_instance, show="*", placeholder_text="Введите пароль")
        self.password_entry.pack(pady=10)

        login_btn = ctk.CTkButton(self.login_window_instance, text="Войти", command=self.login)
        login_btn.pack(pady=20)

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

            self.login_window_instance.destroy()  # Закрываем окно входа
            self.main_window()

        except Exception as e:
            logging.error(f"Не удалось подключиться к FTP-серверу: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")

    def main_window(self):
        self.main_window_instance = ctk.CTk()  # Создаем основное окно
        self.main_window_instance.title("FTP Клиент")
        self.main_window_instance.geometry("1200x600")

        self.dir_frame = ctk.CTkFrame(self.main_window_instance, width=200)
        self.dir_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.dir_frame.grid_propagate(False)

        self.dir_label = ctk.CTkLabel(self.dir_frame, text="Директории")
        self.dir_label.pack(pady=10)

        self.dir_tree = ctk.CTkTextbox(self.dir_frame, width=200, height=300)
        self.dir_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.file_frame = ctk.CTkFrame(self.main_window_instance, width=500)
        self.file_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.file_frame.grid_propagate(False)

        self.file_label = ctk.CTkLabel(self.file_frame, text="Файлы")
        self.file_label.pack(pady=10)

        self.file_list = ctk.CTkTextbox(self.file_frame, width=500, height=300)
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.control_frame = ctk.CTkFrame(self.main_window_instance)
        self.control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        buttons = [
            ("Загрузить", self.upload_file),
            ("Скачать", self.download_file),
            ("Создать папку", self.create_directory),
            ("Удалить", self.delete_item),
            ("Обновить", self.refresh_list),
            ("Войти", self.enter_directory),
            ("Назад", self.back_directory),
            ("Выход", self.exit)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(self.control_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

        self.refresh_list()
        self.main_window_instance.protocol("WM_DELETE_WINDOW", self.exit)
        self.main_window_instance.mainloop()  # Запускаем главный цикл для основного окна

    def refresh_list(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        try:
            self.file_list.delete(1.0, tk.END)
            self.dir_tree.delete(1.0, tk.END)

            items = self.ftp_connection.nlst(self.current_directory)

            for item in items:
                try:
                    self.ftp_connection.cwd(os.path.join(self.current_directory, item))
                    self.dir_tree.insert(tk.END, item + "\n")
                    self.ftp_connection.cwd('..')
                except Exception:
                    self.file_list.insert(tk.END, item + "\n")

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
            messagebox.showinfo("Успех", "Файл успешно загружен")
            self.refresh_list()

        except Exception as e:
            logging.error(f"Не удалось загрузить файл: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def download_file(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_file = self.file_list.get("1.0", tk.END).strip().split("\n")
        if not selected_file or selected_file == ['']:
            messagebox.showwarning("Внимание", "Выберите файл для скачивания")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=selected_file[-1])
        if not save_path:
            return

        try:
            with open(save_path, 'wb') as file:
                self.ftp_connection.retrbinary(f'RETR {selected_file[-1]}', file.write)

            logging.info(f"Файл {selected_file[-1]} успешно скачан")
            messagebox.showinfo("Успех", "Файл успешно скачан")

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
            messagebox.showinfo("Успех", "Директория успешно создана")
            self.refresh_list()

        except Exception as e:
            logging.error(f"Не удалось создать директорию: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось создать директорию: {str(e)}")

    def delete_item(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_file = self.file_list.get("1.0", tk.END).strip().split("\n")
        if not selected_file or selected_file == ['']:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления")
            return

        try:
            if selected_file[-1] in self.dir_tree.get("1.0", tk.END).strip().split("\n"):
                self.ftp_connection.rmd(os.path.join(self.current_directory, selected_file[-1]))
                logging.info(f"Директория {selected_file[-1]} успешно удалена")
                messagebox.showinfo("Успех", "Директория успешно удалена")
            else:
                self.ftp_connection.delete(os.path.join(self.current_directory, selected_file[-1]))
                logging.info(f"Файл {selected_file[-1]} успешно удален")
                messagebox.showinfo("Успех", "Файл успешно удален")
            self.refresh_list()

        except Exception as e:
            logging.error(f"Не удалось удалить элемент: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось удалить элемент: {str(e)}")

    def enter_directory(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_dir = self.dir_tree.get("1.0", tk.END).strip().split("\n")
        if not selected_dir or selected_dir == ['']:
            messagebox.showwarning("Внимание", "Выберите директорию для входа")
            return

        try:
            self.ftp_connection.cwd(os.path.join(self.current_directory, selected_dir[-1]))
            self.current_directory = os.path.join(self.current_directory, selected_dir[-1])
            self.refresh_list()

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

        except Exception as e:
            logging.error(f"Не удалось выйти из директории: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось выйти из директории: {str(e)}")

    def exit(self):
        if self.ftp_connection:
            self.ftp_connection.quit()
            logging.info("Соединение с FTP-сервером закрыто")
        self.main_window_instance.destroy()  # закрываем основное окно

def main():
    app = ModernFTPClient()
    app.login_window_instance.mainloop()  # запускаем главный цикл для окна входа

if __name__ == "__main__":
    main()