class Solution:
    def confusingNumberII(self, n: int) -> int:
        def is_confusing(num):
            rotated = ""
            for char in str(num)[::-1]:
                if char == "0" or char == "1" or char == "8":
                    rotated += char
                elif char == "6":
                    rotated += "9"
                elif char == "9":
                    rotated += "6"
                else:
                    return False
            return rotated != str(num)
        
        def dfs(num, rotated, count):
            if num > n:
                return
            if is_confusing(num):
                count += 1
            for x in [0, 1, 6, 8, 9]:
                dfs(num * 10 + x, x + rotated * 10, count)
        
        count = 0
        for x in [1, 6, 8, 9]:
            dfs(x, x, count)
        
        return count