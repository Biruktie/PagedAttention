from allocators.physical_block import PhysicalBlock

class PhysicalBlockAllocator:

    def __init__(self, num_blocks, block_size):
        self.free_blocks = set()
        self.allocated_blocks = set()
        self.num_blocks = num_blocks
        self.peak_allocated = 0

        for block_id in range(num_blocks):
            block = PhysicalBlock(block_id, block_size)
            self.free_blocks.add(block)

    def allocate(self):
        if not self.free_blocks:
            raise MemoryError(
                "No free physical blocks available."
            )
        
        block = self.free_blocks.pop()
        block.is_allocated = True
        self.allocated_blocks.add(block)

        self.peak_allocated = max(
            self.peak_allocated,
            len(self.allocated_blocks)
        )
        
        return block
    
    def free(self, block):
        if block not in self.allocated_blocks:
            raise ValueError(
                f"Block {block.block_id} is not allocated."
            )
        
        if block.ref_count > 1:
            raise ValueError(
                f"Cannot free shared block {block.block_id}"
                f"(ref_count={block.ref_count})."
            )
        
        self.allocated_blocks.remove(block)

        block.clear()
        block.is_allocated = False
        block.ref_count = 0

        self.free_blocks.add(block)

    def has_free_block(self):
        return bool(self.free_blocks)
    
    def get_peak_utilization(self):
        if self.num_blocks == 0:
            return 0.0
        return self.peak_allocated / self.num_blocks