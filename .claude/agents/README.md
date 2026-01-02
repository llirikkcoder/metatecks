# Custom Claude Code Subagents

Специализированные агенты для автоматизации задач в AI Office проекте.

## Доступные Агенты

### 1. 🗄️ supabase-admin

**Назначение:** Эксперт по базе данных Supabase PostgreSQL

**Использует:** Skill `supabase-db` для максимальной экспертизы

**Возможности:**
- ✅ Создание миграций с backup напоминаниями
- ✅ RPC функции на pl/pgsql
- ✅ RLS политики для безопасности
- ✅ Оптимизация запросов и индексы
- ✅ Schema design best practices
- ✅ Rollback scripts для всех миграций

**Автоматически используется при:**
- Создании/изменении таблиц
- Написании SQL запросов
- Настройке RLS
- Оптимизации производительности
- Работе с миграциями

**Примеры использования:**

```bash
# Автоматическое использование
"Создай миграцию для добавления поля avatar_url в таблицу users"

# Явное использование
"Use supabase-admin to optimize the slow query in deals table"

# Через Task tool
Task(
  subagent_type='supabase-admin',
  prompt='Create RPC function for getting user statistics'
)
```

**Что гарантирует:**
- ⚠️ Напоминание о backup ПЕРЕД миграцией
- ✅ PostgreSQL-совместимый синтаксис
- ✅ Rollback скрипт для каждой миграции
- ✅ RLS для пользовательских данных
- ✅ Правильные типы данных (TIMESTAMPTZ, JSONB, TEXT)

---

### 2. 🧪 test-runner

**Назначение:** Специалист по тестированию и QA

**Возможности:**
- ✅ Автоматический запуск тестов
- ✅ Анализ test failures с root cause
- ✅ Coverage analysis
- ✅ Создание новых тестов
- ✅ Quality checks (lint, type-check, build)
- ✅ E2E тестирование с Playwright

**Тестовые фреймворки:**
- **Backend:** pytest (Python)
- **Frontend:** Vitest (TypeScript/React)
- **E2E:** Playwright

**Автоматически используется при:**
- Изменениях в коде (после commit)
- Падающих тестах
- Проверках качества
- Создании новых фич

**Примеры использования:**

```bash
# Автоматическое использование
"Run tests after my changes"

# Явное использование
"Use test-runner to analyze why test_user_authentication is failing"

# Проактивное
"Run full test suite and show coverage"

# Создание тестов
"test-runner: create tests for the new billing module"
```

**Что гарантирует:**
- ✅ Полный test execution отчет
- ✅ Root cause analysis для failures
- ✅ Конкретные fixes с кодом
- ✅ Verification после исправлений
- ✅ Coverage recommendations

---

## Как Работают Subagents

### Автоматическое Использование

Claude автоматически определяет, когда использовать subagent, основываясь на вашем запросе:

| Ваш запрос | Используемый Agent |
|------------|-------------------|
| "Add column telegram_id to users table" | `supabase-admin` |
| "Create RPC function for search" | `supabase-admin` |
| "Why is test_login failing?" | `test-runner` |
| "Run frontend tests" | `test-runner` |
| "Check test coverage" | `test-runner` |

### Явное Использование

Вы можете явно попросить использовать конкретный agent:

```
Use supabase-admin to create a migration for notifications table
Use test-runner to check if all tests pass
```

### Через Task Tool (Программно)

```python
# В коде или скриптах
Task(
  description="Create database migration",
  prompt="Add email_verified column to users",
  subagent_type="supabase-admin"
)
```

### Resume (Продолжение Работы)

Каждый subagent возвращает `agentId` который можно использовать для продолжения:

```
Resume agent abc123 and now add RLS policies as well
```

---

## Разница: Skills vs Subagents

| Аспект | Skills | Subagents |
|--------|--------|-----------|
| **Цель** | Добавить знания | Делегировать задачу |
| **Контекст** | Общий с главным диалогом | Изолированный |
| **Инструменты** | Те же что у Claude | Могут отличаться |
| **Когда использовать** | Нужны знания/стандарты | Нужна изоляция/специализация |

**Пример:**
- `supabase-db` **(skill)** - дает Claude знания о Supabase
- `supabase-admin` **(subagent)** - делегирует задачу специалисту

Subagent `supabase-admin` **использует** skill `supabase-db` для экспертизы!

---

## Workflow Примеры

### Создание Миграции

```
Вы: Add balance field to users table

Claude: [Автоматически использует supabase-admin]

supabase-admin:
⚠️ BACKUP REQUIRED
Before applying this migration:
1. Supabase Dashboard → Database → Backups
2. Create backup: "pre-add-balance-2025-12-31"

Migration: migrations/028_add_user_balance.sql
[SQL code with proper PostgreSQL syntax]

Rollback: migrations/028_add_user_balance_rollback.sql
[Rollback SQL]

Apply:
PGPASSWORD="..." psql "..." -f migrations/028_add_user_balance.sql
```

### Тестирование После Изменений

```
Вы: I just modified the auth service, check if tests still pass

Claude: [Автоматически использует test-runner]

test-runner:
🔍 Running tests for auth service...

✅ Results:
- test_user_login: PASSED
- test_user_logout: PASSED
- test_invalid_credentials: FAILED

❌ Failure Analysis:
test_invalid_credentials (tests/test_auth.py:42)
Root Cause: Expected error message changed
Fix: [specific code fix]

Would you like me to apply the fix?
```

---

## Расширение: Создание Новых Агентов

Хотите добавить нового специалиста? Создайте файл `.claude/agents/agent-name.md`:

```markdown
---
name: my-agent
description: When to use this agent
tools: Read, Write, Bash
model: inherit
skills: skill1, skill2
---

# Agent System Prompt

Your agent's expertise and instructions here...
```

**Примеры агентов для будущего:**
- `telegram-bot-dev` - Разработка Telegram ботов
- `ai-agent-builder` - Создание AI агентов
- `react-specialist` - React компоненты
- `api-designer` - Проектирование API

---

## Лучшие Практики

1. **Будьте конкретны в запросах**
   - ❌ "Do something with database"
   - ✅ "Add telegram_username field to users with unique index"

2. **Доверяйте автоматике**
   - Claude сам выберет правильного агента
   - Не нужно всегда указывать явно

3. **Используйте resume для сложных задач**
   - Агент может работать поэтапно
   - Resume продолжает с полным контекстом

4. **Проверяйте результаты**
   - Agents дают код - вы решаете применять или нет
   - Всегда делайте backup как советует supabase-admin

---

## FAQ

**Q: Как узнать, используется ли агент?**

A: Claude явно укажет в ответе, например:
```
[Using supabase-admin agent]
```

**Q: Можно ли отключить автоматическое использование?**

A: Да, просто скажите:
```
Don't use agents, I'll handle this manually
```

**Q: Agents изменяют код автоматически?**

A: Нет! Agents только **предлагают** решения. Вы контролируете выполнение.

**Q: Где логи работы agents?**

A: В `.claude/logs/` (если настроен debug режим)

---

## Текущий Статус

| Agent | Статус | Версия |
|-------|--------|--------|
| supabase-admin | ✅ Активен | 1.0 |
| test-runner | ✅ Активен | 1.0 |

---

**Создано:** 2025-12-31
**Проект:** AI Office
**Автор:** Claude Code Subagents System
