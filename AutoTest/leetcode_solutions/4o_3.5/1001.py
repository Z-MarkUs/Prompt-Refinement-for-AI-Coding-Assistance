class Solution:
    def gridIllumination(self, n: int, lamps: List[List[int]], queries: List[List[int]]) -> List[int]:
        def turn_off_lamp(x, y):
            nonlocal lit_rows, lit_cols, lit_diag1, lit_diag2
            
        def is_illuminated(x, y):
            nonlocal lit_rows, lit_cols, lit_diag1, lit_diag2
        
        lit_rows, lit_cols, lit_diag1, lit_diag2 = set(), set(), set(), set()
        
        for lamp in lamps:
            x, y = lamp
            lit_rows.add(x)
            lit_cols.add(y)
            lit_diag1.add(x - y)
            lit_diag2.add(x + y)
        
        result = []
        
        for query in queries:
            x, y = query
            result.append(is_illuminated(x, y))
            turn_off_lamp(x, y)
        
        return result