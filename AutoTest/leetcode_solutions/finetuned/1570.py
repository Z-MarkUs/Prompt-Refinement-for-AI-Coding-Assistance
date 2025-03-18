class SparseVector:
    def __init__(self, nums: List[int]):
        self.vector = {}
        for i, num in enumerate(nums):
            if num != 0:
                self.vector[i] = num

    def dotProduct(self, vec: 'SparseVector') -> int:
        result = 0
        for i in self.vector:
            if i in vec.vector:
                result += self.vector[i] * vec.vector[i]
        return result