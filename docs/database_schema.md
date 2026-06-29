# Схема Базы Данных: Evidence Locker

База данных основана на SQLite и использует SQLAlchemy 2.0 (ORM).
Ниже описаны основные таблицы для MVP-версии, разработанные согласно техническому заданию.

## Таблица `evidence_records`
Основное хранилище подтверждений (артефактов).

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID (Primary Key) | Идентификатор самого Statement. Обязателен как Primary Key. |
| `actor_id` | String | Нормализованный идентификатор пользователя. |
| `verb_id` | String | URI глагола (например, `http://adlnet.gov/expapi/verbs/completed`). |
| `object_id` | String | URI объекта (например, ID курса или теста). |
| `timestamp` | DateTime | Время, когда произошло событие (из `timestamp` xAPI). |
| `source_system` | String | Название внешней системы (например, Git, Redmine). Извлекается из расширений. |
| `source_type` | String | Тип источника (например, commit, task). Извлекается из расширений. |
| `context_id` | String | Идентификатор проекта или курса. Извлекается из context xAPI. |
| `note` | Text | Короткий текстовый фрагмент или пояснение (nullable). |
| `raw_data` | JSON | Вся остальная информация из xAPI Statement (context, definition и т.д.). |
| `review_status` | Enum | Статус подтверждения (`draft`, `pending`, `reviewed`, `rejected`). |
| `reviewed_by` | String | Идентификатор проверяющего (в MVP заполняется `0` при успехе). |
| `stored` | DateTime | Время записи в базу (соответствует `stored` xAPI). |

## Таблица `evidence_competencies`
Таблица связей (Many-to-Many или One-to-Many) между подтверждениями и компетенциями.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID (Primary Key) | Уникальный идентификатор связи. |
| `evidence_id` | UUID (Foreign Key) | Ссылка на запись в таблице `evidence_records`. |
| `competency_id` | String | Внешний идентификатор компетенции. |
| `proposed_by` | String | Кем предложена компетенция (автоматически `collector` или вручную `teacher`). |
| `status` | Enum | Статус связи (`pending`, `approved`, `rejected`, `unlinked`). |
| `reviewed_by` | String | Идентификатор проверяющего, который подтвердил/отклонил связь. |
| `created_at` | DateTime | Время создания связи. |
| `updated_at` | DateTime | Время последнего изменения статуса связи. |

## Связи
* Один `evidence_records` может иметь несколько привязанных `evidence_competencies` (связь One-to-Many).
