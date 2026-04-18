---
name: trello
description: "Получение тикетов, досок, списков и карточек из Trello через REST API. Используй когда пользователь просит: получить задачу из Trello, показать карточку, загрузить вложения/скриншоты карточки, найти тикеты на доске, распарсить ссылку на Trello-карточку."
version: "1.0.0"
last_updated: "2026-04-18"
user_invocable: true
---

# Trello Skill

Получение данных из Trello через REST API: карточки, вложения, списки, доски.

## Routing

Первым делом определи что хочет пользователь:

- **"получи карточку <URL>"** или `trello.com/c/<id>` в сообщении → [Получить карточку по URL](#получить-карточку-по-url)
- **"покажи вложения карточки"** или **"скачай скриншоты из карточки"** → [Получить вложения](#получить-вложения-карточки)
- **"покажи карточки с доски"** или **"список задач"** → [Карточки доски](#карточки-доски)
- **"найди тикет про X"** → [Поиск](#поиск)
- **"покажи мои доски"** → [Список досок](#мои-доски)

## Credentials

Данные доступа лежат в `.claude/skills/trello/config.json` (НЕ коммитится):

```json
{
  "key": "<API_KEY>",
  "token": "<API_TOKEN>"
}
```

**ВАЖНО:** если `config.json` отсутствует — сообщи пользователю и попроси:
1. Получить API key на https://trello.com/app-key
2. Сгенерировать токен по ссылке: `https://trello.com/1/authorize?expiration=never&scope=read&response_type=token&name=ClaudeCode&key=<KEY>`
3. Вписать в `config.json`

Читай credentials так:
```bash
KEY=$(jq -r .key .claude/skills/trello/config.json)
TOKEN=$(jq -r .token .claude/skills/trello/config.json)
```

Или через Python/Node — выбирай что проще в текущем окружении.

## Базовый запрос

Все запросы к Trello API идут на `https://api.trello.com/1/<endpoint>` с параметрами `?key=<KEY>&token=<TOKEN>`.

```bash
curl -s "https://api.trello.com/1/cards/<CARD_ID>?key=${KEY}&token=${TOKEN}"
```

Всегда парси JSON через `jq` и выводи пользователю структурировано.

## Операции

### Получить карточку по URL

URL вида `https://trello.com/c/<SHORT_ID>/<slug>` или `https://trello.com/1/cards/<ID>/...`

Извлеки `<SHORT_ID>` или `<ID>` из URL, затем:

```bash
curl -s "https://api.trello.com/1/cards/${CARD_ID}?key=${KEY}&token=${TOKEN}&attachments=true&checklists=all&members=true"
```

Выведи:
- Название (`name`)
- Описание (`desc`)
- Статус (`closed`, `dueComplete`)
- Дедлайн (`due`)
- Участники (`members[].fullName`)
- Чеклисты (`checklists[].name` + `checkItems`)
- Вложения (`attachments[].name`, `url`)
- Ссылка (`shortUrl`)

### Получить вложения карточки

```bash
curl -s "https://api.trello.com/1/cards/${CARD_ID}/attachments?key=${KEY}&token=${TOKEN}"
```

Для скачивания файла — используй `url` из результата. Вложения Trello требуют авторизации через header:

```bash
curl -L -H "Authorization: OAuth oauth_consumer_key=\"${KEY}\", oauth_token=\"${TOKEN}\"" \
  "${ATTACHMENT_URL}" -o "<filename>"
```

Сохраняй во временную папку: `./tmp/trello/<card_id>/<filename>`.

### Карточки доски

Сначала получи ID доски (или возьми из URL `trello.com/b/<BOARD_ID>`):

```bash
curl -s "https://api.trello.com/1/boards/${BOARD_ID}/cards?key=${KEY}&token=${TOKEN}&fields=name,desc,shortUrl,due,dueComplete,idList,labels"
```

Для получения названий списков:
```bash
curl -s "https://api.trello.com/1/boards/${BOARD_ID}/lists?key=${KEY}&token=${TOKEN}&fields=name"
```

Выведи таблицей: `Список | Название | Срок | Ссылка`.

### Поиск

```bash
curl -s "https://api.trello.com/1/search?key=${KEY}&token=${TOKEN}&query=<QUERY>&modelTypes=cards&card_fields=name,desc,shortUrl"
```

Query поддерживает Trello operators: `@me`, `#label`, `list:Done`, `board:<id>`, `is:open`.

### Мои доски

```bash
curl -s "https://api.trello.com/1/members/me/boards?key=${KEY}&token=${TOKEN}&fields=name,shortUrl,closed&filter=open"
```

## Обработка ошибок

- **401 Unauthorized** → токен истёк или невалиден. Сообщи пользователю и попроси сгенерировать новый.
- **404 Not Found** → карточка/доска не существует или нет доступа.
- **429 Too Many Requests** → rate limit. Подожди 10 секунд, повтори.

## Примеры полезных полей

```json
{
  "id": "...",
  "name": "...",
  "desc": "markdown text",
  "due": "2026-03-07T12:00:00.000Z",
  "dueComplete": false,
  "closed": false,
  "shortUrl": "https://trello.com/c/abc123",
  "url": "https://trello.com/c/abc123/456-full-slug",
  "idBoard": "...",
  "idList": "...",
  "labels": [{"name": "bug", "color": "red"}],
  "members": [{"fullName": "..."}],
  "attachments": [{"name": "...", "url": "...", "mimeType": "image/webp"}],
  "checklists": [{"name": "...", "checkItems": [{"name": "...", "state": "complete"}]}]
}
```

## Важные правила

1. **Никогда не пиши `key` и `token` в видимый код или commit** — только читай из `config.json`
2. **Не логируй полный URL с токеном** — маскируй при выводе: `?key=***&token=***`
3. **Не сохраняй вложения в репозиторий** — используй `./tmp/trello/` и предупреждай что папка во временном хранилище
4. Если пользователь даёт URL на картинку с `trello.com/1/cards/.../attachments/.../download/...` — это authenticated endpoint, скачивай с OAuth header
