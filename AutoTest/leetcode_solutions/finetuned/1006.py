class Solution:
    def clumsy(self, n: int) -> int:
        res = 0
        ops = ['*', '/', '+', '-']
        op_index = 0
        
        while n > 0:
            if n == 1:
                res += 1
            elif n == 2:
                res += 2
            elif n == 3:
                res += 6
            else:
                res += n * (n - 1) // (n - 2) + (n - 3)
            
            n -= 4
            op = ops[op_index % 4]
            
            if op == '*':
                res *= 2
            elif op == '/':
                res = res // n
            elif op == '+':
                res += n
            elif op == '-':
                res -= n
            
            op_index += 1
        
        return res