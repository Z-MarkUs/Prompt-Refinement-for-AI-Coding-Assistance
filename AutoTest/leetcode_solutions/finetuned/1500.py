class FileSharing:

    def __init__(self, m: int):
        self.id = 1
        self.lazyStack = []
        self.allUsers = {}
        self.usersPerChunk = [[] for _ in range(m)]

    def join(self, ownedChunks: List[int]) -> int:
        new_id = self.id if not self.lazyStack else self.lazyStack.pop()
        self.allUsers[new_id] = set(ownedChunks)
        for chunk in ownedChunks:
            self.usersPerChunk[chunk].append(new_id)
        self.id += 1
        return new_id

    def leave(self, userID: int) -> None:
        for chunk in self.allUsers[userID]:
            self.usersPerChunk[chunk].remove(userID)
        self.allUsers.pop(userID)
        self.lazyStack.append(userID)

    def request(self, userID: int, chunkID: int) -> List[int]:
        return sorted(self.usersPerChunk[chunkID]) if chunkID < len(self.usersPerChunk) else []