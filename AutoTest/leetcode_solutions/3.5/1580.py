from typing import List

class Solution:
    def maxBoxesInWarehouse(self, boxes: List[int], warehouse: List[int]) -> int:
        boxes.sort()
        n = len(warehouse)
        for i in range(1, n):
            warehouse[i] = min(warehouse[i], warehouse[i-1])
        res = 0
        j = n - 1
        for box in reversed(boxes):
            if j >= 0 and warehouse[j] >= box:
                res += 1
                j -= 1
        return res