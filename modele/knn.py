from re import S
import numpy as np
import shapeanalyzer


class KNN:
    def __init__(self, dimensions, k_constant):
        self.__dataset = np.empty((0, dimensions + 1), dtype=np.float32)
        self.__dimensions = dimensions
        self.__k_constant = k_constant
        self.__k_tags = np.empty(0, dtype=np.str_)
        # self.__k_tags = []

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
        classified_point = [unclassified_point, tag]
        return classified_point

        # point = un ensemble de métriques

    def get_most_common_tag(self, tags):
        # https://stackoverflow.com/questions/19909167/how-to-find-most-frequent-string-element-in-numpy-ndarray
        tags_unique, pos = np.unique(tags.T, return_inverse=True)  # Finds all unique elements and their positions
        counts = np.bincount(pos)  # Count the number of each unique element
        position = counts.argmax()  # Va trouver la position de l'élément le plus commun
        return tags_unique[position]

    # Retourne le tableau des k voisins
    def get_k_neighbours(self, unclassified_point):
        distances = self.distances_from_point(unclassified_point)
        k_neighbours_distances_and_tags = distances.argsort()[self.__k_constant:]  # https://stackoverflow.com/questions/16817948/i-have-need-the-n-minimum-index-values-in-a-numpy-array  # À TESTER
        return k_neighbours_distances_and_tags

    # Retourne le tableau des tags des k voisins
    def get_k_neighbours_tags(self, k_neighbours):
        k_neighbours_tags = k_neighbours[-1, :]  # https://stackoverflow.com/questions/17710672/create-2-dimensional-array-with-2-one-dimensional-array
        # on crée un nouveau tableau qui va chercher les tags de notre autre tableau
        tags_occurences = self.__k_tags
        return k_neighbours_tags

    def distances_from_point(self, unclassified_point):
        distances_only_array = np.sum((unclassified_point - self.dataset[:-1, :]) ** 2, axis=1) ** 0.5
        tag_index_array = self.dataset[-1, :]  # indices associatifs pour les tags
        distances_and_index_array = np.vstack((distances_only_array, tag_index_array)).T  # À TESTER
        return distances_and_index_array

    def new_dataset(self, data):
        # self.dataset.clear()
        pass

    def add_training_point(self, point, tag):
        # on transforme point en nparray si pas le cas
        if tag not in self.__k_tags:
            self.add_tag(tag)
        index_tag = np.where(self.__k_tags == tag)
        point = np.append(point, index_tag[0], axis=0)
        if point.shape[0] is not self.__dataset.shape[1]:
            raise ValueError('Méchant problème')
        self.__dataset = np.append(self.__dataset, point[np.newaxis, :], axis=0)

    # faire un round sur le floating point de l'index

    # séparer les tags
