```python
from typing import List

class StreamChecker:

    def __init__(self, words: List[str]):
        self.trie = {}
        self.stream = ""
        
        for word in words:
            node = self.trie
            for char in word[::-1]:
                if char not in node:
                    node[char] = {}
                node = node[char]
            node['$'] = True

    def query(self, letter: str) -> bool:
        self.stream = letter + self.stream
        node = self.trie
        for char in self.stream:
            if char in node:
                node = node[char]
                if '$' in node:
                    return True
            else:
                break
        return False
```