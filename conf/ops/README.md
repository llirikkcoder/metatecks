# Эксплуатационные конфиги сервера

Здесь лежит то, что ставится **на хост** VPS, а не внутрь контейнеров.
В отличие от `conf/vps/` (устаревшие конфиги дооркестрационного развёртывания),
эти файлы актуальны и применяются скриптом `scripts/vps_disk_hygiene.sh`.

Все файлы — с переводами строк LF: они копируются на Linux как есть.

## Зачем

21.08.2026 прод лёг с `OperationalError: the database system is in recovery mode`.
Диск был занят на 100%, Postgres не смог записать WAL и аварийно завершился:

```
PANIC: could not write to file "pg_logical/replorigin_checkpoint.tmp": No space left on device
```

Первопричина — **на сервере не установлен `logrotate`**. Конфиги в
`/etc/logrotate.d/` присутствовали (их кладут пакеты nginx, postgresql, redis),
но сам пакет отсутствовал, поэтому не ротировался ни один лог. За восемь месяцев
`/var/log/nginx/metateks-docker_access.log` вырос до 1.5 ГБ.

Вторая причина — `docker-compose build --no-cache` на каждый деплой: старый образ
оставался мёртвым грузом, кеш сборки рос. К моменту аварии — 5.9 ГБ образов и
4.1 ГБ кеша при разделе в 30 ГБ.

## Файлы

| Файл | Куда ставится | Что делает |
|---|---|---|
| `logrotate-metateks` | `/etc/logrotate.d/metateks` | ротация логов, которые не покрывает пакетный конфиг nginx |
| `journald-metateks.conf` | `/etc/systemd/journald.conf.d/metateks.conf` | лимит systemd-журнала 200 МБ вместо 10% раздела |
| `docker-daemon.json` | `/etc/docker/daemon.json` | ротация json-логов контейнеров, 50 МБ × 3 |

## Применение

```bash
ssh root@5.188.138.16
cd /opt/metatecks
git pull origin main
bash scripts/vps_disk_hygiene.sh            # настройка на будущее
bash scripts/vps_disk_hygiene.sh --reclaim  # + освободить место сейчас
```

Лимит на логи контейнеров действует только для **пересозданных** контейнеров —
уже запущенные продолжают писать по-старому, пока не будет
`docker-compose up -d --force-recreate`.

## Что осталось вне скрипта

`/usr/app` — 4.4 ГБ остатков развёртывания вне Docker (`back/media` на 1.7 ГБ).
Ни один активный конфиг на него не ссылается. Трогать автоматикой нельзя:
сначала нужно сверить, что медиафайлы оттуда есть в `/opt/metatecks/media`.
