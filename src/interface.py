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
        
        self.ll_list = [55.756086, 37.617531]
        self.ll = f"{self.ll_list[0]},{self.ll_list[1]}"
        self.enter_cor.setText(self.ll)
     
        self.spn = [0.05, 0.05]
        self.zoom_speed = 0.9
    
    def get_image(self):
        if not self.ll:
            return
        
        text_coords = self.enter_cor.toPlainText()
        if text_coords:
            try:
                lon, lat = text_coords.split(',')
                self.ll_list = [float(lon.strip()), float(lat.strip())]
                self.ll = text_coords
            except:
                pass
        
        map_request = "https://static-maps.yandex.ru/v1"
        params = {
            'apikey': os.getenv('GEOCODE_APIKEY'),
            'll': self.ll,
            'spn': f"{self.spn[0]},{self.spn[1]}",
            'size': '600,400',
            'lang': 'ru_RU'
        }
        
        response = requests.get(map_request, params=params)
        
        if response.status_code != 200:
            print(f"Ошибка {response.status_code}: {response.url}")
            return
        
        with open('data/image.png', "wb") as file:
            file.write(response.content)
        
        pixmap = QPixmap('data/image.png')
        self.picture_here.setPixmap(pixmap)
        self.picture_here.resize(pixmap.width(), pixmap.height())
    
    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key.Key_W:
            self.spn = [x * self.zoom_speed for x in self.spn]
            self.get_image()
        elif ev.key() == Qt.Key.Key_S:
            self.spn = [x / self.zoom_speed for x in self.spn]
            self.get_image()
        
        move_step = self.spn[0] * 0.5
        if ev.key() == Qt.Key.Key_Up:
            self.ll_list[1] += move_step
        elif ev.key() == Qt.Key.Key_Down:
            self.ll_list[1] -= move_step
        elif ev.key() == Qt.Key.Key_Right:
            self.ll_list[0] += move_step
        elif ev.key() == Qt.Key.Key_Left:
            self.ll_list[0] -= move_step
        else:
            return
        
        self.ll = f"{self.ll_list[0]},{self.ll_list[1]}"
        self.enter_cor.setText(self.ll)
        self.get_image()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())

