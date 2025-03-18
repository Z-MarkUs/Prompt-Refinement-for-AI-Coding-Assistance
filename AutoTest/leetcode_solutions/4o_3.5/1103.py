class Solution:
    def distributeCandies(self, candies: int, num_people: int) -> List[int]:
        distribution = [0] * num_people
        give_candies = 1
        index = 0
        
        while candies > 0:
            distribution[index] += min(candies, give_candies)
            candies -= give_candies
            give_candies += 1
            index = (index + 1) % num_people
        
        return distribution