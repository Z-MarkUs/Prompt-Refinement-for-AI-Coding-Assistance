class Solution:
    def minInsertions(self, s: str) -> int:
        stack = []
        insertions = 0
        i = 0
        
        while i < len(s):
            if s[i] == '(':
                stack.append('(')
                i += 1
            else:
                if i + 1 < len(s) and s[i + 1] == ')':
                    if stack:
                        stack.pop()
                    else:
                        insertions += 1
                    i += 2
                else:
                    if stack:
                        stack.pop()
                        insertions += 1
                    else:
                        insertions += 2
                    i += 1
        
        insertions += len(stack) * 2
        
        return insertions