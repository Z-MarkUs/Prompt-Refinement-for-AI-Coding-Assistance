from typing import List

class Solution:
    def trimMean(self, arr: List[int]) -> float:
        arr.sort()
        n = len(arr)
        start = n // 20
        end = n - start
        return sum(arr[start:end]) / (n * 0.9)