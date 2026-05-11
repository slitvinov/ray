#!/bin/sh
set -e

(
    rm -f /tmp/m-*.sock
    while ! test -S /tmp/m.sock; do sleep 0.05; done
    while IFS= read -r host; do
        ssh -o ControlMaster=no -o ControlPath=none -o LogLevel=QUIET "$host" 'rm -f /tmp/m-*.sock' &
    done < hosts
    wait
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
