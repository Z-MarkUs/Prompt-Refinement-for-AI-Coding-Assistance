class Solution:
    def frequencySort(self, nums: List[int]) -> List[int]:
        freq_map = {}
        for num in nums:
            if num in freq_map:
                freq_map[num] += 1
            else:
                freq_map[num] = 1
        
        nums.sort(key=lambda x: (freq_map[x], -x))
        
        return nums