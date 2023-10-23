import os
import sys
import time
import sqlite3
from error_codes import error_codes
from pynput import keyboard
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QTextEdit,
)


class Handler:
    """Вывод информации в логи"""

    def __call__(self, value, end="\n"):
        """Добавить информацию в переменную логи"""
        logs.append(value + end)


class Menu(QMainWindow):
    """Основное меню программы"""

    def __init__(self):
        """Инициализировать программу"""
        super().__init__()
        self.switch = True
        self.initUI()

    def initUI(self):
        """Настроить интерфейс виджета"""
        self.move(origin_x, origin_y)
        self.setFixedSize(330, 216)
        uic.loadUi("menu.ui", self)

        if skin_directory is not None:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setStyleSheet(stylesheet)

            self.pad_image = orig_pad_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(330, 216)
            self.pad.setPixmap(self.padding_map)

            self.border_image = orig_bound_file.copy()
            self.boundmap = QPixmap.fromImage(self.border_image).scaled(330, 216)
            self.border.setPixmap(self.boundmap)

            self.orig_logo_file = QImage(skin_directory + "/logo.png")
            self.logo_image = self.orig_logo_file.copy()
            self.pixmap = QPixmap.fromImage(self.logo_image).scaledToWidth(330)
            self.logo.setPixmap(self.pixmap)

        self.close_btn.clicked.connect(self.exit)
        self.config_btn.clicked.connect(self.call_config)
        self.settings_btn.clicked.connect(self.call_settings)

    def exit(self):
        """Закрыть все кастомные виджеты и выйти из программы"""
        if error:
            log_output = open(f"log{time.time()}.txt", "w")
            log_output.write("\n".join(logs))
            log_output.close()
        self.close()
        for elem in existing_widgets:
            elem.close()
        sys.exit()

    def call_config(self):
        """Переключить программу в режим Конфигурации"""
        global current_Mode
        config_menu.show()
        current_Mode = "Config"
        self.hide()

    def call_settings(self):
        """Переключить программу в режим Настройки"""
        global current_Mode
        settings_menu.show()
        current_Mode = "Settings"
        self.hide()

    def visibility(self):
        """Убрать и показать виджет при нажатии кнопки Home"""
        if self.switch:
            self.hide()
        elif not self.switch and current_Mode == "Menu":
            self.show()
        self.switch = not self.switch


class Settings(QWidget):
    """Меню Настройки"""

    def __init__(self):
        """Инициализировать программу"""
        super().__init__()
        self.switch = True
        self.initUI()

    def initUI(self):
        global importWidgets, exportWidgets
        """Настроить интерфейс виджета"""
        self.move(origin_x, origin_y)
        self.setFixedSize(330, 216)
        uic.loadUi("settings.ui", self)
        if skin_directory is not None:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setStyleSheet(stylesheet)

            self.pad_image = orig_pad_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(330, 216)
            self.pad.setPixmap(self.padding_map)

            self.border_image = orig_bound_file.copy()
            self.boundmap = QPixmap.fromImage(self.border_image).scaled(330, 216)
            self.border.setPixmap(self.boundmap)

        self.close_btn.clicked.connect(self.exit)
        self.export_btn.clicked.connect(exportWidgets)
        self.import_btn.clicked.connect(importWidgets)
        self.reset_btn.clicked.connect(resetWidgets)
        self.debug_btn.setChecked(debug)
        self.debug_btn.clicked.connect(self.debug_mode)

        self.refresh_rate.addItems(["1 Hz", "2 Hz", "5 Hz", "10 Hz"])
        self.ui_skin.resize(85, 18)
        self.ui_skin.addItems(available_skins)

        self.location = QLabel(f"Current code location: {directory[:40]}", self)
        self.location.resize(330 - 2, int(216 * 0.15))
        self.location.move(int(330 * 0.017), int(216 * 0.80))

    def exit(self):
        """Переключить программу в режим Меню"""
        global current_Mode
        menu.show()
        current_Mode = "Menu"
        self.hide()

    def visibility(self):
        """Убрать и показать виджет при нажатии кнопки Home"""
        if self.switch:
            self.hide()
        elif not self.switch and current_Mode == "Settings":
            self.show()
        self.switch = not self.switch

    def debug_mode(self):
        """Переключить режим откладки"""
        global debug
        debug = self.debug_btn.isChecked()


class Configure(QWidget):
    """Меню Конфгурации"""

    def __init__(self):
        """Инициализировать программу"""
        super().__init__()
        self.switch = True
        self.initUI()

    def initUI(self):
        """Настроить интерфейс виджета"""
        global area, saveWidgets
        self.move(origin_x, origin_y)
        self.setFixedSize(330, 216)
        uic.loadUi("config.ui", self)
        if skin_directory is not None:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            self.setStyleSheet(stylesheet)

            self.pad_image = orig_pad_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(330, 216)
            self.pad.setPixmap(self.padding_map)

            self.border_image = orig_bound_file.copy()
            self.boundmap = QPixmap.fromImage(self.border_image).scaled(330, 216)
            self.border.setPixmap(self.boundmap)

        self.selected_label = QLabel("Selected Label", self)
        self.selected_label.setGeometry(10, 70, 121, 21)

        self.selected = QComboBox(self)
        self.selected.setGeometry(90, 70, 161, 22)
        self.selected.addItems(["Label", "Image"])

        self.spawn_btn = QPushButton("Spawn", self)
        self.spawn_btn.setGeometry(260, 70, 61, 23)
        self.spawn_btn.clicked.connect(self.relay)

        self.save_btn.clicked.connect(saveWidgets)
        self.opacity.valueChanged.connect(self.updateOpacity)

        self.close_btn.clicked.connect(self.exit)
        self.layer.resize(85, 18)

    def exit(self):
        """Переключить программу в режим Меню"""
        global current_Mode
        menu.show()
        current_Mode = "Menu"
        self.hide()

    def visibility(self):
        """Убрать и показать виджет при нажатии кнопки Home"""
        if self.switch:
            self.hide()
        elif not self.switch and current_Mode == "Config":
            self.show()
        self.switch = not self.switch

    def relay(self):
        """Создать Виджет"""
        x = 60
        y = 120
        scale_x = 200
        scale_y = 100
        widget_type = self.selected.currentText()

        if widget_type == "Label":
            Text_Request().exec()
        elif widget_type == "Image":
            file, _ = QFileDialog.getOpenFileName(
                None, "Open File", None, "Image (*.png *.jpg *jpeg)"
            )
            print(file)
            if file != "":
                ImageWidget(x, y, scale_x, scale_y, file)

    def updateOpacity(self, value):
        """Изменить прозрачность виджетов"""
        self.value = value / 100
        for elem in existing_widgets:
            elem.setWindowOpacity(self.value)
        self.opacity.sliderPosition = self.value
        self.opacity.update()


class CustomWidget(QDialog):
    """Основа всех кастомных виджетов"""

    def __init__(self, x, y, scale_x, scale_y, data, *args):
        """Инициализировать программу"""
        global existing_widgets, skin_directory
        super().__init__()
        existing_widgets.append(self)

        self.setGeometry(x, y, scale_x, scale_y)
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.current_x = x
        self.current_y = y
        self.data = data

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.edit = True
        self.drag = False
        self.switch = True
        self.oldPos = self.pos()

        if skin_directory is not None:
            self.pad = QLabel(self)
            self.pad.move(0, 0)
            self.pad_image = widget_pad_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(
                self.scale_x, self.scale_y
            )
            self.pad.setPixmap(self.padding_map)

        self.initUI()
        self.setSizeGripEnabled(True)
        self.show()

    def mousePressEvent(self, event):
        """При нажатии конпки мыши"""
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        """При передвижении мыши"""
        location = event.globalPos()
        part1 = location.x() < self.scale_x - 12 + self.x()
        part2 = location.y() < self.scale_y - 12 + self.y()
        if part1 and part2 or self.drag:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            self.drag = True

    def mouseReleaseEvent(self, event):
        """
        При отпуске мыши
        Удаляет виджет если мышь находилась в 5 пикселях от верхне левого угла экрана
        """
        self.drag = False
        location = event.globalPos()
        part1 = location.x() < 5
        part2 = location.y() < 5
        if part1 and part2:
            self.close()

    def resizeEvent(self, event):
        """При изменении размера"""
        if skin_directory is not None:
            self.scale_x = self.frameGeometry().width()
            self.scale_y = self.frameGeometry().height()
            self.pad.resize(self.scale_x, self.scale_y)
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(
                self.scale_x, self.scale_y
            )
            self.pad.setPixmap(self.padding_map)
            QDialog.resizeEvent(self, event)

    def settings(self):
        """Вернуть настройки виджета"""
        return (
            str(type(self)),
            f"{self.x()},{self.y()}",
            f"{self.scale_x},{self.scale_y}",
            self.data,
        )

    def visibility(self):
        """Убрать и показать виджет при нажатии кнопки Home"""
        if self.switch:
            self.pad.hide()
        elif not self.switch:
            self.pad.show()
        self.switch = not self.switch

    def close(self):
        """Закрыть себя"""
        global existing_widgets
        existing_widgets.remove(self)
        super().close()


class LabelWidget(CustomWidget):
    """Кастомный виджет показа текста"""

    def initUI(self):
        """Настроить интерфейс виджета"""
        self.setStyleSheet("color: orange; font: bold 16px;")

        self.label = QLabel(self.data, self)
        self.label.setGeometry(0, 0, self.scale_x, self.scale_y)
        self.label.setWordWrap(True)

    def resizeEvent(self, event):
        """При изменении размера"""
        self.label.resize(self.scale_x, self.scale_y)
        self.label.setWordWrap(True)
        super().resizeEvent(event)


class ImageWidget(CustomWidget):
    """Кастомный виджет показа текста"""

    def initUI(self):
        """Настроить интерфейс виджета"""
        self.file = self.data[0]
        self.label = QLabel(self)

    def resizeEvent(self, event):
        """При изменении размера"""
        self.scale_x = self.frameGeometry().width()
        self.scale_y = self.frameGeometry().height()
        self.label.resize(self.scale_x, self.scale_y)
        self.pixmap = QPixmap(self.data).scaled(self.scale_x, self.scale_y)
        self.label.setPixmap(self.pixmap)
        super().resizeEvent(event)


class Reset_Warning(QDialog):
    """Виджет предупреждения. Показывается при попытке сбросить все виджеты"""
    def __init__(self):
        """Настроить интерфейс виджета"""
        super().__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Warning!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Are you sure you want to reset your layer configuration?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class Text_Request(QDialog):
    """Запрос текста для виджета текста"""
    def __init__(self):
        """Настроить интерфейс виджета"""
        super().__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Text Request")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        message = QLabel("Text:")
        self.edit = QTextEdit(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(message)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self):
        """При нажатии конпки OK"""
        LabelWidget(60, 120, 200, 100, self.edit.toPlainText())
        super().accept()


def loadWidgets(location="widgets.db"):
    """Загрузить виджеты из локального файла"""
    global existing_widgets
    for elem in existing_widgets:
        elem.close()
    existing_widgets = []
    connection = sqlite3.connect(location)
    cursor = connection.cursor()
    try:
        result = cursor.execute("SELECT * FROM Layer1")
        users = cursor.fetchall()
        for elem in users:
            x, y = elem[1].split(",")
            scale_x, scale_y = elem[2].split(",")
            arg = elem[3]
            x, y, scale_x, scale_y = int(x), int(y), int(scale_x), int(scale_y)
            if elem[0] == "<class '__main__.LabelWidget'>":
                LabelWidget(x, y, scale_x, scale_y, arg)
            elif elem[0] == "<class '__main__.ImageWidget'>":
                ImageWidget(x, y, scale_x, scale_y, arg)
    except Exception:
        error = True
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Layer1 (
        type TEXT NOT NULL,
        location TEXT NOT NULL,
        size TEXT NOT NULL,
        argument TEXT NOT NULL
        )
        """
        )
        connection.commit()
        connection.close()
        output(error_codes["NoDBFile"])
        print(error_codes["NoDBFile"])


def saveWidgets():
    """Сохранить виджеты в локальный файл"""
    global existing_widgets
    connection = sqlite3.connect("widgets.db")
    cursor = connection.cursor()
    cursor.execute("DELETE from Layer1")
    for elem in existing_widgets:
        data = elem.settings()
        cursor.execute(
            "INSERT INTO Layer1 (type, location, size, argument) VALUES (?, ?, ?, ?)",
            data,
        )
    connection.commit()
    connection.close()


def exportWidgets():
    """Сохранить виджеты в указанный файл"""
    name = QFileDialog.getSaveFileName(None, "Save File", None, "Database (*.db)")[0]
    file = open(name, "wb")
    copy = open("widgets.db", "rb")
    data = copy.read()
    file.write(bytearray(data))
    file.close()


def importWidgets():
    """Загрузить виджеты из выбранного файла"""
    file = QFileDialog.getOpenFileName(None, "Open File", None, "Database (*.db)")[0]
    if file != '':
        loadWidgets(file)


def resetWidgets():
    """Удалить все виджеты"""
    global existing_widgets
    if Reset_Warning().exec():
        existing_widgets = []
        saveWidgets()
        loadWidgets()


def global_visibility(*key):
    """Разослать сигнал о переключении видимости"""
    global existing_widgets
    if keyboard.Key.home in key:
        menu.visibility()
        settings_menu.visibility()
        config_menu.visibility()
        for elem in existing_widgets:
            elem.visibility()
        output("Visibility Key pressed")


def reload():
    """Перезагрузить виджеты. Обновление скинов будет в новом обновлении"""
    load_widgets()


def except_hook(cls, exception, traceback):
    """Сбор непредвиденных ошибок"""
    sys.__excepthook__(cls, exception, traceback)


output = Handler()
logs = []
skin_directory = "Classic Gray"
available_skins = []
origin_x = int(1920 * 0.80)
origin_y = int(1080 * 0.05)
current_Mode = "Menu"
directory = os.getcwd()
error = False
debug = True
existing_widgets = []
for path in os.listdir(directory):
    if not os.path.isfile(os.path.join(directory, path)) and os.path.exists(
        os.path.join(directory, path + "/style.css")
    ):
        available_skins.append(path)
try:
    settings = open("settings.json", "r")
except Exception:
    error = True
    settings_file = open("settings.json", "w")
    settings_file.close()
    output(error_codes["NoSettingsFile"])
    print(error_codes["NoSettingsFile"])
try:
    fh = open(skin_directory + "/style.css", "r")
    stylesheet = fh.read()
    orig_pad_file = QImage(skin_directory + "/Padding.png")
    widget_pad_file = QImage(skin_directory + "/WidgetPadding.png")
    orig_bound_file = QImage(skin_directory + "/Border.png")
    fh.close()
except Exception:
    error = True
    if skin_directory != "Classic Gray":
        output(error_codes["NoCustomStylesheet"])
        print(error_codes["NoCustomStylesheet"])
    try:
        fh = open("Classic Gray/style.css", "r")
        stylesheet = fh.read()
        orig_pad_file = QImage("Classic Gray/Padding.png")
        orig_bound_file = QImage("Classic Gray/Border.png")
        fh.close()
        skin_directory = "Classic Gray"
    except Exception:
        output(error_codes["NoStylesheet"])
        print(error_codes["NoStylesheet"])
        skin_directory = None


if __name__ == "__main__":
    listener = keyboard.Listener(on_press=global_visibility)
    listener.start()
    app = QApplication(sys.argv)
    menu = Menu()
    settings_menu = Settings()
    config_menu = Configure()
    menu.show()
    loadWidgets()
    sys.excepthook = except_hook
    sys.exit(app.exec())
