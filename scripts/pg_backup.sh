#!/bin/bash
#
# Ежедневный дамп базы metateks с ротацией.
#
# До 21.08.2026 регулярных бэкапов не было вообще: в /opt/metatecks/backups
# лежал один архив от 31.12.2025. В тот день переполнение диска уронило
# Postgres в recovery — восстановился сам, но при другом раскладе потеряли бы
# всё, включая заказы с оплатами.
#
# Ставится скриптом vps_disk_hygiene.sh в /usr/local/bin/metateks-pg-backup
# и запускается из /etc/cron.d/metateks-backup.
#
# Ручной запуск:  /usr/local/bin/metateks-pg-backup
# Восстановление: docker exec -i metateks_db pg_restore -U <user> -d <db> \
#                     --clean --if-exists < metateks_ГГГГММДД_ЧЧММСС.dump
#
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/opt/metatecks/backups}"
CONTAINER="${CONTAINER:-metateks_db}"
KEEP="${KEEP:-14}"
MIN_FREE_MB="${MIN_FREE_MB:-3072}"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }

mkdir -p "$BACKUP_DIR"

# Бэкап не должен сам доводить диск до того состояния, из-за которого он
# понадобился: при нехватке места отказываемся с ошибкой, а не пишем впритык.
free_mb=$(df -Pm "$BACKUP_DIR" | awk 'NR==2 {print $4}')
if [ "$free_mb" -lt "$MIN_FREE_MB" ]; then
    log "ОТМЕНА: свободно ${free_mb} МБ, нужно минимум ${MIN_FREE_MB} МБ"
    exit 1
fi

if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || echo false)" != "true" ]; then
    log "ОШИБКА: контейнер $CONTAINER не запущен"
    exit 1
fi

stamp=$(date '+%Y%m%d_%H%M%S')
target="$BACKUP_DIR/metateks_${stamp}.dump"
tmp="${target}.tmp"

log "Дамп -> $(basename "$target")"

# -Fc — собственный формат pg_dump: уже сжат и восстанавливается выборочно.
# Логин и база берутся из окружения самого контейнера, пароли наружу не ходят.
if ! docker exec "$CONTAINER" sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$tmp"; then
    log "ОШИБКА: pg_dump упал, частичный файл удалён"
    rm -f "$tmp"
    exit 1
fi

# Оборванный дамп страшнее отсутствующего: он выглядит как рабочий бэкап.
size=$(stat -c %s "$tmp")
if [ "$size" -lt 1048576 ]; then
    log "ОШИБКА: дамп всего ${size} байт — это не похоже на рабочую базу"
    rm -f "$tmp"
    exit 1
fi

mv "$tmp" "$target"
log "Готово, размер $(du -h "$target" | cut -f1)"

# Ротация. Маска metateks_*.dump намеренно не задевает старые архивы
# metateks_backup_*.tar.gz — их удаляем только руками.
count=$(find "$BACKUP_DIR" -maxdepth 1 -name 'metateks_*.dump' | wc -l)
if [ "$count" -gt "$KEEP" ]; then
    find "$BACKUP_DIR" -maxdepth 1 -name 'metateks_*.dump' -printf '%T@ %p\n' \
        | sort -rn | tail -n +$((KEEP + 1)) | cut -d' ' -f2- \
        | while read -r old; do
            log "Удаляю старый дамп: $(basename "$old")"
            rm -f "$old"
        done
fi

log "Дампов: $(find "$BACKUP_DIR" -maxdepth 1 -name 'metateks_*.dump' | wc -l), каталог занимает $(du -sh "$BACKUP_DIR" | cut -f1)"
