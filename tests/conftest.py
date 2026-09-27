import os
# Ensure unit tests run deterministically and fast without external network waits
os.environ["TESTING"] = "1"
os.environ["USE_FAST_EMBEDDINGS"] = "1"
