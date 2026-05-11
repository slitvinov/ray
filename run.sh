#!/bin/sh
set -e

export MANAGER_SOCK_DRIVER=/tmp/m-$$.sock
trap 'rm -f /tmp/m-$$*.sock' EXIT

(
    while ! test -S "$MANAGER_SOCK_DRIVER"; do sleep 0.05; done
    while IFS= read -r host; do
        ssh \
	    -o ConnectTimeout=10 \
	    -o LogLevel=QUIET \
	    "$host" 'rm -f /tmp/m-*.sock' &
    done < hosts
    wait
    i=0
    while IFS= read -r host; do
        sock=/tmp/m-$$-$i.sock
        ssh -R "$sock:$MANAGER_SOCK_DRIVER" \
            -o StreamLocalBindUnlink=yes \
            -o ExitOnForwardFailure=yes \
            -o ConnectTimeout=10 \
            -o LogLevel=QUIET \
            "$host" "MANAGER_SOCK=$sock ~/miniforge3/bin/python3 -" < worker.py &
        i=$((i + 1))
    done < hosts
    wait
) &

python3 "$@"
