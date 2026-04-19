from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import fastbloom

app = FastAPI(
    title="PyFastBloom Enterprise API",
    description="A high-performance REST API wrapping a concurrent C++ Bloom Filter engine.",
    version="1.0.0",
)

try:
    bloom = fastbloom.BloomFilter(1000000, 7)
except AttributeError:
    bloom = None
    print("Warning: fastbloom module not found or failed to initialize.")

class BloomResponse(BaseModel):
    key: str
    exists: bool

@app.get("/")
def read_root():
    return {"message": "Welcome to PyFastBloom Enterprise API"}

@app.post("/add")
def add_key(key: str):
    if bloom is None:
        raise HTTPException(status_code=500, detail="Bloom filter engine not initialized.")
    bloom.add(key)
    return {"status": "success", "key": key, "message": "Key added to the filter."}

@app.get("/check/{key}", response_model=BloomResponse)
def check_key(key: str):
    if bloom is None:
        raise HTTPException(status_code=500, detail="Bloom filter engine not initialized.")

    exists = bloom.contains(key)
    return BloomResponse(key=key, exists=exists)

@app.get("/stats")
def get_stats():
    if bloom is None:
        raise HTTPException(status_code=500, detail="Bloom filter engine not initialized.")
    return {
        "size": bloom.size,
        "hash_count": bloom.hash_count
    }
