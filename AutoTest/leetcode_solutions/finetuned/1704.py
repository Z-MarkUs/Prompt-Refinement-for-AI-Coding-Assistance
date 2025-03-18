class Solution:
    def halvesAreAlike(self, s: str) -> bool:
        vowels = set(['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'])
        count_a = count_b = 0
        mid = len(s) // 2
        
        for i in range(mid):
            if s[i] in vowels:
                count_a += 1
            if s[mid + i] in vowels:
                count_b += 1
        
        return count_a == count_b