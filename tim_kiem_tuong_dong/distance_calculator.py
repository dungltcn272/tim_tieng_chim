from scipy.spatial.distance import euclidean

def calculate_distance(vector1, vector2):
    return euclidean(vector1.values[0], vector2.values[0])
