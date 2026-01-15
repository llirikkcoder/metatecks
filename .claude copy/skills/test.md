# Testing Skill

Специализированный навык для написания, исправления и запуска тестов в AI Office проекте.

## Когда использовать этот skill

- Пользователь просит написать тесты
- Пользователь просит исправить падающие тесты
- Пользователь просит проверить покрытие кода
- Пользователь просит запустить тесты
- После внесения изменений в код нужно обновить тесты

## Правила тестирования AI Office

### 1. Структура тестов

```
tests/
├── unit/              # Модульные тесты (изолированные функции/классы)
├── integration/       # Интеграционные тесты (взаимодействие компонентов)
├── database/          # Тесты для database слоя
├── tools/             # Тесты для AI tools
├── telegram/          # Тесты для Telegram bot handlers
└── test_*.py          # Тесты для core модулей
```

### 2. Именование тестов

✅ **ПРАВИЛЬНО:**
```python
def test_create_project_success():
    """Test successful project creation."""

def test_create_project_invalid_type():
    """Test project creation with invalid type."""

class TestDatabaseManager:
    def test_get_today_kpi_when_exists(self):
        """Test getting today's KPI when record exists."""
```

❌ **НЕПРАВИЛЬНО:**
```python
def test1():  # Неясное имя
def testCreateProject():  # Неправильный snake_case
def test_it_works():  # Слишком общее
```

### 3. Использование фикстур

**Для временных файлов:**
```python
def test_with_temp_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

**Для БД:**
```python
@pytest.fixture
def db():
    """Create in-memory SQLite database for testing."""
    database = DatabaseManager(database_url="sqlite:///:memory:")
    yield database
    database.close()
```

**Для моков:**
```python
@pytest.fixture
def mock_service():
    """Mock external service."""
    with patch('module.external_service') as mock:
        mock.return_value = expected_value
        yield mock
```

### 4. Типы тестов и их требования

#### Unit тесты (самые простые)

**Что тестировать:**
- Изолированные функции
- Методы классов без внешних зависимостей
- Логика валидации
- Утилиты

**Требования:**
- Быстрые (< 0.1 сек)
- Изолированные (никаких БД, API, файлов)
- Используют моки для всех зависимостей

**Пример:**
```python
def test_format_date():
    """Test date formatting utility."""
    from ai_office.utils import format_date
    from datetime import datetime

    date = datetime(2025, 12, 25)
    assert format_date(date) == "2025-12-25"
```

#### Integration тесты (средняя сложность)

**Что тестировать:**
- Взаимодействие между компонентами
- Database операции
- Workflow и state transitions

**Требования:**
- Используют in-memory SQLite
- Изолированы от внешних API
- Моки для AI/LLM вызовов

**Пример:**
```python
def test_complete_workflow(db):
    """Test complete task workflow."""
    task = Task(task_id="test-1", description="Test task description")
    task.start()
    task.complete()

    saved = db.fetch_one("SELECT * FROM tasks WHERE task_id = ?", ("test-1",))
    assert saved['status'] == 'completed'
```

#### E2E тесты (избегать)

❌ **НЕ СОЗДАВАТЬ:**
- Тесты требующие Playwright
- Тесты требующие реальные API ключи
- Тесты требующие Docker/сервисы

### 5. Мокирование внешних зависимостей

#### CrewAI Tools
```python
from ai_office.tools import project_tools

# Tools обернуты декоратором @tool, доступ через .func
create_project = project_tools.create_project.func
update_project = project_tools.update_project.func
list_projects = project_tools.list_projects.func
```

#### PostgreSQL адаптер
```python
@patch('psycopg2.connect')
def test_postgres(mock_connect):
    """PostgreSQL adapter returns dicts from RealDictCursor."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    # RealDictCursor возвращает dict, НЕ tuple!
    mock_cursor.fetchone.return_value = {'id': 1, 'name': 'test'}
```

#### Google Drive API
```python
@patch('src.ai_office.tools.google_drive_tools._get_drive_service')
@patch('src.ai_office.tools.google_drive_tools.MediaIoBaseDownload')
@patch('io.BytesIO')
def test_gdrive_download(mock_bytesio, mock_download, mock_service):
    # Mock BytesIO для возврата контента
    mock_fh = MagicMock()
    mock_fh.getvalue.return_value = b"file content"
    mock_bytesio.return_value = mock_fh

    # Mock MediaIoBaseDownload.next_chunk() -> (status, done)
    mock_downloader = MagicMock()
    mock_downloader.next_chunk.return_value = (MagicMock(), True)
    mock_download.return_value = mock_downloader
```

#### LangChain / OpenAI
```python
@patch('ai_office.agents.base.ChatOpenAI')
def test_agent(mock_llm):
    """Mock LLM вызовы."""
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance

    # Создаем агента
    agent = BaseAgent(config=config)
    assert agent.llm is not None
```

### 6. Pydantic валидация

**КРИТИЧЕСКИ ВАЖНО:** Pydantic модели имеют минимальные требования к длине строк!

✅ **ПРАВИЛЬНО:**
```python
task = Task(
    task_id="2025-12-25-001",
    description="Complete task description here",  # >= 10 символов
    assigned_agents=["task_manager"]
)

agent_config = {
    "agent_id": "researcher",
    "role": "Research Specialist",
    "goal": "Find accurate information",
    "backstory": "Expert researcher with deep knowledge",  # >= 20 символов
}
```

❌ **НЕПРАВИЛЬНО:**
```python
task = Task(
    description="Test",  # < 10 символов - ValidationError!
)

agent_config = {
    "backstory": "Expert",  # < 20 символов - ValidationError!
}
```

### 7. Database тесты

**Используйте SQLite для тестов:**
```python
@pytest.fixture
def db():
    """Create in-memory SQLite database for testing."""
    database = DatabaseManager(database_url="sqlite:///:memory:")
    database.connect()

    # Создать необходимые таблицы
    database.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    yield database
    database.close()
```

**Тестирование CRUD операций:**
```python
def test_insert(db):
    """Test insert operation."""
    data = {"name": "test_item"}
    row_id = db.insert("test_table", data)

    assert row_id is not None
    result = db.fetch_one("SELECT * FROM test_table WHERE id = ?", (row_id,))
    assert result["name"] == "test_item"
```

### 8. Покрытие кода (Coverage)

**Цели покрытия:**
- Core database модули: **75%+**
- Core business logic: **70%+**
- Tools: **50%+**
- Handlers: **50%+**

**Запуск с покрытием:**
```bash
# Все тесты с покрытием
python -m pytest --cov=ai_office --cov-report=term-missing

# Конкретный модуль
python -m pytest tests/test_database_manager.py --cov=ai_office.database.manager --cov-report=term-missing

# HTML отчет
python -m pytest --cov=ai_office --cov-report=html
open htmlcov/index.html
```

### 9. Что НЕ нужно тестировать

❌ **Не тестировать:**
- Внешние библиотеки (pytest, CrewAI, LangChain)
- Константы и простые геттеры
- Конфигурационные файлы
- Очевидный код без логики

### 10. Исправление падающих тестов

**Процесс:**

1. **Запустить тест с подробным выводом:**
```bash
python -m pytest tests/path/to/test.py::test_name -vv --tb=long
```

2. **Идентифицировать причину:**
   - `ValidationError` → проверить Pydantic требования (длина строк!)
   - `TypeError: 'Tool' object is not callable` → использовать `.func`
   - `TypeError: cannot convert dict` → проверить моки (dict vs tuple)
   - `FileNotFoundError` → создать временный файл через `tmp_path`
   - `ModuleNotFoundError` → проверить импорты

3. **Типичные исправления:**

**ValidationError:**
```python
# Было
description="Test"  # Слишком короткое

# Стало
description="Test task description"  # >= 10 символов
```

**Tool wrapper:**
```python
# Было
from ai_office.tools.project_tools import create_project
result = create_project(name="Test")  # Tool object is not callable!

# Стало
from ai_office.tools import project_tools
create_project = project_tools.create_project.func
result = create_project(name="Test")
```

**Dict vs Tuple в моках:**
```python
# Было
mock_cursor.fetchone.return_value = (1, "name")  # Tuple

# Стало (для PostgreSQL/RealDictCursor)
mock_cursor.fetchone.return_value = {'id': 1, 'name': 'name'}  # Dict
```

**Временные файлы:**
```python
# Было
@patch('os.path.exists')
def test_upload(mock_exists):
    mock_exists.return_value = True
    result = upload_file('/fake/path.txt')  # Файл не существует!

# Стало
def test_upload(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    result = upload_file(str(test_file))  # Реальный файл
```

### 11. Запуск тестов

**Основные команды:**
```bash
# Все тесты
python -m pytest

# С подробным выводом
python -m pytest -v

# Конкретный файл
python -m pytest tests/test_database_manager.py

# Конкретный класс
python -m pytest tests/test_database_manager.py::TestDatabaseManagerKPIMethods

# Конкретный тест
python -m pytest tests/test_database_manager.py::TestDatabaseManagerKPIMethods::test_get_today_kpi_when_exists

# Тесты по паттерну
python -m pytest -k "kpi"

# Быстрый запуск (без покрытия)
python -m pytest --no-cov

# Остановка на первой ошибке
python -m pytest -x

# С покрытием и минимальным порогом
python -m pytest --cov=ai_office --cov-fail-under=50
```

### 12. Best Practices

✅ **DO:**
- Писать понятные docstrings для тестов
- Использовать AAA паттерн (Arrange, Act, Assert)
- Тестировать edge cases (пустые списки, None, исключения)
- Использовать параметризацию для похожих тестов
- Изолировать тесты (каждый независим)
- Мокировать внешние зависимости
- Использовать descriptive assertion messages

```python
def test_list_projects_with_filters(db):
    """Test listing projects with filters."""
    # Arrange - настройка
    db.insert("projects", {"name": "Project 1", "status": "active"})
    db.insert("projects", {"name": "Project 2", "status": "completed"})

    # Act - выполнение
    result = list_projects(status="active")

    # Assert - проверка
    assert result['success'] is True
    assert result['count'] == 1
    assert result['projects'][0]['name'] == "Project 1"
```

❌ **DON'T:**
- Тестировать несколько не связанных вещей в одном тесте
- Зависеть от порядка выполнения тестов
- Использовать sleep() - используйте моки
- Создавать реальные файлы вне tmp_path
- Делать реальные API вызовы
- Использовать хардкод путей
- Игнорировать warnings

### 13. Параметризация тестов

**Для множества похожих случаев:**
```python
@pytest.mark.parametrize("status,expected_count", [
    ("active", 2),
    ("completed", 1),
    ("planning", 0),
])
def test_filter_by_status(db, status, expected_count):
    """Test filtering projects by different statuses."""
    db.insert("projects", {"name": "P1", "status": "active"})
    db.insert("projects", {"name": "P2", "status": "active"})
    db.insert("projects", {"name": "P3", "status": "completed"})

    result = list_projects(status=status)
    assert result['count'] == expected_count
```

### 14. Тестирование исключений

```python
def test_create_project_invalid_type():
    """Test project creation with invalid type."""
    from pydantic_core import ValidationError

    with pytest.raises(ValidationError, match="Invalid project_type"):
        create_project(
            name="Test Project",
            project_type="invalid_type"
        )
```

### 15. Async тесты

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Test asynchronous operation."""
    result = await async_function()
    assert result is not None
```

## Workflow: Как писать новые тесты

1. **Определить тип теста:** unit, integration или database
2. **Создать файл:** `tests/{category}/test_{module_name}.py`
3. **Создать тестовый класс:** `class Test{FeatureName}:`
4. **Создать фикстуры:** для БД, моков, временных файлов
5. **Написать тесты:** покрыть success cases, edge cases, error cases
6. **Запустить:** `python -m pytest tests/path/to/test.py -v`
7. **Проверить покрытие:** `pytest --cov=module --cov-report=term-missing`
8. **Исправить:** если coverage < целевого процента

## Workflow: Как исправить падающие тесты

1. **Запустить с подробным выводом:**
   ```bash
   python -m pytest path/to/test.py::test_name -vv --tb=long
   ```

2. **Прочитать traceback снизу вверх** - найти реальную причину

3. **Типичные причины и решения:**
   - ValidationError → удлинить строки (description >= 10, backstory >= 20)
   - Tool not callable → добавить `.func`
   - Dict/tuple mismatch → проверить моки
   - File not found → использовать `tmp_path`
   - Import error → проверить путь импорта

4. **Исправить и проверить:**
   ```bash
   python -m pytest path/to/test.py::test_name -v
   ```

5. **Запустить все тесты:**
   ```bash
   python -m pytest --no-cov
   ```

## Примеры полных тестов

### Unit тест
```python
def test_format_currency():
    """Test currency formatting utility."""
    from ai_office.utils import format_currency

    assert format_currency(1000) == "1,000 ₽"
    assert format_currency(1500.50) == "1,500.50 ₽"
    assert format_currency(0) == "0 ₽"
```

### Database тест
```python
@pytest.fixture
def db():
    database = DatabaseManager(database_url="sqlite:///:memory:")
    database.connect()
    database.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT)")
    yield database
    database.close()

def test_get_tasks_by_status(db):
    """Test getting tasks filtered by status."""
    db.insert("tasks", {"title": "Task 1", "status": "pending"})
    db.insert("tasks", {"title": "Task 2", "status": "completed"})

    pending = db.get_tasks_by_status("pending")
    assert len(pending) == 1
    assert pending[0]['title'] == "Task 1"
```

### Tool тест с моками
```python
@patch('ai_office.tools.project_tools.get_db')
def test_create_project(mock_get_db):
    """Test project creation tool."""
    from ai_office.tools import project_tools
    create_project = project_tools.create_project.func

    mock_db = MagicMock()
    mock_db.fetch_one.side_effect = [
        None,  # No existing project
        {'id': 1, 'name': 'Test Project'}  # Created project
    ]
    mock_get_db.return_value = mock_db

    result = create_project(
        name="Test Project",
        project_type="internal",
        auth_owner_id="test-uuid"
    )

    assert result['success'] is True
    assert result['project_id'] == 1
```

## Итоговый чеклист

При написании/исправлении тестов проверьте:

- [ ] Тест имеет понятное имя `test_{what}_{condition}`
- [ ] Есть docstring объясняющий что тестируется
- [ ] Используется правильная фикстура (db, tmp_path, моки)
- [ ] Все строки соответствуют Pydantic требованиям (description >= 10, backstory >= 20)
- [ ] CrewAI tools доступны через `.func`
- [ ] PostgreSQL моки возвращают dict, не tuple
- [ ] Файловые операции используют tmp_path
- [ ] Внешние зависимости замокированы
- [ ] Тест изолирован и независим
- [ ] Используется AAA паттерн (Arrange, Act, Assert)
- [ ] Проверены edge cases
- [ ] Тест проходит: `pytest path/to/test.py::test_name -v`
- [ ] Покрытие достаточное: `pytest --cov=module`

---

**Документация:**
- См. `tests/README.md` для quick reference
- См. `docs/TESTING_GUIDE.md` для полного руководства
- Текущее покрытие: **147 passing tests**, 0 failures
