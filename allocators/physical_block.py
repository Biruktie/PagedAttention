class PhysicalBlock:
    def __init__(self, block_id, block_size):
        self.block_id = block_id
        self.block_size = block_size
        self.tokens = []
        self.ref_count = 1
        self.is_allocated = False

    def is_full(self):
        return len(self.tokens) >= self.block_size
    
    def add_token(self, token):
        if self.is_full():
            raise ValueError(
                f"Physical block {self.block_id} is already full."
            )
        
        self.tokens.append(token)

    def read_token(self, index):
        if not self.is_allocated:
            raise RuntimeError(
                f"Physical block {self.block_id} "
                f"has been freed"
            )
        
        if index < 0 or index >= len(self.tokens):
            raise IndexError(
                f"Token index {index} is out of bounds."
            )
        
        return self.tokens[index]

    def clear(self):
        self.tokens.clear()

    def __str__(self):
        return (
            f"PhysicalBlock("
            f"id={self.block_id}, "
            f"tokens={self.tokens}, "
            f"ref_count={self.ref_count}"
            f")"
        )