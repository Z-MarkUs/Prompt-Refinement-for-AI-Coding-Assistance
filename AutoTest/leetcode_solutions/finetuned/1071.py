class Solution:
    def gcdOfStrings(self, str1: str, str2: str) -> str:
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        len1, len2 = len(str1), len(str2)
        divisor_len = gcd(len1, len2)
        divisor_str = str1[:divisor_len]
        
        if str1 == divisor_str * (len1 // divisor_len) and str2 == divisor_str * (len2 // divisor_len):
            return divisor_str
        else:
            return ""