class Solution:
    def diagonalSum(self, mat: List[List[int]]) -> int:
        n = len(mat)
        primary_sum = sum(mat[i][i] for i in range(n))
        secondary_sum = sum(mat[i][n-1-i] for i in range(n))
        
        if n % 2 == 1:
            center_element = mat[n//2][n//2]
            return primary_sum + secondary_sum - center_element
        else:
            return primary_sum + secondary_sum