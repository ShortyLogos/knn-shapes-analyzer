from re import S
import numpy as np
import shapeanalyzer


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

    def classify(self, unclassified_point):
        neighbours = self.get_k_neighbours(unclassified_point)
        tags = self.get_k_neighbours_tags(neighbours)
        tag = self.get_most_common_tag(tags)
        classified_point = [unclassified_point, tag]
        return classified_point

        # point = un ensemble de métriques

    def add_training_point(self, point, tag):
        if point.shape[1] is not self.dataset.shape[1]:
            raise ValueError('ayoye')
        self.__dataset = np.append(self.__dataset, point, axis=0)

    def get_most_common_tag(self, tags):
        # https://stackoverflow.com/questions/19909167/how-to-find-most-frequent-string-element-in-numpy-ndarray
        tags_unique, pos = np.unique(tags.T, return_inverse=True)  # Finds all unique elements and their positions
        counts = np.bincount(pos)  # Count the number of each unique element
        position = counts.argmax()  # Va trouver la position de l'élément le plus commun
        return tags_unique[position]

    # Retourne le tableau des k voisins
    def get_k_neighbours(self, unclassified_point):
        distances = self.distances_from_point(unclassified_point)
        k_neighbours_distances_and_tags = distances.argsort()[
                                          self.__k_constant:]  # https://stackoverflow.com/questions/16817948/i-have-need-the-n-minimum-index-values-in-a-numpy-array
        return k_neighbours_distances_and_tags

    # Retourne le tableau des tags des k voisins
    def get_k_neighbours_tags(self, k_neighbours):
        k_neighbours_tags = [i[1] for i in
                             k_neighbours]  # https://stackoverflow.com/questions/17710672/create-2-dimensional-array-with-2-one-dimensional-array
        return k_neighbours_tags

    def distances_from_point(self, unclassified_point):
        distances_only_array = np.sum((unclassified_point - self.dataset[0, :]) ** 2, axis=1) ** 0.5
        tag_only_array = [i[-1] for i in self.dataset]
        distances_and_tag_array = np.vstack((distances_only_array, tag_only_array)).T
        return distances_and_tag_array

    def new_dataset(self, data):
        pass

        # self.dataset.clear()
