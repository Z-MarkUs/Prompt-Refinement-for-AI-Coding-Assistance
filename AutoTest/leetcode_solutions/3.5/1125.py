from typing import List

class Solution:
    def smallestSufficientTeam(self, req_skills: List[str], people: List[List[str]]) -> List[int]:
        def dfs(need, i):
            if i == len(people):
                return [] if need else [[]]
            if (i, need) in memo:
                return memo[(i, need)]
            res = dfs(need, i + 1)
            for skill in people[i]:
                need.discard(skill)
            if not need:
                res = [res, [i]]
            else:
                for subset in dfs(need, i + 1):
                    res = min(res, [i] + subset, key=len)
            for skill in people[i]:
                need.add(skill)
            memo[(i, need)] = res
            return res
        
        memo = {}
        people = [set(person) for person in people]
        need = set(req_skills)
        return dfs(need, 0)