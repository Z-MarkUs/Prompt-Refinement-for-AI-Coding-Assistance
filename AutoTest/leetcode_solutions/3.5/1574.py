from typing import List

class Solution:
    def findLengthOfShortestSubarray(self, arr: List[int]) -> int:
        n = len(arr)
        left, right = 0, n - 1
        
        while left < n - 1 and arr[left] <= arr[left + 1]:
            left += 1
        
        if left == n - 1:
            return 0
        
        while right > 0 and arr[right] >= arr[right - 1]:
            right -= 1
        
        result = min(n - left - 1, right)
        
        for i in range(left + 1):
            if arr[i] <= arr[right]:
                result = min(result, right - i - 1)
            elif right < n - 1:
                right += 1
            else:
                break
        
        return result