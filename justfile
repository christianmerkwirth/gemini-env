# List available recipes
default:
    @just --list

# Remove temporary Python artifacts and caches
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Archive all run_* directories into a central archive folder and then remove them
archive:
    #!/usr/bin/env bash
    mkdir -p archive
    find . -type d -name "run_*" -not -path "./archive/*" | while read -r dir; do
        name=$(basename "$dir")
        parent=$(dirname "$dir")
        if tar -czf "archive/$name.tar.gz" -C "$parent" "$name"; then
            echo "Archived $dir to archive/$name.tar.gz"
            rm -rf "$dir"
            echo "Removed $dir"
        else
            echo "Failed to archive $dir" >&2
        fi
    done
