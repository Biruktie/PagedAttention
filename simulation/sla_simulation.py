from models.request import RequestStatus


class SLASimulation:

    def __init__(
        self,
        requests,
        paged_allocator,
        scheduler,
        preemption_manager
    ):

        self.requests = requests
        self.paged_allocator = paged_allocator
        self.scheduler = scheduler
        self.preemption_manager = preemption_manager

        self.current_time = 0.0
        self.next_request_index = 0

        self.waiting_requests = []
        self.active_requests = []

        self.finished_requests = []
        self.terminated_requests = []

        self.recompute_count = 0
        self.swap_count = 0

    def admit_new_requests(self):

        while (
            self.next_request_index
            < len(self.requests)

            and self.requests[
                self.next_request_index
            ].arrival_time
            <= self.current_time
        ):

            request = self.requests[self.next_request_index]
            self.waiting_requests.append(request)
            self.next_request_index += 1

    def check_deadlines(self):

        for request in self.waiting_requests:
            if request.deadline_missed:
                continue

            if self.scheduler.has_missed_deadline(request, self.current_time):
                request.deadline_missed = True

                self.scheduler.record_deadline_miss()

                print(
                f"Deadline missed: "
                f"Request {request.request_id}"
            )

    def schedule_waiting_requests(self):

        while (
            len(self.active_requests) < self.scheduler.max_active_requests 
            and self.waiting_requests
            ):

            request = self.scheduler.select_next(self.waiting_requests)

            if request is None:
                break

            if request.status == RequestStatus.SWAPPED:
                self.preemption_manager.restore(request)

            request.status = RequestStatus.RUNNING

            self.active_requests.append(request)

    def generate_tokens(self):

        remaining_requests = []

        for request in self.active_requests:

            if request.status != RequestStatus.RUNNING:
                continue

            token = (
                f"R{request.request_id}"
                f"_T{request.generated_tokens}"
            )

            success =self.paged_allocator.allocate_token(request, token)

            if not success:
                victim = self.preemption_manager.choose_victim(self.active_requests)
                if victim is not None:
                    mode = self.preemption_manager.evict(victim)

                    if mode == "recompute":
                        self.recompute_count += 1
                    elif mode == "swap":
                        self.swap_count += 1

                    self.active_requests.remove(victim)
                    self.waiting_requests.append(victim)

                remaining_requests.append(request)

                continue

            if self.scheduler.should_terminate_for_budget(request):
                self.scheduler.terminate_for_budget(request)
                self.terminated_requests.append(request)
                continue

            if request.is_finished():
                self.paged_allocator.free_request(request)
                self.finished_requests.append(request)
                continue

            remaining_requests.append(request)

        self.active_requests = remaining_requests

    def get_metrics(self):

        orphaned_blocks = self.scheduler.get_orphaned_blocks()


        return {
            "total_requests": len(self.requests),
            "finished": len(self.finished_requests),
            "budget_terminations": self.scheduler.budget_terminations,
            "deadline_misses": self.scheduler.deadline_misses,
            "orphaned_blocks": orphaned_blocks,
            "recompute_evictions": self.recompute_count,
            "swap_evictions": self.swap_count
        }

    def run(self):
        while (
            self.next_request_index < len(self.requests)
            or self.waiting_requests
            or self.active_requests
        ):
            self.admit_new_requests()
            self.schedule_waiting_requests()
            self.check_deadlines()
            self.generate_tokens()
            self.current_time += 1.0

        return self.get_metrics()