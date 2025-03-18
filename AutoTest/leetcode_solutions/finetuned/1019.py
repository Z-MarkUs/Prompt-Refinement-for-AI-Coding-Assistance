class Solution:
    def nextLargerNodes(self, head: Optional[ListNode]) -> List[int]:
        stack = []
        result = []
        index = 0
        
        while head:
            result.append(0)
            while stack and stack[-1][0] < head.val:
                val, i = stack.pop()
                result[i] = head.val
            stack.append((head.val, index))
            index += 1
            head = head.next
        
        return result