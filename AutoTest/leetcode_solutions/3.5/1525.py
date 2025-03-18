class Solution:
    def numSplits(self, s: str) -> int:
        left_count = {}
        right_count = {}
        good_splits = 0
        
        for char in s:
            right_count[char] = right_count.get(char, 0) + 1
        
        for char in s:
            left_count[char] = left_count.get(char, 0) + 1
            right_count[char] -= 1
            
            if right_count[char] == 0:
                del right_count[char]
            
            if len(left_count) == len(right_count):
                good_splits += 1
        
        return good_splits