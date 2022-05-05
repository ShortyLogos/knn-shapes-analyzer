import numpy as np
from knn import KNN
from shapeanalyzer import ShapeAnalyzer

# 1)
def create_image(size):
  return np.zeros((size[1], size[0]), dtype=np.uint8)

# 2)
def fill(image, color=1):
  image[:] = color

# 3)
def clear(image):
  fill(image, 0)

# 4)
def randomize(image, percent=0.5):
  rng = np.random.default_rng()
  image[:] = (rng.random((image.shape)) <= percent).astype(image.dtype)

# 5)
def draw_point(image, point, color=1):
  if point[0] >= 0 and point[0] < image.shape[1] and point[1] >= 0 and point[1] < image.shape[0]:
    image[point[1], point[0]] = color

# 6)
def draw_rectangle(image, top_left, bottom_right):
    top_left = (max(0,top_left[0]), max(0,top_left[1]))
    bottom_right = (min(image.shape[1],bottom_right[0]), min(image.shape[0],bottom_right[1]))
    image[top_left[1]:bottom_right[1],top_left[0]:bottom_right[0]] = 1

# 7)
def reset_border(image):
  # image[:,0] = image[:,-1] = 0 # reset left/right 
  # image[0,:] = image[-1,:] = 0 # reset top/bottom

  
  image[:,[0,-1]] = image[[0,-1]] = 0

# 8)
def draw_random_point(image, color=1):
  rng = np.random.default_rng()
  x = rng.integers(0,image.shape[1])
  y = rng.integers(0,image.shape[0])
  draw_point(image, (x, y), color)

# 9)
def draw_random_point_on(image, color=0):
  # étape par étape
  c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
  match = image == color
  match_col = c[match]
  match_row = r[match]
  rng = np.random.default_rng()
  i = rng.integers(0, match_col.size)
  x = match_col[i]
  y = match_row[i]
  image[y, x] = int(not color)

# 10)
def distance_between_two_points(image):
  c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
  points = np.empty((2,2), np.int)
  points[:,0] = c[image == 1]
  points[:,1] = r[image == 1]
  return np.sum((points[0,:] - points[1,:])**2)**0.5
  

# 11)
def draw_circle(image, center, radius):
  c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
  dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
  circle = (dist <= radius).astype(np.uint8)
  image[:,:] = np.logical_or(image[:,:], circle)
  
  # image[:,:] = np.logical_or(image[:,:], (((r-center[1])**2 + (c-center[0])**2) <= radius * radius).astype(np.uint8))

# 12)
def area(image):
  return np.sum(image)

# 13)
def centroid(image):
  c, r = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
  return (np.sum(r * image), np.sum(c * image)) / area(image)

# 14)
def perimeter(image):
    # tbd
    pass

if __name__ == '__main__':
    # img_test = create_image((10, 10))
    # draw_rectangle(img_test, (2, 2), (7, 7))
    # analyzer = ShapeAnalyzer(img_test, 0.2)
    # print(analyzer.analyze(img_test))
    metrics1 = [0.1, 0.5, 0.3]
    metrics1 = np.array(metrics1)
    metrics2 = [0.5, 0.4, 0.32]
    metrics2 = np.array(metrics2)
    metrics3 = [0.11, 0.78, 0.45]
    metrics3 = np.array(metrics3)
    point = [0.2, 0.4, 0.2]
    point = np.array(point)
    knn = KNN(3, 1)
    knn.add_training_point(metrics1, "triangle")
    knn.add_training_point(metrics2, "carré")
    knn.add_training_point(metrics2, "triangle")
    #print(knn.dataset)
    knn.classify(point)
    print("On pratique le debugger")




