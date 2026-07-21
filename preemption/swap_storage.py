class SwapStorage:
    def __init__(self):
        self.storage = {}

    def save(self, request):
        self.storage[request.request_id] = {
            "tokens": request.tokens.copy(),
            "generated_tokens": request.generated_tokens
        }

    def load(self, request):
        if request.request_id not in self.storage:
            raise KeyError(
                f"No swapped data found for "
                f"request {request.request_id}."
            )
        
        data = self.storage[request.request_id]

        request.tokens = data["tokens"].copy()
        request.generated_tokens = data["generated_tokens"]

    def remove(self, request_id):
        if request_id in self.storage:
            del self.storage[request_id]

    def has(self, request_id):
        return request_id in self.storage