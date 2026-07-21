from workload.work_load_generator import WorkLoadGenerator
from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator

from preemption.preemption_manager import PreemptionManager
from simulation.preemptive_simulation import PreemptiveSimulation

generator = WorkLoadGenerator(
    seed=42,
    num_requests=5,
    arrival_rate=0.5,
    service_rate=0.01
)

requests = generator.generate_workload()

block_size = 4
num_blocks = 10

physical_allocator = PhysicalBlockAllocator(
    num_blocks=num_blocks,
    block_size=block_size
)

paged_allocator = PagedAllocator(
    physical_allocator=physical_allocator,
    block_size=block_size
)

threshold = 20

preemption_manager = PreemptionManager(
    paged_allocator=paged_allocator,
    threshold=threshold
)

simulation = PreemptiveSimulation(
    requests=requests,
    paged_allocator=paged_allocator,
    preemption_manager=preemption_manager
)

simulation.run()

print()
print("===== PREEMPTION TEST =====")

print(
    "Finished:",
    len(simulation.finished_requests)
)

print(
    "Recompute count:",
    simulation.recompute_count
)

print(
    "Swap count:",
    simulation.swap_count
)

print(
    "Free blocks:",
    len(physical_allocator.free_blocks)
)

print(
    "Allocated blocks:",
    len(physical_allocator.allocated_blocks)
)

print(
    "Total blocks:",
    physical_allocator.num_blocks
)