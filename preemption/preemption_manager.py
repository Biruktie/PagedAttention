from preemption.swap_storage import SwapStorage
from memory.page_table import PageTable

class PreemptionManager:
    def __init__(self, paged_allocator, threshold):
        self.paged_allocator = paged_allocator
        self.threshold = threshold
        self.swap_storage = SwapStorage()

    def choose_victim(self, active_requests):
        if not active_requests:
            return None
        
        return min(
            active_requests,
            key=lambda request: request.generated_tokens
        )
    
    def evict(self, request):
        if request.generated_tokens < self.threshold:
            return self.recompute(request)
        
        return self.swap(request)
    
    def recompute(self, request):
        if request.page_table is not None:
            self.paged_allocator.free_request(request)
        else:
            request.reset()
        return "recompute"
    
    def swap(self, request):
        self.swap_storage.save(request)
        self.paged_allocator.free_request(request, reset_request=False)
        request.mark_swapped()
        return "swap"
    
    def restore(self, request):
        if not self.swap_storage.has(request.request_id):
            return False

        self.swap_storage.load(request)
        self.swap_storage.remove(request.request_id)

        request.page_table = PageTable()
        request.current_physical_block = None
        success = self.paged_allocator.restore_request(request)

        return success