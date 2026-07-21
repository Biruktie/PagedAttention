from models.request import Request
from models.request_config import RequestConfig
from models.request import RequestStatus

from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator

from sla_scheduling.sla_scheduler import SLAScheduler
from preemption.preemption_manager import PreemptionManager

from simulation.sla_simulation import SLASimulation


def create_test_requests():

    high_priority = Request(
        RequestConfig(
            request_id=1,
            arrival_time=0.0,
            max_length=20,
            actual_length=10,
            priority=1,
            deadline=20,
            token_budget=3
        )
    )

    medium_priority = Request(
        RequestConfig(
            request_id=2,
            arrival_time=0.0,
            max_length=20,
            actual_length=10,
            priority=2,
            deadline=30,
            token_budget=5
        )
    )

    low_priority = Request(
        RequestConfig(
            request_id=3,
            arrival_time=0.0,
            max_length=20,
            actual_length=10,
            priority=3,
            deadline=40,
            token_budget=7
        )
    )

    return [
        high_priority,
        medium_priority,
        low_priority
    ]


def test_priority_ordering():

    print()
    print("===== TESTING PRIORITY ORDERING =====")

    allocator = PhysicalBlockAllocator(
        num_blocks=20,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    scheduler = SLAScheduler(
        paged_allocator=paged_allocator
    )

    requests = create_test_requests()

    waiting_requests = [
        requests[2], 
        requests[0],  
        requests[1]   
    ]

    selected = scheduler.select_next(waiting_requests)

    assert selected.request_id == 1, (
        "Highest-priority request was not selected first."
    )

    selected = scheduler.select_next(waiting_requests)

    assert selected.request_id == 2, (
        "Second-highest-priority request was not selected second."
    )

    selected = scheduler.select_next(waiting_requests)

    assert selected.request_id == 3, (
        "Lowest-priority request was not selected last."
    )

    print("Priority ordering: PASSED")

def test_priority_under_contention():

    print()
    print(
        "===== TESTING PRIORITY UNDER CONTENTION ====="
    )

    requests = [
        Request(
            RequestConfig(
                request_id=1,
                arrival_time=0.0,
                max_length=20,
                actual_length=2,
                priority=3,
                deadline=100,
                token_budget=2
            )
        ),

        Request(
            RequestConfig(
                request_id=2,
                arrival_time=0.0,
                max_length=20,
                actual_length=2,
                priority=1,
                deadline=100,
                token_budget=2
            )
        ),

        Request(
            RequestConfig(
                request_id=3,
                arrival_time=0.0,
                max_length=20,
                actual_length=2,
                priority=2,
                deadline=100,
                token_budget=2
            )
        )
    ]

    allocator = PhysicalBlockAllocator(
        num_blocks=20,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    scheduler = SLAScheduler(
        paged_allocator=paged_allocator,
        max_active_requests=1
    )

    preemption_manager = PreemptionManager(
        paged_allocator=paged_allocator,
        threshold=10
    )

    simulation = SLASimulation(
        requests=requests,
        paged_allocator=paged_allocator,
        scheduler=scheduler,
        preemption_manager=preemption_manager
    )

    simulation.admit_new_requests()

    assert len(simulation.waiting_requests) == 3

    simulation.schedule_waiting_requests()

    assert len(simulation.active_requests) == 1

    first_request = (
        simulation.active_requests[0]
    )

    assert first_request.request_id == 2, (
        "Highest-priority request was not "
        "scheduled first."
    )

    print(
        "First scheduled request: "
        f"{first_request.request_id}"
    )

    simulation.active_requests.remove(first_request)

    first_request.status = (
        RequestStatus.FINISHED
    )

    simulation.schedule_waiting_requests()

    assert len(simulation.active_requests) == 1

    second_request = simulation.active_requests[0]

    print(
        "Second scheduled request: "
        f"{second_request.request_id}"
    )

    assert second_request.request_id == 3, (
        "Second-highest-priority request "
        "was not scheduled second."
    )

    print(
        "Priority under contention: PASSED"
    )

def test_deadline_priority():

    print()
    print(
        "===== TESTING DEADLINE-AWARE SCHEDULING ====="
    )

    requests = [

        Request(
            RequestConfig(
                request_id=1,
                arrival_time=0.0,
                max_length=20,
                actual_length=5,
                priority=3,
                deadline=100,
                token_budget=5
            )
        ),

        Request(
            RequestConfig(
                request_id=2,
                arrival_time=0.0,
                max_length=20,
                actual_length=5,
                priority=1,
                deadline=1,
                token_budget=5
            )
        )
    ]

    allocator = PhysicalBlockAllocator(
        num_blocks=20,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    scheduler = SLAScheduler(
        paged_allocator=paged_allocator,
        max_active_requests=1
    )

    preemption_manager = PreemptionManager(
        paged_allocator=paged_allocator,
        threshold=10
    )

    simulation = SLASimulation(
        requests=requests,
        paged_allocator=paged_allocator,
        scheduler=scheduler,
        preemption_manager=preemption_manager
    )

    simulation.admit_new_requests()

    simulation.schedule_waiting_requests()

    assert len(
        simulation.active_requests
    ) == 1

    selected = (
        simulation.active_requests[0]
    )

    assert selected.request_id == 2, (
        "Request with highest priority and "
        "earliest deadline was not selected."
    )

    print(
        "Selected request: "
        f"{selected.request_id}"
    )

    assert not scheduler.has_missed_deadline(
        selected,
        simulation.current_time
    ), (
        "Request missed its deadline even "
        "though sufficient capacity existed."
    )

    print(
        "Deadline-aware scheduling: PASSED"
    )

def test_budget_termination():

    print()
    print("===== TESTING TOKEN BUDGET =====")

    allocator = PhysicalBlockAllocator(
        num_blocks=20,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    scheduler = SLAScheduler(
        paged_allocator=paged_allocator
    )

    request = Request(
        RequestConfig(
            request_id=100,
            arrival_time=0.0,
            max_length=20,
            actual_length=20,
            priority=1,
            deadline=100,
            token_budget=3
        )
    )

    request.status = RequestStatus.RUNNING

    for i in range(3):
        token = f"R100_T{i}"

        success = paged_allocator.allocate_token(request, token)

        assert success, (
            "Token allocation unexpectedly failed."
        )

    print(
        f"Generated tokens: "
        f"{request.generated_tokens}"
    )

    assert request.generated_tokens == 3, (
        "Request did not generate exactly "
        "the expected number of tokens."
    )

    assert scheduler.should_terminate_for_budget(request), (
        "Scheduler failed to detect "
        "token budget exhaustion."
    )

    scheduler.terminate_for_budget(request)

    assert request.generated_tokens == 3, (
        "Token count changed after termination."
    )

    assert request.status.value == "TERMINATED", (
        "Request was not marked TERMINATED."
    )

    assert len(allocator.allocated_blocks) == 0, (
        "Blocks were not freed after "
        "budget termination."
    )

    assert len(allocator.free_blocks) == allocator.num_blocks, (
        "Not all blocks were returned "
        "to the free pool."
    )

    assert scheduler.budget_terminations == 1, (
        "Budget termination was not counted."
    )

    print(
        "Exact budget termination: PASSED"
    )


def test_sla_simulation():

    print()
    print("===== TESTING SLA SIMULATION =====")

    requests = create_test_requests()

    allocator = PhysicalBlockAllocator(
        num_blocks=20,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    scheduler = SLAScheduler(
        paged_allocator=paged_allocator,
        max_active_requests=1
    )

    preemption_manager = PreemptionManager(
        paged_allocator=paged_allocator,
        threshold=10
    )

    simulation = SLASimulation(
        requests=requests,
        paged_allocator=paged_allocator,
        scheduler=scheduler,
        preemption_manager=preemption_manager
    )

    metrics = simulation.run()

    print()
    print("===== SLA METRICS =====")

    for name, value in metrics.items():
        print(
            f"{name}: {value}"
        )

    assert metrics[
        "orphaned_blocks"
    ] == 0, (
        "Orphaned physical blocks detected."
    )

    print()
    print(
        "Orphaned block check: PASSED"
    )


if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "         SLA SCHEDULER TEST SUITE"
    )

    print(
        "=========================================="
    )

    test_priority_ordering()
    test_priority_under_contention()
    test_deadline_priority()
    test_budget_termination()
    test_sla_simulation()

    print()
    print(
        "=========================================="
    )

    print(
        "ALL SLA TESTS PASSED"
    )

    print(
        "=========================================="
    )