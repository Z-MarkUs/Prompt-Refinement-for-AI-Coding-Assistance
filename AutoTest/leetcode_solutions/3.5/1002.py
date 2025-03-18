from typing import List

class Solution:
    def commonChars(self, words: List[str]) -> List[str]:
        common = []
        for char in set(words[0]):
            count = min(word.count(char) for word in words)
            common.extend([char]*count)
        return common