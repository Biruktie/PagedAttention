from models.request import RequestStatus

class SLAScheduler:
    def __init__(self, paged_allocator, max_active_requests=1):
        self.deadline_misses = 0
        self.budget_terminations = 0
        self.max_active_requests = max_active_requests

        self.paged_allocator = paged_allocator

    def select_next(self, waiting_requests):
        if not waiting_requests:
            return None

        waiting_requests.sort(
            key=lambda request: (request.priority, request.arrival_time + request.deadline if request.deadline is not None else float("inf"))
        )

        return waiting_requests.pop(0)

    def has_capacity(self):
        return self.paged_allocator.physical_allocator.has_free_block()

    def has_missed_deadline(self, request, current_time):
        if request.deadline is None:
            return False

        deadline_time = request.arrival_time + request.deadline

        return current_time > deadline_time

    def record_deadline_miss(self):
        self.deadline_misses += 1

    def should_terminate_for_budget(self, request):
        if request.token_budget is None:
            return False

        return request.generated_tokens >= request.token_budget

    def terminate_for_budget(self, request):
        if request.status in (RequestStatus.FINISHED, RequestStatus.TERMINATED):
            return False

        self.paged_allocator.free_request(request, reset_request=False)
        request.status = RequestStatus.TERMINATED

        self.budget_terminations += 1

        return True

    def get_orphaned_blocks(self):
        return len(self.paged_allocator.physical_allocator.allocated_blocks)