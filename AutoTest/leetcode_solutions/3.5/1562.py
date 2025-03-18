from typing import List

class Solution:
    def findLatestStep(self, arr: List[int], m: int) -> int:
        n = len(arr)
        if n == m:
            return n
        res = -1
        length = [0] * (n + 2)
        for i in range(n):
            left = length[arr[i] - 1]
            right = length[arr[i] + 1]
            length[arr[i] - left] = length[arr[i] + right] = left + right + 1
            if left == m or right == m:
                res = i
            if left > 0:
                length[arr[i] - left + 1] = left
            if right > 0:
                length[arr[i] + right - 1] = right
        return res