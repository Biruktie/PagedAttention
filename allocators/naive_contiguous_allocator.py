from models.allocation_dc import Allocation

class NaiveContiguousAllocator:

    def __init__(self, total_memory):
        self.total_memory = total_memory
        self.memory = [None] * total_memory
        self.allocations = {}

        self.rejected_requests = 0
        self.peak_allocated = 0
        self.peak_external_fragmentation = 0

    def find_free_region(self, required_length):
        free_start = None
        free_length = 0

        for index in range(self.total_memory):
            if self.memory[index] is None:

                if free_start is None:
                    free_start = index
                
                free_length += 1

                if free_length >= required_length:
                    return free_start
                
            else:
                free_start = None
                free_length = 0

        return None
    
    def allocate(self, request):
        required_length = request.max_length
        start = self.find_free_region(required_length)

        if start is None:
            self.rejected_requests += 1
            return False
        
        for index in range(start, start + required_length):
            self.memory[index] = request.request_id
        
        self.allocations[request.request_id] = Allocation(
            request_id=request.request_id,
            start=start,
            length=required_length
        )

        current_allocated = sum(
            1 for slot in self.memory
            if slot is not None
        )

        self.peak_allocated = max(
            self.peak_allocated,
            current_allocated
        )

        return True
    
    def free(self, request):
        request_id = request.request_id

        if request_id not in self.allocations:
            raise ValueError(
                "Cannot free a request that is not allocated."
            )
        
        allocation = self.allocations[request_id]

        for index in range(allocation.start, allocation.start + allocation.length):
            self.memory[index] = None

        del self.allocations[request_id]

    def get_free_memory(self):
        return sum(
            1
            for slot in self.memory
            if slot is None
        )

    def get_largest_free_region(self):
        current_length = 0
        largest_length = 0

        for slot in self.memory:
            if slot is None:
                current_length += 1

                largest_length = max(largest_length, current_length)

            else:
                current_length = 0

        return largest_length
    
    def get_external_fragmentation(self, required_length):
        external_fragmentation = 0
        current_free_length = 0

        for slot in self.memory:
            if slot is None:
                current_free_length += 1
            else:
                if ( 0 < current_free_length < required_length):
                    external_fragmentation += current_free_length
                
                current_free_length = 0

        if ( 0 < current_free_length < required_length):
            external_fragmentation += current_free_length

        return external_fragmentation
    
    def get_external_fragmentation_ratio(self, required_length):
        free_memory = self.get_free_memory()

        if free_memory == 0:
            return 0.0
        
        external_fragmentation = self.get_external_fragmentation(required_length)

        return external_fragmentation / free_memory
    
    def get_peak_external_fragmentation(self):
        return self.peak_external_fragmentation
    
    def get_memory_map(self):
        if not self.allocations:
            return "Empty"
        
        regions = []

        for request_id, allocation in sorted(self.allocations.items(), key=lambda item: item[1].start):
            end = (allocation.start + allocation.length)
            regions.append(
                f"R{request_id}"
                f"[{allocation.start}:{end}]"
            )

        return " | ".join(regions)
    
    def __str__(self):
        return str(self.memory)