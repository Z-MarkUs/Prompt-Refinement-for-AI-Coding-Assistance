class Solution:
    def removeVowels(self, s: str) -> str:
        vowels = set("aeiouAEIOU")
        result = ""
        for char in s:
            if char not in vowels:
                result += char
        return result