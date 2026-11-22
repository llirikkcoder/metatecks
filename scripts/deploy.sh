#!/bin/bash
# Called by the SSH workflow after fetching the exact revision, under flock.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
guard_script="$PWD/scripts/celery_deploy_guard.py"
old_worker=""
resume_needed=0

guard() {
    docker exec -i "$old_worker" python - "$@" < "$guard_script"
}

cleanup() {
    result=$?
    trap - EXIT INT TERM
    if [ "$resume_needed" = 1 ]; then
        running=$(docker inspect -f '{{.State.Running}}' "$old_worker" 2>/dev/null || true)
        if [ "$running" = true ]; then
            if ! guard resume; then
                echo "ERROR: consumers could not resume on $old_worker; manual recovery required" >&2
                result=1
            fi
        elif docker inspect "$old_worker" >/dev/null 2>&1; then
            echo "ERROR: old worker is stopped; inspect deployment before restarting it" >&2
            result=1
        fi
    fi
    exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

free_mb=$(df -Pm . | awk 'NR==2 {print $4}')
if [ "$free_mb" -lt 3072 ]; then
    echo "ERROR: only $free_mb MiB free, at least 3072 required before build" >&2
    exit 1
fi

# A build failure leaves the original worker consuming normally.
docker compose build web celery
# Run against the candidate image; bypass entrypoint to avoid migrations/indexing.
docker compose run --rm --no-deps -T --entrypoint python \
    -e PYTHONPATH=/app \
    -v "$PWD/scripts/test_search_pagination.py:/tmp/test_search_pagination.py:ro" \
    web /tmp/test_search_pagination.py
old_worker=$(docker compose ps -q celery)
if [ -z "$old_worker" ] || [[ "$old_worker" = *$'\n'* ]]; then
    echo "ERROR: expected exactly one running celery container" >&2
    exit 1
fi
resume_needed=1
echo "Draining old celery container: $old_worker"
guard drain

# The old worker stays alive but paused until web has migrated and is healthy.
docker compose up -d --no-deps web
for attempt in $(seq 1 30); do
    if curl --max-time 5 -fsS -o /dev/null http://127.0.0.1:8001/health/; then
        break
    fi
    if [ "$attempt" = 30 ]; then
        docker compose logs --tail=50 web
        echo "ERROR: web did not become healthy; old worker will resume" >&2
        exit 1
    fi
    sleep 10
done

# Re-read the upstream's IP without restarting nginx when config is unchanged.
docker compose up -d --no-deps nginx
docker compose exec -T nginx nginx -t
docker compose exec -T nginx nginx -s reload
curl --max-time 15 -fsS -o /dev/null -H 'Host: metateks.ru' http://127.0.0.1:8080/

# No consumer can acquire a task in the gap before the old container is stopped.
docker compose up -d --no-deps celery
new_worker=$(docker compose ps -q celery)
if [ -z "$new_worker" ]; then
    echo "ERROR: new celery container is not running" >&2
    exit 1
fi
if [ "$new_worker" = "$old_worker" ]; then
    guard resume
fi
for attempt in $(seq 1 12); do
    if docker exec -i "$new_worker" python - check < "$guard_script"; then
        break
    fi
    [ "$attempt" -lt 12 ] || { echo "ERROR: celery did not become ready" >&2; exit 1; }
    sleep 5
done
resume_needed=0

docker image prune -f
docker compose ps
echo "Deployment completed successfully"
