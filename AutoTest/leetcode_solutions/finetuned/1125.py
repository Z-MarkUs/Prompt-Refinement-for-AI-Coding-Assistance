class Solution:
    def smallestSufficientTeam(self, req_skills: List[str], people: List[List[str]]) -> List[int]:
        def bit_mask(skills):
            mask = 0
            for skill in skills:
                mask |= 1 << req_skills.index(skill)
            return mask
        
        n = len(req_skills)
        target = (1 << n) - 1
        dp = {0: []}
        
        for i, p_skills in enumerate(people):
            p_mask = bit_mask(p_skills)
            for prev_mask, prev_team in list(dp.items()):
                new_mask = prev_mask | p_mask
                if new_mask == prev_mask:
                    continue
                if new_mask not in dp or len(dp[new_mask]) > len(prev_team) + 1:
                    dp[new_mask] = prev_team + [i]
        
        return dp[target]