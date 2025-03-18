from typing import List

class StreamChecker:

    def __init__(self, words: List[str]):
        self.words = set(words)
        self.stream = ""

    def query(self, letter: str) -> bool:
        self.stream += letter
        for i in range(len(self.stream), 0, -1):
            if self.stream[i:] in self.words:
                return True
        return False