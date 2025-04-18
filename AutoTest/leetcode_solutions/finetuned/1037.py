class Solution:
    def isBoomerang(self, points: List[List[int]) -> bool:
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]
        
        if (x1 == x2 and y1 == y2) or (x1 == x3 and y1 == y3) or (x2 == x3 and y2 == y3):
            return False
        
        return (y3 - y2) * (x2 - x1) != (y2 - y1) * (x3 - x2)