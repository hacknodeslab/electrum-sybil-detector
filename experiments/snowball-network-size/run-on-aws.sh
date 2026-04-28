#!/usr/bin/env bash
# Run the Phase-1 snowball crawl on a remote IPv6-enabled AWS instance to
# bypass the IPv4-only routing limitation on the local Mac. Reuses the
# unchanged snowball.py — what changes is just where it executes.
#
# Usage:
#   ./run-on-aws.sh -h <host> -i ~/.ssh/<key>.pem [-u <user>] [--skip-preflight]
#
# Outputs (next to this script):
#   discovered-aws.json   crawler dump (full host records)
#   run-aws.log           stdout of the run, including the summary banner

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST=""
SSH_USER="${USER}"          # defaults to local system user, override with -u
KEY=""
SKIP_PREFLIGHT=0
REMOTE_DIR="/tmp/snowball-$(date -u +%Y%m%d-%H%M%S)"

usage() {
    cat <<USAGE
Usage: $0 -h <host> -i <ssh-key> [-u <user>] [--skip-preflight]

  -h, --host         SSH target hostname/IP (e.g. ec2-3-x-x-x.compute.amazonaws.com)
  -i, --identity     Path to SSH private key (.pem)
  -u, --user         Remote SSH user (default: \$USER = "${USER}")
  --skip-preflight   Skip the IPv6 reachability check on the remote
  --help             Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--host)        HOST="$2"; shift 2 ;;
        -i|--identity)    KEY="$2"; shift 2 ;;
        -u|--user)        SSH_USER="$2"; shift 2 ;;
        --skip-preflight) SKIP_PREFLIGHT=1; shift ;;
        --help)           usage; exit 0 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ -z "$HOST" || -z "$KEY" ]]; then
    echo "error: --host and --identity are required" >&2
    usage; exit 2
fi
if [[ "$HOST" == *"@"* ]]; then
    echo "error: --host should be hostname only (got '$HOST'); pass the user via -u" >&2
    exit 2
fi
if [[ -z "$SSH_USER" ]]; then
    echo "error: empty SSH user (\$USER unset and -u not passed)" >&2
    exit 2
fi
if [[ ! -f "$KEY" ]]; then
    echo "error: key file not found: $KEY" >&2
    exit 2
fi
INST_HOST="${SSH_USER}@${HOST}"

SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)
SCP_OPTS=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)

banner() { printf '\n=== %s ===\n' "$*"; }

# -------------------------------------------------------------------
banner "1/4 IPv6 pre-flight on $INST_HOST (user=$SSH_USER host=$HOST)"
if [[ $SKIP_PREFLIGHT -eq 0 ]]; then
    ssh "${SSH_OPTS[@]}" "$INST_HOST" '
        set +e
        echo "-- global v6 addrs --"
        ip -6 addr show scope global 2>/dev/null | grep "inet6 " || echo "(none)"
        echo "-- default v6 route --"
        ip -6 route show default 2>/dev/null || echo "(none)"
        echo "-- v6 outbound test --"
        curl -6 -sS --max-time 5 https://ipv6.google.com -o /dev/null \
             -w "result http=%{http_code} remote=%{remote_ip} time=%{time_total}s\n" \
          || echo "FAILED — instance has no working v6 outbound"
    '
    echo
    read -r -p "continue with the crawl? [y/N] " ans
    [[ "$ans" =~ ^[yY]$ ]] || { echo "aborted"; exit 1; }
else
    echo "(skipped via --skip-preflight)"
fi

# -------------------------------------------------------------------
banner "2/4 staging inputs to $INST_HOST:$REMOTE_DIR"
ssh "${SSH_OPTS[@]}" "$INST_HOST" "mkdir -p '$REMOTE_DIR'"
scp "${SCP_OPTS[@]}" \
    "$SCRIPT_DIR/snowball.py" \
    "$SCRIPT_DIR/bootstrap.json" \
    "$INST_HOST:$REMOTE_DIR/"

# -------------------------------------------------------------------
banner "3/4 running snowball.py remotely"
# Stream output live with `tee` on the remote side, so cancelling locally still
# leaves a usable log on the host. exec via bash -lc to ensure PATH has python3.
ssh "${SSH_OPTS[@]}" "$INST_HOST" \
    "cd '$REMOTE_DIR' && python3 snowball.py 2>&1 | tee '$REMOTE_DIR/run-aws.log'"

# -------------------------------------------------------------------
banner "4/4 retrieving outputs"
scp "${SCP_OPTS[@]}" \
    "$INST_HOST:$REMOTE_DIR/discovered.json" \
    "$SCRIPT_DIR/discovered-aws.json"
scp "${SCP_OPTS[@]}" \
    "$INST_HOST:$REMOTE_DIR/run-aws.log" \
    "$SCRIPT_DIR/run-aws.log"

# -------------------------------------------------------------------
banner "DONE"
echo "  $SCRIPT_DIR/discovered-aws.json"
echo "  $SCRIPT_DIR/run-aws.log"
echo
echo "remote workdir left at $INST_HOST:$REMOTE_DIR (clean it manually if needed)"
echo
echo "summary from the remote run:"
tail -n 30 "$SCRIPT_DIR/run-aws.log"
