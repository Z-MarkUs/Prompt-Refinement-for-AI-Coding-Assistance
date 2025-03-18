from typing import List

class Solution:
    def getMinDistSum(self, positions: List[List[int]]) -> float:
        def euclidean_distance(x1, y1, x2, y2):
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        def total_distance(x, y):
            return sum(euclidean_distance(x, y, px, py) for px, py in positions)
        
        def gradient_descent(learning_rate=0.1):
            x, y = sum(x for x, _ in positions) / len(positions), sum(y for _, y in positions) / len(positions)
            while True:
                total_dist = total_distance(x, y)
                found_new_min = False
                for dx, dy in [(0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1)]:
                    new_x, new_y = x + dx, y + dy
                    new_total_dist = total_distance(new_x, new_y)
                    if new_total_dist < total_dist:
                        x, y = new_x, new_y
                        found_new_min = True
                        break
                if not found_new_min:
                    break
            return total_dist, (x, y)
        
        return gradient_descent()[0]