# List available recipes
default:
    @just --list

# Remove temporary Python artifacts and caches
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Archive all run_* directories into a central archive folder
archive:
    #!/usr/bin/env bash
    mkdir -p archive
    find . -type d -name "run_*" -not -path "./archive/*" | while read -r dir; do
        name=$(basename "$dir")
        parent=$(dirname "$dir")
        tar -czf "archive/$name.tar.gz" -C "$parent" "$name"
        echo "Archived $dir to archive/$name.tar.gz"
    done
