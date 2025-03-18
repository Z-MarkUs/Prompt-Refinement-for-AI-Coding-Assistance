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
                if operator == '!':
                    stack.append('t' if 'f' in seen else 'f')
                elif operator == '&':
                    stack.append('t' if 'f' not in seen else 'f')
                elif operator == '|':
                    stack.append('t' if 't' in seen else 'f')
            elif char != ',':
                stack.append(char)
        return stack[0] == 't'