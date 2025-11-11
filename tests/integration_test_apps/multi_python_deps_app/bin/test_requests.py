#!/usr/bin/env python3
"""
Script that uses the requests library
"""
import sys
sys.path.insert(0, '../lib')

def main():
    try:
        import requests
        print(f"Requests library version: {requests.__version__}")
    except ImportError:
        print("Requests library not installed")

if __name__ == "__main__":
    main()
