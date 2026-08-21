#!/bin/bash
#
# Профилактика переполнения диска на VPS.
#
# 21.08.2026 прод лёг: диск заполнился на 100%, Postgres не смог записать WAL и
# ушёл в recovery. Первопричина — на сервере не установлен logrotate, поэтому
# логи не ротировались ни разу с момента развёртывания.
#
# Скрипт идемпотентен, повторный запуск безопасен.
#
#   bash scripts/vps_disk_hygiene.sh            # только настройка на будущее
#   bash scripts/vps_disk_hygiene.sh --reclaim  # + освободить место прямо сейчас
#
set -euo pipefail

RECLAIM=0
[ "${1:-}" = "--reclaim" ] && RECLAIM=1

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONF_DIR="$REPO_DIR/conf/ops"

say() { echo -e "\033[1;33m==> $1\033[0m"; }

if [ "$(id -u)" -ne 0 ]; then
    echo "Нужны права root" >&2
    exit 1
fi

say "Диск до:"
df -h /

# --------------------------------------------------------------------------
# 1. logrotate. Конфиги в /etc/logrotate.d/ лежали, а самого пакета не было —
#    поэтому не ротировался ни один лог, включая /var/log/nginx/*.log.
# --------------------------------------------------------------------------
if ! command -v logrotate >/dev/null 2>&1; then
    say "Устанавливаю logrotate"
    apt-get update -qq
    apt-get install -y -qq logrotate
else
    say "logrotate уже установлен: $(logrotate --version | head -1)"
fi

say "Конфиг ротации логов проекта -> /etc/logrotate.d/metateks"
install -m 644 "$CONF_DIR/logrotate-metateks" /etc/logrotate.d/metateks

# --------------------------------------------------------------------------
# 2. Лимит systemd-журнала.
# --------------------------------------------------------------------------
say "Лимит journald -> /etc/systemd/journald.conf.d/metateks.conf"
mkdir -p /etc/systemd/journald.conf.d
install -m 644 "$CONF_DIR/journald-metateks.conf" /etc/systemd/journald.conf.d/metateks.conf
systemctl restart systemd-journald

# --------------------------------------------------------------------------
# 3. Ротация логов контейнеров. Без daemon.json json-file-логи растут без
#    предела: на 21.08.2026 один контейнер накопил 725 МБ.
#    Лимит применяется только к пересозданным контейнерам (docker-compose up -d
#    --force-recreate), уже существующие продолжают писать по-старому.
# --------------------------------------------------------------------------
if [ -f /etc/docker/daemon.json ]; then
    say "/etc/docker/daemon.json уже существует — не трогаю, слейте вручную:"
    cat "$CONF_DIR/docker-daemon.json"
else
    say "Ротация логов контейнеров -> /etc/docker/daemon.json"
    mkdir -p /etc/docker
    install -m 644 "$CONF_DIR/docker-daemon.json" /etc/docker/daemon.json
    systemctl reload docker || systemctl restart docker
fi

# --------------------------------------------------------------------------
# 4. Освобождение места (только с --reclaim).
# --------------------------------------------------------------------------
if [ "$RECLAIM" -eq 1 ]; then
    say "Чищу кеш сборки и неиспользуемые образы Docker"
    docker builder prune -af || true
    docker image prune -af || true

    say "Обнуляю разросшиеся логи"
    # Именно truncate, а не удаление: nginx держит файлы открытыми, после rm
    # место не вернётся до перезапуска процесса.
    for f in /var/log/nginx/*.log /var/log/metateks/nginx/*.log /var/log/btmp; do
        [ -f "$f" ] && truncate -s 0 "$f"
    done

    say "Ужимаю systemd-журнал"
    journalctl --vacuum-size=200M >/dev/null

    say "Прогоняю logrotate принудительно"
    logrotate -f /etc/logrotate.conf || true
fi

say "Диск после:"
df -h /
