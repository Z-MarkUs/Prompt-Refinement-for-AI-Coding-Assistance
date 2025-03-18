class Solution:
    def getWinner(self, arr: List[int], k: int) -> int:
        n = len(arr)
        if k >= n - 1:
            return max(arr)
        
        consecutive_wins = 0
        current_winner = arr[0]
        
        for i in range(1, n):
            if arr[i] > current_winner:
                current_winner = arr[i]
                consecutive_wins = 1
            else:
                consecutive_wins += 1
            
            if consecutive_wins == k:
                return current_winner
        
        return current_winner