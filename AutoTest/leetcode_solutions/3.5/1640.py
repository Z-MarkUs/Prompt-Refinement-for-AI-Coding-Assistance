class Solution:
    def canFormArray(self, arr: List[int], pieces: List[List[int]]) -> bool:
        arr_str = ''.join(map(str, arr))
        pieces_str = [''.join(map(str, piece)) for piece in pieces]
        
        while arr_str:
            found = False
            for piece_str in pieces_str:
                if arr_str.startswith(piece_str):
                    arr_str = arr_str[len(piece_str):]
                    found = True
                    break
            if not found:
                return False
        
        return True