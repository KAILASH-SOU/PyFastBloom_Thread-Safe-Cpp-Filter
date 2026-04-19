import pytest
from concurrent.futures import ThreadPoolExecutor
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fastbloom

def test_concurrency_stress():
    """
    Bombard the C++ Bloom Filter with thousands of concurrent read and write operations
    to prove that the std::shared_mutex prevents memory corruption.
    """
    NUM_THREADS = 100
    OPERATIONS_PER_THREAD = 1000

    bf = fastbloom.BloomFilter(1000000, 7)

    keys_to_write = [str(uuid.uuid4()) for _ in range(NUM_THREADS * OPERATIONS_PER_THREAD)]

    def worker_task(thread_id):
        start_idx = thread_id * OPERATIONS_PER_THREAD
        end_idx = start_idx + OPERATIONS_PER_THREAD

        for i in range(start_idx, end_idx):
            key = keys_to_write[i]
            bf.add(key)

            assert bf.contains(key) is True

            bf.contains(f"non_existent_{uuid.uuid4()}")

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(worker_task, i) for i in range(NUM_THREADS)]

        for future in futures:
            future.result()

    for key in keys_to_write[:1000]:
        assert bf.contains(key) is True

    assert bf.size == 1000000
    assert bf.hash_count == 7
