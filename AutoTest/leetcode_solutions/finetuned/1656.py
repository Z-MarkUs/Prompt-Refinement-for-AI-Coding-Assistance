class OrderedStream:

    def __init__(self, n: int):
        self.stream = [None] * n
        self.curr = 0

    def insert(self, idKey: int, value: str) -> List[str]:
        idKey -= 1
        self.stream[idKey] = value
        res = []
        while self.curr < len(self.stream) and self.stream[self.curr]:
            res.append(self.stream[self.curr])
            self.curr += 1
        return res