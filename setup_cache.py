#!/usr/bin/env python3
"""
RTMLib cache directory wrapper
Sets cache directory to persistent storage before importing rtmlib
"""
import os

# Set cache directory to /data (Home Assistant persistent storage)
cache_dir = "/data/.cache/rtmlib"
os.makedirs(cache_dir, exist_ok=True)

# Set environment variable for rtmlib to use this cache
os.environ['TORCH_HOME'] = cache_dir
os.environ['HF_HOME'] = cache_dir

# Also create the hub checkpoints directory
checkpoints_dir = os.path.join(cache_dir, "hub", "checkpoints")
os.makedirs(checkpoints_dir, exist_ok=True)

print(f"✓ RTMLib cache configured: {cache_dir}")
