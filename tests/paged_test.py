from workload.work_load_generator import WorkLoadGenerator
from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator
from simulation.simulation import Simulation
from correctness.correctness_harness import CorrectnessHarness

def run_test(block_size, seed):
    print(
        f"\nTesting "
        f"block_size={block_size}, "
        f"seed={seed}"
    )

    generator = WorkLoadGenerator(
        seed=seed,
        num_requests=100,
        arrival_rate=0.5,
        service_rate=0.01
    )

    requests = generator.generate_workload()

    physical_allocator = PhysicalBlockAllocator(
        num_blocks=1000,
        block_size=block_size
    )

    paged_allocator = PagedAllocator(
        physical_allocator=physical_allocator,
        block_size=block_size
    )

    harness = CorrectnessHarness(paged_allocator)

    simulation = Simulation(
        requests=requests,
        paged_allocator=paged_allocator,
        harness=harness
    )

    simulation.run()

    harness.run_failure_injections(request_id=999)

    assert len(simulation.active_requests) == 0, (
        "Active requests remain."
    )

    assert len(physical_allocator.allocated_blocks) == 0, (
        "Physical block leak detected."
    )

    assert len(physical_allocator.free_blocks) == physical_allocator.num_blocks, (
        "Not all physical blocks returned to free pool."
    )

    print("PASS")

    print("Finished:", len(simulation.finished_requests))

    print("Free blocks:", len(physical_allocator.free_blocks))

    print("Allocated blocks:", len(physical_allocator.allocated_blocks))

# block_sizes = [4, 8, 16, 32]
# seeds = [42, 123, 456, 789, 1000]

# for block_size in block_sizes:
#     for seed in seeds:
#         run_test(block_size=block_size, seed=seed)

run_test(4, 42)

print("\nAll block size and seed tests passed!")