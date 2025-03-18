class Solution:
    def thousandSeparator(self, n: int) -> str:
        return '{:,}'.format(n).replace(',', '.')