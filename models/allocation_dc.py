from dataclasses import dataclass

@dataclass
class Allocation:
    request_id: int
    start: int
    length: int