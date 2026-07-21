import copy
import math

from workload.work_load_generator import WorkLoadGenerator
from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator

from simulation.baseline_simulation import BaselineSimulation
from simulation.preemptive_simulation import PreemptiveSimulation

from preemption.preemption_manager import PreemptionManager

seed = 42
num_requests = 500
block_size = 4
preemption_threshold = 100

baseline_blocks = 10000
oversubscription_factor = 3

generator = WorkLoadGenerator(
    seed=seed,
    num_requests=num_requests,
    arrival_rate=0.5,
    service_rate=0.01
)

requests = generator.generate_workload()

total_token_demand  = sum(
    request.actual_length
    for request in requests
)

print("Total token demand:", total_token_demand)

total_demand_blocks = math.ceil(total_token_demand / block_size)

preemptive_num_blocks = 1000

print("Total demand in blocks:", total_demand_blocks)
print("Preemptive physical capacity:", preemptive_num_blocks)
print("Required 3x oversubsciption:", total_demand_blocks >= 3 * preemptive_num_blocks)

assert ( total_demand_blocks >= 3 * preemptive_num_blocks), (
    "Oversubscription requirement failed."
)

baseline_requests = copy.deepcopy(requests)
preemptive_requests = copy.deepcopy(requests)

baseline_physical_allocator = PhysicalBlockAllocator(
    num_blocks=baseline_blocks,
    block_size=block_size
)

baseline_paged_allocator = PagedAllocator(
    physical_allocator=baseline_physical_allocator,
    block_size=block_size
)

baseline_simulation = BaselineSimulation(
    requests=baseline_requests,
    paged_allocator=baseline_paged_allocator
)

print()
print("===== RUNNING BASELINE =====")

baseline_hashes = baseline_simulation.run()

print("Baseline finished:", len(baseline_simulation.finished_requests))

assert(len(baseline_simulation.finished_requests) == num_requests), (
    "Baseline did not finish all requests."
)

preemtive_physical_allocator = PhysicalBlockAllocator(
    num_blocks=preemptive_num_blocks,
    block_size=block_size
)

preemptive_paged_allocator = PagedAllocator(
    physical_allocator=preemtive_physical_allocator,
    block_size=block_size
)

preemptive_manager = PreemptionManager(
    paged_allocator=preemptive_paged_allocator,
    threshold=preemption_threshold
)

preemptive_simulation = PreemptiveSimulation(
    requests=preemptive_requests,
    paged_allocator=preemptive_paged_allocator,
    preemption_manager=preemptive_manager
)

print()
print("===== RUNNING PREEMPTIVE SIMULATION =====")

preemptive_success = preemptive_simulation.run()

print()
print("===== COMPLETION CHECK =====")

print("Preemptive finished:", len(preemptive_simulation.finished_requests))

assert (len(preemptive_simulation.finished_requests) == num_requests), (
    "Preemptive simulation did not finish all requests."
)

preemptive_hashes = {
    request.request_id: request.completion_hash
    for request in preemptive_simulation.finished_requests
}

mismatches = []

for request_id, baseline_hash in baseline_hashes.items():
    preemptive_hash = preemptive_hashes.get(request_id)
    if baseline_hash != preemptive_hash:
        mismatches.append(request_id)

print()
print("===== HASH VERIFICATION =====")

print("Total requests:", num_requests)
print("Hash mismatches:", len(mismatches))

if mismatches:
    print("Mismatched request IDs:", mismatches)

assert not mismatches, ("Token output mismatch detected")

print()
print("===== MEMORY CHECK =====")

free_blocks = len(preemtive_physical_allocator.free_blocks)
allocated_blocks = len(preemtive_physical_allocator.allocated_blocks)

print("Free blocks:", free_blocks)
print("Allocated blocks", allocated_blocks)

assert(free_blocks == preemtive_physical_allocator.num_blocks), ("Not all physical blocks returned to free pool.")

print( "==========================================")

print("Requests:", num_requests)
print("Total token demand:", total_token_demand)
print("Preemptive capacity:", preemptive_num_blocks)
print("Oversubscription satisfied: YES")
print("Recompute evictions", preemptive_simulation.recompute_count)
print("Swap evictions:", preemptive_simulation.swap_count)
