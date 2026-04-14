#pragma once

#include <vector>
#include <string>
#include <shared_mutex>
#include <cstdint>
#include <functional>
#include <algorithm>
#include <cmath>


class ConcurrentBloomFilter {
private:
    std::vector<bool> bits;
    size_t m; // Number of bits
    size_t k; // Number of hash functions
    mutable std::shared_mutex mutex;

    uint64_t compute_base_hash(const std::string& key) const {
        return std::hash<std::string>{}(key);
    }

public:
    ConcurrentBloomFilter(size_t size, size_t num_hashes) 
        : m(size), k(num_hashes) {
        bits.resize(m, false);
    }

    void add(const std::string& key) {
        uint64_t hash_val = compute_base_hash(key);
        uint32_t h1 = static_cast<uint32_t>(hash_val);
        uint32_t h2 = static_cast<uint32_t>(hash_val >> 32);

        std::unique_lock<std::shared_mutex> lock(mutex);
        for (size_t i = 0; i < k; ++i) {
            size_t idx = (h1 + i * h2) % m;
            bits[idx] = true;
        }
    }

    bool contains(const std::string& key) const {
        uint64_t hash_val = compute_base_hash(key);
        uint32_t h1 = static_cast<uint32_t>(hash_val);
        uint32_t h2 = static_cast<uint32_t>(hash_val >> 32);

        std::shared_lock<std::shared_mutex> lock(mutex);
        for (size_t i = 0; i < k; ++i) {
            size_t idx = (h1 + i * h2) % m;
            if (!bits[idx]) return false;
        }
        return true;
    }

    size_t size() const { return m; }
    size_t hash_count() const { return k; }
};
