class Solution:
    def findKthBit(self, n: int, k: int) -> str:
        def generateString(n):
            if n == 1:
                return "0"
            prev = generateString(n-1)
            return prev + "1" + "".join(['1' if c == '0' else '0' for c in prev[::-1]])
        
        return generateString(n)[k-1]