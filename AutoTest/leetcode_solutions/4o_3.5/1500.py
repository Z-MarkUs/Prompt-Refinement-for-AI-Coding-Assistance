from typing import List

class FileSharing:

    def __init__(self, m: int):
        pass

    def join(self, ownedChunks: List[int]) -> int:
        pass

    def leave(self, userID: int) -> None:
        pass

    def request(self, userID: int, chunkID: int) -> List[int]:
        pass
