class Solution:
    def containsPattern(self, arr: List[int], m: int, k: int) -> bool:
        n = len(arr)
        for i in range(n - m * k + 1):
            if arr[i:i+m] * k == arr[i:i+m*k]:
                return True
        return False