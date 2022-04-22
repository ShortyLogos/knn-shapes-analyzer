import sys

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar # wait for qt6!!! (is not working for now)

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QTimer
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QImage, QPainter
from __feature__ import snake_case, true_property # !!! must be the last import


class KNN:
    def __init__(self, dimension):
        self.training_data = np.empty((0,dimension), dtype=np.float32)

    def add_training_point(self, point, label):
        if point.shape[1] is not self.training_data.shape[1]:
            raise ValueError('ayoye')
        self.training_data = np.append(self.training_data, point, axis=0)


class MPLApp(QMainWindow):

    def __init__(self, parent = None):
        super().__init__(parent)

        self._knn = KNN(3)

        self._elevation = 30
        self._azimuth = 45
        self._azimuth_inc = 2.5

        self._mpl_widget = QtWidgets.QLabel()

        self.set_central_widget(self._mpl_widget)

        self.create_data()

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.start(1000)

    
    def create_data(self):
        rng = np.random.default_rng()
        for _ in range(5):
            self._knn.add_training_point(rng.random((1,3)), 'star')
        # self._data1 = rng.random((4,3))
        # self._data2 = rng.random((4,3))

    @Slot()
    def _rotate(self):
        self.update_mpl()
        self._azimuth += self._azimuth_inc
   
    def update_mpl(self):

        width = 500
        height = 500
        dpi = 100
        figure = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111, projection='3d')
        ax.set_proj_type('persp')

        ax.scatter(self._knn.training_data[:,0], self._knn.training_data[:,1], self._knn.training_data[:,2], marker='o', color='r')
        # ax.scatter(self._data1[:,0], self._data1[:,1], self._data1[:,2], marker='o', color='r')
        # ax.scatter(self._data2[:,0], self._data2[:,1], self._data2[:,2], marker='*', color='b')

        ax.set_title('Espace de solution')
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        ax.view_init(self._elevation, self._azimuth)

        canvas.draw()
        w, h = canvas.get_width_height()
        img = QImage(canvas.buffer_rgba(), w, h, w * 4, QImage.Format_ARGB32)

        self._mpl_widget.setPixmap(QtGui.QPixmap.from_image(img))


def main():
    # QApplication.set_attribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    mpl_app = MPLApp()
    mpl_app.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

