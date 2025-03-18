class Solution:
    def numTriplets(self, nums1: List[int], nums2: List[int]) -> int:
        def count_triplets(nums1, nums2):
            count = 0
            for i in range(len(nums1)):
                for j in range(len(nums2)):
                    for k in range(j+1, len(nums2)):
                        if nums1[i] ** 2 == nums2[j] * nums2[k]:
                            count += 1
            return count
        
        return count_triplets(nums1, nums2) + count_triplets(nums2, nums1)