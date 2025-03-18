class Solution:
    def maxSatisfied(self, customers: List[int], grumpy: List[int], minutes: int) -> int:
        n = len(customers)
        satisfied = 0
        for i in range(n):
            if grumpy[i] == 0:
                satisfied += customers[i]
        
        max_additional = 0
        additional = 0
        for i in range(minutes):
            if grumpy[i] == 1:
                additional += customers[i]
        
        max_additional = additional
        for i in range(minutes, n):
            if grumpy[i] == 1:
                additional += customers[i]
            if grumpy[i - minutes] == 1:
                additional -= customers[i - minutes]
            max_additional = max(max_additional, additional)
        
        return satisfied + max_additional