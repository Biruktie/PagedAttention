from dataclasses import dataclass

@dataclass
class RequestConfig:
    request_id: int
    arrival_time: float
    max_length: int
    actual_length: int

    priority: int = 3
    deadline: int | None = None
    token_budget: int | None = None