import sys
import requests
import os
from dotenv import load_dotenv
from untitled_ui import Ui_MainWindow

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, 'data', '.env')
load_dotenv(dotenv_path=ENV_PATH, override=True)

MIN_LON, MAX_LON = -180.0, 180.0
MIN_LAT, MAX_LAT = -90.0, 90.0
MIN_SPN = 0.0001
MAX_SPN_X = 180.0
MAX_SPN_Y = 90.0


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.search.clicked.connect(self.get_image)
        self.checkBox.stateChanged.connect(self.turn_mode)

        self.ll_list = [37.617531, 55.756086]
        self.ll = f"{self.ll_list[0]},{self.ll_list[1]}"
        self.enter_cor.setText(self.ll)

        self.spn = [0.05, 0.05]
        self.zoom_speed = 0.9
        self.move_factor = 0.5
        self.dark = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        self.get_image()

    @staticmethod
    def _clamp(value, low, high):
        return max(low, min(high, value))

    def _normalize_coords(self, lon, lat):
        lon = self._clamp(lon, MIN_LON, MAX_LON)
        lat = self._clamp(lat, MIN_LAT, MAX_LAT)
        return lon, lat

    def _normalize_spn(self):
        self.spn[0] = self._clamp(self.spn[0], MIN_SPN, MAX_SPN_X)
        self.spn[1] = self._clamp(self.spn[1], MIN_SPN, MAX_SPN_Y)

    def _move_map(self, dx_sign, dy_sign):
        self._normalize_spn()
        move_step_x = self.spn[0] * self.move_factor
        move_step_y = self.spn[1] * self.move_factor

        self.ll_list[0] += dx_sign * move_step_x
        self.ll_list[1] += dy_sign * move_step_y
        self.ll_list[0], self.ll_list[1] = self._normalize_coords(self.ll_list[0], self.ll_list[1])

        self.ll = f"{self.ll_list[0]},{self.ll_list[1]}"
        self.enter_cor.setText(self.ll)
        self.get_image()

    def _zoom(self, zoom_in):
        if zoom_in:
            self.spn = [x * self.zoom_speed for x in self.spn]
        else:
            self.spn = [x / self.zoom_speed for x in self.spn]
        self._normalize_spn()
        self.get_image()

    def get_image(self):
        if not self.ll:
            return

        text_coords = self.enter_cor.toPlainText().strip()
        if text_coords:
            try:
                lon, lat = text_coords.split(',')
                lon = float(lon.strip())
                lat = float(lat.strip())
                lon, lat = self._normalize_coords(lon, lat)
                self.ll_list = [lon, lat]
                self.ll = f"{self.ll_list[0]},{self.ll_list[1]}"
            except Exception as e:
                print("Ошибка парсинга координат:", e)
                return

        self._normalize_spn()

        api_key = os.getenv('STATICMAPS_APIKEY')
        if not api_key:
            print("Не найден STATICMAPS_APIKEY в окружении")
            return
        
        if self.dark:
            thema = 'dark'
        else:
            thema = 'light'

        response = requests.get(
            "https://static-maps.yandex.ru/v1",
            params={
                'apikey': api_key,
                'll': self.ll,
                'spn': f"{self.spn[0]},{self.spn[1]}",
                'size': '650,400',
                'lang': 'ru_RU',
                'theme': thema
            },
            timeout=10,
        )

        if response.status_code != 200:
            print(f"Ошибка {response.status_code}")
            print("Ответ сервера:", response.text)
            return

        os.makedirs('data', exist_ok=True)
        with open('data/image.png', 'wb') as f:
            f.write(response.content)

        pixmap = QPixmap('data/image.png')
        self.picture_here.setPixmap(pixmap)
        self.picture_here.resize(pixmap.width(), pixmap.height())
    
    def turn_mode(self):
        self.dark = self.checkBox.isChecked()

    def keyPressEvent(self, ev):
        key = ev.key()

        if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            self._move_map(0.0, +1.0)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self._move_map(0.0, -1.0)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self._move_map(-1.0, 0.0)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self._move_map(+1.0, 0.0)
        elif key == Qt.Key.Key_PageUp:
            self._zoom(True)
        elif key == Qt.Key.Key_PageDown:
            self._zoom(False)
        else:
            super().keyPressEvent(ev)
            return

        ev.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
