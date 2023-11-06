import os
import io
import sys
import time
import sqlite3
import PIL, tesserocr
from mss import mss
from PIL import Image
from pynput import keyboard
from PyQt5 import QtCore, uic
from tesserocr import PyTessBaseAPI
from error_codes import error_codes
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter
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
    QRadioButton,
    QListWidget,
    QPushButton,
    QSpinBox,
    QColorDialog,
)


class Handler:
    """Output information into the logs"""

    def __call__(self, value, end="\n"):
        """Add information to logs.
        __call__(value, end) -> logs.append(value + ned)"""
        logs.append(value + end)


class Menu(QMainWindow):
    """Main menu of the program"""

    def __init__(self):
        """Initiate the program"""
        super().__init__()
        self.switch = True
        self.initUI()

    def initUI(self):
        """Configure the widget UI"""
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
        """Close the program"""
        if error:
            log_output = open(f"log{time.time()}.txt", "w")
            log_output.write("\n".join(logs))
            log_output.close()
        self.close()
        for elem in existing_widgets:
            elem.close()
        sys.exit()

    def call_config(self):
        """Switch to config mode"""
        global current_Mode
        config_menu.show()
        current_Mode = "Config"
        self.hide()

    def call_settings(self):
        """Switch to setings mode"""
        global current_Mode
        settings_menu.show()
        current_Mode = "Settings"
        self.hide()

    def visibility(self):
        """Show and hide the widget on call"""
        if self.switch:
            self.hide()
        elif not self.switch and current_Mode == "Menu":
            self.show()
        self.switch = not self.switch


class Settings(QWidget):
    """Settings menu"""

    def __init__(self):
        """Initiate the program"""
        super().__init__()
        self.switch = True
        self.initUI()

    def initUI(self):
        global importWidgets, exportWidgets, hertz
        """Configure the widget UI"""
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

        self.refresh_rate.addItems(["0.5 Hz", "1 Hz", "2 Hz"])
        self.refresh_rate.setCurrentText(f"{hertz} Hz")
        self.ui_skin.resize(85, 18)
        self.ui_skin.addItems(available_skins)
        try:
            self.ui_skin.setCurrentText(skin_directory)
        except Exception:
            try:
                self.ui_skin.setCurrentText("Classic Gray")
            except Exception:
                1 == 1

        self.location = QLabel(f"Current data location: {folder[:40]}", self)
        self.location.resize(330 - 2, int(216 * 0.15))
        self.location.move(int(330 * 0.017), int(216 * 0.80))

        self.close_btn.clicked.connect(self.exit)
        self.export_btn.clicked.connect(exportWidgets)
        self.import_btn.clicked.connect(importWidgets)
        self.reset_btn.clicked.connect(resetWidgets)
        self.debug_btn.toggled.connect(self.debug_mode)
        self.ui_skin.currentTextChanged.connect(self.updateRelay)
        self.refresh_rate.currentTextChanged.connect(self.updateRelay)
        self.tutorial_btn.clicked.connect(self.relink)

        self.debug_btn.setChecked(debug)

    def exit(self):
        """Switch to main menu mode"""
        global current_Mode
        menu.show()
        current_Mode = "Menu"
        self.hide()

    def visibility(self):
        """Show and hide the widget on call"""
        if self.switch:
            self.hide()
        elif not self.switch and current_Mode == "Settings":
            self.show()
        self.switch = not self.switch

    def debug_mode(self):
        """Switch to debug mode"""
        global debug
        debug = self.debug_btn.isChecked()
        saveSettings()

    def updateRelay(self):
        """Update the program settings"""
        global hertz, skin_directory
        hertz = self.refresh_rate.currentText()[:-3]
        skin_directory = self.ui_skin.currentText()
        saveSettings()

    def updateSpeed(self):
        """Update the speed execution label"""
        self.speed.setText(f"Average speed: {median:.3f} seconds")

    def relink(self):
        """Relink the OCR training data"""
        global folder
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder != "":
            self.location.setText(f"Current data location: {folder[:40]}")
            saveSettings()


class Configure(QWidget):
    """Config menu"""

    def __init__(self):
        """Initiate the program"""
        super().__init__()
        self.switch = True
        self.initUI()

    def initUI(self):
        """Configure the widget UI"""
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

        self.listWidget.addItem("Label")
        self.listWidget.addItem("Image")
        self.listWidget.addItem("Recorder")
        self.listWidget.addItem("Variable Display")

        self.save_btn.clicked.connect(saveWidgets)
        self.opacity.valueChanged.connect(self.updateOpacity)
        self.close_btn.clicked.connect(self.exit)
        self.spawn_btn.clicked.connect(self.relay)

    def exit(self):
        """Switch to main menu mode"""
        global current_Mode
        menu.show()
        current_Mode = "Menu"
        self.hide()

    def visibility(self):
        """Show and hide the widget on call"""
        if self.switch:
            self.hide()
        elif not self.switch and current_Mode == "Config":
            self.show()
        self.switch = not self.switch

    def relay(self):
        """Сreate CustomWidget"""
        x = 60
        y = 120
        scale_x = 200
        scale_y = 100
        widget_type = self.listWidget.currentItem().text()
        if widget_type == "Label":
            Text_Request().exec()
        elif widget_type == "Image":
            file, _ = QFileDialog.getOpenFileName(
                None, "Open File", None, "Image (*.png *.jpg *jpeg)"
            )
            if file != "":
                ImageWidget(x, y, scale_x, scale_y, file)
        elif widget_type == "Recorder":
            Recorder(x, y, scale_x, scale_y)
        elif widget_type == "Variable Display":
            if working_variables != {}:
                Variable_Request().exec()

    def updateOpacity(self, value):
        """Change the opacity of the widgets
Parameters:
value (int): the opacity effect value."""
        self.value = value / 100
        for elem in existing_widgets:
            elem.setWindowOpacity(self.value)
        self.opacity.sliderPosition = self.value
        self.opacity.update()


class CustomWidget(QDialog):
    """The base of all custom widgets"""

    def __init__(self, x, y, scale_x, scale_y, data, args=""):
        """Initiate the program.
Parameters:
x int: the origin of the window
y int: the origin of the window
scale_x int: the size of the window
scale_y int: the size of the window
data str: main data
args str: additional data"""
        global existing_widgets, skin_directory
        super().__init__()
        existing_widgets.append(self)

        self.setGeometry(x, y, scale_x, scale_y)
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.current_x = x
        self.current_y = y
        self.data = data
        self.args = args

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.edit = True
        self.drag = False
        self.switch = True
        self.config = False
        self.last = time.time()
        self.oldPos = self.pos()
        self.layout = QVBoxLayout(self)

        if skin_directory is not None:
            self.pad = QLabel(self)
            self.pad.move(0, 0)
            self.pad_image = widget_pad_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(
                self.scale_x, self.scale_y
            )

        self.selectedArea = Selected(self)
        self.layout.addWidget(self.selectedArea)
        self.initUI()
        self.setSizeGripEnabled(True)
        self.menu = WidgetMenu(self)
        self.menu.hide()
        self.show()

    def mousePressEvent(self, event):
        """On mouse press"""
        self.oldPos = event.globalPos()
        current = time.time()
        if current - self.last < 0.3:
            self.config = not self.config
            if self.config and self.switch:
                self.menu.show()
            else:
                self.menu.hide()
        self.last = current

    def mouseMoveEvent(self, event):
        """On mouse move"""
        location = event.globalPos()
        part1 = location.x() < self.scale_x - 15 + self.x()
        part2 = location.y() < self.scale_y - 15 + self.y()
        if part1 or part2 or self.drag:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            self.drag = True
            if not (self.x() == delta.x() and self.y() == delta.y()):
                self.config = False
                self.menu.hide()
            self.menu.move(self, self.x(), self.y())

    def mouseReleaseEvent(self, event):
        """On mouse release"""
        self.drag = False
        location = event.globalPos()
        part1 = location.x() < 5
        part2 = location.y() < 5
        if part1 and part2:
            self.close()
        self.menu.move(self, self.x(), self.y())

    def resizeEvent(self, event):
        """On screen size change"""
        if skin_directory is not None:
            self.scale_x = self.frameGeometry().width()
            self.scale_y = self.frameGeometry().height()
            self.pad.resize(self.scale_x, self.scale_y)
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(
                self.scale_x, self.scale_y
            )
            self.pad.setPixmap(self.padding_map)
            QDialog.resizeEvent(self, event)
        self.config = False
        self.menu.hide()
        self.menu.move(self, self.x(), self.y())

    def settings(self):
        """Return the dettings of the widget
Returns ((x, y), (scale_x, scale_y), data, args)"""
        return (
            str(type(self)),
            f"{self.x()},{self.y()}",
            f"{self.scale_x},{self.scale_y}",
            self.data,
            self.args,
        )

    def visibility(self):
        """Show and hide the widget on call"""
        if self.switch:
            self.pad.hide()
            self.menu.hide()
            self.config = False
        elif not self.switch:
            self.pad.show()
        self.switch = not self.switch

    def close(self):
        """On program close"""
        self.menu.close()
        super().close()


class LabelWidget(CustomWidget):
    """Кастомный виджет показа текста"""

    def initUI(self):
        """Configure the widget UI"""
        self.setFont(self.args)

        self.label = QLabel(self.data, self)
        self.label.setGeometry(0, 0, self.scale_x, self.scale_y)
        self.label.setWordWrap(True)

    def resizeEvent(self, event):
        """On size change"""
        self.label.resize(self.scale_x, self.scale_y)
        self.label.setWordWrap(True)
        super().resizeEvent(event)

    def setText(self, data):
        """Set the new static label text
Parameters:
data str: new text value"""
        self.data = data
        self.label.setText(data)

    def setFont(self, inp):
        """Set the new label font
Parameters
inp str: compacted info about the font"""
        font, size, color = inp.split(";")
        self.args = inp
        self.setStyleSheet(f"color: {color}; font-family: {font}; font-size: {size}px;")


class VariableWidget(CustomWidget):
    """CustomWidget, shows the result from Recorder"""

    def initUI(self):
        """Configure the widget UI"""
        self.setFont(self.args)

        self.label = QLabel(self.data, self)
        self.label.setGeometry(0, 0, self.scale_x, self.scale_y)
        self.label.setWordWrap(True)

        if skin_directory is not None:
            self.icon_label = QLabel(self)
            self.icon_label.setGeometry(0, 0, 10, 10)
            self.icon_image = QImage(skin_directory + "/line.png")
            self.icon_map = QPixmap.fromImage(self.icon_image).scaled(10, 10)
            self.icon_label.setPixmap(self.icon_map)

    def resizeEvent(self, event):
        """On size change"""
        self.label.resize(self.scale_x, self.scale_y)
        self.label.setWordWrap(True)
        super().resizeEvent(event)

    def setText(self, data):
        """Set the new dynamic label text
Parameters:
data str: new text value"""
        self.data = data
        self.label.setText(data)

    def setFont(self, inp):
        """Set the new label font
Parameters
inp str: compacted info about the font"""
        font, size, color = inp.split(";")
        self.args = inp
        self.setStyleSheet(f"color: {color}; font-family: {font}; font-size: {size}px;")

    def updateText(self):
        """Updates the label text according to the results of Recorder"""
        if self.data in working_variables:
            self.label.setText(working_variables[self.data])

    def visibility(self):
        """Show and hide the widget on call"""
        if self.switch:
            self.pad.hide()
            self.menu.hide()
            self.icon_label.hide()
            self.config = False
        elif not self.switch:
            self.pad.show()
            self.icon_label.show()
        self.switch = not self.switch


class ImageWidget(CustomWidget):
    """CustomWidget, shows static image"""

    def initUI(self):
        """Configure the widget UI"""
        self.file = self.data[0]
        self.label = QLabel(self)

    def updateImage(self):
        """Update the given image"""
        self.scale_x = self.frameGeometry().width()
        self.scale_y = self.frameGeometry().height()
        self.label.resize(self.scale_x, self.scale_y)
        self.pixmap = QPixmap(self.data).scaled(self.scale_x, self.scale_y)
        self.label.setPixmap(self.pixmap)

    def resizeEvent(self, event):
        """On size change"""
        self.updateImage()
        super().resizeEvent(event)


class Recorder(CustomWidget):
    """CustomWidget, records data from the screen"""

    def __init__(self, x, y, scale_x, scale_y, data=""):
        """Initiate the program.
Parameters:
x int: the origin of the window
y int: the origin of the window
scale_x int: the size of the window
scale_y int: the size of the window
data str: stored variable name"""
        if data != "":
            self.variable = data
            working_variables[data] = ""
        else:
            i = 0
            while True:
                if "untitled" + str(i) not in working_variables:
                    working_variables["untitled" + str(i)] = ""
                    self.variable = "untitled" + str(i)
                    break
                i += 1
        self.data = self.variable
        super().__init__(x, y, scale_x, scale_y, self.data)

    def initUI(self):
        """Configure the widget UI"""
        if skin_directory is not None:
            self.pad_image = orig_recorder_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(
                self.scale_x, self.scale_y
            )
            self.pad.setPixmap(self.padding_map)
        self.title = QLabel(self.variable, self)
        self.title.move(0, -10)
        self.title.setStyleSheet("QLabel{color: gray}")

    def visibility(self):
        """Show and hide the widget on call"""
        if self.switch:
            self.pad.hide()
            self.title.hide()
        elif not self.switch:
            self.pad.show()
            self.title.show()
        super().visibility()

    def variable(self):
        """Returns the sored variable"""
        return self.variable

    def close(self):
        """Closes the widget"""
        global working_variables
        del working_variables[self.variable]
        super().close()


class WidgetMenu(QWidget):
    """QWidgtet, submenu of the CustomWidget"""

    def __init__(self, owner):
        """Initiate the program
Parameters:
owner CustomWidget: the root of the program"""
        super().__init__()
        self.data = owner.settings()
        location = self.data[1].split(",")
        size = self.data[2].split(",")
        self.scale_x = int(size[0])
        self.scale_y = int(size[1])
        self.x = int(location[0]) + self.scale_x + 10
        self.y = int(location[1])
        self.setGeometry(self.x, self.y, 200, 200)
        self.owner = owner
        self.value = owner.args
        self.initUI()

    def initUI(self):
        """Configure the widget UI"""
        global working_variables
        if skin_directory is not None:
            self.setWindowFlag(Qt.FramelessWindowHint)
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            self.pad = QLabel(self)
            self.pad.move(2, 4)
            self.pad_image = widget_pad_file.copy()
            self.padding_map = QPixmap.fromImage(self.pad_image).scaled(198, 194)
            self.pad.setPixmap(self.padding_map)

            self.border = QLabel(self)
            self.border.move(0, 0)
            self.border_image = orig_bound_file.copy()
            self.boundmap = QPixmap.fromImage(self.border_image).scaled(200, 200)
            self.border.setPixmap(self.boundmap)

        if self.data[0] == "<class '__main__.LabelWidget'>":
            self.name = QLabel("Label", self)
            self.name.move(10, 10)
            self.variable = QTextEdit(self)
            self.variable.move(10, 40)
            self.variable.resize(180, 60)
            self.variable.setText(self.owner.data)
            self.variable.textChanged.connect(self.updateText)
            self.variable_title = QLabel("Text:", self)
            self.variable_title.move(10, 25)
            self.fontInit()

        elif self.data[0] == "<class '__main__.ImageWidget'>":
            self.name = QLabel("Image", self)
            self.name.move(10, 10)
            self.text_name = QLabel("Selected image:", self)
            self.text_name.move(15, 25)
            self.variable_name = QLabel(self.owner.data, self)
            self.variable_name.move(10, 40)
            self.variable_name.resize(180, 40)
            self.variable_name.setWordWrap(True)
            self.variable = QPushButton("Open", self)
            self.variable.move(140, 90)
            self.variable.resize(50, 20)
            self.variable.clicked.connect(self.updateText)

        elif self.data[0] == "<class '__main__.Recorder'>":
            self.name = QLabel("Recorder", self)
            self.name.move(10, 10)
            self.variable_title = QLabel("Connected variable:", self)
            self.variable_title.move(10, 30)
            self.variable = QLabel(self.owner.variable, self)
            self.variable.move(10, 50)

        elif self.data[0] == "<class '__main__.VariableWidget'>":
            self.name = QLabel("Variable Display", self)
            self.name.move(10, 10)
            self.variable_title = QLabel("Connected variable:", self)
            self.variable_title.move(10, 30)
            self.variable = QListWidget(self)
            self.variable.move(10, 50)
            self.variable.resize(180, 50)
            for elem in working_variables:
                self.variable.addItem(elem)
            if self.variable.findItems(self.owner.data, Qt.MatchExactly) != []:
                self.variable.setCurrentItem(
                    self.variable.findItems(self.owner.data, Qt.MatchExactly)[0]
                )
            else:
                self.variable.setCurrentRow(0)
            self.variable.itemSelectionChanged.connect(self.updateText)
            self.fontInit()

        if skin_directory is not None:
            self.name.setStyleSheet("QLabel{font: bold 14px}")
            self.setStyleSheet(stylesheet)
            self.variable.setStyleSheet("QLabel{font: bold 14px}")

        if (
            self.data[0] == "<class '__main__.LabelWidget'>"
            or self.data[0] == "<class '__main__.VariableWidget'>"
        ):
            self.color_button.setStyleSheet(
                "QPushButton{background-color:"
                + self.color
                + "; border-image: url(); border-style: none}"
            )

    def move(self, caller, x, y):
        """Move to according location on call"""
        self.setGeometry(x + caller.scale_x + 10, y, 200, 200)

    def updateText(self):
        """Update the owner class"""
        if self.data[0] == "<class '__main__.LabelWidget'>":
            self.owner.setFont(self.value)
            self.owner.setText(self.variable.toPlainText())
        elif self.data[0] == "<class '__main__.VariableWidget'>":
            self.owner.setFont(self.value)
            self.owner.variable = self.variable.currentItem().text()
            self.owner.setText(self.variable.currentItem().text())
        elif self.data[0] == "<class '__main__.ImageWidget'>":
            file, _ = QFileDialog.getOpenFileName(
                None, "Open File", None, "Image (*.png *.jpg *jpeg)"
            )
            if file != "":
                self.owner.data = file
            self.owner.updateImage()
            self.variable_name.setText(file)

    def show(self):
        """On show"""
        if self.data[0] == "<class '__main__.VariableWidget'>":
            self.variable.clear()
            for elem in working_variables:
                self.variable.addItem(elem)
            if self.variable.findItems(self.owner.data, Qt.MatchExactly) != []:
                self.variable.setCurrentItem(
                    self.variable.findItems(self.owner.data, Qt.MatchExactly)[0]
                )
            else:
                self.variable.setCurrentRow(0)
            self.variable.itemChanged.connect(self.updateText)
        super().show()

    def fontInit(self):
        """Initiate the font selection menu when the owner is LabelWidget or VariableWidget"""
        self.font_family, self.font_size, self.color = self.value.split(";")
        self.font_size = int(self.font_size)

        self.font_label = QLabel("Font:", self)
        self.font_label.move(10, 100)
        self.font_label.setStyleSheet("QLabel{font: bold 14px}")

        self.size_label = QSpinBox(self)
        self.size_label.setRange(4, 128)
        self.size_label.setSingleStep(2)
        self.size_label.setValue(self.font_size)
        self.size_label.move(10, 120)

        self.font = QListWidget(self)
        self.font.move(50, 100)
        self.font.resize(140, 60)
        self.font.addItems(["Arial", "Helvetica", "Times New Roman", "Verdana"])
        self.font.setCurrentItem(
            self.font.findItems(self.font_family, Qt.MatchExactly)[0]
        )

        self.color_button = QPushButton(self)
        self.color_button.move(10, 140)
        self.color_button.resize(40, 17)

        self.size_label.valueChanged.connect(self.exportFont)
        self.font.currentItemChanged.connect(self.exportFont)
        self.color_button.clicked.connect(self.colorSelect)

    def exportFont(self):
        """Returns the compact font
Returns: self.font_family;self.font_size;self.color str"""
        self.font_family, self.font_size = (
            self.font.currentItem().text(),
            self.size_label.value(),
        )
        self.value = f"{self.font_family};{self.font_size};{self.color}"
        self.updateText()

    def colorSelect(self):
        """Updates the owner widget color"""
        self.color = QColorDialog.getColor().name()
        self.color_button.setStyleSheet(
            "QPushButton{background-color:"
            + self.color
            + "; border-image: url(); border-style: none}"
        )
        self.exportFont()


class Selected(QWidget):
    """Selection of the widget. Deprecated..."""

    def __init__(self, owner):
        """Initiate the program"""
        super().__init__()
        size = owner.settings()[2].split(",")
        self.scale_x = int(size[0])
        self.scale_y = int(size[1])
        self.setGeometry(0, 0, self.scale_x, self.scale_y)
        self.switch = True
        self.initUI()

    def initUI(self):
        """Configure the widget UI"""
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        if skin_directory is not None:
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.selected = QLabel(self)
            self.selected.setGeometry(0, 0, self.scale_x, self.scale_y)
            self.selected.setStyleSheet(
                'background-image: url("Classic Gray/wid_selected.png");'
            )
            self.hide()
        else:
            self.setWindowOpacity(0.4)
            self.selected = QLabel(self)
            self.selected.setGeometry(0, 0, self.scale_x, self.scale_y)
            self.selected.setStyleSheet("background-color: skyBlue")
            self.hide()


class Reset_Warning(QDialog):
    """Showed upon trying to reset all widgets"""

    def __init__(self):
        """Configure the widget UI"""
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
    """QDialog, creates LabelWidget"""

    def __init__(self):
        """Configure the widget UI"""
        super().__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Text Request")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.message = QLabel("Text:")
        self.edit = QTextEdit(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def accept(self):
        """On success"""
        LabelWidget(60, 120, 200, 100, self.edit.toPlainText(), "Arial;24;ddd")
        super().accept()


class Variable_Request(QDialog):
    """QDialog, creates variableWidget"""

    def __init__(self):
        """Configure the widget UI"""
        super().__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Variable Display Request")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.message = QLabel("Selected Variable:")
        self.edit = QListWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.buttonBox)
        for elem in working_variables:
            self.edit.addItem(elem)

        self.setLayout(self.layout)

    def accept(self):
        """On success"""
        VariableWidget(
            60, 120, 200, 100, self.edit.currentItem().text(), "Arial;24;ddd"
        )
        super().accept()


def loadWidgets(location="widgets.db"):
    """Load widgets from the local database
Parameters:
location str: location of the database, 'widgets.db' by default"""
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
            font = elem[4]
            x, y, scale_x, scale_y = int(x), int(y), int(scale_x), int(scale_y)
            if elem[0] == "<class '__main__.LabelWidget'>":
                LabelWidget(x, y, scale_x, scale_y, arg, font)
            if elem[0] == "<class '__main__.VariableWidget'>":
                VariableWidget(x, y, scale_x, scale_y, arg, font)
            elif elem[0] == "<class '__main__.ImageWidget'>":
                ImageWidget(x, y, scale_x, scale_y, arg)
            elif elem[0] == "<class '__main__.Recorder'>":
                Recorder(x, y, scale_x, scale_y, arg)
    except sqlite3.OperationalError:
        error = True
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS Layer1 (
        type TEXT NOT NULL,
        location TEXT NOT NULL,
        size TEXT NOT NULL,
        data TEXT NOT NULL,
        argument TEXT NOT NULL
        )
        """
        )
        connection.commit()
        connection.close()
        output(error_codes["NoDBFile"])
        print(error_codes["NoDBFile"])


def saveWidgets(reset=False):
    """Save all widgets to a local file
Parameters:
reset bool: check if we don't save the widgets.
Ivan pls check if this actually does smth."""
    global existing_widgets
    connection = sqlite3.connect("widgets.db")
    cursor = connection.cursor()
    cursor.execute("DELETE from Layer1")
    buffer = []
    if not reset:
        for elem in existing_widgets:
            data = elem.settings()
            if data[0] == "<class '__main__.VariableWidget'>":
                buffer.append(elem)
            else:
                cursor.execute(
                    "INSERT INTO Layer1 (type, location, size, data, argument) VALUES (?, ?, ?, ?, ?)",
                    data,
                )
        for elem in buffer:
            data = elem.settings()
            cursor.execute(
                "INSERT INTO Layer1 (type, location, size, data, argument) VALUES (?, ?, ?, ?, ?)",
                data,
            )
    connection.commit()
    connection.close()


def exportWidgets():
    """Export all widgets to a selected file"""
    name = QFileDialog.getSaveFileName(None, "Save File", None, "Database (*.db)")[0]
    file = open(name, "wb")
    copy = open("widgets.db", "rb")
    data = copy.read()
    file.write(bytearray(data))
    file.close()


def importWidgets():
    """Import all widgets from selected file"""
    file = QFileDialog.getOpenFileName(None, "Open File", None, "Database (*.db)")[0]
    if file != "":
        loadWidgets(file)


def resetWidgets():
    """Remove all widges"""
    global existing_widgets
    if Reset_Warning().exec():
        saveWidgets(reset=True)
        loadWidgets()


def saveSettings():
    """Save local settings to a file"""
    global folder
    settings_file = open("settings.txt", "w")
    loc_debug = 0
    if debug == True:
        loc_debug = 1
    if folder == "":
        folder = 'C:\\Program Files\\Tesseract-OCR\\tessdata"'
    settings_file.write(f"{skin_directory}\n{hertz}\n{loc_debug}\n{folder}")
    settings_file.close()
    interval = int(1000 // float(hertz))
    timer.setInterval(interval)


def global_visibility(*key):
    """Switch visibility upon Home key press"""
    global existing_widgets, working, timer
    if keyboard.Key.home in key:
        if finished:
            menu.visibility()
            settings_menu.visibility()
            config_menu.visibility()
            for elem in existing_widgets:
                elem.visibility()
            working = not working


def globalThread():
    "Update all CustomWidget classes"
    time_one = time.time()
    global finished, median, folder
    finished = False
    if working:
        original = sct.grab(sct.monitors[1])
        original = Image.frombytes("RGB", original.size, original.bgra, "raw", "BGRX")
        for elem in existing_widgets:
            if (
                str(type(elem)) == "<class '__main__.Recorder'>"
                and elem.variable in working_variables
            ):
                data = elem.settings()
                location = data[1].split(",")
                size = data[2].split(",")
                x = int(location[0])
                y = int(location[1])
                scale_x = int(size[0])
                scale_y = int(size[1])
                image = original.crop((x, y, scale_x + x, scale_y + y))
                try:
                    working_variables[data[3]] = tesserocr.image_to_text(
                        image, path=folder
                    )
                except RuntimeError:
                    print(
                        "There is an error with the OCR. You may need to relink it in the settings."
                    )
                    settings_menu.relink()
            if str(type(elem)) == "<class '__main__.VariableWidget'>":
                elem.updateText()
        medium_time.append(time.time() - time_one)
        if len(medium_time) > 5:
            medium_time.remove(medium_time[0])
        median = sum(medium_time) / len(medium_time)
        settings_menu.updateSpeed()
    finished = True


def reload():
    """Reload the widgets"""
    load_widgets()


def except_hook(cls, exception, traceback):
    """Collect the errors"""
    output(error_codes["GenericError"])
    print(error_codes["GenericError"])
    sys.__excepthook__(cls, exception, traceback)


output = Handler()
timer = QTimer()
logs = []
available_skins = []
origin_x = int(1920 * 0.80)
origin_y = int(1080 * 0.05)
current_Mode = "Menu"
directory = os.getcwd()
error = False
finished = False
working = False
debug = False
medium_time = []
existing_widgets = []
working_variables = {}
median = 0
setup = 0
for path in os.listdir(directory):
    if not os.path.isfile(os.path.join(directory, path)) and os.path.exists(
        os.path.join(directory, path + "/style.css")
    ):
        available_skins.append(path)
try:
    settings = open("settings.txt", "r")
    skin_directory = settings.readline()[:-1]
    hertz = settings.readline()[:-1]
    debug = bool(int(settings.readline()[0]))
    folder = settings.readline()
    if folder == "":
        folder = 'C:\\Program Files\\Tesseract-OCR\\tessdata"'
except Exception:
    error = True
    settings_file = open("settings.txt", "w")
    skin_directory = "Classic Gray"
    settings_file.write("Classic Gray\n1\n1\n0")
    settings_file.close()
    output(error_codes["NoSettingsFile"])
    print(error_codes["NoSettingsFile"])
    skin_directory = "Classic Gray"
    hertz = 1
    debug = 0
    folder = 'C:\\Program Files\\Tesseract-OCR\\tessdata"'
try:
    fh = open(skin_directory + "/style.css", "r")
    stylesheet = fh.read()
    orig_pad_file = QImage(skin_directory + "/Padding.png")
    widget_pad_file = QImage(skin_directory + "/WidgetPadding.png")
    orig_bound_file = QImage(skin_directory + "/Border.png")
    orig_selected_file = QImage(skin_directory + "/wid_selected.png")
    orig_recorder_file = QImage(skin_directory + "/recorder.png")
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
        widget_pad_file = QImage("Classic Gray/WidgetPadding.png")
        orig_bound_file = QImage("Classic Gray/Border.png")
        orig_selected_file = QImage("Classic Gray/wid_selected.png")
        orig_recorder_file = QImage("Classic Gray/recorder.png")
        fh.close()
        skin_directory = "Classic Gray"
    except Exception:
        output(error_codes["NoStylesheet"])
        print(error_codes["NoStylesheet"])
        skin_directory = None

if __name__ == "__main__":
    listener = keyboard.Listener(on_press=global_visibility)
    listener.start()
    sct = mss()
    app = QApplication(sys.argv)
    menu = Menu()
    settings_menu = Settings()
    config_menu = Configure()
    menu.show()
    loadWidgets()
    interval = int(1000 // float(hertz))
    timer = QTimer()
    timer.setSingleShot(False)
    timer.setInterval(interval)
    timer.timeout.connect(globalThread)
    timer.start()
    sys.excepthook = except_hook
    sys.exit(app.exec())
