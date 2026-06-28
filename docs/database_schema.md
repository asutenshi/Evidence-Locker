# Схема Базы Данных: Evidence Locker

База данных основана на SQLite и использует SQLAlchemy 2.0 (ORM).
Ниже описаны основные таблицы для MVP-версии, разработанные согласно техническому заданию.

## Таблица `evidence_records`
Основное хранилище подтверждений (артефактов).

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID (Primary Key) | Уникальный идентификатор записи. |
| `actor_id` | String | Идентификатор пользователя (из `actor` xAPI). |
| `source_system` | String | Источник данных (система, отправившая подтверждение). |
| `source_type` | String | Тип артефакта (из `object.definition.type` xAPI). |
| `evidence_link` | String | Ссылка на артефакт (из `object.id` xAPI). |
| `context` | String | Контекст, например, название проекта (из `context` xAPI). |
| `timestamp` | DateTime | Время совершения события (из `timestamp` xAPI). |
| `review_status` | Enum | Статус подтверждения (`draft`, `pending`, `reviewed`, `rejected`). |
| `reviewed_by` | String | Идентификатор проверяющего (в MVP заполняется `0` при успехе). |
| `created_at` | DateTime | Дата и время добавления записи в базу. |

## Таблица `evidence_competencies`
Таблица связей (Many-to-Many или One-to-Many) между подтверждениями и компетенциями.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID (Primary Key) | Уникальный идентификатор связи. |
| `evidence_id` | UUID (Foreign Key) | Ссылка на запись в таблице `evidence_records`. |
| `competency_id` | String | Внешний идентификатор компетенции. |
| `proposed_by` | String | Кем предложена компетенция (автоматически `collector` или вручную `teacher`). |

## Связи
* Один `evidence_records` может иметь несколько привязанных `evidence_competencies` (связь One-to-Many).
