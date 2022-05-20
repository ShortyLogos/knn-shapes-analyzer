import numpy as np
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QImage, Qt
from PySide6.QtWidgets import QWidget, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QScrollBar
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
        self.markers = ('o', '.', 'v', '2', '8', 's', 'X', 'D', '*', 'H')
        self.couleurs =np.array([(1, 1, 0),(1, 0, 1),(1, 0, 0),(.2, .2, .2),(.5, .2, .2),(.2, .5, .2),(.2, .5, .2),(.7, 1, .7),(.7, .5, .7),(.5, 1, .7),(.7, 1, .5)])

        self._elevation = 30
        self._azimuth = 45
        self._azimuth_inc = 2.5

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.start(1000)

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
        # color = rgb(random(0,1), random(0,1), random(0,1))
        # marker = self.markers[random(0, (len(self.markers)-1))]
        index =self._controleur.knn.dataset[:,-1].astype(int)
        ax.scatter(self._controleur.knn.dataset[:, 0], self._controleur.knn.dataset[:, 1],
                   self._controleur.knn.dataset[:, 2], marker='o', color=self.couleurs[(index-1)])

        if self._point_analyse is not None:
            ax.scatter(self._point_analyse[0], self._point_analyse[1], self._point_analyse[2], marker='p',
                       color=(1, 1, 1), edgecolors=(0.8, 0.8, 0.8))  ###########################################

        ax.set_title(self._title)
        ax.set_xlabel(self._x_label)
        ax.set_ylabel(self._y_label)
        ax.set_zlabel(self._z_label)

        ax.view_init(self._elevation, self._azimuth)

        canvas.draw()
        w, h = canvas.get_width_height()
        img = QImage(canvas.buffer_rgba(), w, h, w * 4, QImage.Format_ARGB32)

        self.general_widget.set_pixmap(QtGui.QPixmap.from_image(img))



class KlustRKnnParamsWidget(QWidget):
    value_changed = Signal(str)
    def __init__(self):
        super().__init__()
        self.knn = "knn"
        self.dist = "dist"
        self.general_widget = QGroupBox("Knn parameters")
        general_layout = QVBoxLayout(self.general_widget)

        k_widget = QWidget()
        k_layout = QHBoxLayout(k_widget)
        self.__k_label = QLabel("K = 1")
        k_layout.add_widget(self.__k_label)
        self.__k_scrollbar = QScrollBar()
        self.__k_scrollbar.orientation = Qt.Horizontal
        self.__k_scrollbar.set_range(1,5)
        self.__k_scrollbar.value=1
        k_layout.add_widget(self.__k_scrollbar)
        general_layout.add_widget(k_widget)
        self.__k_scrollbar.valueChanged.connect(self.__update_knn_param)


        #K minimum toujours 1, maximum c'est racine carré du nbr de pop / nbr categorie et le centre est / 2 ou quelque chose du genre
        #dist c'est un hypothénuse d'une genre de normalisation entre tes n axes de ton knn

        dist_widget = QWidget()
        dist_layout = QHBoxLayout(dist_widget)
        self.__dist_label = QLabel("Max dist = 0.3")
        dist_layout.add_widget(self.__dist_label)
        self.__dist_scrollbar = QScrollBar()
        self.__dist_scrollbar.orientation = Qt.Horizontal
        self.__dist_scrollbar.set_range(1, 9)
        self.__dist_scrollbar.value = 3
        dist_layout.add_widget(self.__dist_scrollbar)
        general_layout.add_widget(dist_widget)
        self.__dist_scrollbar.valueChanged.connect(self.__update_distance)

    @Slot()
    def __update_distance(self):
        self.__dist_label.set_text("Max dist = "+str(self.__dist_scrollbar.value/10))
    @Slot()
    def __update_knn_param(self):
        #######ici je dois set self.__k_scrollbar.set_range(1,max_range) avec squareroot(image count)/2 comment get image count?
         self.__k_label.set_text("k = "+str(self.__k_scrollbar.value))

