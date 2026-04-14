#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "bloom_filter.hpp"

namespace py = pybind11;

PYBIND11_MODULE(fastbloom, m) {
    m.doc() = "Fast, thread-safe Bloom Filter native extension";

    py::class_<ConcurrentBloomFilter>(m, "BloomFilter")
        .def(py::init<size_t, size_t>(), py::arg("size"), py::arg("num_hashes"))
        .def("add", &ConcurrentBloomFilter::add, "Add a key to the filter", py::arg("key"))
        .def("contains", &ConcurrentBloomFilter::contains, "Check if a key is present", py::arg("key"))
        .def_property_readonly("size", &ConcurrentBloomFilter::size)
        .def_property_readonly("hash_count", &ConcurrentBloomFilter::hash_count);
}
