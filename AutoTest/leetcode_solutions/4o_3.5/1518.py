class Solution:
    def numWaterBottles(self, numBottles: int, numExchange: int) -> int:
        total_bottles = numBottles
        empty_bottles = 0
        
        while numBottles >= numExchange:
            empty_bottles += numBottles
            numBottles = empty_bottles // numExchange
            empty_bottles %= numExchange
            total_bottles += numBottles
        
        return total_bottles