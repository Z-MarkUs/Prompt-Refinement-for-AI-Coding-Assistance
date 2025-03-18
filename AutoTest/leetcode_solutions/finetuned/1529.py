class Solution:
    def minFlips(self, target: str) -> int:
        flips = int(target[0] == '1')
        for i in range(1, len(target)):
            if target[i] != target[i - 1]:
                flips += 1
        return flips