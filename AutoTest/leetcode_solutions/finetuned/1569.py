class Solution:
    def numOfWays(self, nums: List[int]) -> int:
        def count_ways(arr):
            if len(arr) <= 2:
                return 1
            left = [x for x in arr if x < arr[0]]
            right = [x for x in arr if x > arr[0]]
            return comb(len(left) + len(right), len(left)) * count_ways(left) * count_ways(right) % (10**9 + 7)
        
        def comb(n, k):
            numerator = 1
            denominator = 1
            for i in range(n, n - k, -1):
                numerator = (numerator * i) % (10**9 + 7)
            for i in range(1, k + 1):
                denominator = (denominator * i) % (10**9 + 7)
            return pow(denominator, 10**9 + 7 - 2, 10**9 + 7) * numerator % (10**9 + 7)
        
        return (count_ways(nums) - 1) % (10**9 + 7)