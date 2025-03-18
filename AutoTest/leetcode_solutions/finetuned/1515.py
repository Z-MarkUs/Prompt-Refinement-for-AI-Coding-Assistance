class Solution:
    def getMinDistSum(self, positions: List[List[int]) -> float:
        def distance(x, y):
            return sum(math.sqrt((x - px) ** 2 + (y - py) ** 2) for px, py in positions)
        
        def ternary_search_x(minX, maxX):
            while maxX - minX > 1e-7:
                mid1 = minX + (maxX - minX) / 3
                mid2 = maxX - (maxX - minX) / 3
                if distance(mid1, y) < distance(mid2, y):
                    maxX = mid2
                else:
                    minX = mid1
            return (minX + maxX) / 2
        
        def ternary_search_y(minY, maxY, x):
            while maxY - minY > 1e-7:
                mid1 = minY + (maxY - minY) / 3
                mid2 = maxY - (maxY - minY) / 3
                if distance(x, mid1) < distance(x, mid2):
                    maxY = mid2
                else:
                    minY = mid1
            return (minY + maxY) / 2
        
        minX = minY = 0
        maxX = maxY = 100
        for px, py in positions:
            minX = min(minX, px)
            maxX = max(maxX, px)
            minY = min(minY, py)
            maxY = max(maxY, py)
        
        x = (minX + maxX) / 2
        y = (minY + maxY) / 2
        
        x = ternary_search_x(minX, maxX)
        y = ternary_search_y(minY, maxY, x)
        
        return round(distance(x, y), 5)