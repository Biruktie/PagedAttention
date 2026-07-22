class WaitForGraph:
    def __init__(self):
        self.graph = {}

    def build(self, active_requests):
        self.graph = {
            request.request_id: set()
            for request in active_requests
        }

        block_owner = {}

        for request in active_requests:
            if request.page_table is None:
                continue

            blocks = request.page_table.get_all_blocks()

            for block in blocks:
                block_owner[block.block_id] = request.request_id

        for request in active_requests:
            waiting_block = request.waiting_for_block

            if waiting_block is None:
                continue

            owner_id = block_owner.get(waiting_block.block_id)

            if owner_id is not None and owner_id != request.request_id:
                self.graph[request.request_id].add(owner_id)

        return self.graph