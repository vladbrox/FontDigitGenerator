# build.py
import os
import shutil
from PyInstaller.__main__ import run

# Очистка предыдущих сборок
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Настройки для PyInstaller
opts = [
    'window.py',  # Основной файл приложения
    '--onefile',  # Собрать в один файл
    '--windowed',  # Не показывать консоль (для GUI)
    '--add-data', 'templates;templates',  # Добавить папку templates
    '--add-data', 'static;static',  # Добавить папку static
    '--icon=app.ico',  # Иконка приложения (опционально)
    '--name=FontDigitGenerator'  # Имя исполняемого файла
]

# Запуск PyInstaller
run(opts)