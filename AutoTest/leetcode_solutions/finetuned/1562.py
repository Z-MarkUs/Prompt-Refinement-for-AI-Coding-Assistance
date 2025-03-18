class Solution:
    def findLatestStep(self, arr: List[int], m: int) -> int:
        n = len(arr)
        if m > n:
            return -1
        
        if m == n:
            return n
        
        groups = {0: n}
        result = -1
        
        for i in range(n - 1, -1, -1):
            pos = arr[i] - 1
            left = right = pos
            if pos - 1 in groups:
                left = pos - groups.pop(pos - 1) + 1
            if pos + 1 in groups:
                right = pos + groups.pop(pos + 1) - 1
            
            length = right - left + 1
            groups[left] = groups[right] = length
            
            if length == m:
                result = i
        
        return result