class Solution:
    def maxBoxesInWarehouse(self, boxes: List[int], warehouse: List[int]) -> int:
        boxes.sort()
        left, right = 0, len(warehouse) - 1
        count = 0
        
        while left <= right and boxes:
            if boxes[-1] <= warehouse[left]:
                count += 1
                boxes.pop()
            elif boxes[-1] <= warehouse[right]:
                count += 1
                boxes.pop()
            
            if warehouse[left] < warehouse[right]:
                left += 1
            else:
                right -= 1
        
        return count