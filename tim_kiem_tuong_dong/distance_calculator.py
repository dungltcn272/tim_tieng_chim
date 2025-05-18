from scipy.spatial.distance import euclidean


# tính toán khoảng cách 2 vector
def calculate_distance(vector1, vector2):
    return euclidean(vector1.values[0], vector2.values[0])
