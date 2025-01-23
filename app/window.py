# window.py
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from threading import Thread
from app import app  # Импортируем Flask-приложение

class FlaskAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Font Digit Generator")
        self.setGeometry(100, 100, 800, 600)  # Размер окна

        # Встроенный браузер
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://localhost:5000"))
        self.setCentralWidget(self.browser)

        # Запуск Flask в отдельном потоке
        self.flask_thread = Thread(target=self.run_flask)
        self.flask_thread.daemon = True
        self.flask_thread.start()

    def run_flask(self):
        app.run(port=5000)

if __name__ == "__main__":
    # Создаем приложение PyQt
    qt_app = QApplication(sys.argv)
    window = FlaskAppWindow()
    window.show()

    # Запускаем главный цикл PyQt
    sys.exit(qt_app.exec_())