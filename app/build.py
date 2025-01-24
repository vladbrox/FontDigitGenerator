import os
import shutil
from PyInstaller.__main__ import run

if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

separator = ';' if os.name == 'nt' else ':'

opts = [
    'window.py',  # Основной файл приложения
    '--onefile',  # Собрать в один файл
    '--windowed',  # Не показывать консоль (для GUI)
    '--add-data', f'templates{separator}templates',  # Добавить папку templates
    '--add-data', f'static{separator}static',  # Добавить папку static
    '--icon=app.ico',  # Иконка приложения (опционально)
    '--name=FontDigitGenerator'  # Имя исполняемого файла
]

run(opts)
