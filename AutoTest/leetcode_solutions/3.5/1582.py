from typing import List

class Solution:
    def numSpecial(self, mat: List[List[int]]) -> int:
        count = 0
        rows = [0] * len(mat)
        cols = [0] * len(mat[0])
        
        for i in range(len(mat)):
            for j in range(len(mat[0])):
                rows[i] += mat[i][j]
                cols[j] += mat[i][j]
        
        for i in range(len(mat)):
            for j in range(len(mat[0])):
                if mat[i][j] == 1 and rows[i] == 1 and cols[j] == 1:
                    count += 1
        
        return count