class Solution:
    def validSubarrays(self, nums: List[int]) -> int:
        count = 0
        stack = []
        
        for num in nums:
            while stack and num < stack[-1]:
                stack.pop()
            stack.append(num)
            count += len(stack)
        
        return count