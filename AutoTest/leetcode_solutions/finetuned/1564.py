class Solution:
    def maxCoins(self, piles: List[int]) -> int:
        piles.sort(reverse=True)
        total_coins = 0
        for i in range(1, len(piles), 2):
            total_coins += piles[i]
        return total_coins