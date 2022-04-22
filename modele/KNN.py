import numpy as np
import ShapeAnalzyer as sa

class KNN:
    def __init__(self, dimensions, k_constant):
        self.__dataset = np.empty((0, dimensions), dtype=np.float32)
        self.__dimensions = dimensions
        self.__k_constant = k_constant

    @property
    def dataset(self):
        return self.__dataset

    @dataset.setter
    def dataset(self, data):
        self.__dataset = data

    @property
    def k_constant(self):
        return self.__k_constant

    @k_constant.setter
    def k_constant(self, value):
        self.__k_constant = value

    # point = un ensemble de métriques
    def add_training_point(self, point, tag):
        if point.shape[1] is not self.dataset.shape[1]:
            raise ValueError('ayoye')
        self.__dataset = np.append(self.__dataset, point, axis=0)

    def classify(self, unclassified_point):
        np.sum((unclassified_point - self.dataset) ** 2, axis=1) ** 0.5
        # cette fonction return un tag

    def k_neighbours(self, unclassified_point):
        pass

    # pop les tags des voisins trouvés à mettre dans une nouvelle liste
    # l'occurence la plus commune devient le tag du unclassified_point

    def new_dataset(self, data):
        pass

        # self.dataset.clear()