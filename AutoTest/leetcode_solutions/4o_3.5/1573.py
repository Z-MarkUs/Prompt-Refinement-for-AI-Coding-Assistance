class Solution:
    def numWays(self, s: str) -> int:
        total_ones = s.count('1')
        if total_ones % 3 != 0:
            return 0
        
        if total_ones == 0:
            return ((len(s) - 1) * (len(s) - 2) // 2) % (10**9 + 7)
        
        target = total_ones // 3
        count1, count2 = 0, 0
        ones = 0
        
        for c in s:
            if c == '1':
                ones += 1
            if ones == target:
                count1 += 1
            elif ones == 2 * target:
                count2 += 1
        
        return (count1 * count2) % (10**9 + 7)