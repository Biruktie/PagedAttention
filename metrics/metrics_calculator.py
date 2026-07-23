import math

class MetricsCalculator:

    @staticmethod
    def calculate_current_internal_fragmentation(active_requests):
        total_reserved = 0
        total_idle = 0

        for request in active_requests:
            total_reserved += request.max_length

            total_idle += (request.max_length - request.generated_tokens)
        
        if total_reserved == 0:
            return 0.0
        
        return total_idle / total_reserved
    
    
    @staticmethod
    def calculate_internal_fragmentation_ratio(requests):
        total_reserved = sum(
            request.max_length
            for request in requests
        )

        if total_reserved == 0:
            return 0.0

        total_used = sum(
            request.actual_length
            for request in requests
        )
                
        return (total_reserved - total_used) / total_reserved
    
    @staticmethod
    def calculate_paged_internal_fragmentation(requests, block_size):
        total_fragmentation = 0

        for request in requests:
            blocks_needed = math.ceil(request.actual_length / block_size)
            allocated_memory = blocks_needed * block_size

            fragmentation = allocated_memory - request.actual_length
            total_fragmentation += fragmentation

        return total_fragmentation
    
    @staticmethod
    def calculate_paged_internal_fragmentation_ratio(requests, block_size):
        total_allocated = 0

        for request in requests:
            blocks_needed = math.ceil(request.actual_length / block_size)
            total_allocated += (blocks_needed * block_size)

        if total_allocated == 0:
            return 0.0
        
        fragmentation = MetricsCalculator.calculate_paged_internal_fragmentation(requests, block_size)

        return fragmentation / total_allocated

    @staticmethod
    def calculate_external_fragmentation(allocator):
        free_memory = allocator.get_free_memory()

        largest_free_region = allocator.get_largest_free_region()

        return free_memory - largest_free_region
    
    @staticmethod
    def calculate_external_fragmentation_ratio(allocator):
        free_memory = allocator.get_free_memory()

        if free_memory == 0:
            return 0.0
        
        return MetricsCalculator.calculate_external_fragmentation(allocator) / free_memory
        
    @staticmethod
    def calculate_peak_utilization(allocator):
        return allocator.peak_allocated / allocator.total_memory

    @staticmethod
    def calculate_rejection_rate(rejected_requests, total_requests):
        if len(total_requests) == 0:
            return 0.0
        
        return len(rejected_requests) / len(total_requests)