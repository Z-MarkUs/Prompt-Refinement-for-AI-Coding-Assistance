```python
from typing import List

class Solution:
    def indexPairs(self, text: str, words: List[str]) -> List[List[int]:
        def is_prefix(s, prefix):
            if len(s) < len(prefix):
                return False
            return s[:len(prefix)] == prefix

        def find_matches(start, s):
            matches = []
            for word in words:
                if is_prefix(s[start:], word):
                    matches.append([start, start + len(word) - 1])
            return matches

        result = []
        for i in range(len(text)):
            matches = find_matches(i, text)
            for match in matches:
                result.append(match)

        return sorted(result)
```