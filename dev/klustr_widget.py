
# KlustRDataSourceViewWidget
# 
# Exemple d'utilisation :
#  credential = PostgreSQLCredential(host='jcd-prof-cvm-69b5.aivencloud.com', port=11702, database='data_kit', user='klustr_reader', password='h$2%1?')
#  klustr_dao = PostgreSQLKlustRDAO(credential)
#  source_data_widget = KlustRDataSourceViewWidget(klustr_dao)
#
# Après avoir cliqué sur le widget d'image à droite, copie dans le 'clipboard' :
#   - enter -> copie l'image
#   - space -> copie le text
# 
# 
# Ce widget reste un exemple pédagogique relativement simple malgré qu'il soit long.
# 
# Un mini modèle est mis en place pour chaque structure afin de présenter le 
# concept Modèle/Vue/Délégué de Qt (même si aucun délégué n'est utilisé). 
# L'information présentée est en lecture seule.
#
# L'approche actuelle reste simple car on actualise constamment chacune des 3 vues 
# liés aux 3 modèles. Cette approche n'optimise en rien les requêtes de données.
# 
# Une approche mieux adaptée utiliserait :
#   - un seul modèle plus étayé
#   - un objet proxy (voir QAbstractProxyModel) afin d'appliquer : 
#       - sous-modèle
#       - filtre
#       - trie
# 
# Cette dernière approche serait plus complexe et longue à mettre en place mais 
# beaucoup plus efficace et, surtout, plus modulaire.

from re import S
import sys

import numpy as np ###################################################################################
from knn import KNN
from shapeanalyzer import ShapeAnalyzer
from db_credential import PostgreSQLCredential
from klustr_dao import PostgreSQLKlustRDAO
from klustr_utils import qimage_argb32_from_png_decoding

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QSize,QTimer
from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtWidgets import (QApplication, QWidget, QListView, QTreeView,
                               QGroupBox, QLabel, QCheckBox, QPlainTextEdit,
                               QGridLayout, QHBoxLayout, QVBoxLayout, QSplitter, QSizePolicy,
                               QMessageBox, QTabWidget, QMainWindow, QPushButton, QComboBox, QScrollBar, QFormLayout)
from PySide6.QtGui import  (QImage, QPixmap, QIcon, QPainter, QFont, QPen, QBrush, QColor, 
                            QStandardItemModel, QStandardItem,
                            QClipboard)

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from __feature__ import snake_case, true_property 



#     ___  _       _ _                          __                      _      _     
#    / _ \| |_    (_) |_ ___ _ __ ___  ___     / /  _ __ ___   ___   __| | ___| |___ 
#   | | | | __|   | | __/ _ \ '_ ` _ \/ __|   / /  | '_ ` _ \ / _ \ / _` |/ _ \ / __|
#   | |_| | |_    | | ||  __/ | | | | \__ \  / /   | | | | | | (_) | (_| |  __/ \__ \
#    \__\_\\__|   |_|\__\___|_| |_| |_|___/ /_/    |_| |_| |_|\___/ \__,_|\___|_|___/
#                                                                                    

class KlustRDatasetItem(QStandardItem):
    def __init__(self, id, name, translated='', rotated='', scaled='', label_count='', training_image_count='', test_image_count=''):
        super().__init__(name)

        self._id = id
        self._name = name

        if id == -1:
            pass
        else:
            for name, count in [['Training', training_image_count], ['Test', test_image_count]]:
                self.append_row([   
                        QStandardItem(name), 
                        QStandardItem(translated), 
                        QStandardItem(rotated), 
                        QStandardItem(scaled), 
                        QStandardItem(label_count), 
                        QStandardItem(count)])

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name


class KlustRDatasetModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

        self.connectNotify = self.connect_notify  # patch ?!

    def update(self, klustr_dao):
        self.clear()
        self.set_horizontal_header_labels(['Name', 'Translation', 'Rotation', 'Scaling', 'Label count', 'Image count'])

        total_label_image_count = klustr_dao.total_label_image_count
        label_count = total_label_image_count[0][0]
        image_count = total_label_image_count[0][1]
        self.append_row([
                    KlustRDatasetItem(-1, 'All available images'),
                    QStandardItem('-'), 
                    QStandardItem('-'), 
                    QStandardItem('-'), 
                    QStandardItem(f'{label_count}'),
                    QStandardItem(f'{image_count}')])

        for dataset in klustr_dao.available_datasets:
            translated = 'true' if dataset[2] else 'false'
            rotated = 'true' if dataset[3] else 'false'
            scaled = 'true' if dataset[4] else 'false'
            label_count = f'{dataset[5]}'
            training_image_count = f'{dataset[6]}'
            test_image_count = f'{dataset[7]}'
            image_count = f'{dataset[8]}'
            self.append_row([
                    KlustRDatasetItem(dataset[0], dataset[1], translated, rotated, scaled, label_count, training_image_count, test_image_count),
                    QStandardItem(translated), 
                    QStandardItem(rotated), 
                    QStandardItem(scaled), 
                    QStandardItem(label_count),
                    QStandardItem(image_count)]
                    )

    # def flags(self, index):
    #     item = index.model().item_from_index(index)
    #     if isinstance(item, KlustRDatasetItem) and id != -1:
    #         return super().flags(index) & ~Qt.ItemIsSelectable
    #     else:
    #         return super().flags(index)


class KlustRLabelItem(QStandardItem):
    def __init__(self, id, name, thumbnail):
        self._id = id
        self._name = name

        img = qimage_argb32_from_png_decoding(thumbnail)
        self._thumbnail_icon = QIcon() if img.is_null() else QIcon(QPixmap.from_image(img))

        super().__init__(self._thumbnail_icon, self._name)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

class KlustRLabelModel(QStandardItemModel):
    def __init__(self):
        super().__init__()

        self.connectNotify = self.connect_notify  # patch ?!

    def _update(self, dataset):
        sb = QtCore.QSignalBlocker(self)
        self.clear()
        sb.unblock()
        for image_label in dataset:
            self.append_row(KlustRLabelItem(image_label[0], image_label[1], image_label[2]))

    def update_for_all_images(self, klustr_dao):
        self._update(klustr_dao.available_labels)

    def update_from_dataset(self, dataset_name, klustr_dao):
        self._update(klustr_dao.labels_from_dataset(dataset_name))

class KlustRImageItem(QStandardItem):

    def __init__(self, label_id, image_id, name, width, height, image, thumbnail, transformation):
        self._label_id = label_id
        self._image_id = image_id
        self._name = name
        self._width = width
        self._height = height
        self._translated = transformation[0] == '1'
        self._rotated = transformation[1] == '1'
        self._scaled = transformation[2] == '1'

        img = qimage_argb32_from_png_decoding(thumbnail)
        self._thumbnail_icon = QIcon() if img.is_null() else QIcon(QPixmap.from_image(img))

        img = qimage_argb32_from_png_decoding(image)
        self._image = QIcon() if img.is_null() else img

        super().__init__(self._thumbnail_icon, self._name)

    @property
    def label_id(self):
        return self._label_id

    @property
    def image_id(self):
        return self._image_id

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def image(self):
        return self._image

    @property
    def translated(self):
        return self._translated

    @property
    def rotated(self):
        return self._rotated

    @property
    def scaled(self):
        return self._scaled


class KlustRImageModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self._label_id = None

        self.connectNotify = self.connect_notify # patch ?!

    def _update(self, images):
        sb = QtCore.QSignalBlocker(self)
        self.clear()
        sb.unblock()
        for image_info in images:
            # label_id, image_id, name, width, height, image, thumbnail, transformation
            new_item = KlustRImageItem(image_info[0], image_info[2], image_info[3], image_info[4], image_info[5], image_info[6], image_info[7], image_info[11])
            self.append_row(new_item)

    def update_for_all_images(self, klustr_dao, label_id, translated, rotated, scaled, exclusive):
        klustr_dao.set_transformation_filters(translated, rotated, scaled, exclusive)
        self._update(klustr_dao.image_from_label(label_id))

    def update_from_dataset(self, klustr_dao, dataset_name, label_id, training_image):
        self._update(klustr_dao.image_from_dataset_label(dataset_name, label_id, training_image))


class ColoredWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._brush = QBrush(Qt.white)
        self._pen = QPen(Qt.black, 1.)

    @property
    def brush(self):
        return self._brush

    @brush.setter
    def brush(self, value):
        self._brush = value
        self.update()

    @property
    def pen(self):
        return self._pen

    @pen.setter
    def pen(self, value):
        self._pen = value
        self.update()

    def paint_event(self, event):
        painter = QPainter(self)
        painter.set_brush(self.brush)
        painter.set_pen(self.pen)
        painter.draw_rect(self.rect)



#    _  ___           _   ____  ___                            ___        __    __        ___     _            _   
#   | |/ / |_   _ ___| |_|  _ \|_ _|_ __ ___   __ _  __ _  ___|_ _|_ __  / _| __\ \      / (_) __| | __ _  ___| |_ 
#   | ' /| | | | / __| __| |_) || || '_ ` _ \ / _` |/ _` |/ _ \| || '_ \| |_ / _ \ \ /\ / /| |/ _` |/ _` |/ _ \ __|
#   | . \| | |_| \__ \ |_|  _ < | || | | | | | (_| | (_| |  __/| || | | |  _| (_) \ V  V / | | (_| | (_| |  __/ |_ 
#   |_|\_\_|\__,_|___/\__|_| \_\___|_| |_| |_|\__,_|\__, |\___|___|_| |_|_|  \___/ \_/\_/  |_|\__,_|\__, |\___|\__|
#                                                   |___/                                           |___/          

class KlustRImageInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.focus_policy = Qt.StrongFocus

        self.view_label = QLabel()
        self.view_label.style_sheet = 'QLabel { background-color : #313D4A; padding : 10px 10px 10px 10px; }' # 354A64
        self.view_label.alignment = Qt.AlignCenter

        self.red_color = QColor(205, 65, 65)
        self.green_color = QColor(65, 205, 82)

        transf_widget_size = QSize(28, 12)
        self.translated_widget = ColoredWidget()
        self.rotated_widget = ColoredWidget()
        self.scaled_widget = ColoredWidget()
        self.translated_widget.set_fixed_size(transf_widget_size)
        self.rotated_widget.set_fixed_size(transf_widget_size)
        self.scaled_widget.set_fixed_size(transf_widget_size)
        self.translated_widget.tool_tip = 'translation was applied'
        self.rotated_widget.tool_tip = 'rotation was applied'
        self.scaled_widget.tool_tip = 'scaling was applied'
        self.translated_widget.brush = QBrush(self.green_color)
        self.rotated_widget.brush = QBrush(self.red_color)
        self.scaled_widget.brush = QBrush(self.green_color)
        transformation_layout = QHBoxLayout()
        transformation_layout.add_stretch()
        transformation_layout.add_widget(self.translated_widget)
        transformation_layout.add_widget(self.rotated_widget)
        transformation_layout.add_widget(self.scaled_widget)
        transformation_layout.add_stretch()

        self.info = QPlainTextEdit()
        font = self.info.font
        font.set_family('Courier New') # monospace
        self.info.font = font
        self.info.read_only = True
        self.info.line_wrap_mode = QPlainTextEdit.NoWrap

        layout = QVBoxLayout(self)
        layout.add_widget(QLabel('Image information'))
        layout.add_widget(self.view_label)
        layout.add_layout(transformation_layout)
        layout.add_widget(self.info)
        layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)

    def key_press_event(self, event):
        clipboard = QClipboard()
        if event.key() == Qt.Key_Return:
            clipboard.set_pixmap(self.view_label.pixmap)
        elif event.key() == Qt.Key_Space:
            clipboard.set_text(self.info.plain_text)

    def update_info(self, image_item):
        def str_info(t, info, length=60):
            title = t + ' ' + '-' * (length - len(t) - 1)
            info = '\n'.join([f' - {k:<15} : {str(value)}' for k, value in info.items()])
            return title + '\n' + info + '\n'

        data_base_info = {
                'Image name': image_item.name,
                'Width' : image_item.width,
                'Height' : image_item.height,
                'Translated' : image_item.translated,
                'Rotated' : image_item.rotated,
                'Scaled' : image_item.scaled
            }
        image_info = {
                'Width' : image_item.image.width(),
                'Height' : image_item.image.height(),
                'Format' : image_item.image.format(),
                'Depth' : image_item.image.depth(),
                'Bytes per line' : image_item.image.bytes_per_line(),
                'Cache key' : hex(image_item.image.cache_key())
            }

        metadata_info = {k:image_item.image.text(k) for k in image_item.image.text_keys()}

        self.info.plain_text = str_info('From database', data_base_info) \
                                + str_info('From image', image_info) \
                                + str_info('From meta data', metadata_info)
        self.view_label.pixmap = QPixmap.from_image(image_item.image)

        self.translated_widget.brush = QBrush(self.green_color) if image_item.translated else QBrush(self.red_color)
        self.rotated_widget.brush = QBrush(self.green_color) if image_item.rotated else QBrush(self.red_color)
        self.scaled_widget.brush = QBrush(self.green_color) if image_item.scaled else QBrush(self.red_color)



#    _  ___           _   ____  ____        _        ____                         __     ___              __        ___     _            _   
#   | |/ / |_   _ ___| |_|  _ \|  _ \  __ _| |_ __ _/ ___|  ___  _   _ _ __ ___ __\ \   / (_) _____      _\ \      / (_) __| | __ _  ___| |_ 
#   | ' /| | | | / __| __| |_) | | | |/ _` | __/ _` \___ \ / _ \| | | | '__/ __/ _ \ \ / /| |/ _ \ \ /\ / /\ \ /\ / /| |/ _` |/ _` |/ _ \ __|
#   | . \| | |_| \__ \ |_|  _ <| |_| | (_| | || (_| |___) | (_) | |_| | | | (_|  __/\ V / | |  __/\ V  V /  \ V  V / | | (_| | (_| |  __/ |_ 
#   |_|\_\_|\__,_|___/\__|_| \_\____/ \__,_|\__\__,_|____/ \___/ \__,_|_|  \___\___| \_/  |_|\___| \_/\_/    \_/\_/  |_|\__,_|\__, |\___|\__|
#                                                                                                                             |___/          

class KlustRDataSourceViewWidget(QWidget):

    def __init__(self, klustr_dao, parent=None):
        
        super().__init__(parent)

        self.klustr_dao = klustr_dao
        if self.klustr_dao.is_available:
            self._setup_models()
            self._setup_gui()

            self._update_dataset()
            # self.label_model.update_for_all_images(self.pg_cursor)
            # self.image_label_list_view.set_current_index(self.label_model.index(0, 0))
            # self.image_list_view.set_current_index(self.image_model.index(0, 0))
        else:
            self._setup_invalid_gui()

    def _setup_models(self):
        self.dataset_model = KlustRDatasetModel()
        self.label_model = KlustRLabelModel()
        self.image_model = KlustRImageModel()

    def _setup_invalid_gui(self):
        not_available = QLabel('Data access unavailable')
        not_available.alignment = Qt.AlignCenter
        not_available.enabled = False
        layout = QGridLayout(self)
        layout.add_widget(not_available)
        QMessageBox.warning(self, 'Data access unavailable', 'Data access unavailable.')

    def _setup_gui(self):
        # setup 3 widget model view : QTreeView - QListView - QListView
        self.dataset_tree_view, self.dataset_count_label, dataset_widget = self._setup_view_widget(QTreeView(), 'Dataset', self.dataset_model, self.select_dataset, -1)
        self.image_label_list_view, self.image_label_count_label, image_label_widget = self._setup_view_widget(QListView(), 'Label', self.label_model, self.select_label)
        self.image_list_view, self.image_count_label, image_widget = self._setup_view_widget(QListView(), 'Image', self.image_model, self.select_image)

        # configure QTreeView
        self.dataset_tree_view.header_hidden = False
        self.dataset_tree_view.horizontal_scroll_mode = QTreeView.ScrollPerPixel
        self.dataset_tree_view.horizontal_scroll_bar_policy = Qt.ScrollBarAsNeeded
        self.dataset_tree_view.selection_mode = QTreeView.SingleSelection
        self.dataset_tree_view.edit_triggers = QtWidgets.QAbstractItemView.NoEditTriggers

        # setup image view widget
        self.image_info_widget = KlustRImageInfoWidget()

        # layouting main widget
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        view_layout.add_widget(dataset_widget)
        view_layout.add_widget(image_label_widget)
        view_layout.add_widget(image_widget)

        view_splitter = QSplitter()
        view_splitter.orientation = Qt.Horizontal
        view_splitter.add_widget(view_widget)
        view_splitter.add_widget(self.image_info_widget)
        view_splitter.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        # setup transformation filter widget
        self.filter_box = QGroupBox('Filter')
        self.filter_box.enabled = False

        self.translation_checkbox = QCheckBox('Translation')
        self.rotation_checkbox = QCheckBox('Rotation')
        self.scaling_checkbox = QCheckBox('Scaling')
        self.exclusive_checkbox = QCheckBox('Exclusive')

        self.translation_checkbox.checked = True
        self.rotation_checkbox.checked = True
        self.scaling_checkbox.checked = True
        self.exclusive_checkbox.checked = False

        # setup transformation filter widget
        filter_layout = QHBoxLayout(self.filter_box)
        filter_layout.add_widget(self.translation_checkbox)
        filter_layout.add_widget(self.rotation_checkbox)
        filter_layout.add_widget(self.scaling_checkbox)
        filter_layout.add_widget(self.exclusive_checkbox)
        filter_layout.add_stretch()

        # connect transformation filter widget
        self.translation_checkbox.stateChanged.connect(self._update_models)
        self.rotation_checkbox.stateChanged.connect(self._update_models)
        self.scaling_checkbox.stateChanged.connect(self._update_models)
        self.exclusive_checkbox.stateChanged.connect(self._update_models)

        # main layouting
        layout = QVBoxLayout(self)
        layout.add_widget(view_splitter)
        layout.add_widget(self.filter_box)

    def _setup_view_widget(self, view_widget, title, model, update_slot, width=250):
        view_widget.set_model(model)
        view_widget.selection_behavior = QtWidgets.QAbstractItemView.SelectRows
        view_widget.selection_model().selectionChanged.connect(update_slot)
        view_widget.edit_triggers = QtWidgets.QAbstractItemView.NoEditTriggers
        count_widget = QLabel()
        count_widget.alignment = Qt.AlignRight
        font = count_widget.font
        font.set_italic(True)
        count_widget.font = font
        widget = QWidget()
        if width > 0:
            widget.set_fixed_width(width)
        layout = QVBoxLayout(widget)
        layout.add_widget(QLabel(title))
        layout.add_widget(view_widget)
        layout.add_widget(count_widget)
        layout.contents_margins = QtCore.QMargins(0, 0, 0, 0)
        return view_widget, count_widget, widget

    @Slot()
    def _update_dataset(self):
        self.dataset_model.update(self.klustr_dao)
        self.dataset_count_label.text  = f'''{self.dataset_model.row_count() - 1} datasets'''
        self.dataset_tree_view.set_current_index(self.dataset_model.index(0, 0))

    @Slot()
    def _update_models(self):
        self.image_model.update_for_all_images(self.label_model.item(0, 0).id,
                                self.pg_cursor,
                                self.translation_checkbox.checked,
                                self.rotation_checkbox.checked,
                                self.scaling_checkbox.checked,
                                self.exclusive_checkbox.checked)
        self.image_label_count_label.text  = f'''{self.label_model.row_count()} labels'''
        self.image_list_view.set_current_index(self.image_model.index(0, 0))

    def show_event(self, event):
        pass

    @Slot()
    def select_dataset(self, selected, deselected):
        if selected:
            index = selected.indexes()[0]
            item = index.model().item_from_index(index)
            if isinstance(item, KlustRDatasetItem):
                if item.id == -1:
                    self.label_model.update_for_all_images(self.klustr_dao)
                else:
                    self.dataset_tree_view.set_current_index(self.dataset_model.index(0, 0, index))
            else:
                self.label_model.update_from_dataset(item.parent().name, self.klustr_dao)
            self.image_label_list_view.set_current_index(self.label_model.index(0, 0))
            self.image_label_count_label.text  = f'''{self.label_model.row_count()} labels'''


    @Slot()
    def select_label(self, selected, deselected):
        if selected:
            dataset_index = self.dataset_tree_view.selection_model().selected_indexes[0]
            dataset_item = self.dataset_model.item_from_index(dataset_index)
            if isinstance(dataset_item, KlustRDatasetItem):
                self.image_model.update_for_all_images(
                                        self.klustr_dao, 
                                        self.label_model.item_from_index(selected.indexes()[0]).id, 
                                        self.translation_checkbox.checked,
                                        self.rotation_checkbox.checked,
                                        self.scaling_checkbox.checked,
                                        self.exclusive_checkbox.checked)
            else:
                training = dataset_index.row() == 0
                dataset_index = self.dataset_tree_view.selection_model().selected_indexes[0].parent()
                dataset_item = self.dataset_model.item_from_index(dataset_index)
                label_index = self.image_label_list_view.selection_model().selected_indexes[0]
                label_item = self.label_model.item_from_index(label_index)
                self.image_model.update_from_dataset(self.klustr_dao, dataset_item.name, label_item.id, training)
            self.image_list_view.set_current_index(self.image_model.index(0, 0))
            self.image_count_label.text  = f'''{self.image_model.row_count()} images'''

    @Slot()
    def select_image(self, selected, deselected):
        if selected:
            self.image_info_widget.update_info(self.image_model.item_from_index(selected.indexes()[0]))

#     ___  _       _ _                          __                      _      _     
#    / _ \| |_    (_) |_ ___ _ __ ___  ___     / /  _ __ ___   ___   __| | ___| |___ 
#   | | | | __|   | | __/ _ \ '_ ` _ \/ __|   / /  | '_ ` _ \ / _ \ / _` |/ _ \ / __|
#   | |_| | |_    | | ||  __/ | | | | \__ \  / /   | | | | | | (_) | (_| |  __/ \__ \
#    \__\_\\__|   |_|\__\___|_| |_| |_|___/ /_/    |_| |_| |_|\___/ \__,_|\___|_|___/
#      

class KlustRDatasetAnalyzeModel(QWidget):
    dataset_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.__general_widget = QGroupBox("Dataset")
        general_layout = QVBoxLayout(self.__general_widget)

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

    @property
    def general_widget(self):
        return self.__general_widget

    @Slot()
    def __selection_dataset(self,choix):
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
    classify = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.__general_widget = QGroupBox("Single test")
        general_layout = QVBoxLayout(self.__general_widget)
        
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
            self.single_test_combo_box.add_item(image_label[1], image_label)
    
    def update_from_dataset(self, dataset):
        self._update(dataset)

    def update_text(self, answer):
        self.classify_result.text = answer

    @property
    def general_widget(self):
        return self.__general_widget

    @Slot()
    def __selection_img(self, choix):
        if choix != -1: 
            self.name_image = self.single_test_combo_box.item_text(choix)
            image = self.single_test_combo_box.item_data(choix)[2]
            image = qimage_argb32_from_png_decoding(image)
            self.chosen_image = image
            image_item = QPixmap.from_image(image)
            self.image_container.pixmap = image_item

    @Slot()
    def __classify(self):
        if self.chosen_image is None:
            self.classify_result.text = "Not Classified"
        else:
            self.classify.emit(self.chosen_image)


class KlustRKnnParamsWidget(QWidget):
    value_changed = Signal(str)
    def __init__(self):
        super().__init__()
        self.__knn = "knn"
        self.__dist = "dist"
        self.__general_widget = QGroupBox("Knn parameters")
        general_layout = QVBoxLayout(self.__general_widget)

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

    @property
    def knn(self):
        return self.__knn

    @property
    def dist(self):
        return self.__dist

    @property
    def general_widget(self):
        return self.__general_widget

    @Slot()
    def __update_distance(self):
        self.__dist_label.set_text("Max dist = "+str(self.__dist_scrollbar.value/10))
        
    @Slot()
    def __update_knn_param(self):
        #######ici je dois set self.__k_scrollbar.set_range(1,max_range) avec squareroot(image count)/2 comment get image count?
         self.__k_label.set_text("k = "+str(self.__k_scrollbar.value))

class KlustR3DModel(QWidget):
    def __init__(self, knn, title, xLabel, yLabel, zLabel):
        super().__init__()
        self.__general_widget = QLabel()
        self.__knn = knn
        
        self._title = title
        self._x_label = xLabel
        self._y_label = yLabel
        self._z_label = zLabel
        self._markers = ('o', '.', 'v', '2', '8', 's', 'X', 'D', '*', 'H')

        self._elevation = 30
        self._azimuth = 45
        self._azimuth_inc = 2.5
        
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._rotate)
        self._timer.start(1000)

    @property
    def general_widget(self):
        return self.__general_widget

    @Slot()
    def _rotate(self):
        self.update_graphic()
        self._azimuth += self._azimuth_inc
   
    def update_graphic(self):
        width = 500
        height = 500
        dpi = 100
        figure = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111, projection='3d')
        ax.set_proj_type('persp')

        #for shapes in dataset:
        #   color = rgb(random(0,1), random(0,1), random(0,1))
        #   marker = self.markers[random(0, (len(self.markers)-1)]
        #   ax.scatter(self.__knn.training_data[:,0], self.__knn.training_data[:,1], self.__knn.training_data[:,2], marker='o', color='r')

        if self.__knn.point_classifie is not None:
            ax.scatter(self.__knn.point_classifie.x, self.__knn.point_classifie.y, self.__knn.point_classifie.z, marker='p', color='') ###########################################

        ax.set_title(self._title)
        ax.set_xlabel(self._x_label)
        ax.set_ylabel(self._y_label)
        ax.set_zlabel(self._z_label)

        ax.view_init(self._elevation, self._azimuth)

        canvas.draw()
        w, h = canvas.get_width_height()
        img = QImage(canvas.buffer_rgba(), w, h, w * 4, QImage.Format_ARGB32)

        self.__general_widget.set_pixmap(QtGui.QPixmap.from_image(img))


#  _  __  _                 _     ____    ____            _                _                      _                       __     __  _                    __        __  _       _                  _   
# | |/ / | |  _   _   ___  | |_  |  _ \  |  _ \    __ _  | |_    __ _     / \     _ __     __ _  | |  _   _   ____   ___  \ \   / / (_)   ___  __      __ \ \      / / (_)   __| |   __ _    ___  | |_ 
# | ' /  | | | | | | / __| | __| | |_) | | | | |  / _` | | __|  / _` |   / _ \   | '_ \   / _` | | | | | | | |_  /  / _ \  \ \ / /  | |  / _ \ \ \ /\ / /  \ \ /\ / /  | |  / _` |  / _` |  / _ \ | __|
# | . \  | | | |_| | \__ \ | |_  |  _ <  | |_| | | (_| | | |_  | (_| |  / ___ \  | | | | | (_| | | | | |_| |  / /  |  __/   \ V /   | | |  __/  \ V  V /    \ V  V /   | | | (_| | | (_| | |  __/ | |_ 
# |_|\_\ |_|  \__,_| |___/  \__| |_| \_\ |____/   \__,_|  \__|  \__,_| /_/   \_\ |_| |_|  \__,_| |_|  \__, | /___|  \___|    \_/    |_|  \___|   \_/\_/      \_/\_/    |_|  \__,_|  \__, |  \___|  \__|
#                                                                                                     |___/                                                                         |___/              

class KlustRDataAnalyzeViewWidget(QWidget):
    def __init__(self, controleur, klustr_dao, parent=None):
        super().__init__(parent)
        self.__klustr_dao = klustr_dao
        self.__controleur = controleur
        if self.__klustr_dao.is_available:
            self._setup_gui()
            self._setup_models()
        else:
            self._setup_invalid_gui()

    def _setup_models(self):
        self.__dataset_widget.update(self.__klustr_dao)

    def _setup_invalid_gui(self):
        not_available = QLabel('Data access unavailable')
        not_available.alignment = Qt.AlignCenter
        not_available.enabled = False
        layout = QGridLayout(self)
        layout.add_widget(not_available)
        QMessageBox.warning(self, 'Data access unavailable', 'Data access unavailable.')

    def _setup_gui(self):
        #--------- Dataset ---------#
        self.__dataset_widget = KlustRDatasetAnalyzeModel()
        self.__dataset_widget.dataset_selected.connect(self._update_from_selection)

        #--------- Knn params ---------#
        self.__knn_parameters_widget = KlustRKnnParamsWidget()

        #--------- Single_test ---------#
        self.__single_test_widget = KlustRSingleAnalyzeModel()
        self.__single_test_widget.classify.connect(self._classify)

        #--------- About Button ---------#
        bouton_about = QPushButton("About")
        bouton_about.clicked.connect(self.__show_dialog)

        #--------- Data General layout ---------#
        view_data_widget = QWidget()
        view_data_layout = QVBoxLayout(view_data_widget)
        view_data_layout.add_widget(self.__dataset_widget.general_widget)
        view_data_layout.add_widget(self.__knn_parameters_widget.general_widget)
        view_data_layout.add_widget(self.__single_test_widget.general_widget)
        view_data_layout.add_widget(bouton_about)

        #--------- 3D General Layout ---------#
        view_graphic_widget = QWidget()
        view_graphic_layout = QVBoxLayout(view_graphic_widget)
        self.__graphic_widget = KlustR3DModel(self.__controleur,'KLUSTR KNN CLASSIFICATION', 'X Label', 'Y Label', 'Z Label')
        view_graphic_layout.alignment = Qt.AlignHCenter #######################################################################
        view_graphic_layout.add_widget(self.__graphic_widget.general_widget)

        #--------- Main Layout ---------#
        layout = QHBoxLayout(self)
        layout.add_widget(view_data_widget)
        layout.add_widget(view_graphic_widget)        

    @Slot()
    def __show_dialog(self):
        msgBox = QMessageBox()
        with open("readme.txt") as readme:
            contents = readme.read()
            msgBox.text=(contents)
        msgBox.exec()

    @Slot()
    def _update_from_selection(self, chosen_dataset):
        dataset = self.__klustr_dao.labels_from_dataset(chosen_dataset)
        self.__single_test_widget.update_from_dataset(dataset)
        self.__controleur.new_dataset(dataset) ###################################################################################### dataset au complet

    @Slot()
    def _classify(self, chosen_image):
        chosen_image = self.__single_test_widget.name_image ######################################################################
        knn = self.__knn_parameters_widget.knn
        dist = self.__knn_parameters_widget.dist
        answer = self.__controleur.classify(chosen_image, knn, dist) ####################################################################
        
        self.__single_test_widget.update_text(answer)


#  __  __      _      ___   _   _ 
# |  \/  |    / \    |_ _| | \ | |
# | |\/| |   / _ \    | |  |  \| |
# | |  | |  / ___ \   | |  | |\  |
# |_|  |_| /_/   \_\ |___| |_| \_|
#                                 

class KlustrMain(QWidget):  
    def __init__(self, controleur, klustr_dao, parent=None):
        super().__init__(parent)
        self.tabs = QTabWidget()
        self.tab1 = KlustRDataSourceViewWidget(klustr_dao)
        self.tab2 = KlustRDataAnalyzeViewWidget(controleur, klustr_dao)
        self.tabs.add_tab(self.tab1,"Tab 1")
        self.tabs.add_tab(self.tab2,"Tab 2")

class Main():
    def __init__(self):
        credential = PostgreSQLCredential(password='AAAaaa111')
        klustr_dao = PostgreSQLKlustRDAO(credential)
        self.source_data_widget = KlustrMain(self, klustr_dao)
        self.source_data_widget.window_title = 'Kluster App'
        self.knn = KNN(3,3) ############################### 
        self.shape_analyzer = ShapeAnalyzer(None,None)
        self.point_classifie = None

    def new_dataset(self, dataset):
        pass

    def classify(self, chosen_image, k_constant, dist):
        self.knn.k_constant(k_constant) # setter du k_constant (la distribution)
        unclassified_point = self.shape_analyzer.analyze(chosen_image)
        classe = self.knn.classify(unclassified_point)
        return [unclassified_point, classe]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.source_data_widget.tabs.show()
    sys.exit(app.exec_())    