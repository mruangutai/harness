# In check-domain.sh / bash-write-guard.sh (conceptual patch)

resolve_secure_target() {
    local target="$1"
    local resolved
    
    # If the target or its parent exists, check inode/device identity
    if [ -e "$target" ]; then
        # Capture device and inode to defeat hardlink aliases
        local dev_ino
        if ! dev_ino=$(stat -c '%D:%i' "$target" 2>/dev/null || stat -f '%Sd:%i' "$target" 2>/dev/null); then
            # FAIL CLOSED: If stat fails on an existing file within guarded scope, block the write.
            exit 2
        fi
        echo "$dev_ino"
    else
        # For non-existent files, resolve parent directory path canonically
        local parent
        parent="$(dirname "$target")"
        if [ ! -d "$parent" ]; then
            exit 2
        fi
        realpath -s "$target"
    fi
}