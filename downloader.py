import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
from urllib.parse import urlparse
import base64
import zlib


def download_file(url, dest_path, progress_callback):
    response = requests.get(url, stream=True)
    total_length = response.headers.get('content-length')

    if total_length is None:  # если не удалось получить размер
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        progress_callback(100)
    else:
        total_length = int(total_length)
        dl = 0
        with open(dest_path, 'wb') as f:
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(100 * dl / total_length)
                progress_callback(done)

    return dest_path


def confirm_download(url):
    return messagebox.askyesno("Подтверждение", f"Скачать файл с адреса {url}?")


def select_file_path(default_filename):
    return filedialog.asksaveasfilename(
        title="Выберите директорию и имя файла для сохранения",
        initialfile=default_filename,
        defaultextension=".fsmf",
        filetypes=[("All Files", "*.*")]
    )


class DownloadApp(tk.Tk):
    def __init__(self, url, filename):
        super().__init__()

        self.url = url
        self.filename = filename
        self.filepath = None

        self.title("FSMF Downloader")
        self.geometry("400x150")

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.start_download()

    def start_download(self):
        if confirm_download(self.url):
            self.filepath = select_file_path(self.filename)
            if not self.filepath:
                messagebox.showwarning("Внимание", "Не выбран файл для сохранения")
                self.destroy()
                return

            self.download_file_with_progress()
        else:
            self.destroy()

    def download_file_with_progress(self):
        def update_progress(progress):
            self.progress['value'] = progress
            self.update_idletasks()

        download_file(self.url, self.filepath, update_progress)
        messagebox.showinfo("Завершено", f"Файл успешно скачан в {self.filepath}!")
        self.destroy()


def extract_url_and_filename(argument):
    if argument.startswith("fsmf://"):
        url = argument[7:]
        if url.startswith('0'):
            return extract_url_and_filename('fsmf://' + process_url(*url.split(':', 1)))
        parsed = urlparse(url)

        # Разделение на URL и имя файла, если оно указано через ":"
        if ':' in parsed.path:
            path, filename = parsed.path.split(':')
            url = parsed._replace(path=path).geturl()  # URL без имени файла
        else:
            url = parsed.geturl()
            filename = os.path.basename(parsed.path) or f"file_{hash(url)}.fsmf"

        return url, filename
    elif argument.endswith(".fsmf"):
        with open(argument, 'r') as f:
            return extract_url_and_filename('fsmf://' + f.read().rstrip())
    else:
        raise ValueError("Некорректный формат аргумента")


def process_url(methods, data):
    if 'b64' in methods:
        try:
            # Пробуем декодировать Base64
            decoded_data = base64.b64decode(data)
            try:
                # Пробуем распаковать данные
                decompressed_data = zlib.decompress(decoded_data)
                return decompressed_data.decode()
            except zlib.error:
                return decoded_data.decode()
        except (base64.binascii.Error, TypeError):
            raise ValueError("Нарушена работа декодера Base64")


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 downloader.py <fsmf://url_address> или <путь к файлу .fsmf>")
        sys.exit(1)

    argument = sys.argv[1]
    try:
        url, filename = extract_url_and_filename(argument)
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    app = DownloadApp(url, filename)
    app.mainloop()


if __name__ == "__main__":
    main()
