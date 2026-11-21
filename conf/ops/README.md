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
| `cron-metateks-backup` | `/etc/cron.d/metateks-backup` | дамп PostgreSQL ежедневно в 03:30 по времени сервера |

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

## Бэкапы и логи: исправление 21.11.2026

Последний ночной дамп был за 17 ноября. В сохранившихся логах за 14–15 и
18–21 ноября cron запускался, но `pg_backup.sh` отказывался писать при
свободном месте меньше `MIN_FREE_MB=3072`. Ротация выполняется только после
успешного нового дампа, поэтому сама по себе место для очередного запуска
не освобождает. Порог 3 ГБ сохранён: освобождать нужно занятое место.

В контейнере nginx обнаружено 2,1 ГБ файлов `metateks_access.log` и
`metateks_error.log`. Они не попадали ни в logrotate хоста, ни в ротацию
Docker. Теперь nginx пишет в stdout/stderr, а для сервиса nginx в Compose
явно задан `json-file`, 50 МБ × 3. Это требует пересоздания **только nginx**:

```bash
docker compose exec -T nginx nginx -t
docker compose up -d --no-deps nginx
docker inspect metateks_nginx --format '{{json .HostConfig.LogConfig}}'
```

Старые файлы логов нужно сохранить до пересоздания контейнера. Не запускать
полный `docker compose up` ради этих изменений: web и Celery не менялись.
Ротация Django дополнительно покрывает `/opt/metatecks/logs/*.log`.

`scripts/pg_backup.sh` устанавливается отдельно от образов приложения:

```bash
install -m 755 scripts/pg_backup.sh /usr/local/bin/metateks-pg-backup
install -m 644 conf/ops/logrotate-metateks /etc/logrotate.d/metateks
chmod 700 /opt/metatecks/backups
find /opt/metatecks/backups -maxdepth 1 -type f -name '*.dump' -exec chmod 600 {} +
/usr/local/bin/metateks-pg-backup
```

Новые дампы имеют права 600. `flock` исключает параллельные запуски, временный
файл удаляется при ошибке или сигнале. До публикации и удаления старых дампов
`pg_restore --file=/dev/null` читает и распаковывает весь архив без подключения
к базе. Хранятся последние 14 успешных дампов. Проверка скрипта на Linux:
`python3 scripts/test_pg_backup.py` (подставные команды, рабочую БД не трогает).

Ручная проверка cron и запаса диска:

```bash
df -h /
tail -30 /var/log/metateks/pg_backup.log
find /opt/metatecks/backups -maxdepth 1 -name 'metateks_*.dump' -printf '%TY-%Tm-%Td %TH:%TM %f\n' | sort
```

Регулярного хранения вне VPS пока нет. Ручная копия на рабочем Mac не заменяет
автоматический внешний бэкап. Нельзя удалять единственный исторический архив
без проверенной копии на другом устройстве.

### Проверенный результат 21 ноября

- Создан `metateks_20261121_172232.dump`, 175 672 200 байт, права 600.
- Проверенная копия находится на Mac в
  `/Users/omoto/Projects/metatecks/backups/ops-20261121/` (игнорируется Git).
  SHA-256 обеих копий:
  `75a9cec47d36a6e0924e244f1f6a607c67fa5ea7619684ee0be4c660030599c1`.
- Полностью восстановлен в отдельный PostgreSQL на том же образе, что прод,
  без сети, с ограничением 512 МБ памяти и одного CPU. Восстановились 99 таблиц
  и 301 индекс, размер базы — 1233 МБ. Временные контейнер и volume удалены.
- Скрипт проверки и протокол сохранены на VPS в
  `/root/metateks-ops-20261121/verify-restore.sh` и `restore-check.log`.
- Логи старого nginx сохранены в
  `/var/log/metateks/nginx/legacy-container-20261121.tar.gz` (155 МБ), архив
  прошёл `gzip -t` и проверку списка файлов. Исторический архив БД за 2025 год
  оставлен на сервере.
- После пересоздания только nginx и удаления кеша сборки старше 48 часов
  свободно 5,8 ГБ (80% занято) против 2,6 ГБ (91%). Web, Celery, PostgreSQL и
  Redis не перезапускались. Главная, поиск и healthcheck отвечают 200.

Ops-коммит помечен `[skip ci]`: конфиги и скрипт применены вручную описанными
выше командами, полный автодеплой приложения для этих изменений не нужен.

## Что осталось вне скрипта

`/usr/app` — 4.4 ГБ остатков развёртывания вне Docker (`back/media` на 1.7 ГБ).
Ни один активный конфиг на него не ссылается. Трогать автоматикой нельзя:
сначала нужно сверить, что медиафайлы оттуда есть в `/opt/metatecks/media`.

## nginx-default-drop.conf

Catch-all для host-nginx: обрывает запросы с чужим Host (444) и отклоняет
TLS-хендшейк с чужим SNI (`ssl_reject_handshake`, nginx >= 1.19.4). Поставлен
28.08.2026 при отвязке домена metateks.vlch.dev прежнего разработчика — его
DNS-запись всё ещё указывает на наш IP, удалить её может только владелец зоны.

```bash
install -m 644 conf/ops/nginx-default-drop.conf /etc/nginx/sites-available/000-default-drop.conf
ln -sf /etc/nginx/sites-available/000-default-drop.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Сертификат metateks.vlch.dev и его автопродление удалены с сервера
(`certbot delete --cert-name metateks.vlch.dev`).

## nginx-1c-exchange.conf — лимиты для обмена с 1С

Ставится в `/etc/nginx/sites-available/metateks-docker.conf`, перед `location /`.
Бэкап прежнего конфига при правке 16.09.2026:
`/etc/nginx/sites-available/metateks-docker.conf.bak-20260916`.

Без этого блока 1С получает **413** на загрузке каталога: полная выгрузка
весит ~186 МБ при общем лимите 100 МБ, плюс таймаут 60s вместо нужных 600s.
Запрос при этом не доходит до Django, поэтому в админке «Обмен с 1C» пусто —
выглядит так, будто 1С вообще не обращалась. Смотреть надо
`/var/log/nginx/metateks-docker_access.log`.
