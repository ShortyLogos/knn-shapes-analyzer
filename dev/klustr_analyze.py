#  _  __  _                 _     ____    ____            _                _                      _                       __     __  _                    __        __  _       _                  _
# | |/ / | |  _   _   ___  | |_  |  _ \  |  _ \    __ _  | |_    __ _     / \     _ __     __ _  | |  _   _   ____   ___  \ \   / / (_)   ___  __      __ \ \      / / (_)   __| |   __ _    ___  | |_
# | ' /  | | | | | | / __| | __| | |_) | | | | |  / _` | | __|  / _` |   / _ \   | '_ \   / _` | | | | | | | |_  /  / _ \  \ \ / /  | |  / _ \ \ \ /\ / /  \ \ /\ / /  | |  / _` |  / _` |  / _ \ | __|
# | . \  | | | |_| | \__ \ | |_  |  _ <  | |_| | | (_| | | |_  | (_| |  / ___ \  | | | | | (_| | | | | |_| |  / /  |  __/   \ V /   | | |  __/  \ V  V /    \ V  V /   | | | (_| | | (_| | |  __/ | |_
# |_|\_\ |_|  \__,_| |___/  \__| |_| \_\ |____/   \__,_|  \__|  \__,_| /_/   \_\ |_| |_|  \__,_| |_|  \__, | /___|  \___|    \_/    |_|  \___|   \_/\_/      \_/\_/    |_|  \__,_|  \__, |  \___|  \__|
#                                                                                                     |___/                                                                         |___/
import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, \
    QGroupBox, QComboBox, QFormLayout

from dev.klustr_model3D import KlustRKnnParamsWidget, KlustR3DModel
from dev.klustr_utils import qimage_argb32_from_png_decoding, ndarray_from_qimage_argb32
from __feature__ import snake_case, true_property


class KlustRDataAnalyzeViewWidget(QWidget):
    def __init__(self, controleur, klustr_dao, parent=None):
        super().__init__(parent)
        self._klustr_dao = klustr_dao
        self._controleur = controleur
        if self._klustr_dao.is_available:
            self._setup_gui()
            self._setup_models()
        else:
            self._setup_invalid_gui()

    def _setup_models(self):
        self.dataset_widget.update(self._klustr_dao)

    def _setup_invalid_gui(self):
        not_available = QLabel('Data access unavailable')
        not_available.alignment = Qt.AlignCenter
        not_available.enabled = False
        layout = QGridLayout(self)
        layout.add_widget(not_available)
        QMessageBox.warning(self, 'Data access unavailable', 'Data access unavailable.')

    def _setup_gui(self):
        #--------- Dataset ---------#
        self.dataset_widget = KlustRDatasetAnalyzeModel()
        self.dataset_widget.dataset_selected.connect(self._update_from_selection)

        #--------- Knn params ---------#
        self.knn_parameters_widget = KlustRKnnParamsWidget()

        #--------- Single_test ---------#
        self.single_test_widget = KlustRSingleAnalyzeModel()
        self.single_test_widget.classify.connect(self._classify)

        #--------- About Button ---------#
        bouton_about = QPushButton("About")
        bouton_about.clicked.connect(self.__show_dialog)

        #--------- Data General layout ---------#
        view_data_widget = QWidget()
        view_data_layout = QVBoxLayout(view_data_widget)
        view_data_layout.add_widget(self.dataset_widget.general_widget)
        view_data_layout.add_widget(self.knn_parameters_widget.general_widget)
        view_data_layout.add_widget(self.single_test_widget.general_widget)
        view_data_layout.add_stretch()
        view_data_layout.add_widget(bouton_about)
        view_data_widget.set_fixed_width(500)

        #--------- 3D General Layout ---------#
        view_graphic_widget = QWidget()
        view_graphic_layout = QVBoxLayout(view_graphic_widget)
        self.graphic_widget = KlustR3DModel(self._controleur,'KLUSTR KNN CLASSIFICATION', "Pixels On Outer Radius", "Donut Ratio", "Complexity Index")
        view_graphic_layout.add_widget(self.graphic_widget.general_widget)

        #--------- Main Layout ---------#
        layout = QHBoxLayout(self)
        layout.add_widget(view_data_widget)
        layout.add_stretch()
        layout.add_widget(view_graphic_widget)
        layout.add_stretch()

    @Slot()
    def __show_dialog(self):
        msgBox = QMessageBox()
        with open("readme.txt") as readme:
            contents = readme.read()
            msgBox.text=(contents)
        msgBox.exec()

    @Slot()
    def _update_from_selection(self, chosen_dataset):
        dataset_train = self._klustr_dao.image_from_dataset(chosen_dataset,True)
        dataset_test = self._klustr_dao.image_from_dataset(chosen_dataset,False)
        self.single_test_widget.update_from_dataset(dataset_test)
        self._controleur.new_dataset(dataset_train)

    @Slot()
    def _classify(self, chosen_image): #type ndarray
        knn = self.knn_parameters_widget.knn
        dist = self.knn_parameters_widget.dist
        point, label = self._controleur.classify(chosen_image) ####################################################################
        self.graphic_widget.point_analyse = point
        self.single_test_widget.update_text(label)


class KlustRDatasetAnalyzeModel(QWidget):
    dataset_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.general_widget = QGroupBox("Dataset")
        general_layout = QVBoxLayout(self.general_widget)

        self.dataset_combo_box = QComboBox()
        self.dataset_combo_box.currentIndexChanged.connect(self.__selection_dataset)
        general_layout.add_widget(self.dataset_combo_box)

        infos_widget = QWidget()
        infos_layout = QHBoxLayout(infos_widget)

        inclusion_group = QGroupBox('Included in dataset')
        inclusion_layout = QVBoxLayout(inclusion_group)
        inclusion_form = QFormLayout()
        self.category_count = QLabel('0')
        self.training_image_count = QLabel('0')
        self.test_image_count = QLabel('0')
        self.total_image_count = QLabel('0')
        inclusion_form.add_row('Category count:', self.category_count)
        inclusion_form.add_row('Training image count:', self.training_image_count)
        inclusion_form.add_row('Test image count:', self.test_image_count)
        inclusion_form.add_row('Total image count:', self.total_image_count)
        inclusion_layout.add_layout(inclusion_form)
        infos_layout.add_widget(inclusion_group)

        transformation_group = QGroupBox('Transformation')
        transformation_layout = QVBoxLayout(transformation_group)
        transformation_form = QFormLayout()
        self.translated = QLabel('False')
        self.rotated = QLabel('False')
        self.scaled = QLabel('False')
        transformation_form.add_row('Translated:', self.translated)
        transformation_form.add_row('Rotated:', self.rotated)
        transformation_form.add_row('Scaled:', self.scaled)
        transformation_layout.add_layout(transformation_form)
        infos_layout.add_widget(transformation_group)

        general_layout.add_widget(infos_widget)

    def update(self, klustr_dao):
        for dataset in klustr_dao.available_datasets:
            self.dataset_combo_box.add_item(dataset[1], dataset)

    @Slot()
    def __selection_dataset(self, choix):
        chosen_dataset = self.dataset_combo_box.item_data(choix)
        self.category_count.text = (str(chosen_dataset[5]))
        self.training_image_count.text = str(chosen_dataset[6])
        self.test_image_count.text = str(chosen_dataset[7])
        self.total_image_count.text = str(chosen_dataset[8])
        self.translated.text = str(chosen_dataset[2])
        self.rotated.text = str(chosen_dataset[3])
        self.scaled.text = str(chosen_dataset[4])
        self.dataset_selected.emit(chosen_dataset[1])


class KlustRSingleAnalyzeModel(QWidget):
    classify = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.general_widget = QGroupBox("Single test")
        general_layout = QVBoxLayout(self.general_widget)

        self.single_test_combo_box = QComboBox()
        self.single_test_combo_box.add_items(["item1", "item2", "item3"])
        self.single_test_combo_box.currentIndexChanged.connect(self.__selection_img)
        general_layout.add_widget(self.single_test_combo_box)

        self.image_container = QLabel()
        self.image_container.style_sheet = 'QLabel { background-color : #313D4A; padding : 10px 10px 10px 10px; }'
        self.image_container.alignment = Qt.AlignCenter
        general_layout.add_widget(self.image_container)

        bouton_classify = QPushButton("Classify")
        bouton_classify.clicked.connect(self.__classify)
        general_layout.add_widget(bouton_classify)
        self.classify_result = QLabel("Not Classified")
        self.classify_result.alignment = Qt.AlignCenter
        general_layout.add_widget(self.classify_result)

    def _update(self, dataset):
        sb = QtCore.QSignalBlocker(self)
        self.single_test_combo_box.clear()
        sb.unblock()
        for image_label in dataset:
            self.single_test_combo_box.add_item(image_label[3], image_label)

    def update_from_dataset(self, dataset):
        self._update(dataset)

    def update_text(self, answer):
        self.classify_result.text = answer

    @Slot()
    def __selection_img(self, choix):
        if choix != -1:
            self.name_image = self.single_test_combo_box.item_text(choix)
            image = self.single_test_combo_box.item_data(choix)[6]
            image = qimage_argb32_from_png_decoding(image)
            self.chosen_image = image
            image_item = QPixmap.from_image(image)
            self.image_container.pixmap = image_item

    @Slot()
    def __classify(self):
        if self.chosen_image is None:
            self.classify_result.text = "Not Classified"
        else:
            image = ndarray_from_qimage_argb32(self.chosen_image)
            self.classify.emit(image)


