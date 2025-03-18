from typing import List

class Solution:
    def gridIllumination(self, n: int, lamps: List[List[int]], queries: List[List[int]]) -> List[int]:
        def turn_off_neighbors(row, col):
            nonlocal lamps_set
            for r in range(row-1, row+2):
                for c in range(col-1, col+2):
                    if (r, c) in lamps_set:
                        lamps_set.remove((r, c))
        
        lamps_set = set((r, c) for r, c in lamps)
        row_count = [0] * n
        col_count = [0] * n
        diag_count = [0] * (2*n - 1)
        anti_diag_count = [0] * (2*n - 1)
        
        for r, c in lamps:
            row_count[r] += 1
            col_count[c] += 1
            diag_count[r+c] += 1
            anti_diag_count[r-c+n-1] += 1
        
        result = []
        for r, c in queries:
            if row_count[r] > 0 or col_count[c] > 0 or diag_count[r+c] > 0 or anti_diag_count[r-c+n-1] > 0:
                result.append(1)
                turn_off_neighbors(r, c)
                row_count[r] = 0
                col_count[c] = 0
                diag_count[r+c] = 0
                anti_diag_count[r-c+n-1] = 0
            else:
                result.append(0)
        
        return result