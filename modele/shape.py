import numpy as np


class ShapeAnalyzer:
    def __init__(self, outer_radius_buffer):
        self.__outer_radius_buffer = outer_radius_buffer

    @property
    def outer_radius_buffer(self):
        return self.__outer_radius_buffer

    @outer_radius_buffer.setter
    def outer_radius_buffer(self, value):
        self.__outer_radius_buffer = value

    def analyze(self, image):
        metrics = [self.sum_sommets(image), self.donut_ratio(image), self.complexity_index(image)]
        return metrics

    #### TROIS MÉTRIQUES ###
    # nombre de sommets
    def sum_sommets(self, image):
        distances = self.centroid_distances(image)
        rayon = np.max(distances)
        condition_sommet = distances[
            np.where(
                (rayon - self.__outer_radius_buffer <= distances) & (distances <= rayon + self.__outer_radius_buffer))]
        return np.size(condition_sommet)

    # ratio entre le rayon externe et interne
    def donut_ratio(self, image):
        distances = self.centroid_distances(image)
        inner_radius = np.min(distances)
        outer_radius = np.max(distances)
        return inner_radius / outer_radius

    # indice de complexité
    def complexity_index(self, image):
        return self.area(image) / self.perimeter(image) ** 2

    ##################################

    # calcul du centroïde
    def centroid(self, image):
        c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        return (np.sum(r * image), np.sum(c * image)) / self.area(image)

    # calcul de l'aire
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
        match = perimetre == 1
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

    ## POUR DES TESTS --- A EFFACER!!!!!
    def create_image(self, size):
        return np.zeros((size[1], size[0]), dtype=np.uint8)

    def draw_rectangle(self, image, top_left, bottom_right):
        top_left = (max(0, top_left[0]), max(0, top_left[1]))
        bottom_right = (min(image.shape[1], bottom_right[0]), min(image.shape[0], bottom_right[1]))
        image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = 1


# if __name__ == '__main__':
#     analyzer = ShapeAnalyzer(0.2)
#     img_test = analyzer.create_image((10, 10))
#     analyzer.draw_rectangle(img_test, (2, 2), (7, 7))
#     analyzer.sum_sommets(img_test)
