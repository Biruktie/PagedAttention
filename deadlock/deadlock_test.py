from deadlock.deadlock_detector import DeadlockDetector
from deadlock.deadlock_manager import DeadlockManager
from deadlock.wait_for_graph import WaitForGraph

from models.request import Request
from models.request_config import RequestConfig

from allocators.physical_block_allocator import PhysicalBlockAllocator
from allocators.paged_allocator import PagedAllocator

def test_no_deadlock():
    print()
    print(
        "===== TESTING NO DEADLOCK ====="
    )

    graph = {
        1: {2},
        2: {3},
        3: set()
    }

    detector = DeadlockDetector()

    cycle = detector.detect_cycle(graph)

    assert cycle is None, (
        "False deadlock detected."
    )

    print("No deadlock detected: PASSED")


def test_two_request_deadlock():

    print()
    print(
        "===== TESTING TWO-REQUEST DEADLOCK ====="
    )

    graph = {
        1: {2},
        2: {1}
    }

    detector = DeadlockDetector()

    cycle = detector.detect_cycle(graph)

    assert cycle is not None, (
        "Deadlock was not detected."
    )

    assert set(cycle) == {1, 2}, (
        "Incorrect cycle detected."
    )

    print(
        f"Detected cycle: {cycle}"
    )

    print(
        "Two-request deadlock: PASSED"
    )


def test_three_request_deadlock():

    print()
    print(
        "===== TESTING THREE-REQUEST DEADLOCK ====="
    )

    graph = {
        1: {2},
        2: {3},
        3: {1}
    }

    detector = DeadlockDetector()

    cycle = detector.detect_cycle(graph)

    assert cycle is not None, (
        "Three-request deadlock was not detected."
    )

    assert set(cycle) == {
        1,
        2,
        3
    }, (
        "Incorrect cycle detected."
    )

    print(
        f"Detected cycle: {cycle}"
    )

    print(
        "Three-request deadlock: PASSED"
    )

def test_victim_selection():

    print()
    print(
        "===== TESTING VICTIM SELECTION ====="
    )

    manager = DeadlockManager(
        paged_allocator=None
    )

    class MockRequest:

        def __init__(
            self,
            request_id,
            block_count,
            generated_tokens
        ):

            self.request_id = request_id
            self.generated_tokens = (
                generated_tokens
            )

            self.page_table = (
                MockPageTable(
                    block_count
                )
            )


    class MockPageTable:

        def __init__(
            self,
            block_count
        ):

            self.block_count = (
                block_count
            )

        def get_all_blocks(self):

            return [
                object()
                for _ in range(
                    self.block_count
                )
            ]


    request_a = MockRequest(
        request_id=1,
        block_count=2,
        generated_tokens=10
    )

    request_b = MockRequest(
        request_id=2,
        block_count=5,
        generated_tokens=20
    )

    request_c = MockRequest(
        request_id=3,
        block_count=5,
        generated_tokens=8
    )

    active_requests = [
        request_a,
        request_b,
        request_c
    ]

    cycle = [
        1,
        2,
        3
    ]

    victim = manager.choose_victim(
        cycle,
        active_requests
    )

    assert victim.request_id == 3, (
        "Incorrect deadlock victim selected."
    )

    print(
        f"Selected victim: "
        f"Request {victim.request_id}"
    )

    print(
        "Victim selection: PASSED"
    )

def create_deadlocked_requests():

    request_a = Request(
        RequestConfig(
            request_id=1,
            arrival_time=0.0,
            max_length=20,
            actual_length=20
        )
    )

    request_b = Request(
        RequestConfig(
            request_id=2,
            arrival_time=0.0,
            max_length=20,
            actual_length=20
        )
    )

    return (
        request_a,
        request_b
    )


def test_real_deadlock_detection():

    print()
    print(
        "===== TESTING REAL DEADLOCK ====="
    )

    request_a, request_b = create_deadlocked_requests()

    allocator = PhysicalBlockAllocator(
        num_blocks=2,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    block_a = allocator.allocate()
    block_b = allocator.allocate()

    request_a.initialize_page_table()
    request_b.initialize_page_table()

    request_a.page_table.map_block(0, block_a)

    request_b.page_table.map_block(0, block_b)

    request_a.waiting_for_block = block_b
    

    request_b.waiting_for_block = block_a

    active_requests = [
        request_a,
        request_b
    ]

    wait_for_graph = WaitForGraph()

    graph = wait_for_graph.build(active_requests)

    print(
        f"Wait-for graph: {graph}"
    )

    detector = DeadlockDetector()

    cycle = detector.detect_cycle(graph)

    assert cycle is not None, (
        "Expected deadlock was not detected."
    )

    assert set(cycle) == {
        1,
        2
    }, (
        "Incorrect deadlock cycle detected."
    )

    print(
        f"Deadlock detected: {cycle}"
    )

    print(
        "Real deadlock detection: PASSED"
    )

def test_deadlock_recovery():

    print()
    print(
        "===== TESTING DEADLOCK RECOVERY ====="
    )

    request_a, request_b = (
        create_deadlocked_requests()
    )

    allocator = PhysicalBlockAllocator(
        num_blocks=2,
        block_size=4
    )

    paged_allocator = PagedAllocator(
        physical_allocator=allocator,
        block_size=4
    )

    block_a = allocator.allocate()
    block_b = allocator.allocate()

    request_a.initialize_page_table()
    request_b.initialize_page_table()

    request_a.page_table.map_block(
        0,
        block_a
    )

    request_b.page_table.map_block(
        0,
        block_b
    )

    request_a.generated_tokens = 5
    request_b.generated_tokens = 10

    request_a.waiting_for_block = block_b

    request_b.waiting_for_block = block_a

    active_requests = [
        request_a,
        request_b
    ]

    wait_for_graph = WaitForGraph()

    graph = wait_for_graph.build(active_requests)

    detector = DeadlockDetector()

    cycle = detector.detect_cycle(graph)

    assert cycle is not None, (
        "Expected deadlock was not detected."
    )

    print(
        f"Deadlock detected: {cycle}"
    )

    manager = DeadlockManager(
        paged_allocator
    )

    victim = manager.recover_deadlock(
        cycle,
        active_requests
    )

    print(
        f"Victim evicted: "
        f"Request {victim.request_id}"
    )

    assert victim.request_id == 1, (
        "Incorrect victim selected. "
        "Request 1 should be selected "
        "because it generated fewer tokens."
    )

    assert victim not in active_requests, (
        "Victim was not removed from "
        "active requests."
    )

    assert len(
        allocator.allocated_blocks
    ) == 1, (
        "Victim's physical blocks "
        "were not freed."
    )

    recovered_graph = wait_for_graph.build(active_requests)

    recovered_cycle = detector.detect_cycle(recovered_graph)

    assert recovered_cycle is None, (
        "Deadlock was not recovered "
        "within the same timestep."
    )

    print(
        "Deadlock recovered in the same timestep: PASSED"
    )

    print(
        f"Remaining active requests: "
        f"{len(active_requests)}"
    )

    print(
        f"Free blocks: "
        f"{len(allocator.free_blocks)}"
    )

if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "       DEADLOCK DETECTION TEST SUITE"
    )

    print(
        "=========================================="
    )

    test_no_deadlock()
    test_two_request_deadlock()
    test_three_request_deadlock()
    test_victim_selection()
    test_real_deadlock_detection()
    test_deadlock_recovery()

    print()
    print(
        "=========================================="
    )

    print(
        "ALL DEADLOCK TESTS PASSED"
    )

    print(
        "=========================================="
    )