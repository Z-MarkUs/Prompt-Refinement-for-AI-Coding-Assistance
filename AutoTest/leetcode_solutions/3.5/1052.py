from typing import List

class Solution:
    def maxSatisfied(self, customers: List[int], grumpy: List[int], minutes: int) -> int:
        satisfied = 0
        max_additional_customers = 0
        additional_customers = 0
        start = 0
        
        for i in range(len(customers)):
            if grumpy[i] == 0:
                satisfied += customers[i]
            else:
                additional_customers += customers[i]
            
            if i - start >= minutes:
                if grumpy[start] == 1:
                    additional_customers -= customers[start]
                start += 1
            
            max_additional_customers = max(max_additional_customers, additional_customers)
        
        return satisfied + max_additional_customers