class PagedAllocator:

    def __init__(self, physical_allocator, block_size):
        self.physical_allocator = physical_allocator
        self.block_size = block_size

        self._is_power_of_two = (block_size & (block_size -1)) == 0
        if self._is_power_of_two:
            self._shift_amount = block_size.bit_length() - 1

    def _get_logical_block(self, token_index):
        if self._is_power_of_two:
            return token_index >> self._shift_amount
        return token_index // self.block_size

    def allocate_logical_block(self, request, logical_block):
        physical_block = self.physical_allocator.allocate()
        request.page_table.map_block(logical_block, physical_block)

        request.current_physical_block = physical_block

        return physical_block
    
    def allocate_token(self, request, token):
        if request.page_table is None:
            request.initialize_page_table()

        physical_block = request.current_physical_block
        
        if (physical_block is None or physical_block.is_full()):
            token_index = request.generated_tokens
            logical_block = self._get_logical_block(token_index)

            if request.page_table.has_block(logical_block):
                physical_block = request.page_table.get_physical_block(logical_block)
            else:
                if not self.physical_allocator.has_free_block():
                    return False

                physical_block = self.allocate_logical_block(request, logical_block)

            request.current_physical_block = physical_block
       
        physical_block.add_token(token)
        request.record_token_generated(token)

        return True

    def free_request(self, request, reset_request=True):
        if request.page_table is None:
            raise ValueError(
                "Cannot free a request that has no page table yet."
            )
        
        blocks = request.page_table.get_all_blocks()

        for block in blocks:
            self.physical_allocator.free(block)

        assert(
            all(
                block in self.physical_allocator.free_blocks
                for block in blocks
            )
        ), (
            f"Physical block leak detected "
            f"for request {request.request_id}."
        )
        
        assert (
            len(self.physical_allocator.allocated_blocks)
            + len(self.physical_allocator.free_blocks)
            == self.physical_allocator.num_blocks
        ), (
            f"Physical block count mismatch after "
            f"freeing request {request.request_id}."
        )

        request.page_table.clear()

        request.current_physical_block = None

        if reset_request:
            request.reset()

    def restore_request(self, request):

        if request.page_table is None:
            request.initialize_page_table()

        request.current_physical_block = None

        for token_index, token in enumerate(request.tokens):

            logical_block = self._get_logical_block(
                token_index
            )

            if not request.page_table.has_block(
                logical_block
            ):

                if not self.physical_allocator.has_free_block():
                    return False

                physical_block = (
                    self.allocate_logical_block(
                        request,
                        logical_block
                    )
                )

            else:

                physical_block = (
                    request.page_table
                    .get_physical_block(
                        logical_block
                    )
                )

            physical_block.add_token(token)

            request.current_physical_block = (
                physical_block
            )

        return True