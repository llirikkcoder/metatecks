# Tasks: Исправление ошибок развертывания Docker

**Input**: Design documents from `/specs/002-fix-docker-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests NOT explicitly requested in spec.md. Testing will be manual via `docker compose` commands.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Docker config**: Repository root (`docker-compose.yml`, `Dockerfile`, `docker-entrypoint.sh`)
- **Migrations**: `apps/orders/migrations/`
- **Documentation**: `docs/`, root level markdown files

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create supporting files and documentation before implementing fixes

- [X] T001 Create `.wslconfig.example` file at repository root with WSL2 memory configuration (8GB RAM, 4 CPUs, 2GB swap)
- [X] T002 Create `docs/SIGBUS_TROUBLESHOOTING.md` with SIGBUS error diagnosis and solutions for WSL2 environment
- [X] T003 [P] Create backup of current `Dockerfile` as `Dockerfile.backup` before modifications
- [X] T004 [P] Create backup of current `docker-compose.yml` as `docker-compose.yml.backup` before modifications
- [X] T005 [P] Create backup of current `docker-entrypoint.sh` as `docker-entrypoint.sh.backup` before modifications

**Checkpoint**: All backups created, supporting documentation in place

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Verify current Docker issues by running `docker compose down -v && docker compose up -d` and documenting the error - CONFIRMED: Issues exist
- [X] T007 Confirm IntegrityError exists by checking logs: `docker compose logs web | grep -i "integrityerror\|duplicate key"` - CONFIRMED: IntegrityError on pg_type_typname_nsp_index
- [X] T008 Confirm SIGBUS issue exists on WSL by running `docker compose build --no-cache` and checking for SIGBUS errors - DOCUMENTED: See docs/SIGBUS_TROUBLESHOOTING.md
- [X] T009 Test current celery container lacks health check via `docker inspect metateks_celery | grep -A 10 Health` - CONFIRMED: No health check configured

**Checkpoint**: Issues confirmed and documented - user story implementation can now begin

---

## Phase 3: User Story 1 - Надежный запуск Docker окружения (Priority: P1) 🎯 MVP

**Goal**: Eliminate IntegrityError when running `docker compose up -d` - ensure all containers start successfully without PostgreSQL type conflicts

**Independent Test**:
1. Run `docker compose down -v` to remove all volumes
2. Run `docker compose up -d` - should succeed without errors
3. Check logs: `docker compose logs web` - no IntegrityError should appear
4. Verify all containers healthy: `docker compose ps` - all should show "healthy" or "running"

### Implementation for User Story 1

- [X] T010 [US1] Create migration `apps/orders/migrations/0010_fix_delivery_company_type.py` with `drop_orphaned_delivery_company_type()` function that drops orphaned `orders_deliverycompany` composite type
- [X] T011 [US1] Add migration dependencies in `apps/orders/migrations/0010_fix_delivery_company_type.py` depending on `0009_order_warehouse`
- [X] T012 [US1] Implement SQL in migration: Check if type exists AND table doesn't exist before dropping, with proper error handling
- [X] T013 [US1] Update `docker-entrypoint.sh` to add pre-migration notice explaining type cleanup (add echo statement before migrate command)
- [X] T014 [US1] Test migration locally: Migration applied successfully, type cleanup logic verified
- [X] T015 [US1] Test migration idempotency: Re-running migrations shows "No migrations to apply" - idempotent ✓
- [X] T016 [US1] Verify data integrity: Table exists with 5 delivery companies - data preserved ✓

**Checkpoint**: IntegrityError eliminated, fresh volume deployment works reliably

---

## Phase 4: User Story 2 - Стабильные миграции базы данных (Priority: P2)

**Goal**: Ensure migrations are idempotent and can be re-run without errors - Django correctly identifies already-applied migrations

**Independent Test**:
1. Run migrations: `docker exec metateks_web python manage.py migrate`
2. Run migrations again: `docker exec metateks_web python manage.py migrate` - should output "No migrations to apply"
3. Check `django_migrations` table to confirm migration 0008 is recorded
4. Run `docker exec metateks_web python manage.py showmigrations orders` - all should show [X]

### Implementation for User Story 2

- [ ] T017 [P] [US2] Verify migration `0008_fix_delivery_company_type.py` uses `migrations.RunPython` with proper `reverse_code=migrations.RunPython.noop` for rollback support
- [ ] T018 [US2] Add RAISE NOTICE in migration SQL to log when type is dropped (helps with troubleshooting)
- [ ] T019 [US2] Test migration rollback: `docker exec metateks_web python manage.py migrate orders 0007` then re-apply `docker exec metateks_web python manage.py migrate orders`
- [ ] T020 [US2] Verify idempotency after volume removal: `docker compose down -v && docker compose up -d && docker compose restart web` - should succeed
- [ ] T021 [US2] Document migration behavior in `docs/DOCKER_DEPLOYMENT.md` - add section "Migration Idempotency" explaining the type cleanup
- [ ] T022 [US2] Create `scripts/test-migrations.sh` script that automates migration testing (fresh start, re-run, rollback)

**Checkpoint**: Migrations are idempotent and safe to re-run in any scenario

---

## Phase 5: User Story 3 - Оптимизированная сборка для WSL (Priority: P3)

**Goal**: Eliminate SIGBUS errors during Docker build in WSL2 - enable reliable image building on Windows+WSL

**Independent Test**:
1. Move project to WSL filesystem: `cp -r /mnt/c/_KIPOL/_WORK/_metatecks ~/projects/metateks`
2. Build images: `cd ~/projects/metateks && docker compose build --no-cache` - should complete without SIGBUS
3. Start containers: `docker compose up -d` - should work normally
4. Verify build time is reasonable (< 5 minutes)

### Implementation for User Story 3

- [ ] T023 [P] [US3] Rewrite `Dockerfile` with multi-stage build: create `builder` stage with build dependencies (gcc, g++, libpq-dev) and install Python packages to `/root/.local`
- [ ] T024 [P] [US3] Modify `Dockerfile` final stage to `COPY --from=builder /root/.local /root/.local` and set `ENV PATH=/root/.local/bin:$PATH`
- [ ] T025 [P] [US3] Update `Dockerfile` runtime dependencies to only install what's needed (libpq5, libjpeg62-turbo, libpng16-16, libwebp6, zlib1g, curl)
- [ ] T026 [US3] Add `.dockerignore` file at repository root excluding `__pycache__`, `*.pyc`, `.git`, `venv`, `.vscode`, `*.md` except docs
- [ ] T027 [US3] Update `docs/DOCKER_DEPLOYMENT.md` with WSL2 section explaining critical requirement to use `~/projects/` not `/mnt/c/`
- [ ] T028 [US3] Copy `.wslconfig.example` to `C:\Users\<User>\.wslconfig` documentation in quickstart
- [ ] T029 [US3] Test build on WSL filesystem: `cd ~/projects/metateks && docker compose build` and verify no SIGBUS
- [ ] T030 [US3] Test build on Windows filesystem (for comparison): `cd /mnt/c/_KIPOL/_WORK/_metatecks && docker compose build --no-cache` and document any SIGBUS
- [ ] T031 [US3] Measure and compare build times and image sizes between old and new Dockerfile

**Checkpoint**: Docker builds complete successfully in WSL2 without SIGBUS errors

---

## Phase 6: User Story 4 - Улучшенные health checks и зависимости (Priority: P3)

**Goal**: Add health check for Celery worker - enable proper dependency tracking and automatic restart on failure

**Independent Test**:
1. Start containers: `docker compose up -d`
2. Check celery health: `docker inspect metateks_celery | grep -A 10 Health` - should show health status
3. Wait for health check: watch `docker compose ps` until celery shows "healthy"
4. Test failure recovery: restart celery `docker compose restart celery` - should return to healthy

### Implementation for User Story 4

- [ ] T032 [US4] Add `healthcheck` section to celery service in `docker-compose.yml`: `test: ["CMD", "celery", "-A", "main", "inspect", "ping"]`
- [ ] T033 [US4] Configure health check intervals in `docker-compose.yml`: `interval: 30s`, `timeout: 10s`, `retries: 3`, `start_period: 40s`
- [ ] T034 [US4] Verify celery command path is correct by testing in container: `docker exec metateks_celery which celery`
- [ ] T035 [US4] Test health check manually: `docker exec metateks_celery celery -A main inspect ping` - should return pong
- [ ] T036 [US4] Restart all containers: `docker compose down && docker compose up -d` and verify celery becomes healthy
- [ ] T037 [US4] Check all services health: `docker compose ps` - verify db, redis, web, celery all show "healthy"

**Checkpoint**: All Docker services have proper health checks and report status correctly

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates, validation, and cleanup

- [ ] T038 [P] Update `README_WSL.md` with link to `docs/DOCKER_DEPLOYMENT.md` for Docker instructions
- [ ] T039 [P] Update `docs/DOCKER_DEPLOYMENT.md` with complete troubleshooting section including IntegrityError, SIGBUS, and health check issues
- [ ] T040 [P] Create quick reference card in `docs/DOCKER_COMMANDS.md` with common Docker commands for this project
- [ ] T041 Validate all success criteria from spec.md: run `docker compose down -v && docker compose up -d` 10 times and count failures (should be 0)
- [ ] T042 Measure startup time: `time docker compose up -d` and verify system is ready in < 90 seconds
- [ ] T043 Run full integration test following `quickstart.md` verification steps
- [ ] T044 Remove backup files (`.backup`) if all tests pass
- [ ] T045 Create git commit with all changes: `git add . && git commit -m "fix: Eliminate Docker IntegrityError and SIGBUS errors in WSL"`

**Checkpoint**: All documentation complete, success criteria validated, ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on backups from Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase confirmation
  - User Story 1 (P1): Must complete first (fixes critical IntegrityError)
  - User Story 2 (P2): Depends on US1 completion (builds on migration fix)
  - User Story 3 (P3): Can proceed in parallel with US1/US2 (different concern - build optimization)
  - User Story 4 (P3): Can proceed in parallel with US1/US2/US3 (different concern - health checks)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories (CRITICAL PATH)
- **User Story 2 (P2)**: Depends on US1 - Extends migration fix from US1
- **User Story 3 (P3)**: Can start after Foundational - Independent of US1/US2 (Dockerfile changes)
- **User Story 4 (P3)**: Can start after Foundational - Independent of US1/US2/US3 (docker-compose changes)

### Within Each User Story

- US1: Migration creation (T010-T012) → testing (T014-T016) → sequential
- US2: Migration verification (T017-T018) → testing (T019-T020) → documentation (T021-T022) → sequential
- US3: Dockerfile modifications (T023-T026) → documentation (T027-T028) → testing (T029-T031) → sequential
- US4: Health check addition (T032-T033) → verification (T034-T037) → sequential

### Parallel Opportunities

- **Setup phase**: T003, T004, T005 can run in parallel (all backups)
- **US3 parallelization**: T023, T024, T025, T026 can run in parallel (different sections of Dockerfile)
- **US3 + US4 parallelization**: Once US1 complete, US3 and US4 can be worked on simultaneously
- **Polish phase**: T038, T039, T040 can run in parallel (all documentation)

---

## Parallel Example: User Story 3 + User Story 4

After US1 is complete, US3 (WSL optimization) and US4 (health checks) can proceed in parallel:

```bash
# US3 Tasks (Dockerfile optimization):
T023: "Rewrite Dockerfile with multi-stage build"
T024: "Modify Dockerfile final stage to copy from builder"
T025: "Update Dockerfile runtime dependencies"
T026: "Add .dockerignore file"

# US4 Tasks (Celery health check) - CAN RUN IN PARALLEL:
T032: "Add healthcheck section to celery service in docker-compose.yml"
T033: "Configure health check intervals in docker-compose.yml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - CRITICAL PATH FIX

1. Complete Phase 1: Setup (backups)
2. Complete Phase 2: Foundational (confirm issues exist)
3. Complete Phase 3: User Story 1 (IntegrityError fix)
4. **STOP and VALIDATE**: Test `docker compose down -v && docker compose up -d` 5 times - all should succeed
5. This fixes the critical blocking issue for all developers

### Incremental Delivery

1. MVP (US1) → Deploy - IntegrityError eliminated, developers can work
2. Add US2 → Deploy - Migrations now idempotent and reliable
3. Add US3 → Deploy - WSL developers can build without SIGBUS
4. Add US4 → Deploy - All services properly monitored
5. Polish → Documentation complete, onboarding improved

### Sequential vs Parallel

**Single Developer** (recommended execution order):
1. Setup → Foundational → US1 → US2 → US3 → US4 → Polish

**Multiple Developers** (if available):
1. Together: Setup → Foundational
2. Developer A: US1 (critical path)
3. Developer B: US3 (can start in parallel with US1)
4. After US1: Developer A → US2, Developer B → US4
5. Together: Polish

---

## Notes

- [P] tasks = different files, no dependencies on incomplete work
- [US1], [US2], etc. labels map task to specific user story for traceability
- Each user story should be independently verifiable
- US1 is CRITICAL PATH - fixes the main blocking issue
- US3 and US4 can proceed in parallel once US1 is done
- Commit after each task or logical group for easy rollback
- Stop at any checkpoint to validate story independently
- Test on clean volumes (`docker compose down -v`) to verify fixes work
