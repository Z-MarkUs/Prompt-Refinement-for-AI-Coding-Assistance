class Solution:
    def relativeSortArray(self, arr1: List[int], arr2: List[int]) -> List[int]:
        count = {}
        result = []
        
        for num in arr1:
            count[num] = count.get(num, 0) + 1
        
        for num in arr2:
            if num in count:
                result.extend([num] * count[num])
                del count[num]
        
        remaining = []
        for num, freq in count.items():
            remaining.extend([num] * freq)
        
        remaining.sort()
        
        return result + remaining