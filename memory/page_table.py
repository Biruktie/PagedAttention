class PageTable:
    def __init__(self):
        self.mapping = {}

    def map_block(self, logical_block, physical_block):
        self.mapping[logical_block] = physical_block

    def get_physical_block(self, logical_block):
        
        if logical_block not in self.mapping:
            raise KeyError(
                f"Logical block {logical_block} is not mapped."
            )
        
        return self.mapping[logical_block]
    
    def get_all_blocks(self):
        return list(self.mapping.values())
    
    def has_block(self, logical_block):
        return logical_block in self.mapping
    
    def remove_block(self, logical_block):
        if logical_block not in self.mapping:
            raise KeyError(
                f"Logical block {logical_block} is not mapped."
            )
        
        del self.mapping[logical_block]

    def clear(self):
        self.mapping.clear()

    def __len__(self):
        return len(self.mapping)

    def __str__(self):
        lines = []

        for logical_block in sorted(self.mapping):
            physical_block = self.mapping[logical_block]

            lines.append(
                f"Logical Block {logical_block} "
                f"-> Physical Block {physical_block.block_id}"
            )

        return "\n".join(lines)