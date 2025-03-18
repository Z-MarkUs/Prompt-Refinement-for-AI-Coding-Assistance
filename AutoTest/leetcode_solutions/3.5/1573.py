class Solution:
    def numWays(self, s: str) -> int:
        ones_count = s.count('1')
        if ones_count % 3 != 0:
            return 0
        
        if ones_count == 0:
            return ((len(s) - 1) * (len(s) - 2) // 2) % (10**9 + 7)
        
        ones_per_part = ones_count // 3
        count1, count2 = 0, 0
        prefix_zeros = 0
        suffix_zeros = 0
        
        for char in s:
            if char == '1':
                count1 += 1
            if count1 == ones_per_part:
                prefix_zeros += 1
            if char == '1' and count1 == ones_per_part:
                break
        
        for char in s[::-1]:
            if char == '1':
                count2 += 1
            if count2 == ones_per_part:
                suffix_zeros += 1
            if char == '1' and count2 == ones_per_part:
                break
        
        return (prefix_zeros * suffix_zeros) % (10**9 + 7)