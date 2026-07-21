class CorrectnessHarness:
    def __init__(self, paged_allocator):
        self.paged_allocator = paged_allocator

    def check_no_shared_blocks(self, active_requests):
        seen_blocks = set()

        for request in active_requests:
            if request.page_table is None:
                continue

            request_blocks = set(
                request.page_table.get_all_blocks()
            )

            if seen_blocks.intersection(request_blocks):
                raise AssertionError(
                    f"Shared physical block detected "
                    f"for request {request.request_id}"
                )
            
            seen_blocks.update(request_blocks)

    def inject_double_free(self, request_id):
        allocator = self.paged_allocator.physical_allocator

        block = allocator.allocate()

        allocator.free(block)
        caught = False

        try:
            allocator.free(block)
        except ValueError:
            caught = True
            print(
                f"DOUBLE_FREE caught "
                f"for request {request_id}"
            )

        assert caught, ("Double-free failure was not caught.")

    def inject_use_after_free(self, request_id):
        allocator = self.paged_allocator.physical_allocator
        block = allocator.allocate()

        block.add_token("TEST TOKEN")

        allocator.free(block)
        caught = False

        try:
            block.read_token(0)
        except RuntimeError:
            caught = True
            print(
                f"USE-AFTER-FREE caught "
                f"for request {request_id}"
            )
        
        assert caught, ("Use-after-free failure was not caught.")

    def inject_boundary_miss(self, request_id):
        from memory.page_table import PageTable

        page_table = PageTable()
        caught = False

        try:
            page_table.get_physical_block(0)
        except KeyError:
            caught = True
            print(
                f"BOUNDARY-MISS caught "
                f"for request {request_id}"
            )

        assert caught, ("Boundary-miss failure was not caught.")

    def run_failure_injections(self, request_id):
        print("===== FAILURE INJECTION TESTS =====")

        self.inject_double_free(request_id)
        self.inject_use_after_free(request_id)
        self.inject_boundary_miss(request_id)

        print("All failure injections passed.")