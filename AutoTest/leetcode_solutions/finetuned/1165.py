class Solution:
    def calculateTime(self, keyboard: str, word: str) -> int:
        char_to_index = {char: index for index, char in enumerate(keyboard)}
        sum_time = 0
        prev_index = 0
        for char in word:
            curr_index = char_to_index[char]
            sum_time += abs(curr_index - prev_index)
            prev_index = curr_index
        return sum_time