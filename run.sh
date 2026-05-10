#!/bin/sh
set -e

(
    while ! python3 -c "import socket;s=socket.socket(socket.AF_UNIX);s.connect('/tmp/m.sock');s.close()" 2>/dev/null; do sleep 0.05; done
    i=0
    while IFS= read -r host; do
        sock=/tmp/m-$i.sock
        ssh -R "$sock:/tmp/m.sock" \
            -o StreamLocalBindUnlink=yes \
            -o ExitOnForwardFailure=yes \
            -o LogLevel=QUIET \
            "$host" "PATH=\$HOME/miniforge3/bin:\$PATH MANAGER_SOCK=$sock python3 -" < worker.py &
        i=$((i + 1))
    done < hosts
    wait
) &

python3 "$@"
