class Solution:
    def removeOuterParentheses(self, s: str) -> str:
        result = ""
        count = 0
        
        for char in s:
            if char == "(":
                count += 1
                if count > 1:
                    result += char
            else:
                count -= 1
                if count > 0:
                    result += char
        
        return result