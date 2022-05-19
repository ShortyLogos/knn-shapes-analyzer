import numpy as np
import math

class ShapeAnalyzer:
    def __init__(self, image=None, outer_radius_buffer=None, perimeter_color=1):
        self.__perimeter_color = perimeter_color
        self.__metrics_name = ["Pixels On Outer Radius", "Donut Ratio", "Complexity Index"]
        self.__image = image
        self.__outer_radius_buffer = outer_radius_buffer
        if self.image is not None:
            self.__area_shape = self.area(self.image)
            self.__perimeter_shape = self.perimeter(self.image)

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, new_image):
        self.__image = new_image

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
    def centroid_shape(self):
        pass

    def analyze(self, image):
        metrics = [self.pixels_on_perimeter(image), self.donut_ratio(image), self.complexity_index(image)]
        # metrics = ['{0:.3g}'.format(self.pixels_on_perimeter(image)), '{0:.3g}'.format(self.donut_ratio(image)), '{0:.3g}'.format(self.complexity_index(image))]
        return metrics

    #### TROIS MÉTRIQUES ####
    # nombre de pixels dans une zone du radius circoncis
    def pixels_on_perimeter(self, image):
        distances = self.centroid_distances(image)
        radius = np.max(distances)
        # condition_sommet = distances[np.where((radius - self.__outer_radius_buffer <= distances) & (distances <= radius + self.__outer_radius_buffer))]
        condition_sommet = distances[radius - self.__outer_radius_buffer <= distances]
        # après le calcul, on normalise les données et on les retourne
        return np.size(condition_sommet) / (np.pi * radius ** 2 - np.pi * (radius - self.__outer_radius_buffer) ** 2)
        # return np.size(condition_sommet) / self.outer_donut_area(image, self.centroid(image), radius)

    # ratio entre le radius externe et interne
    def donut_ratio(self, image):
        distances = self.centroid_distances(image)
        inner_radius = np.min(distances)
        outer_radius = np.max(distances)
        return inner_radius / outer_radius

    # indice de complexité
    def complexity_index(self, image):
        # mesure normalisée un peu au-dessus de 1, devoir réviser la façon dont on calcul
        # le périmètre avant la remise. Il est brouillé.
        return ((4 * math.pi * self.area(image))/(self.perimeter(image) ** 2))
    ################################################################################################

    # calcul du centroïde
    def centroid(self, image):
        c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        return (np.sum(r * image), np.sum(c * image)) / self.area(image)

    # calcul de l'aire (tous les elements qui sont 0)
    def area(self, image):
        return np.sum(image)

    # calcul du périmètre de l'image
    def perimeter_array(self, image):
        temp = image.copy()
        for y in range(image.shape[0] - 1):
            for x in range(image.shape[1] - 1):
                if temp[x, y]:
                    temp[x, y] = self.is_perimeter(image, (x, y))
        return temp

    def perimeter(self, image):
        return np.sum(self.perimeter_array(image))

    # vérification d'un pixel sur le périmètre
    def is_perimeter(self, image, index_pixel):
        x, y = index_pixel
        left = max(0, x - 1)
        right = max(0, x + 2)
        bottom = max(0, y - 1)
        top = max(0, y + 2)
        sample = image[left:right, bottom:top]
        return True if not np.sum(sample) == 9 else False

    # tableau des coordonnées de tous le périmetre
    def perimeter_coordinates(self, image):
        perimetre = self.perimeter_array(image)
        c, r = self.image_coordinates(image)
        match = perimetre == self.__perimeter_color
        match_col = c[match]
        match_row = r[match]
        return np.stack((match_col, match_row), axis=1)

    # fonction utilitaire pour générer les coordonnées de l'image
    def image_coordinates(self, image):
        return np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))

    def centroid_distances(self, image):
        return self.calculate_distance(self.centroid(image).astype(image.dtype), self.perimeter_coordinates(image))

    # distance entre deux points
    def calculate_distance(self, centroide, perimetre):
        return np.sum((centroide - perimetre) ** 2, axis=1) ** 0.5

    def draw_circle(self,image, center, radius):
        c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
        circle = (dist <= radius).astype(np.uint8)
        image[:, :] = np.logical_or(image[:, :], circle)