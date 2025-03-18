class Solution:
    def indexPairs(self, text: str, words: List[str]) -> List[List[int]]:
        def is_prefix(s, word):
            if len(s) < len(word):
                return False
            return s[:len(word)] == word

        def find_matches(start):
            matches = []
            for word in words:
                if is_prefix(text[start:], word):
                    matches.append([start, start + len(word) - 1])
            return matches

        result = []
        for i in range(len(text)):
            matches = find_matches(i)
            result.extend(matches)

        result.sort(key=lambda x: (x[0], x[1]))
        return result