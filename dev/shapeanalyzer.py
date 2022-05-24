import numpy as np
import math


class ShapeAnalyzer:
    def __init__(self, image=None, outer_radius_buffer=None, perimeter_color=1):
        self.__perimeter_color = perimeter_color
        self.__metrics_name = ["Pixels On Outer Radius", "Donut Ratio", "Complexity Index"]
        self.__outer_radius_buffer = outer_radius_buffer

        self.__image = image
        if self.__image is not None:
            self.__area_shape = self.area()
            self.__perimeter_shape = self.perimeter()
            self.__distances = self.centroid_distances()

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, new_image):
        self.__image = new_image
        self.__area_shape = self.area()
        self.__perimeter_shape = self.perimeter()
        self.__distances = self.centroid_distances()

    @property
    def outer_radius_buffer(self):
        return self.__outer_radius_buffer

    @outer_radius_buffer.setter
    def outer_radius_buffer(self, value):
        self.__outer_radius_buffer = value

    @property
    def area_shape(self):
        return self.__area_shape

    @area_shape.setter
    def area_shape(self, value):
        self.__area_shape = value

    @property
    def perimeter_shape(self):
        return self.__perimeter_shape

    @perimeter_shape.setter
    def perimeter_shape(self, value):
        self.__perimeter_shape = value

    @property
    def distances(self):
        return self.__distances

    @distances.setter
    def distances(self, value):
        self.__distances = value

    def analyze(self):
        metrics = [self.pixels_on_perimeter(), self.donut_ratio(), self.complexity_index()]
        return metrics

    #### TROIS MÉTRIQUES ####
    # nombre de pixels dans une zone du radius circoncis
    def pixels_on_perimeter(self):
        radius = np.max(self.__distances)
        condition_sommet = self.__distances[radius - self.__outer_radius_buffer <= self.__distances]
        return np.size(condition_sommet) / (np.pi * radius ** 2 - np.pi * (radius - self.__outer_radius_buffer) ** 2)

    # ratio entre le radius externe et interne
    def donut_ratio(self):
        inner_radius = np.min(self.__distances)
        outer_radius = np.max(self.__distances)
        return inner_radius / outer_radius

    # indice de complexité
    def complexity_index(self):
        return (4 * math.pi * self.__area_shape) / (self.__perimeter_shape ** 2)

    ################################################################################################

    # calcul du centroïde
    def centroid(self):
        c, r = np.meshgrid(np.arange(self.__image.shape[1]), np.arange(self.__image.shape[0]))
        return (np.sum(r * self.__image), np.sum(c * self.__image)) / self.area()

    # calcul de l'aire
    def area(self):
        return np.sum(self.__image)

    def perimeter(self):
        return np.sum(self.perimeter_array())

    def perimeter_array(self):
        result = self.__image.copy()
        d0 = self.__image[0:-2, 0:-2]
        d1 = self.__image[1:-1, 0:-2]
        d2 = self.__image[2:, 0:-2]
        d3 = self.__image[0:-2, 1:-1]
        d4 = self.__image[1:-1, 1:-1]
        d5 = self.__image[2:, 1:-1]
        d6 = self.__image[0:-2, 2:]
        d7 = self.__image[1:-1, 2:]
        d8 = self.__image[2:, 2:]
        r = result[1:-1, 1:-1]
        r[:] = np.logical_and((d0 + d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8) != 9, d4 != 0).astype(np.uint8)
        return result

    # tableau des coordonnées de tous le périmetre
    def perimeter_coordinates(self):
        c, r = self.image_coordinates()
        match = self.perimeter_array() == self.__perimeter_color
        match_col = c[match]
        match_row = r[match]
        return np.stack((match_row, match_col), axis=1)

    # fonction utilitaire pour générer les coordonnées de l'image
    def image_coordinates(self):
        return np.meshgrid(np.arange(self.__image.shape[1]), np.arange(self.__image.shape[0]))

    def centroid_distances(self):
        return self.calculate_distance(self.centroid().astype(self.__image.dtype), self.perimeter_coordinates())

    # distance entre deux points
    def calculate_distance(self, centroid, perimeter):
        return np.sum((perimeter - centroid) ** 2, axis=1) ** 0.5

