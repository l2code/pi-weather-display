import os
import shutil

# Paths
BASE_DIR = os.path.dirname(__file__)
SNAPSHOT_PATH = os.path.join(BASE_DIR, "snapshots", "test_output.png")
GOLDEN_PATH = os.path.join(BASE_DIR, "snapshots", "golden_output.png")

# Ensure snapshot exists
if not os.path.exists(SNAPSHOT_PATH):
    print(f"❌ Snapshot file not found: {SNAPSHOT_PATH}")
    exit(1)

# Copy snapshot to golden
shutil.copy2(SNAPSHOT_PATH, GOLDEN_PATH)
print(f"✅ Golden snapshot updated: {GOLDEN_PATH}")
