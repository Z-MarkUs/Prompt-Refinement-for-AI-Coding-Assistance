class Solution:
    def thousandSeparator(self, n: int) -> str:
        n_str = str(n)
        if len(n_str) <= 3:
            return n_str
        result = ""
        for i in range(len(n_str)):
            if i > 0 and (len(n_str) - i) % 3 == 0:
                result += "."
            result += n_str[i]
        return result