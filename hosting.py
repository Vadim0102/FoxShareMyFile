import os
import hashlib
import sys
import threading
import tkinter as tk
from flask import Flask, send_file, jsonify
from pyngrok import ngrok

app = Flask(__name__)

# Глобальные переменные
file_path = None
file_name = None
ngrok_url = None


# Функция для получения хэша файла
def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Роут для отдачи файла через '/'
@app.route('/')
def serve_file():
    return send_file(file_path, as_attachment=True)


# Роут для отдачи файла через '/имя-файла'
# @app.route(f'/{file_name}')
def serve_file_with_name():
    return send_file(file_path, as_attachment=True)


# Роут для отдачи хэша файла
@app.route('/hash')
def serve_hash():
    file_hash = get_file_hash(file_path)
    return jsonify({"hash": file_hash})


# Функция для запуска веб-сервера
def start_flask():
    app.run(port=5000, use_reloader=False)


# Функция для запуска ngrok и возврата публичного URL
def start_ngrok():
    global ngrok_url
    public_url = ngrok.connect(5000)
    ngrok_url = f"fsmf://{public_url.public_url}/{file_name}"
    return ngrok_url


# Функция для копирования текста в буфер обмена
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


# Функция для создания GUI
def create_gui(ngrok_url):
    global root
    root = tk.Tk()
    root.title("Файл-сервер")

    url_label = tk.Label(root, text="URL:")
    url_label.pack()

    url_entry = tk.Entry(root, width=url_label.size()[0])
    url_entry.insert(0, ngrok_url)
    url_entry.pack()

    # Добавление кнопки для копирования URL
    copy_button = tk.Button(root, text="Копировать", command=lambda: copy_to_clipboard(url_entry.get()))
    copy_button.pack()

    root.mainloop()


# Главная функция
if __name__ == '__main__':
    # Получение пути к файлу из аргументов командной строки
    if len(sys.argv) != 2:
        print("Использование: python script.py <путь_к_файлу>")
        sys.exit(1)

    file_path = sys.argv[1]
    file_name = os.path.basename(file_path)

    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        sys.exit(1)

    app.route(f'/{file_name}')(serve_file_with_name)

    # Запуск Flask-сервера в отдельном потоке
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Запуск ngrok и получение публичного URL с именем файла
    ngrok_url = start_ngrok()

    # Создание GUI с URL
    create_gui(ngrok_url)
