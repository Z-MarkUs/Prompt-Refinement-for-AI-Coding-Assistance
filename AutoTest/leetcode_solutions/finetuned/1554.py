class Solution:
    def differByOne(self, dict: List[str]) -> bool:
        def generate_variants(word):
            variants = set()
            for i in range(len(word)):
                variant = word[:i] + '*' + word[i+1:]
                variants.add(variant)
            return variants
        
        variants_map = {}
        for word in dict:
            variants = generate_variants(word)
            for variant in variants:
                if variant in variants_map:
                    if variants_map[variant] != word:
                        return True
                else:
                    variants_map[variant] = word
        
        return False