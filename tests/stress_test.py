from workload.work_load_generator import WorkLoadGenerator
from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator
from correctness.correctness_harness import CorrectnessHarness
from simulation.simulation import Simulation
seeds = [42, 123, 456, 789, 999]

for seed in seeds:
    print(
        f"\n===== TESTING SEED {seed} ====="
    )

    generator = WorkLoadGenerator(
        seed=seed,
        num_requests=10_000,
        arrival_rate=0.5,
        service_rate=0.01
    )

    requests = generator.generate_workload()

    physical_allocator = PhysicalBlockAllocator(
        num_blocks=10_000,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=physical_allocator,
        block_size=4
    )

    harness = CorrectnessHarness(
        paged_allocator
    )

    simulation = Simulation(
        requests=requests,
        paged_allocator=paged_allocator,
        harness=harness
    )

    simulation.run()

    assert len(
        physical_allocator.free_blocks
    ) == physical_allocator.num_blocks

    assert len(
        physical_allocator.allocated_blocks
    ) == 0

    print(
        f"Seed {seed}: PASSED"
    )