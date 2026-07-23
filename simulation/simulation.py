from metrics.metrics_calculator import MetricsCalculator

class Simulation:
    def __init__(self, requests, paged_allocator, harness):
        self.requests = requests
        self.paged_allocator = paged_allocator
        self.harness = harness

        self.current_time = 0.0
        self.next_request_index = 0

        self.active_requests = []
        self.finished_requests = []

    def admit_new_requests(self):
        while(
            self.next_request_index < len(self.requests)
            and self.requests[
                self.next_request_index
            ].arrival_time <= self.current_time
        ):
            request = self.requests[self.next_request_index]

            self.active_requests.append(request)

            self.next_request_index += 1

    def generate_tokens(self):
        successful = 0
        blocked = 0

        for request in self.active_requests:
            token = (
                f"R{request.request_id}"
                f"_T{request.generated_tokens}"
            )
            success = self.paged_allocator.allocate_token(request, token)

            if success: 
                successful += 1
            else:
                blocked += 1

        if blocked > 0:
            print(
                f"Successful: {successful}, "
                f"Blocked: {blocked}, "
                f"Free blocks: "
                f"{len(self.paged_allocator.physical_allocator.free_blocks)}"
            )
    def finish_completed_requests(self):
        remaining_requests = []

        for request in self.active_requests:
            if request.is_finished():
                self.paged_allocator.free_request(request)
                self.finished_requests.append(request)
            else:
                remaining_requests.append(request)
        
        self.active_requests = remaining_requests

    def get_metrics(self):
        return {
            "finished": len(self.finished_requests),
            "rejected": 0,
            "rejection_rate": 0.0,
            "peak_utilization": self.paged_allocator.physical_allocator.get_peak_utilization(),
            "external_fragmentation": 0,
            "internal_fragmentation": MetricsCalculator.calculate_paged_internal_fragmentation(self.finished_requests, self.paged_allocator.block_size),
            "internal_fragmentation_ratio": MetricsCalculator.calculate_paged_internal_fragmentation_ratio(self.finished_requests, self.paged_allocator.block_size)
        }
            
    def run(self):
        while(
            self.next_request_index < len(self.requests)
            or self.active_requests
        ):
            self.admit_new_requests()

            self.generate_tokens()

            self.harness.check_no_shared_blocks(self.active_requests)

            self.finish_completed_requests()

            self.current_time += 1.0