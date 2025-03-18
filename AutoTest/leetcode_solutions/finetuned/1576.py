class Solution:
    def modifyString(self, s: str) -> str:
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        s = list(s)
        
        for i in range(len(s)):
            if s[i] == '?':
                for char in alphabet:
                    if (i == 0 or s[i - 1] != char) and (i == len(s) - 1 or s[i + 1] != char):
                        s[i] = char
                        break
        
        return ''.join(s)