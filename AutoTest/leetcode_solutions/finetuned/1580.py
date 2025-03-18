class Solution:
    def maxBoxesInWarehouse(self, boxes: List[int], warehouse: List[int]) -> int:
        boxes.sort()
        n = len(warehouse)
        m = len(boxes)
        i = 0
        j = n - 1
        count = 0
        
        while i < m and j >= 0:
            if boxes[i] <= warehouse[j]:
                count += 1
                i += 1
            j -= 1
        
        return count