from re import S
import numpy as np
import shapeanalyzer


class KNN:
    def __init__(self, dimensions, k_constant):
        self.__dimensions = dimensions
        self.__dataset = np.empty((0, self.__dimensions + 1), dtype=np.float32)
        self.__k_constant = k_constant
        self.__k_tags = np.empty(0, dtype=np.str_)

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

    @property
    def k_tags(self):
        return self.__k_tags

    def add_tag(self, tag):
        self.__k_tags = np.append(self.__k_tags, tag)
        # self.__k_tags.append(tag)

    def classify(self, unclassified_point):
        neighbours = self.get_k_neighbours(unclassified_point)
        tags = self.get_k_neighbours_tags(neighbours)
        tag = self.get_most_common_tag(tags)
        return tag

    def clear_dataset(self):
        self.__dataset = np.empty((0, self.__dimensions + 1), dtype=np.float32)

    def get_most_common_tag(self, tags):
        # https://stackoverflow.com/questions/19909167/how-to-find-most-frequent-string-element-in-numpy-ndarray
        tags_unique, pos = np.unique(tags.T, return_inverse=True)
        counts = np.bincount(pos)
        position = counts.argmax() 
        return tags_unique[position]

    # Retourne le tableau des k voisins
    def get_k_neighbours(self, unclassified_point):
        distances = self.distances_from_point(unclassified_point)
        print(distances[distances[:,0].argsort()][:self.__k_constant])
        k_neighbours_distances_and_tags = distances[distances[:,0].argsort()][-self.__k_constant:] # A tester
        return k_neighbours_distances_and_tags

    # Retourne le tableau des tags des k voisins
    def get_k_neighbours_tags(self, k_neighbours):
        tags_index = k_neighbours[:, -1].astype(int)
        k_neighbours_tags = self.k_tags[tags_index]
        return k_neighbours_tags

    def distances_from_point(self, unclassified_point):
        distances_only_array = np.sum((unclassified_point - self.dataset[:, :-1]) ** 2, axis=1) ** 0.5
        tag_index_array = self.dataset[:, -1] 
        distances_and_index_array = np.vstack((distances_only_array, tag_index_array)).T
        return distances_and_index_array

    # À ajouter au contrôleur
    def new_dataset(self, data):
        self.clear_dataset()
        for element in data:
            metrics, tag = element
            self.add_training_point(metrics, tag)

    def add_training_point(self, point, tag):
        # on transforme point en nparray si pas le cas
        if tag not in self.__k_tags:
            self.add_tag(tag)
        index_tag = np.where(self.__k_tags == tag)
        point = np.append(point, index_tag[0], axis=0)
        # if point.shape[0] is not self.__dataset.shape[1]:
        #     raise ValueError('Méchant problème')
        self.__dataset = np.append(self.__dataset, point[np.newaxis, :], axis=0)
        # faire un round sur le floating point de l'index

    # séparer les tags
