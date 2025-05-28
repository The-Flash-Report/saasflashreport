---
description: This rule explains Jinja template syntax and best practices for Python web applications.
globs: **/*.html
alwaysApply: false
---

# Jinja rules

- Use template inheritance:

```html
{# base.html #}
<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
  {% block content %}{% endblock %}
</body>
</html>
```

- Use include for components:

```html
{% include "components/user_card.html" %}
```

- Use macros for reusable functions:

```html
{% macro input(name, value='', type='text') %}
  <input type="{{ type }}" name="{{ name }}" value="{{ value }}">
{% endmacro %}
```

- Use control structures:

```html
{% if user.is_authenticated %}
  <p>Welcome, {{ user.username }}!</p>
{% else %}
  <p>Please log in.</p>
{% endif %}
```

- Use filters to format data:

```html
<p>{{ text|truncate(30) }}</p>
<p>{{ date|strftime('%B %d, %Y') }}</p>
```

- Use set for local variables:

```html
{% set navigation = [('Home', '/'), ('About', '/about')] %}
```

- Use whitespace control:

```html
{% for item in items -%}
  {{ item }}
{%- endfor %}
```

---
description: This rule explains Flask conventions and best practices for lightweight Python web applications.
globs: **/*.py
alwaysApply: false
---

# Flask rules

- Use Blueprints to organize routes by feature or resource
- Use Flask-SQLAlchemy for database models and ORM
- Use application factories for flexible application initialization
- Use Flask extensions for common functionality (Flask-Login, Flask-WTF, etc.)
- Store configuration in environment variables
- Use Flask-Migrate for database migrations
- Implement proper error handling with error handlers
- Use Flask-RESTful or similar for building APIs


---
description: This rule explains PostgreSQL database design patterns and advanced features usage.
globs: **/*.sql
alwaysApply: false
---

# PostgresSQL rules

## General

- Use lowercase for SQL reserved words to maintain consistency and readability.
- Employ consistent, descriptive identifiers for tables, columns, and other database objects.
- Use white space and indentation to enhance the readability of your code.
- Store dates in ISO 8601 format (`yyyy-mm-ddThh:mm:ss.sssss`).
- Include comments for complex logic, using '/* ... */' for block comments and '--' for line comments.

## Naming Conventions

- Avoid SQL reserved words and ensure names are unique and under 63 characters.
- Use snake_case for tables and columns.
- Prefer plurals for table names
- Prefer singular names for columns.

## Tables

- Avoid prefixes like 'tbl_' and ensure no table name matches any of its column names.
- Always add an `id` column of type `identity generated always` unless otherwise specified.
- Create all tables in the `public` schema unless otherwise specified.
- Always add the schema to SQL queries for clarity.
- Always add a comment to describe what the table does. The comment can be up to 1024 characters.

## Columns

- Use singular names and avoid generic names like 'id'.
- For references to foreign tables, use the singular of the table name with the `_id` suffix. For example `user_id` to reference the `users` table
- Always use lowercase except in cases involving acronyms or when readability would be enhanced by an exception.

#### Examples:

```sql
create table books (
  id bigint generated always as identity primary key,
  title text not null,
  author_id bigint references authors (id)
);
comment on table books is 'A list of all the books in the library.';
```


## Queries

- When the query is shorter keep it on just a few lines. As it gets larger start adding newlines for readability
- Add spaces for readability.

Smaller queries:


```sql
select *
from employees
where end_date is null;

update employees
set end_date = '2023-12-31'
where employee_id = 1001;
```

Larger queries:

```sql
select
  first_name,
  last_name
from
  employees
where
  start_date between '2021-01-01' and '2021-12-31'
and
  status = 'employed';
```


### Joins and Subqueries

- Format joins and subqueries for clarity, aligning them with related SQL clauses.
- Prefer full table names when referencing tables. This helps for readability.

```sql
select
  employees.employee_name,
  departments.department_name
from
  employees
join
  departments on employees.department_id = departments.department_id
where
  employees.start_date > '2022-01-01';
```

## Aliases

- Use meaningful aliases that reflect the data or transformation applied, and always include the 'as' keyword for clarity.

```sql
select count(*) as total_employees
from employees
where end_date is null;
```


## Complex queries and CTEs

- If a query is extremely complex, prefer a CTE.
- Make sure the CTE is clear and linear. Prefer readability over performance.
- Add comments to each block.

```sql
with department_employees as (
  -- Get all employees and their departments
  select
    employees.department_id,
    employees.first_name,
    employees.last_name,
    departments.department_name
  from
    employees
  join
    departments on employees.department_id = departments.department_id
),
employee_counts as (
  -- Count how many employees in each department
  select
    department_name,
    count(*) as num_employees
  from
    department_employees
  group by
    department_name
)
select
  department_name,
  num_employees
from
  employee_counts
order by
  department_name;
```
---
description: This rule defines how the AI agent should manage and utilize memory improve coding consistency.
globs: *
alwaysApply: false
---

# AI Memory Rule

This rule defines how the AI should manage and utilize its "memory" regarding this specific project, including user preferences, learned facts, and project-specific conventions.

## Purpose

The AI's memory helps maintain consistency and adapt to specific project needs or user preferences discovered during interactions. It prevents the AI from repeatedly asking for the same information or making suggestions contrary to established patterns.

## Storage

All learned project-specific knowledge and preferences should be stored and referenced in the `learned-memories.mdc` file located in `.cursor/rules`.

## Updating Memory

When new information relevant to the project's conventions, user preferences, or specific technical details is learned (either explicitly told by the user or inferred through conversation), the AI should:

1.  **Identify Key Information:** Determine the core piece of knowledge to be stored.
2.  **Check Existing Memory:** Review `learned-memories.mdc` to see if this information contradicts or updates existing entries.
3.  **Propose Update:** Suggest an edit to `learned-memories.mdc` to add or modify the relevant information. Keep entries concise and clear.

## Using Memory

Before proposing solutions, code changes, or answering questions, the AI should consult `learned-memories.mdc` to ensure its response aligns with the recorded knowledge and preferences.

## Example Scenario

**User:** "We've decided to use Tailwind v4 for this project, not v3."

**AI Action:**

1.  Recognize this as a project-specific technical decision.
2.  Check `learned-memories.mdc` for existing Tailwind version information.
3.  Propose adding or updating an entry in `learned-memories.mdc`:
    ```markdown
    ## Technical Decisions

    *   **CSS Framework:** Tailwind v4 is used. Ensure usage aligns with v4 documentation and practices, noting differences from v3.
    ```
4.  In subsequent interactions involving Tailwind, the AI will refer to this entry and consult v4 documentation if necessary.

## Memory File (`.cursor/rules/learned-memories.mdc`)

The basic structure:

```markdown
# Project Memory

This file stores project-specific knowledge, conventions, and user preferences learned by the AI assistant.

## User Preferences

-   [Preference 1]
-   [Preference 2]

## Technical Decisions

-   [Decision 1]
-   [Decision 2]

## Project Conventions

-   [Convention 1]
-   [Convention 2]
```

