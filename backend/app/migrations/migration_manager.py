import asyncio
import json
import argparse
import sys
from typing import Dict, List, Any, Optional, Tuple
from backend.app.core.database import DatabaseConnection, DatabaseConfig, Field
import re

class MigrationManager:
    _instance = None
    
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
        self.applied_migrations = set()
        self.model_versions: Dict[str, int] = {}  # model_name -> current_version
        self.migration_schemas: Dict[str, Dict[int, Any]] = {}  # model_name -> {version: schema_definition}
    
    @classmethod
    def get_instance(cls, db_config: DatabaseConfig = None):
        if cls._instance is None and db_config:
            cls._instance = cls(db_config)
        return cls._instance
    
    async def initialize(self):
        """Create migrations table if it doesn't exist"""
        db = DatabaseConnection.get_instance(self.db_config)
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                # SQLite
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS migrations (
                        id INTEGER PRIMARY KEY,
                        model_name TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        schema_definition TEXT NOT NULL,
                        operations TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(model_name, version)
                    )
                ''')
                conn.commit()
                
                # Load applied migrations
                cursor = conn.execute("SELECT model_name, version, schema_definition FROM migrations")
                for row in cursor.fetchall():
                    self.model_versions[row['model_name']] = row['version']
                    if row['model_name'] not in self.migration_schemas:
                        self.migration_schemas[row['model_name']] = {}
                    self.migration_schemas[row['model_name']][row['version']] = json.loads(row['schema_definition'])
            else:
                # PostgreSQL
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS migrations (
                        id SERIAL PRIMARY KEY,
                        model_name VARCHAR(255) NOT NULL,
                        version INTEGER NOT NULL,
                        schema_definition TEXT NOT NULL,
                        operations TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(model_name, version)
                    )
                ''')
                
                # Load applied migrations
                rows = await conn.fetch("SELECT model_name, version, schema_definition FROM migrations")
                for row in rows:
                    self.model_versions[row['model_name']] = row['version']
                    if row['model_name'] not in self.migration_schemas:
                        self.migration_schemas[row['model_name']] = {}
                    self.migration_schemas[row['model_name']][row['version']] = json.loads(row['schema_definition'])
    
    async def apply_model_migrations(self, model_class):
        """Apply migrations for a specific model based on column changes"""
        model_name = model_class.__name__
        current_version = self.model_versions.get(model_name, 0)
        target_version = getattr(model_class, '_migration_version', 1)
        
        if current_version >= target_version:
            print(f"{model_name} is already at version {current_version} (target: {target_version})")
            return
        
        db = DatabaseConnection.get_instance(self.db_config)
        
        print(f"Migrating {model_name} from v{current_version} to v{target_version}")
        
        # Apply each migration step sequentially
        for version in range(current_version + 1, target_version + 1):
            migration_sql, operations, schema_definition = self._generate_migration_sql(
                model_class, version - 1, version
            )
            
            if not migration_sql:
                print(f"No migration needed for {model_name} to v{version}")
                continue
                
            async with db.get_connection() as conn:
                try:
                    if hasattr(conn, 'execute'):
                        # SQLite - execute each statement separately
                        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
                        for statement in statements:
                            conn.execute(statement)
                        
                        # Store migration schema and operations for downgrade
                        conn.execute(
                            "INSERT INTO migrations (model_name, version, schema_definition, operations) VALUES (?, ?, ?, ?)", 
                            (model_name, version, json.dumps(schema_definition), json.dumps(operations))
                        )
                        conn.commit()
                    else:
                        # PostgreSQL - execute directly
                        await conn.execute(migration_sql)
                        
                        # Store migration schema and operations for downgrade
                        await conn.execute(
                            "INSERT INTO migrations (model_name, version, schema_definition, operations) VALUES ($1, $2, $3, $4)", 
                            model_name, version, json.dumps(schema_definition), json.dumps(operations)
                        )
                    
                    self.model_versions[model_name] = version
                    if model_name not in self.migration_schemas:
                        self.migration_schemas[model_name] = {}
                    self.migration_schemas[model_name][version] = schema_definition
                    
                    print(f"✓ Applied migration for {model_name} to v{version}")
                    
                except Exception as e:
                    print(f"✗ Failed to apply migration for {model_name} to v{version}: {e}")
                    raise
    
    async def downgrade_model(self, model_class, target_version: int):
        """Downgrade a model to a specific version"""
        model_name = model_class.__name__
        current_version = self.model_versions.get(model_name, 0)
        
        if current_version <= target_version:
            print(f"{model_name} is already at version {current_version} (target downgrade: {target_version})")
            return
        
        db = DatabaseConnection.get_instance(self.db_config)
        
        print(f"Downgrading {model_name} from v{current_version} to v{target_version}")
        
        # Downgrade step by step from current version down to target version
        for version in range(current_version, target_version, -1):
            downgrade_sql = self._generate_downgrade_sql(model_name, version)
            
            if not downgrade_sql:
                print(f"No downgrade needed for {model_name} from v{version}")
                continue
                
            async with db.get_connection() as conn:
                try:
                    if hasattr(conn, 'execute'):
                        # SQLite - execute each statement separately
                        statements = [s.strip() for s in downgrade_sql.split(';') if s.strip()]
                        for statement in statements:
                            conn.execute(statement)
                        
                        # Remove the migration record
                        conn.execute(
                            "DELETE FROM migrations WHERE model_name = ? AND version = ?", 
                            (model_name, version)
                        )
                        conn.commit()
                    else:
                        # PostgreSQL - execute directly
                        await conn.execute(downgrade_sql)
                        
                        # Remove the migration record
                        await conn.execute(
                            "DELETE FROM migrations WHERE model_name = $1 AND version = $2", 
                            model_name, version
                        )
                    
                    self.model_versions[model_name] = version - 1
                    if model_name in self.migration_schemas and version in self.migration_schemas[model_name]:
                        del self.migration_schemas[model_name][version]
                    
                    print(f"✓ Downgraded {model_name} from v{version} to v{version - 1}")
                    
                except Exception as e:
                    print(f"✗ Failed to downgrade {model_name} from v{version}: {e}")
                    raise
    
    async def drop_table(self, model_class):
        """Completely drop the table for this model"""
        model_name = model_class.__name__
        table_name = model_class.get_table_name()
        is_sqlite = self.db_config.is_sqlite
        
        db = DatabaseConnection.get_instance(self.db_config)
        
        # Generate drop table SQL
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        
        # Also drop all indexes
        index_sql = []
        for name, field in model_class._columns.items():
            if field.index:
                index_name = f"idx_{table_name}_{name}"
                index_sql.append(f"DROP INDEX IF EXISTS {index_name};")
        
        full_sql = drop_sql + ''.join(index_sql)
        
        async with db.get_connection() as conn:
            try:
                if hasattr(conn, 'execute'):
                    # SQLite
                    statements = [s.strip() for s in full_sql.split(';') if s.strip()]
                    for statement in statements:
                        conn.execute(statement)
                    
                    # Remove all migration records for this model
                    conn.execute("DELETE FROM migrations WHERE model_name = ?", (model_name,))
                    conn.commit()
                else:
                    # PostgreSQL
                    await conn.execute(full_sql)
                    
                    # Remove all migration records for this model
                    await conn.execute("DELETE FROM migrations WHERE model_name = $1", model_name)
                
                # Clear from memory
                if model_name in self.model_versions:
                    del self.model_versions[model_name]
                if model_name in self.migration_schemas:
                    del self.migration_schemas[model_name]
                
                print(f"✓ Dropped table {table_name} for {model_name}")
                
            except Exception as e:
                print(f"✗ Failed to drop table {table_name}: {e}")
                raise
    
    async def reset_database(self, models: List[Any]):
        """Completely reset the database by dropping all tables"""
        for model_class in models:
            await self.drop_table(model_class)
        
        # Recreate tables
        for model_class in models:
            await model_class.create_table()
            await self.apply_model_migrations(model_class)
        
        print("✓ Database reset complete")
    
    async def show_status(self, models: List[Any]):
        """Show current migration status for all models"""
        print("\nMigration Status:")
        print("=================")
        
        for model_class in models:
            model_name = model_class.__name__
            current_version = self.model_versions.get(model_name, 0)
            target_version = getattr(model_class, '_migration_version', 1)
            
            status = "✓ Up to date" if current_version >= target_version else "⚠ Needs update"
            print(f"{model_name}: v{current_version} -> v{target_version} ({status})")
    
    def _generate_migration_sql(self, model_class, from_version: int, to_version: int) -> Tuple[str, Dict, Dict]:
        """Generate SQL for migrating a model between versions"""
        model_name = model_class.__name__
        table_name = model_class.get_table_name()
        is_sqlite = self.db_config.is_sqlite
        
        operations = {
            'added_columns': [],
            'removed_columns': [],
            'modified_columns': [],
            'added_indexes': [],
            'removed_indexes': []
        }
        
        sql_statements = []
        
        # Store the current schema definition for downgrade
        schema_definition = self._serialize_schema(model_class._columns)
        
        # If table doesn't exist yet, create it
        if from_version == 0:
            columns_sql = []
            for name, field in model_class._columns.items():
                columns_sql.append(field.sql_definition(name, is_sqlite))
            
            sql_statements.append(f"CREATE TABLE {table_name} ({', '.join(columns_sql)});")
            
            # Add indexes
            for name, field in model_class._columns.items():
                if field.index:
                    index_name = f"idx_{table_name}_{name}"
                    sql_statements.append(f"CREATE INDEX {index_name} ON {table_name}({name});")
                    operations['added_indexes'].append({
                        'name': name,
                        'index_name': index_name
                    })
            
            return ';'.join(sql_statements), operations, schema_definition
        
        # Get previous schema for comparison
        previous_schema = self.migration_schemas.get(model_name, {}).get(from_version, {})
        current_schema = self._serialize_schema(model_class._columns)
        
        # Compare schemas to generate migration SQL
        previous_cols = set(previous_schema.keys())
        current_cols = set(current_schema.keys())
        
        # Columns to add
        for col_name in current_cols - previous_cols:
            field = model_class._columns[col_name]
            if is_sqlite:
                # SQLite can only add columns with ALTER TABLE
                sql_statements.append(f"ALTER TABLE {table_name} ADD COLUMN {field.sql_definition(col_name, is_sqlite)};")
            else:
                # PostgreSQL can add columns with constraints
                sql_statements.append(f"ALTER TABLE {table_name} ADD COLUMN {field.sql_definition(col_name, is_sqlite)};")
            operations['added_columns'].append({
                'name': col_name,
                'definition': self._serialize_field(field)
            })
        
        # Columns to remove - requires table recreation in SQLite
        columns_to_remove = previous_cols - current_cols
        if columns_to_remove:
            if is_sqlite:
                # SQLite doesn't support DROP COLUMN, so we need to recreate the table
                sql_statements.extend(self._generate_sqlite_column_modification(
                    table_name, model_class._columns, previous_schema, current_schema
                ))
                for col_name in columns_to_remove:
                    operations['removed_columns'].append({
                        'name': col_name,
                        'definition': previous_schema[col_name]
                    })
            else:
                # PostgreSQL supports DROP COLUMN
                for col_name in columns_to_remove:
                    sql_statements.append(f"ALTER TABLE {table_name} DROP COLUMN {col_name};")
                    operations['removed_columns'].append({
                        'name': col_name,
                        'definition': previous_schema[col_name]
                    })
        
        # Column modifications - handle ALTER COLUMN for both databases
        modified_columns = []
        for col_name in previous_cols & current_cols:
            if previous_schema[col_name] != current_schema[col_name]:
                modified_columns.append(col_name)
                operations['modified_columns'].append({
                    'name': col_name,
                    'old_definition': previous_schema[col_name],
                    'new_definition': current_schema[col_name]
                })
        
        # Handle column modifications
        if modified_columns:
            if is_sqlite:
                # SQLite doesn't support MODIFY COLUMN, so we need to recreate the table
                sql_statements.extend(self._generate_sqlite_column_modification(
                    table_name, model_class._columns, previous_schema, current_schema
                ))
            else:
                # PostgreSQL supports ALTER COLUMN with various modifications
                for col_name in modified_columns:
                    field = model_class._columns[col_name]
                    old_field = self._deserialize_field(previous_schema[col_name])
                    
                    # Handle type changes
                    if field.field_type != old_field.field_type:
                        sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE {field.field_type};")
                    
                    # Handle NULL/NOT NULL changes
                    if field.nullable != old_field.nullable:
                        if field.nullable:
                            sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} DROP NOT NULL;")
                        else:
                            sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} SET NOT NULL;")
                    
                    # Handle default value changes
                    if field.default != old_field.default:
                        if field.default is None:
                            sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} DROP DEFAULT;")
                        else:
                            default_value = f"'{field.default}'" if isinstance(field.default, str) else str(field.default)
                            sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} SET DEFAULT {default_value};")
        
        # Handle index changes
        previous_indexes = {name for name, field_data in previous_schema.items() if field_data.get('index', False)}
        current_indexes = {name for name, field_data in current_schema.items() if field_data.get('index', False)}
        
        # Indexes to add
        for index_name in current_indexes - previous_indexes:
            index_sql = f"CREATE INDEX idx_{table_name}_{index_name} ON {table_name}({index_name});"
            sql_statements.append(index_sql)
            operations['added_indexes'].append({
                'name': index_name,
                'index_name': f"idx_{table_name}_{index_name}"
            })
        
        # Indexes to remove
        for index_name in previous_indexes - current_indexes:
            index_sql = f"DROP INDEX IF EXISTS idx_{table_name}_{index_name};"
            sql_statements.append(index_sql)
            operations['removed_indexes'].append({
                'name': index_name,
                'index_name': f"idx_{table_name}_{index_name}"
            })
        
        return ';'.join(sql_statements), operations, schema_definition
    
    def _generate_sqlite_column_modification(self, table_name: str, current_columns: Dict[str, Field], previous_schema: Dict, current_schema: Dict) -> List[str]:
        """Generate SQL for SQLite table recreation (for column removal/modification)"""
        sql_statements = []
        temp_table = f"{table_name}_temp"
        
        # 1. Create temporary table with new schema
        columns_sql = []
        for name, field in current_columns.items():
            columns_sql.append(field.sql_definition(name, True))  # is_sqlite=True
        
        sql_statements.append(f"CREATE TABLE {temp_table} ({', '.join(columns_sql)});")
        
        # 2. Copy data from old table to temporary table
        common_columns = set(previous_schema.keys()) & set(current_schema.keys())
        if common_columns:
            columns_list = ', '.join(common_columns)
            sql_statements.append(f"INSERT INTO {temp_table} ({columns_list}) SELECT {columns_list} FROM {table_name};")
        
        # 3. Drop old table
        sql_statements.append(f"DROP TABLE {table_name};")
        
        # 4. Rename temporary table to original name
        sql_statements.append(f"ALTER TABLE {temp_table} RENAME TO {table_name};")
        
        # 5. Recreate indexes
        for name, field in current_columns.items():
            if field.index:
                index_name = f"idx_{table_name}_{name}"
                sql_statements.append(f"CREATE INDEX {index_name} ON {table_name}({name});")
        
        return sql_statements
    
    def _generate_downgrade_sql(self, model_name: str, from_version: int) -> str:
        """Generate SQL to downgrade from a specific version"""
        # Get the operations that were performed for this version
        migration_data = self.migration_schemas.get(model_name, {}).get(from_version, {})
        if not migration_data:
            return ""
        
        # Get the actual operations from the stored data
        operations = migration_data.get('operations', {}) if isinstance(migration_data, dict) else {}
        if not operations:
            return ""
        
        sql_statements = []
        table_name = model_name.lower() + 's'
        is_sqlite = self.db_config.is_sqlite
        
        # Reverse added columns (remove them)
        for column_info in operations.get('added_columns', []):
            if is_sqlite:
                # For SQLite, we need to recreate the table to remove columns
                # Get the previous schema (version - 1)
                previous_schema = self.migration_schemas.get(model_name, {}).get(from_version - 1, {})
                current_schema = self.migration_schemas.get(model_name, {}).get(from_version, {})
                
                if previous_schema and current_schema:
                    # Convert schema back to field objects
                    previous_fields = {}
                    for col_name, field_data in previous_schema.items():
                        previous_fields[col_name] = self._deserialize_field(field_data)
                    
                    sql_statements.extend(self._generate_sqlite_column_modification(
                        table_name, previous_fields, current_schema, previous_schema
                    ))
                    break  # Only need to do this once for all columns
            else:
                # PostgreSQL can drop columns directly
                sql_statements.append(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_info['name']};")
        
        # Reverse removed columns (add them back with original definition)
        for column_info in operations.get('removed_columns', []):
            field = self._deserialize_field(column_info['definition'])
            sql_statements.append(f"ALTER TABLE {table_name} ADD COLUMN {field.sql_definition(column_info['name'], is_sqlite)};")
        
        # Reverse index changes
        for index_info in operations.get('added_indexes', []):
            sql_statements.append(f"DROP INDEX IF EXISTS {index_info['index_name']};")
        
        # For modified columns, revert the changes
        for column_info in operations.get('modified_columns', []):
            old_field = self._deserialize_field(column_info['old_definition'])
            col_name = column_info['name']
            
            if is_sqlite:
                # SQLite requires table recreation for column modifications
                previous_schema = self.migration_schemas.get(model_name, {}).get(from_version - 1, {})
                current_schema = self.migration_schemas.get(model_name, {}).get(from_version, {})
                
                if previous_schema and current_schema:
                    previous_fields = {}
                    for col_name, field_data in previous_schema.items():
                        previous_fields[col_name] = self._deserialize_field(field_data)
                    
                    sql_statements.extend(self._generate_sqlite_column_modification(
                        table_name, previous_fields, current_schema, previous_schema
                    ))
                    break  # Only need to do this once for all columns
            else:
                # PostgreSQL can alter columns directly
                current_field = self._deserialize_field(column_info['new_definition'])
                
                # Revert type changes
                if old_field.field_type != current_field.field_type:
                    sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE {old_field.field_type};")
                
                # Revert NULL/NOT NULL changes
                if old_field.nullable != current_field.nullable:
                    if old_field.nullable:
                        sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} DROP NOT NULL;")
                    else:
                        sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} SET NOT NULL;")
                
                # Revert default value changes
                if old_field.default != current_field.default:
                    if old_field.default is None:
                        sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} DROP DEFAULT;")
                    else:
                        default_value = f"'{old_field.default}'" if isinstance(old_field.default, str) else str(old_field.default)
                        sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} SET DEFAULT {default_value};")
        
        return ';'.join(sql_statements)
    
    def _serialize_schema(self, columns: Dict[str, Field]) -> Dict:
        """Serialize column definitions for storage"""
        return {name: self._serialize_field(field) for name, field in columns.items()}
    
    def _serialize_field(self, field: Field) -> Dict:
        """Serialize a field definition for storage"""
        return {
            'field_type': field.field_type,
            'primary_key': field.primary_key,
            'autoincrement': field.autoincrement,
            'unique': field.unique,
            'nullable': field.nullable,
            'default': field.default,
            'foreign_key': field.foreign_key,
            'index': field.index
        }
    
    def _deserialize_field(self, field_data: Dict) -> Field:
        """Deserialize a field definition from storage"""
        return Field(
            field_type=field_data['field_type'],
            primary_key=field_data['primary_key'],
            autoincrement=field_data['autoincrement'],
            unique=field_data['unique'],
            nullable=field_data['nullable'],
            default=field_data['default'],
            foreign_key=field_data['foreign_key'],
            index=field_data['index']
        )

async def run_migrations():
    """Run migrations based on command line arguments"""
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("--action", choices=["migrate", "downgrade", "reset", "status"], 
                       default="migrate", help="Action to perform")
    parser.add_argument("--model", help="Specific model to migrate (default: all)")
    parser.add_argument("--version", type=int, help="Target version for downgrade")
    parser.add_argument("--database-url", help="Database connection URL")
    
    args = parser.parse_args()
    
    # Setup database config
    config = DatabaseConfig(args.database_url)
    
    # Import your models here
    from backend.app.models.profile import User
    from models.course import Course
    
    models = [User, Course]
    
    # Filter models if specific model requested
    if args.model:
        models = [m for m in models if m.__name__.lower() == args.model.lower()]
        if not models:
            print(f"Error: Model '{args.model}' not found")
            return
    
    # Initialize migration manager
    manager = MigrationManager.get_instance(config)
    await manager.initialize()
    
    # Perform requested action
    if args.action == "migrate":
        for model in models:
            await manager.apply_model_migrations(model)
        print("✓ Migration completed")
    
    elif args.action == "downgrade":
        if args.version is None:
            print("Error: --version parameter required for downgrade")
            return
        
        for model in models:
            await manager.downgrade_model(model, args.version)
        print("✓ Downgrade completed")
    
    elif args.action == "reset":
        confirm = input("Are you sure you want to reset the database? This will drop all tables! (y/N): ")
        if confirm.lower() == 'y':
            await manager.reset_database(models)
        else:
            print("Reset cancelled")
    
    elif args.action == "status":
        await manager.show_status(models)

async def main():
    try:
        await run_migrations()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())