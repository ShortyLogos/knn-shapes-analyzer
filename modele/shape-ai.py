import numpy as np

# calcul du centroïd
def centroid(image):
    c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    return (np.sum(r * image), np.sum(c * image)) / area(image)

# calcul de l'aire
def area(image):
    return np.sum(image)

# calcul du périmètre de l'image
def perimeter(image):
    # perimeter = image.copy()
    # perimeter[:] = (is_perimeter(image, (image[:]))).astype(perimeter.dtype)
    # # à retravailler

# vérification d'un pixel sur le périmètre
def is_perimeter(image, index_pixel):
    x, y = index_pixel
    left = max(0, x - 1)
    right = max(0, x + 2)
    bottom = max(0, y -1)
    top = max(0, y + 2)
    sample = image[left:right, bottom:top]
    return True if np.sum(sample) not 9 else False

# fonction utilitaire pour générer les coordonnées de l'image
def image_coordinates(image):
    return np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))


