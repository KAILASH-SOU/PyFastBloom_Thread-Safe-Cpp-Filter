import time
import uuid
import redis
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    import fastbloom
except ImportError:
    print("Please build the fastbloom extension first: pip install -e .")
    sys.exit(1)

def run_benchmark():
    print("=" * 50)
    print("PyFastBloom Business Value Benchmark")
    print("=" * 50)
    print("Simulating a high-traffic environment where the database is queried for missing keys.\n")

    redis_host = os.environ.get('REDIS_HOST', 'localhost')

    try:
        r = redis.Redis(host=redis_host, port=6379, db=0)
        r.ping()
    except redis.exceptions.ConnectionError:
        try:
            import fakeredis
            print("Falling back to fakeredis since no real Redis is running.")
            r = fakeredis.FakeRedis()
        except ImportError:
            print(f"Failed to connect to Redis at {redis_host}:6379 and fakeredis not installed.")
            sys.exit(1)

    r.flushdb()

    NUM_EXISTING = 10_000
    NUM_MISSING = 90_000

    bf = fastbloom.BloomFilter(1000000, 7)

    print(f"1. Loading {NUM_EXISTING} existing keys into Redis and Bloom Filter...")
    start_time = time.time()

    existing_keys = [f"user_{uuid.uuid4()}" for _ in range(NUM_EXISTING)]
    missing_keys = [f"user_{uuid.uuid4()}" for _ in range(NUM_MISSING)]

    pipeline = r.pipeline()
    for key in existing_keys:
        pipeline.set(key, "active")
        bf.add(key)

    pipeline.execute()
    print(f"   Done in {time.time() - start_time:.4f} seconds.\n")

    import random
    workload = existing_keys + missing_keys
    random.shuffle(workload)
    total_queries = len(workload)

    print(f"2. Running Control Benchmark (Direct Redis DB Queries)...")
    print(f"   Total Queries: {total_queries} (90% non-existent keys)")

    start_time_redis = time.time()
    redis_hits = 0
    redis_misses = 0

    for key in workload:
        val = r.get(key)
        if val:
            redis_hits += 1
        else:
            redis_misses += 1

    redis_duration = time.time() - start_time_redis
    print(f"   Result: DB hit {redis_hits} times, missed {redis_misses} times.")
    print(f"   Time taken: {redis_duration:.4f} seconds.\n")


    print(f"3. Running Experimental Benchmark (Bloom Filter + Redis)...")

    start_time_bloom = time.time()
    bloom_hits_db_hits = 0
    bloom_hits_db_misses = 0
    bloom_misses = 0

    for key in workload:
        if bf.contains(key):
            val = r.get(key)
            if val:
                bloom_hits_db_hits += 1
            else:
                bloom_hits_db_misses += 1
        else:
            bloom_misses += 1

    bloom_duration = time.time() - start_time_bloom
    print(f"   Result: Bloom filtered {bloom_misses} queries. DB accessed only {bloom_hits_db_hits + bloom_hits_db_misses} times.")
    print(f"   False Positives: {bloom_hits_db_misses}")
    print(f"   Time taken: {bloom_duration:.4f} seconds.\n")

    print("=" * 50)
    print("Business Value Analysis")
    print("=" * 50)
    time_saved = redis_duration - bloom_duration
    percentage_saved = (time_saved / redis_duration) * 100
    db_load_reduction = (redis_misses - bloom_hits_db_misses) / total_queries * 100

    print(f"Database Queries Prevented: {(redis_misses - bloom_hits_db_misses):,}")
    print(f"Database Load Reduction: {db_load_reduction:.2f}%")
    print(f"Total Time Saved: {time_saved:.4f}s ({percentage_saved:.2f}% faster)")
    print("\nCONCLUSION: By short-circuiting DB misses in-memory via PyFastBloom,")
    print("we significantly reduce latency and eliminate database connection overload.")

if __name__ == "__main__":
    run_benchmark()
