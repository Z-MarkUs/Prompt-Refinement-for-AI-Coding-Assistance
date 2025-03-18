class Solution:
    def specialArray(self, nums: List[int]) -> List[int]:
        even_nums = [nums[i] for i in range(len(nums)) if i % 2 == 0]
        odd_nums = [nums[i] for i in range(len(nums)) if i % 2 != 0]
        
        even_nums.sort()
        odd_nums.sort(reverse=True)
        
        result = []
        even_index = 0
        odd_index = 0
        
        for i in range(len(nums)):
            if i % 2 == 0:
                result.append(even_nums[even_index])
                even_index += 1
            else:
                result.append(odd_nums[odd_index])
                odd_index += 1
        
        return result