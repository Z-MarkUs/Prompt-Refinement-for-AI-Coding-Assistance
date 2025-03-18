class Solution:
    def gridIllumination(self, n: int, lamps: List[List[int]], queries: List[List[int]]) -> List[int]:
        def turn_off_lamps(x, y):
            nonlocal lamps_set, row_count, col_count, diag1_count, diag2_count
            
            for lamp_x, lamp_y in lamps_set:
                if lamp_x == x or lamp_y == y or abs(lamp_x - x) == abs(lamp_y - y):
                    lamps_set.remove((lamp_x, lamp_y))
                    row_count[lamp_x] -= 1
                    col_count[lamp_y] -= 1
                    diag1_count[lamp_x + lamp_y] -= 1
                    diag2_count[lamp_x - lamp_y] -= 1
        
        lamps_set = set()
        row_count = defaultdict(int)
        col_count = defaultdict(int)
        diag1_count = defaultdict(int)
        diag2_count = defaultdict(int)
        
        for lamp_x, lamp_y in lamps:
            lamps_set.add((lamp_x, lamp_y))
            row_count[lamp_x] += 1
            col_count[lamp_y] += 1
            diag1_count[lamp_x + lamp_y] += 1
            diag2_count[lamp_x - lamp_y] += 1
        
        result = []
        
        for query_x, query_y in queries:
            if row_count[query_x] > 0 or col_count[query_y] > 0 or diag1_count[query_x + query_y] > 0 or diag2_count[query_x - query_y] > 0:
                result.append(1)
            else:
                result.append(0)
            
            turn_off_lamps(query_x, query_y)
        
        return result