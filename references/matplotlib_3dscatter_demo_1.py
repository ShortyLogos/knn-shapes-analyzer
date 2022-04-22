import matplotlib.pyplot as plt
import numpy as np


def generate_3d_cloud(n_points, mean, stdev, marker, color):
    '''Generate 3d points from normal distribution
    
       Example : generate_3d_cloud(15, (0.0, 10.0, -10.0), (0.0, 0.1, 1.0))
    '''
    # Fixing random state for reproducibility
    rng = np.random.default_rng(123456789)
    data = np.empty((n_points,3), np.float)
    data[:,0] = rng.normal(mean[0], stdev[0], n_points)
    data[:,1] = rng.normal(mean[1], stdev[1], n_points)
    data[:,2] = rng.normal(mean[2], stdev[2], n_points)
    return { 'data':data, 'x':data[:,0], 'y':data[:,1], 'z':data[:,2], 'marker':marker, 'color':color }


def graph_of_2x_cloud3d(title, cloud1, cloud2):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(cloud1['x'], cloud1['y'], cloud1['z'], marker=cloud1['marker'], color=cloud1['color'])
    ax.scatter(cloud2['x'], cloud2['y'], cloud2['z'], marker=cloud2['marker'], color=cloud2['color'])

    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


def main():
    n_points = 500
    cloud1 = generate_3d_cloud(n_points, (0.0, 10.0, -10.0), (0.0, 1.0, 2.0), 'o', (1.0,0.5,0.0))
    cloud2 = generate_3d_cloud(n_points, (10.0, -10.0, 10.0), (5.0, 10.0, 5.0), '^', 'b')
    graph_of_2x_cloud3d('Graphique de dispersion', cloud1, cloud2)

if __name__ == '__main__':
    main()

