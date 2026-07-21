from workload.work_load_generator import WorkLoadGenerator
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

naive_allocator = NaiveContiguousAllocator(
    total_memory=800
)

simulation = NaiveSimulation(
    requests=requests,
    naive_allocator= naive_allocator
)

simulation.run()

metrics = simulation.get_metrics()

for name, value in metrics.items():
    print(f"{name}: {value}")