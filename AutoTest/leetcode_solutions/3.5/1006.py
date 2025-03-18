class Solution:
    def clumsy(self, n: int) -> int:
        stack = [n]
        n -= 1
        ops = 0
        
        while n > 0:
            if ops % 4 == 0:
                stack[-1] *= n
            elif ops % 4 == 1:
                stack[-1] //= n
            elif ops % 4 == 2:
                stack[-1] += n
            elif ops % 4 == 3:
                stack.append(-n)
            
            n -= 1
            ops += 1
        
        return sum(stack)