from typing import List

class Solution:
    def numSubmatrixSumTarget(self, matrix: List[List[int]], target: int) -> int:
        def subarraySum(nums, k):
            count = 0
            prefix_sum = {0: 1}
            curr_sum = 0
            for num in nums:
                curr_sum += num
                count += prefix_sum.get(curr_sum - k, 0)
                prefix_sum[curr_sum] = prefix_sum.get(curr_sum, 0) + 1
            return count
        
        rows, cols = len(matrix), len(matrix[0])
        count = 0
        for left in range(cols):
            prefix_sums = [0] * rows
            for right in range(left, cols):
                for row in range(rows):
                    prefix_sums[row] += matrix[row][right]
                count += subarraySum(prefix_sums, target)
        return count