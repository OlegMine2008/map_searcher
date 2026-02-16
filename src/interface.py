import sys
import requests
import os
from dotenv import load_dotenv

from PyQt6 import uic
import io
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import geocoder as geo

load_dotenv(override=True)

template = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QTextEdit" name="enter_cor">
    <property name="geometry">
     <rect>
      <x>130</x>
      <y>40</y>
      <width>521</width>
      <height>31</height>
     </rect>
    </property>
   </widget>
   <widget class="QLabel" name="label">
    <property name="geometry">
     <rect>
      <x>320</x>
      <y>10</y>
      <width>121</width>
      <height>31</height>
     </rect>
    </property>
    <property name="text">
     <string>Введите координаты</string>
    </property>
    <property name="scaledContents">
     <bool>false</bool>
    </property>
   </widget>
   <widget class="QPushButton" name="search">
    <property name="geometry">
     <rect>
      <x>330</x>
      <y>80</y>
      <width>93</width>
      <height>28</height>
     </rect>
    </property>
    <property name="text">
     <string>Найти</string>
    </property>
   </widget>
   <widget class="QLabel" name="picture_here">
    <property name="geometry">
     <rect>
      <x>110</x>
      <y>120</y>
      <width>591</width>
      <height>391</height>
     </rect>
    </property>
    <property name="text">
     <string>TextLabel</string>
    </property>
   </widget>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>26</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>'''

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)
        self.search.clicked.connect(self.get_image)
        self.enter_cor.setText('55.756086, 37.617531')
        self.ll = self.enter_cor.toPlainText()

        # ищем масштаб
        toponym = geo.geocode(self.ll)
        envelope = toponym["boundedBy"]["Envelope"]

        # левая, нижняя, правая и верхняя границы из координат углов:
        l, b = envelope["lowerCorner"].split(" ")
        r, t = envelope["upperCorner"].split(" ")

        # Вычисляем полуразмеры по вертикали и горизонтали
        dx = abs(float(l) - float(r)) / 2.0
        dy = abs(float(t) - float(b)) / 2.0

        # Собираем размеры в параметр span
        self.spn = [dx, dy]

        self.big = [float(x) * 2 for x in self.spn]
        self.litl = [float(x) / 2 for x in self.spn]
    
    def get_image(self):
        if self.ll:
            map_request = f"https://static-maps.yandex.ru/v1?"
        else:
            map_request = f"https://static-maps.yandex.ru/v1?"

        response = requests.get(map_request, params={'apikey' : os.getenv('GEOCODE_APIKEY'),
                                    'geocode' : self.ll,
                                    'spn': self.spn,
                                    'format' : 'json'})

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        try:
            with open('data/image.png', "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)
        
        pixmap = QPixmap('cat.jpg')
        self.picture_here.setPixmap(pixmap)
        self.setCentralWidget(self.picture_here)
        self.resize(pixmap.width(), pixmap.height())
    
    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key.Key_W:
            if self.spn < self.big:
                self.spn = [x + 10 for x in self.spn]
        elif ev.key() == Qt.Key.Key_S:
            if self.spn > self.litl:
                self.spn = [x - 10 for x in self.spn]
        if ev.key() == Qt.Key.Key_End:
            self.ll[1] += 1
        elif ev.key() == Qt.Key.Key_Home:
            self.ll[1] -= 1
        elif ev.key() == Qt.Key.Key_PageUp:
            self.ll[0] += 1
        elif ev.key() == Qt.Key.Key_PageDown:
            self.ll[1] -= 1
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
