import copy
import math

from workload.work_load_generator import WorkLoadGenerator
from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator
from simulation.simulation import Simulation

from allocators.naive_contiguous_allocator import NaiveContiguousAllocator
from simulation.naive_simulation import NaiveSimulation

from metrics.metrics_calculator import MetricsCalculator

generator = WorkLoadGenerator(
    seed=42,
    num_requests=200,
    arrival_rate=0.5,
    service_rate=0.01
)

requests = generator.generate_workload()

paged_requests = copy.deepcopy(requests)
naive_requests = copy.deepcopy(requests)

physical_allocator = PhysicalBlockAllocator(
    num_blocks=2000,
    block_size=4
)

paged_allocator = PagedAllocator(
    physical_allocator=physical_allocator,
    block_size=4
)

paged_simulation = Simulation(
    requests=paged_requests,
    paged_allocator=paged_allocator
)


naive_allocator = NaiveContiguousAllocator(
    total_memory=8000
)

naive_simulation = NaiveSimulation(
    requests=naive_requests,
    naive_allocator=naive_allocator
)

paged_simulation.run()
naive_simulation.run()

paged_peak_blocks = physical_allocator.peak_allocated
naive_peak_blocks = math.ceil(naive_allocator.peak_allocated / 4)

naive_rejected = len(naive_simulation.rejected_requests)
paged_rejected = 0

naive_internal = naive_simulation.avg_internal_fragmentation
paged_internal = MetricsCalculator.calculate_paged_internal_fragmentation_ratio(paged_simulation.finished_requests, block_size=4)

naive_external = naive_simulation.avg_external_fragmentation
paged_external = 0.0


print()
print("===== HEAD-TO-HEAD COMPARISON =====")

print(
    f"{'Allocator':<12}"
    f"{'Peak Blocks':<15}"
    f"{'Rejected':<12}"
    f"{'Internal Frag.':<18}"
    f"{'External Frag.':<18}"
)

print("-" * 75)

print(
    f"{'Naive':<12}"
    f"{naive_peak_blocks:<15}"
    f"{naive_rejected:<12}"
    f"{naive_internal * 100:<18.2f}"
    f"{naive_external * 100:<18.2f}"
)

print(
    f"{'Paged':<12}"
    f"{paged_peak_blocks:<15}"
    f"{paged_rejected:<12}"
    f"{paged_internal * 100:<18.2f}"
    f"{paged_external * 100:<18.2f}"
)

