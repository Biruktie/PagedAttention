import random

from workload.work_load_generator import WorkLoadGenerator
from models.request_config import RequestConfig

class SLAWorkLoadGenerator(WorkLoadGenerator):
    def __init__(
        self,
        seed,
        num_requests,
        arrival_rate,
        service_rate,
        min_deadline=1,
        max_deadline=20,
        min_token_budget=10,
        max_token_budget=100
    ):
        super().__init__(
            seed=seed,
            num_requests=num_requests,
            arrival_rate=arrival_rate,
            service_rate=service_rate
        )

        self.min_deadline = min_deadline
        self.max_deadline = max_deadline

        self.min_token_budget = min_token_budget

        self.max_token_budget =  max_token_budget

    def generate_workload(self):
        requests = []
        current_time = 0.0

        for request_id in range(self.num_requests):
            interarrival_time = self.random.expovariate(self.arrival_rate)
            current_time += interarrival_time

            max_length = self.random.randint(10, 512)
            actual_length = self.random.randint(1, max_length)
            priority = self.random.randint(1, 3)
            deadline = self.random.randint(self.min_deadline, self.max_deadline)
            token_budget = self.random.randint(self.min_token_budget, self.max_token_budget)

            requests.append(
                RequestConfig(
                    request_id=request_id,
                    arrival_time=current_time,
                    max_length=max_length,
                    actual_length=actual_length,
                    priority=priority,
                    deadline=deadline,
                    token_budget=token_budget
                )
            )

            return [
                self.generate_workload(config)
                for config in requests
            ]