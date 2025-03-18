class Solution:
    def canConvert(self, str1: str, str2: str) -> bool:
        if str1 == str2:
            return True
        
        mapping = {}
        for s1, s2 in zip(str1, str2):
            if s1 in mapping and mapping[s1] != s2:
                return False
            mapping[s1] = s2
        
        return len(set(str2)) < 26