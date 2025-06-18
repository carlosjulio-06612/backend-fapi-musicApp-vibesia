# Alembic Migration History – Vibesia Schema

This folder contains Alembic migration scripts used to manage and evolve the schema of the `vibesia_schema` in a PostgreSQL database. Each script introduces incremental changes with clear documentation of the schema evolution.

## 📋 Migration List and Description

### ✅ `360b16ba22c2_add_password_changed_at_column_to_user_`
* **Description**: Adds a new column `password_changed_at` to the `users` table.
* **Details**: This column is of type `TIMESTAMP WITH TIME ZONE`, not nullable, with a default value of `now()`.
* **Purpose**: To track the timestamp of the last password change for security auditing and password policy enforcement.

### ✅ `2d12193b6184_add_ondelete_cascade_for_user_foreign_`
* **Description**: Applies `ON DELETE CASCADE` to several foreign key relationships involving `users`.
* **Details**:
   * Affects tables like `playlists`, `user_device`, and `playback_history`.
   * Also involves index removals and re-creations for performance optimization.
* **Purpose**: Ensures referential integrity by cascading deletes from `users`, automatically cleaning up related records when a user is deleted.

### ✅ `3cfc87221979_set_on_delete_set_null_for_audit_log_`
* **Description**: Intended to set `ON DELETE SET NULL` for the `app_user_id` foreign key in the `audit_log` table.
* **Status**: ⚠️ Placeholder – no operations defined yet.
* **Purpose**: Prepared for soft deletion logic, allowing `audit_log` to retain records even if the user is deleted, maintaining audit trail integrity.

### ✅ `ecf5acd6708d_make_password_changed_at_nullable`
* **Description**: Modifies the `password_changed_at` column to make it nullable.
* **Details**:
   * Updates the existing column in the `users` table to allow `NULL` values.
   * Removes the NOT NULL constraint added in the previous migration.
* **Purpose**: Allows for more flexibility in the user model, possibly for legacy accounts, system users, or accounts created through external authentication providers.

## 🚀 Usage

These migrations are managed using Alembic. Here are the most common commands:

### Apply all pending migrations:
```bash
alembic upgrade head
```

### Apply migrations up to a specific revision:
```bash
alembic upgrade <revision_id>
```

### Roll back to a specific version:
```bash
alembic downgrade <revision_id>
```

### Roll back one migration:
```bash
alembic downgrade -1
```

### Check current migration status:
```bash
alembic current
```

### View migration history:
```bash
alembic history
```

### Generate a new migration (after model changes):
```bash
alembic revision --autogenerate -m "Description of changes"
```

## 📁 Project Structure

```
alembic/
├── versions/
│   ├── 360b16ba22c2_add_password_changed_at_column_to_user_.py
│   ├── 2d12193b6184_add_ondelete_cascade_for_user_foreign_.py
│   ├── 3cfc87221979_set_on_delete_set_null_for_audit_log_.py
│   └── ecf5acd6708d_make_password_changed_at_nullable.py
├── alembic.ini
├── env.py
└── script.py.mako
```

## ⚠️ Important Notes

* **Target Schema**: All migrations target the `vibesia_schema`.
* **Migration Order**: Migrations should be applied in chronological order, as specified by the `down_revision` in each file.
* **Pending Implementation**: Migration `3cfc87221979` requires implementation of the actual operations.
* **Database Backup**: Always backup your database before applying migrations in production.
* **Environment**: Ensure your database connection string in `alembic.ini` points to the correct environment.

## 🔧 Development Workflow

1. **Before making schema changes**: Always create a database backup
2. **After model changes**: Generate migration with `alembic revision --autogenerate`
3. **Review generated migration**: Manually check the generated migration file
4. **Test migration**: Apply to development/staging environment first
5. **Apply to production**: Only after thorough testing

## 📊 Schema Evolution Timeline

```
Initial Schema
    ↓
360b16ba22c2: Add password_changed_at (NOT NULL, default now())
    ↓
2d12193b6184: Add ON DELETE CASCADE for user relationships
    ↓
3cfc87221979: [PENDING] Set ON DELETE SET NULL for audit_log
    ↓
ecf5acd6708d: Make password_changed_at nullable
    ↓
Current Schema
```

## 🐛 Troubleshooting

### Common Issues:

**Migration fails with foreign key constraint error:**
- Check if there are existing records that would violate the new constraints
- Consider data cleanup before applying the migration

**Column already exists error:**
- Check if the migration was partially applied
- Use `alembic current` to verify the current state

**Connection errors:**
- Verify database credentials in `alembic.ini`
- Ensure the database server is running and accessible

## 📝 Contributing

When adding new migrations:

1. Use descriptive names for migration files
2. Include clear comments in the migration code
3. Test both `upgrade()` and `downgrade()` functions
4. Update this README with the new migration details

## 📞 Support

For questions or issues related to these migrations, please:
- Check the Alembic documentation: https://alembic.sqlalchemy.org/
- Review the migration files for implementation details
- Contact the development team for schema-specific questions