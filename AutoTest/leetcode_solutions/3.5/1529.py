class Solution:
    def minFlips(self, target: str) -> int:
        count = 0
        for bit in target:
            if bit != '0':
                count += 1
        return count