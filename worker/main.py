import sys
import os

# Ensure backend root is in python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.workers.main import run_worker_loop

if __name__ == "__main__":
    run_worker_loop()
