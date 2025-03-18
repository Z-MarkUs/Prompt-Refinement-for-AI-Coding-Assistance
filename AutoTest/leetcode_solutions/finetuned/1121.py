class Solution:
    def canDivideIntoSubsequences(self, nums: List[int], k: int) -> bool:
        freq = {}
        tail = {}
        
        for num in nums:
            if num not in freq:
                freq[num] = 0
            freq[num] += 1
            tail[num] = 0
        
        for num in nums:
            if freq[num] == 0:
                continue
            
            if tail.get(num - 1, 0) > 0:
                tail[num - 1] -= 1
                freq[num] -= 1
                tail[num] = tail.get(num, 0) + 1
            else:
                for i in range(k):
                    if freq.get(num + i, 0) == 0:
                        return False
                    freq[num + i] -= 1
                tail[num + k - 1] = tail.get(num + k - 1, 0) + 1
        
        return True