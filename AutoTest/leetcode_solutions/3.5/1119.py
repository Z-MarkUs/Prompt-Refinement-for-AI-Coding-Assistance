class Solution:
    def removeVowels(self, s: str) -> str:
        vowels = set('aeiou')
        return ''.join(char for char in s if char not in vowels)