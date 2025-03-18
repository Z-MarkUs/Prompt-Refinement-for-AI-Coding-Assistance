class Solution:
    def digitsCount(self, d: int, low: int, high: int) -> int:
        count = 0
        for num in range(low, high+1):
            count += str(num).count(str(d))
        return count