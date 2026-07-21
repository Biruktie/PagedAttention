from models.request import RequestStatus

class PreemptiveSimulation:
    def __init__(self, requests, paged_allocator, preemption_manager):
        self.requests = requests
        self.paged_allocator = paged_allocator
        self.preemption_manager = preemption_manager

        self.current_time = 0.0
        self.next_request_index = 0

        self.waiting_requests = []
        self.active_requests = []

        self.finished_requests = []

        self.recompute_count = 0
        self.swap_count = 0

    def admit_new_requests(self):
        while(
            self.next_request_index < len(self.requests)
            and self.requests[self.next_request_index].arrival_time <= self.current_time
        ):
            request = self.requests[self.next_request_index]
            self.waiting_requests.append(request)
            self.next_request_index += 1

    def schedule_waiting_requests(self):
        while self.waiting_requests:
            request = self.waiting_requests.pop(0)

            if request.status == RequestStatus.SWAPPED:
                self.preemption_manager.restore(request)

            request.status = RequestStatus.RUNNING

            self.active_requests.append(request)

    def generate_tokens(self):
        for request in list(self.active_requests):
            if request.is_finished():
                continue

            token=(
                f"R{request.request_id}"
                f"_T{request.generated_tokens}"
            )

            success = self.paged_allocator.allocate_token(request, token)

            if success:
                continue

            victim = self.preemption_manager.choose_victim(self.active_requests)
            self.preempt_request(victim)

    def preempt_request(self, request):
        mode = self.preemption_manager.evict(request)

        self.active_requests.remove(request)

        if mode == "recompute":
            self.recompute_count += 1
        elif mode == "swap":
            self.swap_count += 1

        self.waiting_requests.append(request)

    def finish_completed_requests(self):
        remaining_requests = []
        for request in self.active_requests:
            if request.is_finished():
                self.paged_allocator.free_request(request)
                self.finished_requests.append(request)
            else:
                remaining_requests.append(request)

        self.active_requests = remaining_requests

    def run(self):
        while(
            self.next_request_index < len(self.requests)
            or self.waiting_requests
            or self.active_requests
        ):
            self.admit_new_requests()
            self.schedule_waiting_requests()
            self.generate_tokens()
            self.finish_completed_requests()
            self.current_time += 1.0
        return True