import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from ftplib import FTP
import os
import logging

# Настройка логирования
logging.basicConfig(filename='ftp_client.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernFTPClient:
    def __init__(self):
        self.login_window()

    def login_window(self):
        self.login_window = ctk.CTk()
        self.login_window.title("Вход")
        self.login_window.geometry("400x300")

        ctk.CTkLabel(self.login_window, text="FTP Клиент", font=("Roboto", 24)).pack(pady=20)

        ctk.CTkLabel(self.login_window, text="Логин:").pack()
        self.username_entry = ctk.CTkEntry(self.login_window, placeholder_text="Введите логин")
        self.username_entry.pack(pady=10)

        ctk.CTkLabel(self.login_window, text="Пароль:").pack()
        self.password_entry = ctk.CTkEntry(self.login_window, show="*", placeholder_text="Введите пароль")
        self.password_entry.pack(pady=10)

        login_btn = ctk.CTkButton(self.login_window, text="Войти", command=self.login)
        login_btn.pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            self.ftp_connection = FTP()
            self.ftp_connection.connect('127.0.0.1', 21)
            self.ftp_connection.login(user=username, passwd=password)
            
            logging.info(f"Успешное подключение к FTP-серверу с логином {username}")
            
            messagebox.showinfo("Успех", "Успешное подключение к FTP-серверу!")
            
            self.login_window.destroy()
            
            self.main_window()

        except Exception as e:
            logging.error(f"Не удалось подключиться к FTP-серверу: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")

    def main_window(self):
        self.main_toplevel = ctk.CTkToplevel()
        self.main_toplevel.title("FTP Клиент")
        self.main_toplevel.geometry("800x600")

        self.current_directory = '/'

        self.dir_frame = ctk.CTkFrame(self.main_toplevel, width=200)
        self.dir_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.dir_frame.grid_propagate(False)

        self.dir_label = ctk.CTkLabel(self.dir_frame, text="Директории")
        self.dir_label.pack(pady=10)

        self.dir_tree = tk.Listbox(self.dir_frame, bg="#2b2b2b", fg="white", selectbackground="#3b3b3b")
        self.dir_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.file_frame = ctk.CTkFrame(self.main_toplevel, width=500)
        self.file_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.file_frame.grid_propagate(False)

        self.file_label = ctk.CTkLabel(self.file_frame, text="Файлы")
        self.file_label.pack(pady=10)

        self.file_list = tk.Listbox(self.file_frame, bg="#2b2b2b", fg="white", selectbackground="#3b3b3b")
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.control_frame = ctk.CTkFrame(self.main_toplevel)
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
        self.main_toplevel.protocol("WM_DELETE_WINDOW", self.exit)

    def refresh_list(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        try:
            self.file_list.delete(0, tk.END)
            self.dir_tree.delete(0, tk.END)

            items = self.ftp_connection.nlst(self.current_directory)

            for item in items:
                try:
                    # Проверяем, является ли элемент директорией
                    self.ftp_connection.cwd(os.path.join(self.current_directory, item))
                    self.dir_tree.insert(tk.END, item)
                    self.ftp_connection.cwd('..')  # Возвращаемся обратно
                except Exception:
                    self.file_list.insert(tk.END, item)

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

        selected_indices = self.file_list.curselection()
        if not selected_indices:
            messagebox.showwarning("Внимание", "Выберите файл для скачивания")
            return

        selected_file = self.file_list.get(selected_indices)

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=selected_file)
        if not save_path:
            return

        try:
            with open(save_path, 'wb') as file:
                self.ftp_connection.retrbinary(f'RETR {selected_file}', file.write)

            logging.info(f"Файл {selected_file} успешно скачан")
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
            # Проверяем, существует ли директория с таким же именем
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

        selected_indices = self.file_list.curselection()
        if not selected_indices:
            selected_indices = self.dir_tree.curselection()
            if not selected_indices:
                messagebox.showwarning("Внимание", "Выберите элемент для удаления")
                return

            selected_item = self.dir_tree.get(selected_indices)
            try:
                self.ftp_connection.rmd(os.path.join(self.current_directory, selected_item))

                logging.info(f"Директория {selected_item} успешно удалена")
                messagebox.showinfo("Успех", "Директория успешно удалена")
                self.refresh_list()

            except Exception as e:
                logging.error(f"Не удалось удалить директорию: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось удалить директорию: {str(e)}")
        else:
            selected_file = self.file_list.get(selected_indices)
            try:
                self.ftp_connection.delete(os.path.join(self.current_directory, selected_file))

                logging.info(f"Файл {selected_file} успешно удален")
                messagebox.showinfo("Успех", "Файл успешно удален")
                self.refresh_list()

            except Exception as e:
                logging.error(f"Не удалось удалить файл: {str(e)}")
                messagebox.showerror("Ошибка", f"Не удалось удалить файл: {str(e)}")

    def enter_directory(self):
        if not self.ftp_connection:
            messagebox.showwarning("Внимание", "Нет подключения к серверу")
            return

        selected_indices = self.dir_tree.curselection()
        if not selected_indices:
            messagebox.showwarning("Внимание", "Выберите директорию для входа")
            return

        selected_dir = self.dir_tree.get(selected_indices)
        try:
            self.ftp_connection.cwd(os.path.join(self.current_directory, selected_dir))
            self.current_directory = os.path.join(self.current_directory, selected_dir)
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
        self.main_toplevel.destroy()  # закрываем окно main_toplevel
        self.login_window.destroy()  # закрываем окно login_window

def main():
    app = ModernFTPClient()
    if hasattr(app, 'main_toplevel'):
        app.main_toplevel.mainloop()
    else:
        app.login_window.mainloop()

if __name__ == "__main__":
    main()