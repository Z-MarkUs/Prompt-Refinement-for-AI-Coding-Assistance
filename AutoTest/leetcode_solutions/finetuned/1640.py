class Solution:
    def canFormArray(self, arr: List[int], pieces: List[List[int]]) -> bool:
        lookup = {piece[0]: piece for piece in pieces}
        
        i = 0
        while i < len(arr):
            if arr[i] not in lookup:
                return False
            
            piece = lookup[arr[i]]
            if arr[i:i+len(piece)] != piece:
                return False
            
            i += len(piece)
        
        return True