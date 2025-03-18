class Solution:
    def findKthBit(self, n: int, k: int) -> str:
        def helper(n, k):
            if n == 1:
                return '0'
            length = 2**(n-1) - 1
            mid = length + 1
            if k == mid:
                return '1'
            elif k < mid:
                return helper(n-1, k)
            else:
                return '1' if helper(n-1, length-k+1) == '0' else '0'
        
        return helper(n, k)