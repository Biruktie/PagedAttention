# Paged Attention Memory Management

A simplified implementation and simulation of memory management techniques inspired by **Paged Attention** for efficient KV-cache management during large language model inference.

The project focuses on managing fixed-size physical memory blocks, mapping logical request blocks to physical blocks, handling memory pressure, and ensuring correctness under heavy workloads.

## Project Overview

Each request generates a sequence of tokens that is stored across fixed-size physical blocks. A page table maps each request's logical blocks to physical blocks, allowing memory to be allocated non-contiguously and efficiently.

The project includes:

- Physical block allocation and deallocation
- Paged memory management using page tables
- Memory correctness checks
- Oversubscription and request preemption
- Recompute and swap-based eviction
- SLA-aware scheduling
- Deadlock detection and recovery

## Task 1 — Memory Management and Correctness

Implemented and tested:

- Physical block allocator
- Paged allocator
- Page table management
- Naive contiguous allocation baseline
- Memory utilization and fragmentation comparisons
- Correctness harness
- Double-free detection
- Use-after-free detection
- Boundary checking
- Stress testing

The correctness tests verify that requests do not share physical blocks incorrectly and that memory is fully returned to the free pool after request completion.

## Task 2a — Oversubscription and Preemption

The system supports workloads where total token demand exceeds available physical memory by at least **3×**.

When physical blocks are exhausted, the system selects a request for eviction:

- **Recompute mode:** Requests below the configured threshold release all blocks and restart from token 0.
- **Swap mode:** Requests at or above the threshold have their complete token sequence serialized, their blocks released, and their state restored when resumed.

Correctness is verified by hashing each request's token sequence and comparing the output before and after interruption.

### Results

- 500 requests tested
- 3× oversubscription verified
- 0 hash mismatches
- 0 orphaned physical blocks

## Task 2b — SLA Scheduler

Implemented an SLA-aware scheduler that supports:

- Request priorities
- Deadline-based scheduling
- Token generation budgets
- Exact budget termination
- Immediate memory release after termination
- Deadline-miss tracking
- Orphaned-block detection

Requests are scheduled according to priority, with earlier deadlines breaking ties between requests of equal priority.

## Task 2c — Deadlock Detection and Recovery

Implemented a wait-for graph to model dependencies between requests.

A DFS-based cycle detection algorithm runs in **O(V + E)** to identify circular waits.

When a deadlock is detected:

1. The request holding the most physical blocks is selected as the victim.
2. Ties are broken by selecting the request with fewer generated tokens.
3. The victim's blocks are released.
4. The victim is removed from the active set.
5. The wait-for graph is rebuilt.
6. The system verifies that the cycle has been removed in the same timestep.

The implementation was tested with two-request and three-request deadlocks, as well as a real allocator-based deadlock scenario.

## Testing

The project includes dedicated tests for:

- Allocation correctness
- Memory safety
- Stress workloads
- Oversubscription
- Preemption
- Output consistency
- SLA scheduling
- Budget enforcement
- Deadline tracking
- Deadlock detection
- Deadlock recovery

All implemented functionality has been validated through targeted tests and end-to-end simulations.

## Project Structure

The project is organized into modules for:

- `allocators/` — physical and paged memory allocation
- `memory/` — page table and memory management
- `models/` — requests and configurations
- `simulation/` — workload and simulation logic
- `preemption/` — recompute and swap management
- `sla_scheduling/` — SLA-aware scheduling
- `deadlock/` — wait-for graphs, cycle detection, and recovery
- `tests/` — correctness and integration tests

## Status

Completed:

- Task 1 — Memory Management and Correctness
- Task 2a — Oversubscription and Preemption
- Task 2b — SLA Scheduler
- Task 2c — Deadlock Detection and Recovery

The project currently provides a functional simulation of paged memory management and request scheduling under memory pressure, including correctness verification and recovery from resource contention.
