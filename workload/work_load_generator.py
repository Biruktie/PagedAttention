import random
import math
from models.request import Request
from models.request_config import RequestConfig

class WorkLoadGenerator:

    def __init__(
        self,
        seed,
        num_requests,
        arrival_rate,
        service_rate
    ):
        self.num_requests = num_requests
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate

        self.current_arrival_time = 0
        self.random = random.Random(seed)

    def generate_arrival_time(self):
        gap = self.random.expovariate(self.arrival_rate)
        self.current_arrival_time += gap
        return self.current_arrival_time
    
    def generate_max_length(self):
        return self.random.randint(10, 512)
    
    def generate_actual_length(self, max_length):
        while True:
            sample = self.random.expovariate(
                self.service_rate
            )

            actual_length = math.ceil(sample)

            if 1 <= actual_length <= max_length:
                return actual_length
            
    def generate_request(self, request_id):
        arrival_time = self.generate_arrival_time()

        max_length = self.generate_max_length()

        actual_length = self.generate_actual_length(max_length)

        config = RequestConfig (
            request_id=request_id,
            arrival_time=arrival_time,
            max_length=max_length,
            actual_length=actual_length,
        )

        return Request(config)
    
    def generate_workload(self):
        requests = []

        for request_id in range(self.num_requests):
            requests.append(
                self.generate_request(request_id)
            )

        return requests