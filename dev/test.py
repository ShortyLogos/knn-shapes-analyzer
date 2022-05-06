import numpy as np
from knn import KNN
from shapeanalyzer import ShapeAnalyzer

def create_image(size):
    return np.zeros((size[1], size[0]), dtype=np.uint8)

def draw_circle(image, center, radius):
    c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
    dist = np.sqrt((r - center[1]) ** 2 + (c - center[0]) ** 2)
    circle = (dist <= radius).astype(np.uint8)
    image[:, :] = np.logical_or(image[:, :], circle)

if __name__ == '__main__':
    # print(analyzer.analyze(img_test))
    metrics1 = [0.1, 0.5, 0.3]
    metrics1 = np.array(metrics1)
    metrics2 = [0.5, 0.4, 0.32]
    metrics2 = np.array(metrics2)
    metrics3 = [0.11, 0.78, 0.45]
    metrics3 = np.array(metrics3)
    metrics4 = [0.31, 0.18, 0.25]
    metrics4 = np.array(metrics4)
    metrics5 = [0.21, 0.98, 0.154]
    metrics5 = np.array(metrics5)
    metrics6 = [0.45, 0.64, 0.534]
    metrics6 = np.array(metrics6)
    point = [0.2, 0.4, 0.2]
    point = np.array(point)
    knn = KNN(3, 3)
    knn.add_training_point(metrics1, "triangle")
    knn.add_training_point(metrics2, "carré")
    knn.add_training_point(metrics3, "triangle")
    knn.add_training_point(metrics4, "losange")
    knn.add_training_point(metrics5, "losange")
    knn.add_training_point(metrics6, "cercle")
    rep = knn.classify(point)





