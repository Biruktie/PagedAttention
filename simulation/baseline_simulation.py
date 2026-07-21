from models.request import RequestStatus

class BaselineSimulation:
    def __init__(self, requests, paged_allocator):
        self.requests = requests
        self.paged_allocator = paged_allocator

        self.current_time = 0.0
        self.next_request_index = 0

        self.waiting_requests = []
        self.active_requests = []

        self.finished_requests = []

    def admit_new_requests(self):

        while (
            self.next_request_index < len(self.requests)
            and self.requests[self.next_request_index].arrival_time <= self.current_time
        ):
            request = self.requests[self.next_request_index]

            self.waiting_requests.append(request)

            self.next_request_index += 1

    def schedule_waiting_requests(self):
        while self.waiting_requests:
            request = self.waiting_requests.pop(0)
            request.status = RequestStatus.RUNNING
            self.active_requests.append(request)

    def generate_tokens(self):
        for request in self.active_requests:
            if request.is_finished():
                continue

            token = (
                f"R{request.request_id}"
                f"_T{request.generated_tokens}"
            )

            success = self.paged_allocator.allocate_token(request, token)
            
            if not success:
                raise MemoryError(
                    "Baseline simulation ran out of physical blocks."
                )
    
    def finish_completed_requests(self):
        remaining_requests = []

        for request in self.active_requests:
            if request.is_finished():
                self.paged_allocator.free_request(request)
                self.finished_requests.append(request)
            else:
                remaining_requests.append(request)

        self.active_requests = (remaining_requests)

    def run(self):
        while (
            self.next_request_index < len(self.requests)
            or self.waiting_requests
            or self.active_requests
        ):
            self.admit_new_requests()

            self.schedule_waiting_requests()

            self.generate_tokens()

            self.finish_completed_requests()

            self.current_time += 1.0

        return {
            request.request_id:
            request.completion_hash

            for request
            in self.finished_requests
        }