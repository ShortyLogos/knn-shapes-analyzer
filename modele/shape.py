from cmath import sqrt
import numpy as np


# calcul du centroïd
def centroid(image):
    c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    return (np.sum(r * image), np.sum(c * image)) / area(image)


# calcul de l'aire
def area(image):
    return np.sum(image)


# calcul du périmètre de l'image
def tableau_perimeter(image):
    temp = image.copy()
    for y in range(image.shape[0] - 1):
        for x in range(image.shape[1] - 1):
            if temp[x, y]:
                temp[x, y] = is_perimeter(image, (x, y))
    return temp


def perimeter(image):
    return np.sum(tableau_perimeter(image))


# vérification d'un pixel sur le périmètre
def is_perimeter(image, index_pixel):
    x, y = index_pixel
    left = max(0, x - 1)
    right = max(0, x + 2)
    bottom = max(0, y - 1)
    top = max(0, y + 2)
    sample = image[left:right, bottom:top]
    return True if not np.sum(sample) == 9 else False


# tableau des coordonnées de tous le périmetre
def perimetre_coordinates(image):
    perimetre = tableau_perimeter(image)
    c, r = image_coordinates(image)
    match = perimetre == 1
    match_col = c[match]
    match_row = r[match]
    return np.stack((match_col, match_row), axis=1)


# fonction utilitaire pour générer les coordonnées de l'image
def image_coordinates(image):
    return np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))


# indice de complexité
def indice_complex(image):
    return area(image) / pow(perimeter(image), 2)


# nombre de sommet
def sum_sommets(image):
    centre = centroid(image).astype(image.dtype)
    perimetres_coordonnees = perimetre_coordinates(image)
    distances = tableau_distance_points(centre, perimetres_coordonnees)
    rayon = np.max(distances)
    condition_sommet = (distances[:] == rayon).astype(int)
    return np.sum(condition_sommet)



# distance entre deux points
def tableau_distance_points(centroide, perimetre):
    return np.sum((centroide - perimetre) ** 2, axis=1) ** 0.5


## A EFFACER!!!!!
def create_image(size):
    return np.zeros((size[1], size[0]), dtype=np.uint8)


def draw_rectangle(image, top_left, bottom_right):
    top_left = (max(0, top_left[0]), max(0, top_left[1]))
    bottom_right = (min(image.shape[1], bottom_right[0]), min(image.shape[0], bottom_right[1]))
    image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = 1


if __name__ == '__main__':
    img_test = create_image((10, 10))
    draw_rectangle(img_test, (2, 2), (7, 7))
    sum_sommets(img_test)
