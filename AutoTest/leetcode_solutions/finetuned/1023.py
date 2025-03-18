class Solution:
    def camelMatch(self, queries: List[str], pattern: str) -> List[bool]:
        def is_match(query: str, pattern: str) -> bool:
            i, j = 0, 0
            while i < len(query) and j < len(pattern):
                if query[i] == pattern[j]:
                    i += 1
                    j += 1
                elif query[i].islower():
                    i += 1
                else:
                    return False
            if j == len(pattern):
                return all(char.islower() for char in query[i:])
            return False
        
        return [is_match(query, pattern) for query in queries]