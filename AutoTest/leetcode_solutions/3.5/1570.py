from typing import List

class SparseVector:
    def __init__(self, nums: List[int]):
        self.nonzeros = {}
        for i, num in enumerate(nums):
            if num != 0:
                self.nonzeros[i] = num

    def dotProduct(self, vec: 'SparseVector') -> int:
        result = 0
        for i, num in self.nonzeros.items():
            if i in vec.nonzeros:
                result += num * vec.nonzeros[i]
        return result