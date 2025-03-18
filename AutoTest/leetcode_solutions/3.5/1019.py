class Solution:
    def nextLargerNodes(self, head: Optional[ListNode]) -> List[int]:
        stack = []
        result = []
        index = 0
        
        while head:
            result.append(0)
            while stack and stack[-1][1] < head.val:
                i, _ = stack.pop()
                result[i] = head.val
            stack.append((index, head.val))
            index += 1
            head = head.next
        
        return result