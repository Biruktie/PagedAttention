from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator
from models.request import Request
from models.request_config import RequestConfig

def validate_allocator(allocator):
    assert allocator.free_blocks.isdisjoint(
        allocator.allocated_blocks
    ), "A block exists in both the free and allocated sets."

    assert (
        len(allocator.free_blocks)
        + len(allocator.allocated_blocks)
        == allocator.num_blocks
    ), "Memory leak detected: total block count changed"

physical_allocator = PhysicalBlockAllocator(
    num_blocks=4,
    block_size=4
)

paged_allocator = PagedAllocator(
    physical_allocator,
    block_size=4
)

config = RequestConfig(
    request_id=1,
    max_length=12,
    actual_length=10,
    arrival_time=0.1
)

request = Request(config=config)

print("======== Initial State ========")
print(f"Free Blocks: {len(physical_allocator.free_blocks)}")
print(f"Allocated Blocks: {len(physical_allocator.allocated_blocks)}")

validate_allocator(physical_allocator)

for i in range(request.actual_length):
    paged_allocator.allocate_token(
        request,
        f"T{i}"
    )

print("\n======== After Generation ========")

print(request.page_table)
print()

for block in physical_allocator.allocated_blocks:
    print(block)

print()

print(f"Generated tokens: {request.generated_tokens}")
print(f"Status: {request.status}")

print(f"Free Blocks: {len(physical_allocator.free_blocks)}")
print(f"Allocated Blocks: {len(physical_allocator.allocated_blocks)}")

validate_allocator(physical_allocator)

paged_allocator.free_request(request)

print("======== After Free ========")

print(f"Page Table: {request.page_table}")
print(f"Generated tokens: {request.generated_tokens}")
print(f"Status: {request.status}")

print(f"Free Blocks: {len(physical_allocator.free_blocks)}")
print(f"Allocated Blocks: {len(physical_allocator.allocated_blocks)}")

validate_allocator(physical_allocator)