import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
from ftplib import FTP_TLS

class FTPClient:
    def __init__(self, master):
        self.master = master
        self.master.title("FTP Client")

        # Первая форма - авторизация
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(padx=10, pady=10)

        tk.Label(self.login_frame, text="Логин:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Пароль:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Войти", command=self.login)
        self.login_button.grid(row=2, columnspan=2)

        # Вторая форма - отображение файлов
        self.file_frame = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            self.ftp = FTP_TLS('127.0.0.1')  # Используем FTP_TLS
            self.ftp.login(user=username, passwd=password)  # Аутентификация
            self.ftp.prot_p()  # Устанавливаем защищенный режим передачи данных
            messagebox.showinfo("Успех", "Успешная авторизация!")
            self.show_files()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")

    def show_files(self):
        # Удаляем форму авторизации
        self.login_frame.pack_forget()

        # Создаем новую форму для отображения файлов
        self.file_frame = tk.Frame(self.master)
        self.file_frame.pack(padx=10, pady=10)

        tk.Label(self.file_frame, text="Список файлов и директорий:").pack()

        self.file_listbox = Listbox(self.file_frame, width=50, height=15)
        self.file_listbox.pack(side=tk.LEFT)

        scrollbar = Scrollbar(self.file_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)

        self.list_files()

        # Кнопка "Выйти"
        self.logout_button = tk.Button(self.file_frame, text="Выйти", command=self.logout)
        self.logout_button.pack(pady=10)

    def list_files(self):
        try:
            files = self.ftp.nlst()  # Получаем список файлов и директорий
            for file in files:
                self.file_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список файлов: {e}")

    def logout(self):
        if hasattr(self, 'ftp'):
            self.ftp.quit()  # Закрываем соединение с FTP-сервером
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
            self.ftp.quit()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClient(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()