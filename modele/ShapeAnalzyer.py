import numpy as np


class ShapeAnalyzer:
    def __init__(self, image=None, outer_radius_buffer=None):
        self.__image = image
        self.__outer_radius_buffer = outer_radius_buffer

    @property
    def outer_radius_buffer(self):
        return self.__outer_radius_buffer

    @outer_radius_buffer.setter
    def outer_radius_buffer(self, value):
        self.__outer_radius_buffer = value

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, new_image):
        self.__image = new_image

    def analyze(self):
        metrics = [self.pixels_on_perimeter(), self.donut_ratio(), self.complexity_index()]
        return metrics

    #### TROIS MÉTRIQUES ###########################################################################
    # nombre de pixels dans une zone du radius circoncis
    def pixels_on_perimeter(self):
        distances = self.centroid_distances()
        radius = np.max(distances)
        condition_sommet = distances[
            np.where(
                (radius - self.__outer_radius_buffer <= distances) & (distances <= radius + self.__outer_radius_buffer))]
        # après le calcul, on normalise les données et on les retourne
        return np.size(condition_sommet) / self.outer_donut_area(image,self.centroid(image),radius)

    # ratio entre le radius externe et interne
    def donut_ratio(self):
        distances = self.centroid_distances()
        inner_radius = np.min(distances)
        outer_radius = np.max(distances)
        return inner_radius / outer_radius

    # indice de complexité
    def complexity_index(self):
        return self.area(self.image) / self.perimeter(self.image) ** 2
    ################################################################################################

    def outer_donut_area(self, center, radius):
        outer_radius_area_buffer = self.image.copy()
        outer_radius_area_minus_buffer = np.zeros((self.image.shape[1], self.image.shape[0])).astype(int)
        self.draw_circle(outer_radius_area_buffer, center, radius + self.__outer_radius_buffer)
        self.draw_circle(outer_radius_area_minus_buffer, center, radius - self.__outer_radius_buffer)
        print(outer_radius_area_buffer)
        print(self.image)
        print(outer_radius_area_minus_buffer)
        return np.sum(outer_radius_area_buffer) - np.sum(outer_radius_area_minus_buffer)

    # calcul du centroïde
    def centroid(self):
        c, r = np.meshgrid(np.arange(self.image.shape[1]), np.arange(self.image.shape[0]))
        return (np.sum(r * self.image), np.sum(c * self.image)) / self.area()

    # calcul de l'aire
    def area(self):
        return np.sum(self.image)

    # calcul du périmètre de l'image
    def perimeter_array(self):
        temp = self.image.copy()
        for y in range(self.image.shape[0] - 1):
            for x in range(self.image.shape[1] - 1):
                if temp[x, y]:
                    temp[x, y] = self.is_perimeter((x, y))
        return temp

    def perimeter(self):
        return np.sum(self.perimeter_array())

    # vérification d'un pixel sur le périmètre
    def is_perimeter(self, index_pixel):

        x, y = index_pixel
        left = max(0, x - 1)
        right = max(0, x + 2)
        bottom = max(0, y - 1)
        top = max(0, y + 2)

        print(left, right, bottom, top, self.image)
        sample = self.image[left:right, bottom:top]
        return True if not np.sum(sample) == 9 else False

    # tableau des coordonnées de tous le périmetre
    def perimeter_coordinates(self):
        perimeter = self.perimeter_array()
        c, r = self.image_coordinates()
        match = perimeter == 1
        match_col = c[match]
        match_row = r[match]
        return np.stack((match_col, match_row), axis=1)

    # fonction utilitaire pour générer les coordonnées de l'image
    def image_coordinates(self):
        return np.meshgrid(np.arange(self.image.shape[1]), np.arange(self.image.shape[0]))

    def centroid_distances(self):
        a = (self.centroid() - self.perimeter()) ** 2
        return np.sum((self.centroid() - self.perimeter()) ** 2, axis=0) ** 0.5

    def draw_circle(self, image, center, radius):
        c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
        circle = (dist <= radius).astype(np.uint8)
        image[:,:] = np.logical_or(image[:,:], circle)

    ## POUR DES TESTS --- A EFFACER!!!!!
    @staticmethod
    def create_image(self, size):
        return np.zeros((size[1], size[0]), dtype=np.uint8)

    def draw_rectangle(self, image, top_left, bottom_right):
        top_left = (max(0, top_left[0]), max(0, top_left[1]))
        bottom_right = (min(image.shape[1], bottom_right[0]), min(image.shape[0], bottom_right[1]))
        image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = 1


if __name__ == '__main__':
    img_test = np.zeros((10, 10), dtype=np.uint8)
    print(img_test)
    analyzer = ShapeAnalyzer(0.2, img_test)
    analyzer.draw_rectangle(img_test, (2, 2), (7, 7))
    analyzer.image = img_test
    print(analyzer.image)
    print(analyzer.pixels_on_perimeter())
