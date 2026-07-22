class DeadlockManager:
    def __init__(self, paged_allocator):
        self.paged_allocator = paged_allocator
        self.deadlocks_detected = 0

        self.recoveries = 0

    def choose_victim(self, cycle, active_requests):
        requests_by_id = {
            request.request_id: request
            for request in active_requests
        }

        cycle_requests = [
            requests_by_id[request_id]
            for request_id in cycle
        ]

        victim = max(
            cycle_requests,
            key=lambda request: (
                self._block_count(request),
                -request.generated_tokens
            )
        )

        return victim

    def _block_count(self, request):
        if request.page_table is None:
            return 0

        return len(request.page_table.get_all_blocks())

    def recover_deadlock(self, cycle, active_requests):
        self.deadlocks_detected += 1
        victim = self.choose_victim(cycle, active_requests)

        if victim.page_table is not None:
            self.paged_allocator.free_request(victim)

        victim.waiting_for_block = None

        active_requests.remove(victim)
        self.recoveries += 1
        return victim