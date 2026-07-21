from enum import Enum
import hashlib
from memory.page_table import PageTable

class RequestStatus(Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    SWAPPED = "SWAPPED"
    FINISHED = "FINISHED"
    REJECTED = "REJECTED"
    TERMINATED = "TERMINATED"

class Request:
    def __init__(
        self,
        config
    ):
        self.request_id = config.request_id
        self.max_length = config.max_length
        self.actual_length = config.actual_length
        self.arrival_time = config.arrival_time

        self.priority = config.priority
        self.deadline = config.deadline
        self.deadline_missed = False
        self.token_budget = config.token_budget

        self.tokens = []
        self.generated_tokens = 0
        self.completion_hash = None

        self.status = RequestStatus.WAITING
        self.page_table = None
        self.current_physical_block = None

    def initialize_page_table(self):
        if self.page_table is None:
            self.page_table = PageTable()

    def record_token_generated(self, token):

        if self.status == RequestStatus.FINISHED:
            return
        
        self.tokens.append(token)
        self.generated_tokens += 1
        
        if self.generated_tokens >= self.actual_length:
            self.status = RequestStatus.FINISHED
            self.completion_hash = self.compute_token_hash()

    def compute_token_hash(self):
        token_bytes = "".join(self.tokens).encode("utf-8")

        return hashlib.sha3_256(token_bytes).hexdigest()

    def is_finished(self):
        return self.status == RequestStatus.FINISHED
    
    def reset(self):
        self.generated_tokens = 0
        self.tokens.clear()
        self.status = RequestStatus.WAITING
        self.current_physical_block = None
        self.completion_hash = None

    def mark_swapped(self):
        self.status = RequestStatus.SWAPPED
        self.current_physical_block = None