from metrics.metrics_calculator import MetricsCalculator

class NaiveSimulation:

    def __init__(self, requests, naive_allocator):
        self.requests = requests
        self.naive_allocator = naive_allocator

        self.current_time = 0.0
        self.next_request_index = 0

        self.active_requests = []
        self.finished_requests = []
        self.rejected_requests = []

        self.internal_fragmentation_history = []
        self.external_fragmentation_history =  []
        self.memory_map_history = []

    def admit_new_requests(self):
        while (
            self.next_request_index < len(self.requests)
            and self.requests[self.next_request_index].arrival_time <= self.current_time
        ):
            request = self.requests[self.next_request_index]

            success = self.naive_allocator.allocate(request)

            if success:
                self.active_requests.append(request)
            else:
                self.rejected_requests.append(request)

            self.next_request_index += 1

    def generate_tokens(self):
        for request in self.active_requests:
            if request.is_finished():
                continue
            token = (
                f"R{request.request_id}"
                f"_T{request.generated_tokens}"
            )

            request.record_token_generated(token)

    def finish_completed_requests(self):
        remaining_requests = []

        for request in self.active_requests:
            if request.is_finished():
                self.naive_allocator.free(request)
                self.finished_requests.append(request)
            else:
                remaining_requests.append(request)

        self.active_requests = remaining_requests

    def record_metrics(self):
        internal_fragmentation = MetricsCalculator.calculate_current_internal_fragmentation(active_requests=self.active_requests)

        if (self.next_request_index < len(self.requests)):
            next_request = self.requests[self.next_request_index]

            external_fragmentation_ratio = self.naive_allocator.get_external_fragmentation_ratio(next_request.max_length * 2)

            self.naive_allocator.peak_external_fragmentation = max(
                self.naive_allocator.peak_external_fragmentation,
                external_fragmentation_ratio
            )
        else:
            external_fragmentation_ratio = 0.0
        
        self.internal_fragmentation_history.append(internal_fragmentation)
        self.external_fragmentation_history.append(external_fragmentation_ratio)

        self.avg_internal_fragmentation = (
            sum(self.internal_fragmentation_history) / len(self.internal_fragmentation_history) if self.internal_fragmentation_history else 0.0
            )
        self.avg_external_fragmentation = (
            sum(self.external_fragmentation_history) / len(self.external_fragmentation_history) if self.external_fragmentation_history else 0.0)

        memory_map = self.naive_allocator.get_memory_map()

        self.memory_map_history.append(memory_map)

        print(
            f"Time {self.current_time:.1f} | "
            f"Memory: {memory_map} | "
            f"IF: {internal_fragmentation * 100:.2f}% | "
            f"EF: {external_fragmentation_ratio * 100:.2f}%"

        )

        print()

    def get_metrics(self):
        return {
            "finished": len(self.finished_requests),
            "rejected": len(self.rejected_requests),
            "rejection_rate": MetricsCalculator.calculate_rejection_rate(rejected_requests=self.rejected_requests, total_requests=self.requests),
            "peak_utilization": MetricsCalculator.calculate_peak_utilization(self.naive_allocator),
            "avg_internal_fragmentaton": f"{self.avg_internal_fragmentation * 100:.2f}%",
            "avg_external_fragmentation": f"{self.avg_external_fragmentation * 100:.2f}%"
        }

    def run(self):
        while (
            self.next_request_index < len(self.requests)
            or self.active_requests
        ):
            self.admit_new_requests()
            self.generate_tokens()
            self.record_metrics()
            self.finish_completed_requests()
            self.current_time += 1.0