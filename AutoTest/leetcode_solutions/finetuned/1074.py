class Solution:
    def numSubmatrixSumTarget(self, matrix: List[List[int]], target: int) -> int:
        def subarraySum(nums: List[int], k: int) -> int:
            count = 0
            prefix_sum = 0
            sum_count = {0: 1}
            for num in nums:
                prefix_sum += num
                count += sum_count.get(prefix_sum - k, 0)
                sum_count[prefix_sum] = sum_count.get(prefix_sum, 0) + 1
            return count
        
        rows, cols = len(matrix), len(matrix[0])
        result = 0
        
        for r1 in range(rows):
            row_sum = [0] * cols
            for r2 in range(r1, rows):
                for c in range(cols):
                    row_sum[c] += matrix[r2][c]
                result += subarraySum(row_sum, target)
        
        return result