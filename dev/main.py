#  __  __      _      ___   _   _
# |  \/  |    / \    |_ _| | \ | |
# | |\/| |   / _ \    | |  |  \| |
# | |  | |  / ___ \   | |  | |\  |
# |_|  |_| /_/   \_\ |___| |_| \_|
#
import sys
import numpy as np
from PySide6.QtWidgets import QWidget, QTabWidget, QApplication
from db_credential import PostgreSQLCredential
from klustr_dao import PostgreSQLKlustRDAO
from klustr_utils import qimage_argb32_from_png_decoding, ndarray_from_qimage_argb32
from klustr_widget import KlustRDataSourceViewWidget
from klustr_analyze import KlustRDataAnalyzeViewWidget
from knn import KNN
from shapeanalyzer import ShapeAnalyzer


class Main():
    def __init__(self):
        credential = PostgreSQLCredential(password='ASDasd123')
        klustr_dao = PostgreSQLKlustRDAO(credential)
        self.training_data = []
        self.knn = KNN(3, 3)
        self.shape_analyzer = ShapeAnalyzer(None, 10)
        self.source_data_widget = KlustrMain(self, klustr_dao)
        self.source_data_widget.window_title = 'Kluster App'

    def new_dataset(self, dataset):
        self.knn.clear_dataset()
        self.training_data.clear()
        for image in dataset:
            label = image[1]
            img_temp = qimage_argb32_from_png_decoding(image[6])
            ndarray = ndarray_from_qimage_argb32(img_temp)
            flipped_ndarray = np.logical_not(ndarray).astype(int)
            point = self.shape_analyzer.analyze(flipped_ndarray)
            self.knn.add_training_point(point, label)
            self.training_data.append(point)

    def classify(self, chosen_image):
        flipped_ndarray = np.logical_not(chosen_image).astype(int)
        unclassified_point = self.shape_analyzer.analyze(flipped_ndarray)
        label = self.knn.classify(unclassified_point)
        return [unclassified_point, label]

    # à utiliser avec le scrollbar de distance
    def set_max_distance(self, distance):
        self.knn.distance_max = distance

    # à utiliser avec le scrollbar de knn
    def set_k_constant(self, k_constant):
        self.knn.k_constant = k_constant

class KlustrMain(QWidget):
    def __init__(self, controleur, klustr_dao, parent=None):
        super().__init__(parent)
        self.tabs = QTabWidget()
        self.tab1 = KlustRDataSourceViewWidget(klustr_dao)
        self.tab2 = KlustRDataAnalyzeViewWidget(controleur, klustr_dao)
        self.tabs.add_tab(self.tab1, "Tab 1")
        self.tabs.add_tab(self.tab2, "Tab 2")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.source_data_widget.tabs.show()
    sys.exit(app.exec_())