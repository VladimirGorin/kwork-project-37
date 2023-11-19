import tkinter as tk
from tkinter import messagebox
import os

class ChannelLinkExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Channel Link Extractor")

        # Создаем поле ввода
        self.label = tk.Label(root, text="Введите номер:")
        self.label.pack(pady=10)
        self.entry = tk.Entry(root)
        self.entry.pack(pady=10)

        # Создаем кнопку
        self.button = tk.Button(root, text="Продолжить", command=self.extract_links)
        self.button.pack(pady=20)

    def extract_links(self):
        number = self.entry.get()
        if not number:
            messagebox.showwarning("Предупреждение", "Введите номер")
            return

        # Создаем папку results, если она не существует
        results_folder = "./results"
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        try:
            # Проверяем наличие .log файла, если его нет - пробуем .txt
            log_file_path = f"./logs/{number}.log"
            if not os.path.exists(log_file_path):
                log_file_path = f"./logs/{number}.txt"

            with open(log_file_path, "r", encoding="utf-8") as log_file:
                with open(f"{results_folder}/{number}.txt", "w") as result_file:
                    for line in log_file:
                        if "Ссылка на канал:" in line:
                            channel_link = line.split("Ссылка на канал:")[1].strip()
                            result_file.write("https://t.me/"+ channel_link + "\n")

            messagebox.showinfo("Успех", "Данные успешно сохранены!")

        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл {number}.log или {number}.txt не найден.")
        except UnicodeDecodeError:
            messagebox.showerror("Ошибка", f"Ошибка декодирования файла. Проверьте кодировку файла.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChannelLinkExtractor(root)
    root.mainloop()
