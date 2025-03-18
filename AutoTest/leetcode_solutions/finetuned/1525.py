class Solution:
    def numSplits(self, s: str) -> int:
        left_count = [0] * len(s)
        right_count = [0] * len(s)
        
        distinct_left = set()
        distinct_right = set()
        
        for i in range(len(s)):
            distinct_left.add(s[i])
            left_count[i] = len(distinct_left)
            
            distinct_right.add(s[-i-1])
            right_count[-i-1] = len(distinct_right)
        
        count = 0
        for i in range(1, len(s)):
            if left_count[i-1] == right_count[i]:
                count += 1
        
        return count