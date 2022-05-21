import numpy as np
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Slot
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QWidget, QLabel
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from __feature__ import snake_case, true_property


class KlustR3DModel(QWidget):
    def __init__(self, controleur, title, xLabel, yLabel, zLabel):
        super().__init__()
        self.general_widget = QLabel()
        self._controleur = controleur
        self._point_analyse = None

        self._title = title
        self._x_label = xLabel
        self._y_label = yLabel
        self._z_label = zLabel
        self.couleurs =np.array([(1, 1, 0),(1, 0, 1),(1, 0, 0),(.2, .2, .2),(.5, .2, .2),(.2, .5, .2),(.2, .5, .2),(.7, 1, .7),(.7, .5, .7),(.5, 1, .7),(.7, 1, .5)])

        self._elevation = 30
        self._azimuth = 45
        self._azimuth_inc = 2.5

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.start(500)

    @property
    def point_analyse(self):
        return self._point_analyse

    @point_analyse.setter
    def point_analyse(self, value):
        self._point_analyse = value

    @Slot()
    def _rotate(self):
        self._update_graphic()
        self._azimuth += self._azimuth_inc

    def _update_graphic(self):
        width = 1000
        height = 1000
        dpi = 100
        figure = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111, projection='3d')
        ax.set_proj_type('persp')
        index =(self._controleur.knn.dataset[:,-1].astype(int))%len(self.couleurs)
        ax.scatter(self._controleur.knn.dataset[:, 0], self._controleur.knn.dataset[:, 1],
                   self._controleur.knn.dataset[:, 2], marker='o', color=self.couleurs[index])

        if self._point_analyse is not None:
            ax.scatter(self._point_analyse[0], self._point_analyse[1], self._point_analyse[2], marker='v', s=200,
                       color=(0, 0, 0)) 

        ax.set_title(self._title)
        ax.set_xlabel(self._x_label)
        ax.set_ylabel(self._y_label)
        ax.set_zlabel(self._z_label)

        ax.view_init(self._elevation, self._azimuth)

        canvas.draw()
        w, h = canvas.get_width_height()
        img = QImage(canvas.buffer_rgba(), w, h, w * 4, QImage.Format_ARGB32)

        self.general_widget.set_pixmap(QtGui.QPixmap.from_image(img))