class Solution:
    def parseBoolExpr(self, expression: str) -> bool:
        stack = []
        for char in expression:
            if char == ')':
                seen = set()
                while stack[-1] != '(':
                    seen.add(stack.pop())
                stack.pop()  # pop '('
                operator = stack.pop()
                if operator == 't':
                    stack.append(True)
                elif operator == 'f':
                    stack.append(False)
                elif operator == '!':
                    stack.append(not seen.pop())
                elif operator == '&':
                    stack.append(all(seen))
                elif operator == '|':
                    stack.append(any(seen))
            elif char.isalpha() or char in ('!', '&', '|'):
                stack.append(char)
        return stack.pop()