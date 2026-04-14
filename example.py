import fastbloom
import threading
import time

def test_single_thread():
    print("--- Testing Single Thread ---")
    bf = fastbloom.BloomFilter(10 * 1024 * 1024 * 8, 7)
    
    keys = ["kailash123", "google", "rubrik", "antigravity"]
    for key in keys:
        bf.add(key)
        print(f"Added: {key}")
        
    for key in keys:
        assert bf.contains(key) == True
        print(f"Verified: {key}")
        
    print(f"Contains 'random': {bf.contains('random')}")
    print("Single thread test passed!")

def test_concurrency():
    print("\n--- Testing Concurrency ---")
    bf = fastbloom.BloomFilter(1000000, 5)
    
    def writer(start, end):
        for i in range(start, end):
            bf.add(f"user_{i}")
            
    def reader(start, end):
        for i in range(start, end):
            bf.contains(f"user_{i}")

    threads = []
    for i in range(10):
        t = threading.Thread(target=writer, args=(i*100, (i+1)*100))
        threads.append(t)
        
    for i in range(50):
        t = threading.Thread(target=reader, args=(0, 1000))
        threads.append(t)
        
    start_time = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    end_time = time.time()
    
    print(f"Concurrency test completed in {end_time - start_time:.4f} seconds.")
    print("Concurrency test passed!")

if __name__ == "__main__":
    try:
        test_single_thread()
        test_concurrency()
    except ImportError:
        print("Error: 'fastbloom' module not found. Please run 'pip install .' in this directory first.")
    except Exception as e:
        print(f"An error occurred: {e}")
