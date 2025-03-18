class Solution:
    def numWays(self, s: str) -> int:
        totalOnes = s.count('1')
        if totalOnes % 3 != 0:
            return 0
        
        if totalOnes == 0:
            n = len(s)
            return (n-1)*(n-2)//2
        
        k = totalOnes // 3
        onesCount = 0
        first, second, third = -1, -1, -1
        
        for i, c in enumerate(s):
            if c == '1':
                onesCount += 1
                if onesCount == k:
                    first = i
                elif onesCount == 2*k:
                    second = i
                elif onesCount == 3*k:
                    third = i
        
        x = first
        y = second - 1
        w = second
        z = third - 1
        
        return (y - x + 1) * (z - w + 1) % (10**9 + 7)