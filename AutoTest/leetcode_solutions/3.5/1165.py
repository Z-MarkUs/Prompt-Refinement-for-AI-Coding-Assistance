class Solution:
    def calculateTime(self, keyboard: str, word: str) -> int:
        key_map = {char: index for index, char in enumerate(keyboard)}
        total_time = key_map[word[0]]
        for i in range(1, len(word)):
            total_time += abs(key_map[word[i]] - key_map[word[i-1]])
        return total_time