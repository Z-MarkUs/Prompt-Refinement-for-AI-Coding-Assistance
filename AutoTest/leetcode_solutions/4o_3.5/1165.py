class Solution:
    def calculateTime(self, keyboard: str, word: str) -> int:
        char_to_index = {char: index for index, char in enumerate(keyboard)}
        total_time = 0
        current_position = 0
        
        for char in word:
            next_position = char_to_index[char]
            total_time += abs(next_position - current_position)
            current_position = next_position
        
        return total_time