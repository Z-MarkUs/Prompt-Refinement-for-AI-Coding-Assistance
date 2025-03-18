from typing import List

class Solution:
    def findKthPositive(self, arr: List[int], k: int) -> int:
        missing_nums = []
        i = 1
        j = 0
        
        while len(missing_nums) < k:
            if j < len(arr) and arr[j] == i:
                j += 1
            else:
                missing_nums.append(i)
            i += 1
        
        return missing_nums[-1]