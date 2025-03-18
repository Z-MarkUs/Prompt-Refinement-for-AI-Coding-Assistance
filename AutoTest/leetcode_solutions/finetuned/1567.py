class Solution:
    def getMaxLen(self, nums: List[int]) -> int:
        pos = 0
        neg = 0
        max_len = 0
        
        for num in nums:
            if num == 0:
                pos = 0
                neg = 0
            elif num > 0:
                pos += 1
                if neg > 0:
                    neg += 1
            else:
                temp = pos
                pos = neg + 1
                neg = temp + 1 if temp > 0 else 0
                
            max_len = max(max_len, pos)
        
        return max_len