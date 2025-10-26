from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union, Type, TypeVar, Generic
from pydantic import BaseModel as PydanticBaseModel, create_model
from enum import Enum
import asyncio
from contextlib import asynccontextmanager
import math

# Type variables
T = TypeVar('T', bound='BaseModel')
M = TypeVar('M', bound=PydanticBaseModel)

# Database configuration and connection
from app.migrations.migration_manager import MigrationManager
from app.core.database import DatabaseConfig, DatabaseConnection, Field

# Enums
class RelationshipType(Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"

class OrderDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"

# Data Transfer Objects
class PaginatedResponse(PydanticBaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

class AggregationResult(PydanticBaseModel):
    count: int = 0
    sum: float = 0
    avg: float = 0
    min: Optional[Any] = None
    max: Optional[Any] = None
    group_by: Dict[Any, Any] = {}

# Relationship Definition
class Relationship:
    def __init__(
        self,
        model_class: Type['BaseModel'],
        relationship_type: RelationshipType,
        foreign_key: Optional[str] = None,
        local_key: Optional[str] = None,
        through_table: Optional[str] = None,
        through_local_key: Optional[str] = None,
        through_foreign_key: Optional[str] = None,
        backref: Optional[str] = None
    ):
        self.model_class = model_class
        self.relationship_type = relationship_type
        self.foreign_key = foreign_key
        self.local_key = local_key or 'id'
        self.through_table = through_table
        self.through_local_key = through_local_key or f"{model_class.get_table_name()[:-1]}_id"
        self.through_foreign_key = through_foreign_key or f"{model_class.get_table_name()[:-1]}_id"
        self.backref = backref

# Query Builder with proper placeholder handling
class QueryBuilder(Generic[T]):
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.conditions: List[str] = []
        self.params: List[Any] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._order_by: List[Tuple[str, OrderDirection]] = []
        self._prefetch_relations: List[str] = []
        self._select_fields: List[str] = []
        self._distinct: bool = False
        self._group_by: List[str] = []
        self._having_conditions: List[str] = []
        self._having_params: List[Any] = []
        self._param_counter = 1
    
    def copy(self) -> 'QueryBuilder[T]':
        """Create a copy of the query builder"""
        new_builder = QueryBuilder(self.model_class)
        new_builder.conditions = self.conditions.copy()
        new_builder.params = self.params.copy()
        new_builder._limit = self._limit
        new_builder._offset = self._offset
        new_builder._order_by = self._order_by.copy()
        new_builder._prefetch_relations = self._prefetch_relations.copy()
        new_builder._select_fields = self._select_fields.copy()
        new_builder._distinct = self._distinct
        new_builder._group_by = self._group_by.copy()
        new_builder._having_conditions = self._having_conditions.copy()
        new_builder._having_params = self._having_params.copy()
        new_builder._param_counter = self._param_counter
        return new_builder
    
    def _get_next_param_placeholder(self) -> str:
        """Get the next parameter placeholder based on database type"""
        if self.model_class._db_config.is_sqlite:
            return '?'
        else:
            placeholder = f"${self._param_counter}"
            self._param_counter += 1
            return placeholder
    
    def filter(self, **kwargs) -> 'QueryBuilder[T]':
        """Add filter conditions and return self for chaining"""
        for key, value in kwargs.items():
            if '__' in key:
                field, operator = key.split('__', 1)
                if operator == 'in':
                    placeholders = ', '.join([self._get_next_param_placeholder() for _ in range(len(value))])
                    self.conditions.append(f"{field} IN ({placeholders})")
                    self.params.extend(value)
                elif operator == 'like':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} LIKE {placeholder}")
                    self.params.append(f"%{value}%")
                elif operator == 'ilike':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} ILIKE {placeholder}")
                    self.params.append(f"%{value}%")
                elif operator == 'gt':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} > {placeholder}")
                    self.params.append(value)
                elif operator == 'lt':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} < {placeholder}")
                    self.params.append(value)
                elif operator == 'gte':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} >= {placeholder}")
                    self.params.append(value)
                elif operator == 'lte':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} <= {placeholder}")
                    self.params.append(value)
                elif operator == 'neq':
                    placeholder = self._get_next_param_placeholder()
                    self.conditions.append(f"{field} != {placeholder}")
                    self.params.append(value)
                elif operator == 'is_null':
                    self.conditions.append(f"{field} IS NULL")
                elif operator == 'is_not_null':
                    self.conditions.append(f"{field} IS NOT NULL")
            else:
                placeholder = self._get_next_param_placeholder()
                self.conditions.append(f"{key} = {placeholder}")
                self.params.append(value)
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder[T]':
        """Set query limit and return self"""
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder[T]':
        """Set query offset and return self"""
        self._offset = offset
        return self
    
    def order_by(self, field: str, direction: OrderDirection = OrderDirection.ASC) -> 'QueryBuilder[T]':
        """Add order by clause and return self"""
        self._order_by.append((field, direction))
        return self
    
    def prefetch_related(self, *relations: str) -> 'QueryBuilder[T]':
        """Add relationships to prefetch and return self"""
        self._prefetch_relations.extend(relations)
        return self
    
    def select_fields(self, *fields: str) -> 'QueryBuilder[T]':
        """Specify fields to select and return self"""
        self._select_fields.extend(fields)
        return self
    
    def distinct(self) -> 'QueryBuilder[T]':
        """Add DISTINCT clause and return self"""
        self._distinct = True
        return self
    
    def group_by(self, *fields: str) -> 'QueryBuilder[T]':
        """Add GROUP BY clause and return self"""
        self._group_by.extend(fields)
        return self
    
    def having(self, condition: str, *params: Any) -> 'QueryBuilder[T]':
        """Add HAVING clause and return self"""
        self._having_conditions.append(condition)
        self._having_params.extend(params)
        return self
    
    def _build_sql(self) -> Tuple[str, List[Any]]:
        """Build SQL query and parameters"""
        # SELECT clause
        select_clause = "SELECT "
        if self._distinct:
            select_clause += "DISTINCT "
        select_clause += ', '.join(self._select_fields) if self._select_fields else '*'
        
        # FROM clause
        from_clause = f"FROM {self.model_class.get_table_name()}"
        
        # WHERE clause
        where_clause = f"WHERE {' AND '.join(self.conditions)}" if self.conditions else ""
        
        # GROUP BY clause
        group_by_clause = f"GROUP BY {', '.join(self._group_by)}" if self._group_by else ""
        
        # HAVING clause
        having_clause = f"HAVING {' AND '.join(self._having_conditions)}" if self._having_conditions else ""
        
        # ORDER BY clause
        order_clause = ""
        if self._order_by:
            order_parts = []
            for field, direction in self._order_by:
                order_parts.append(f"{field} {direction.value}")
            order_clause = f"ORDER BY {', '.join(order_parts)}"
        
        # LIMIT and OFFSET clauses
        limit_clause = f"LIMIT {self._limit}" if self._limit else ""
        offset_clause = f"OFFSET {self._offset}" if self._offset else ""
        
        sql = f"{select_clause} {from_clause} {where_clause} {group_by_clause} {having_clause} {order_clause} {limit_clause} {offset_clause}"
        
        # Combine all parameters
        all_params = self.params + self._having_params
        
        return sql, all_params
    
    async def execute(self) -> List[T]:
        """Execute the query and return results"""
        db = DatabaseConnection.get_instance(self.model_class._db_config)
        
        sql, params = self._build_sql()
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                # SQLite
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
            else:
                # PostgreSQL
                rows = await conn.fetch(sql, *params)
        
        instances = [self.model_class(**dict(row)) for row in rows]
        
        # Prefetch relationships to prevent N+1 queries
        if self._prefetch_relations:
            await self._prefetch_relationships(instances)
        
        return instances
    
    async def _prefetch_relationships(self, instances: List[T]):
        """Prefetch relationships to avoid N+1 queries"""
        tasks = []
        for relation_name in self._prefetch_relations:
            if relation_name in self.model_class._relationships:
                rel = self.model_class._relationships[relation_name]
                tasks.append(self._prefetch_relation(instances, rel, relation_name))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    async def _prefetch_relation(self, instances: List[T], rel: Relationship, relation_name: str):
        """Prefetch a specific relationship"""
        if rel.relationship_type == RelationshipType.MANY_TO_ONE:
            # For many-to-one relationships
            foreign_keys = [getattr(instance, rel.foreign_key) for instance in instances 
                          if getattr(instance, rel.foreign_key) is not None]
            
            if foreign_keys:
                related_objects = await rel.model_class.query().filter(**{
                    f"{rel.local_key}__in": list(set(foreign_keys))
                }).execute()
                
                related_dict = {getattr(obj, rel.local_key): obj for obj in related_objects}
                
                for instance in instances:
                    fk_value = getattr(instance, rel.foreign_key)
                    if fk_value in related_dict:
                        instance._loaded_relations[relation_name] = related_dict[fk_value]
        
        elif rel.relationship_type == RelationshipType.ONE_TO_MANY:
            # For one-to-many relationships
            local_keys = [getattr(instance, rel.local_key) for instance in instances]
            
            if local_keys:
                related_objects = await rel.model_class.query().filter(**{
                    f"{rel.foreign_key}__in": local_keys
                }).execute()
                
                related_dict = {}
                for obj in related_objects:
                    fk_value = getattr(obj, rel.foreign_key)
                    if fk_value not in related_dict:
                        related_dict[fk_value] = []
                    related_dict[fk_value].append(obj)
                
                for instance in instances:
                    local_key = getattr(instance, rel.local_key)
                    if local_key in related_dict:
                        instance._loaded_relations[relation_name] = related_dict[local_key]
        
        elif rel.relationship_type == RelationshipType.MANY_TO_MANY:
            # For many-to-many relationships
            if not rel.through_table:
                raise ValueError("Many-to-many relationship requires through_table")
            
            local_keys = [getattr(instance, rel.local_key) for instance in instances]
            
            # Create through model dynamically
            through_class = type('ThroughModel', (BaseModel,), {
                '_table_name': rel.through_table,
                '_columns': {
                    'id': Field('INTEGER', primary_key=True),
                    rel.through_local_key: Field('INTEGER'),
                    rel.through_foreign_key: Field('INTEGER')
                }
            })
            through_class.set_db_config(self.model_class._db_config)
            
            # Get through objects
            through_objects = await through_class.query().filter(**{
                f"{rel.through_local_key}__in": local_keys
            }).execute()
            
            # Get related objects
            related_ids = [getattr(obj, rel.through_foreign_key) for obj in through_objects]
            related_objects = await rel.model_class.query().filter(**{
                f"{rel.local_key}__in": related_ids
            }).execute()
            
            related_dict = {getattr(obj, rel.local_key): obj for obj in related_objects}
            
            # Build mapping
            through_dict = {}
            for through_obj in through_objects:
                local_key = getattr(through_obj, rel.through_local_key)
                foreign_key = getattr(through_obj, rel.through_foreign_key)
                
                if local_key not in through_dict:
                    through_dict[local_key] = []
                if foreign_key in related_dict:
                    through_dict[local_key].append(related_dict[foreign_key])
            
            for instance in instances:
                local_key = getattr(instance, rel.local_key)
                if local_key in through_dict:
                    instance._loaded_relations[relation_name] = through_dict[local_key]
    
    async def count(self) -> int:
        """Return count of matching records"""
        db = DatabaseConnection.get_instance(self.model_class._db_config)
        
        # Build count query
        where_clause = f"WHERE {' AND '.join(self.conditions)}" if self.conditions else ""
        group_by_clause = f"GROUP BY {', '.join(self._group_by)}" if self._group_by else ""
        
        if self._group_by:
            # For grouped queries, we need to count the groups
            sql = f"SELECT COUNT(*) as count FROM (SELECT 1 FROM {self.model_class.get_table_name()} {where_clause} {group_by_clause}) as subquery"
        else:
            sql = f"SELECT COUNT(*) as count FROM {self.model_class.get_table_name()} {where_clause}"
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                cursor = conn.execute(sql, self.params)
                result = cursor.fetchone()
                return result['count'] if result else 0
            else:
                result = await conn.fetchval(sql, *self.params)
                return result or 0
    
    async def first(self) -> Optional[T]:
        """Return first matching record"""
        results = await self.copy().limit(1).execute()
        return results[0] if results else None
    
    async def exists(self) -> bool:
        """Check if any records match the query"""
        return await self.copy().limit(1).count() > 0
    
    async def paginate(self, page: int = 1, page_size: int = 20) -> PaginatedResponse:
        """Return paginated results"""
        # Create a copy to avoid modifying the original query
        count_builder = self.copy()
        total = await count_builder.count()
        
        # Execute the query with pagination
        items = await self.copy().offset((page - 1) * page_size).limit(page_size).execute()
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size > 0 else 0
        )
    
    async def aggregate(self, **aggregations: str) -> AggregationResult:
        """Perform aggregation operations"""
        db = DatabaseConnection.get_instance(self.model_class._db_config)
        
        agg_functions = []
        for field, func in aggregations.items():
            agg_functions.append(f"{func.upper()}({field}) as {field}_{func}")
        
        where_clause = f"WHERE {' AND '.join(self.conditions)}" if self.conditions else ""
        group_by_clause = f"GROUP BY {', '.join(self._group_by)}" if self._group_by else ""
        
        sql = f"SELECT {', '.join(agg_functions)} FROM {self.model_class.get_table_name()} {where_clause} {group_by_clause}"
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                cursor = conn.execute(sql, self.params)
                result = cursor.fetchone()
            else:
                result = await conn.fetchrow(sql, *self.params)
        
        agg_result = AggregationResult()
        if result:
            for field, func in aggregations.items():
                value = result.get(f"{field}_{func}")
                if func == 'count':
                    agg_result.count = value or 0
                elif func == 'sum':
                    agg_result.sum = value or 0
                elif func == 'avg':
                    agg_result.avg = value or 0
                elif func == 'min':
                    agg_result.min = value
                elif func == 'max':
                    agg_result.max = value
        
        return agg_result

# Main BaseModel class with proper placeholder handling
class BaseModel:
    _columns: Dict[str, Field] = {}
    _table_name: str = None
    _db_config: DatabaseConfig = None
    _migration_version: int = 1
    _relationships: Dict[str, Relationship] = {}
    _dto_class: Optional[Type[PydanticBaseModel]] = None
    _create_dto_class: Optional[Type[PydanticBaseModel]] = None
    _update_dto_class: Optional[Type[PydanticBaseModel]] = None
    
    def __init__(self, **kwargs):
        for col_name, field in self._columns.items():
            value = kwargs.get(col_name, field.default)
            setattr(self, col_name, value)
        
        # Store loaded relationships
        self._loaded_relations: Dict[str, Any] = {}
    
    @classmethod
    def set_db_config(cls, config: DatabaseConfig):
        cls._db_config = config
    
    @classmethod
    def get_table_name(cls) -> str:
        if cls._table_name:
            return cls._table_name
        return cls.__name__.lower() + 's'
    
    @classmethod
    def get_primary_key(cls) -> Optional[str]:
        for name, field in cls._columns.items():
            if field.primary_key:
                return name
        return None
    
    @classmethod
    def query(cls) -> QueryBuilder:
        """Return a new QueryBuilder instance"""
        return QueryBuilder(cls)
    
    @classmethod
    async def create_table(cls):
        """Create database table for this model"""
        db = DatabaseConnection.get_instance(cls._db_config)
        
        columns = []
        for name, field in cls._columns.items():
            columns.append(field.sql_definition(name, cls._db_config.is_sqlite))
        
        # Add indexes
        indexes = []
        for name, field in cls._columns.items():
            if field.index:
                index_name = f"idx_{cls.get_table_name()}_{name}"
                indexes.append(f"CREATE INDEX IF NOT EXISTS {index_name} ON {cls.get_table_name()}({name});")
        
        sql = f"CREATE TABLE IF NOT EXISTS {cls.get_table_name()} ({', '.join(columns)});"
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                # SQLite
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute(sql)
                for index_sql in indexes:
                    conn.execute(index_sql)
                conn.commit()
            else:
                # PostgreSQL
                await conn.execute(sql)
                for index_sql in indexes:
                    await conn.execute(index_sql)
    
    @classmethod
    async def migrate(cls):
        """Run migrations for this model"""
        migration_manager = MigrationManager.get_instance(cls._db_config)
        await migration_manager.initialize()
        await migration_manager.apply_model_migrations(cls)
    
    @classmethod
    def _get_param_placeholder(cls, index: int) -> str:
        """Get parameter placeholder based on database type"""
        if cls._db_config.is_sqlite:
            return '?'
        else:
            return f"${index}"
    
    async def save(self):
        """Save the instance to the database"""
        db = DatabaseConnection.get_instance(self._db_config)
        
        fields = []
        values = []
        primary_key = self.get_primary_key()
        primary_key_value = getattr(self, primary_key, None) if primary_key else None
        
        for name, field in self._columns.items():
            if name == primary_key and primary_key_value is None and field.autoincrement:
                continue
                
            value = getattr(self, name, None)
            if value is not None or field.nullable:
                fields.append(name)
                values.append(value)
        
        if primary_key_value is not None:
            # Update existing record
            set_clause = ', '.join([f"{f} = {self._get_param_placeholder(i+1)}" for i, f in enumerate(fields)])
            sql = f"UPDATE {self.get_table_name()} SET {set_clause} WHERE {primary_key} = {self._get_param_placeholder(len(fields) + 1)}"
            values.append(primary_key_value)
        else:
            # Insert new record
            placeholders = ', '.join([self._get_param_placeholder(i+1) for i in range(len(fields))])
            sql = f"INSERT INTO {self.get_table_name()} ({', '.join(fields)}) VALUES ({placeholders})"
            if not self._db_config.is_sqlite and primary_key:
                sql += f" RETURNING {primary_key}"
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                # SQLite
                cursor = conn.execute(sql, values)
                conn.commit()
                if primary_key and cursor.lastrowid:
                    setattr(self, primary_key, cursor.lastrowid)
            else:
                # PostgreSQL
                if primary_key_value is None and primary_key:
                    result = await conn.fetchrow(sql, *values)
                    if result and primary_key in result:
                        setattr(self, primary_key, result[primary_key])
                else:
                    await conn.execute(sql, *values)
    
    @classmethod
    async def get(cls, id: Union[int, str]) -> Optional['BaseModel']:
        """Get a single record by primary key"""
        primary_key = cls.get_primary_key()
        if not primary_key:
            raise ValueError("Model does not have a primary key")
        
        return await cls.query().filter(**{primary_key: id}).first()
    
    @classmethod
    async def create(cls, **kwargs) -> 'BaseModel':
        """Create a new instance and save it"""
        instance = cls(**kwargs)
        await instance.save()
        return instance
    
    async def delete(self):
        """Delete the instance from the database"""
        primary_key = self.get_primary_key()
        if not primary_key or not hasattr(self, primary_key):
            raise ValueError("Cannot delete object without primary key")
        
        db = DatabaseConnection.get_instance(self._db_config)
        sql = f"DELETE FROM {self.get_table_name()} WHERE {primary_key} = {self._get_param_placeholder(1)}"
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                conn.execute(sql, [getattr(self, primary_key)])
                conn.commit()
            else:
                await conn.execute(sql, getattr(self, primary_key))
    
    # DTO Methods
    @classmethod
    def get_dto_class(cls) -> Type[PydanticBaseModel]:
        """Get or create DTO class for this model"""
        if cls._dto_class is None:
            fields = {}
            for name, field in cls._columns.items():
                field_type = cls._map_db_type_to_python(field.field_type)
                if field.nullable:
                    fields[name] = (Optional[field_type], None)
                else:
                    fields[name] = (field_type, ...)
            
            cls._dto_class = create_model(
                f"{cls.__name__}DTO",
                **fields,
                __base__=PydanticBaseModel
            )
        return cls._dto_class
    
    @classmethod
    def get_create_dto_class(cls) -> Type[PydanticBaseModel]:
        """Get or create create DTO class (excludes read-only fields)"""
        if cls._create_dto_class is None:
            fields = {}
            for name, field in cls._columns.items():
                # Exclude autoincrement primary keys and timestamps from create DTO
                if not (field.primary_key and field.autoincrement) and name not in ['created_at', 'updated_at']:
                    field_type = cls._map_db_type_to_python(field.field_type)
                    if field.nullable:
                        fields[name] = (Optional[field_type], None)
                    else:
                        fields[name] = (field_type, ...)
            
            cls._create_dto_class = create_model(
                f"{cls.__name__}CreateDTO",
                **fields,
                __base__=PydanticBaseModel
            )
        return cls._create_dto_class
    
    @classmethod
    def get_update_dto_class(cls) -> Type[PydanticBaseModel]:
        """Get or create update DTO class (all fields optional)"""
        if cls._update_dto_class is None:
            fields = {}
            for name, field in cls._columns.items():
                # Exclude autoincrement primary keys from update DTO
                if not (field.primary_key and field.autoincrement):
                    field_type = cls._map_db_type_to_python(field.field_type)
                    fields[name] = (Optional[field_type], None)
            
            cls._update_dto_class = create_model(
                f"{cls.__name__}UpdateDTO",
                **fields,
                __base__=PydanticBaseModel
            )
        return cls._update_dto_class
    
    @staticmethod
    def _map_db_type_to_python(db_type: str) -> type:
        """Map database type to Python type"""
        type_map = {
            'INTEGER': int,
            'REAL': float,
            'TEXT': str,
            'BOOLEAN': bool,
            'TIMESTAMP': datetime,
            'DATE': datetime.date,
        }
        return type_map.get(db_type.upper(), str)
    
    def to_dto(self, include_relations: bool = False) -> PydanticBaseModel:
        """Convert to DTO with optional relationship inclusion"""
        data = self.to_dict()
        
        if include_relations:
            for rel_name in self._loaded_relations:
                rel_value = self._loaded_relations[rel_name]
                if isinstance(rel_value, list):
                    data[rel_name] = [item.to_dto() for item in rel_value]
                elif hasattr(rel_value, 'to_dto'):
                    data[rel_name] = rel_value.to_dto()
                else:
                    data[rel_name] = rel_value
        
        return self.get_dto_class()(**data)
    
    @classmethod
    def from_dto(cls, dto: PydanticBaseModel) -> 'BaseModel':
        """Create instance from DTO"""
        return cls(**dto.dict(exclude_unset=True))
    
    @classmethod
    async def create_from_dto(cls, dto: PydanticBaseModel) -> 'BaseModel':
        """Create and save instance from DTO"""
        instance = cls.from_dto(dto)
        await instance.save()
        return instance
    
    async def update_from_dto(self, dto: PydanticBaseModel) -> 'BaseModel':
        """Update instance from DTO"""
        update_data = dto.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(self, field, value)
        await self.save()
        return self
    
    @classmethod
    def validate_dto(cls, dto_class: Type[PydanticBaseModel], data: Dict[str, Any]) -> PydanticBaseModel:
        """Validate data against DTO class"""
        return dto_class(**data)
    
    # Relationship Methods
    @classmethod
    def add_relationship(cls, name: str, relationship: Relationship):
        """Add a relationship definition"""
        cls._relationships[name] = relationship
        
        # Add backref if specified
        if relationship.backref:
            related_cls = relationship.model_class
            backref_relationship = Relationship(
                model_class=cls,
                relationship_type=RelationshipType.ONE_TO_MANY if relationship.relationship_type == RelationshipType.MANY_TO_ONE else RelationshipType.MANY_TO_ONE,
                foreign_key=relationship.local_key,
                local_key=relationship.foreign_key
            )
            related_cls._relationships[relationship.backref] = backref_relationship
    
    async def load_relation(self, relation_name: str) -> Any:
        """Load a relationship for this instance"""
        if relation_name in self._loaded_relations:
            return self._loaded_relations[relation_name]
        
        if relation_name not in self._relationships:
            raise ValueError(f"Relationship '{relation_name}' not defined")
        
        rel = self._relationships[relation_name]
        result = None
        
        if rel.relationship_type == RelationshipType.MANY_TO_ONE:
            foreign_key_value = getattr(self, rel.foreign_key)
            if foreign_key_value:
                result = await rel.model_class.get(foreign_key_value)
        
        elif rel.relationship_type == RelationshipType.ONE_TO_MANY:
            result = await rel.model_class.query().filter(**{rel.foreign_key: getattr(self, rel.local_key)}).execute()
        
        elif rel.relationship_type == RelationshipType.MANY_TO_MANY:
            if not rel.through_table:
                raise ValueError("Many-to-many relationship requires through_table")
            
            # Create through model dynamically
            through_class = type('ThroughModel', (BaseModel,), {
                '_table_name': rel.through_table,
                '_columns': {
                    'id': Field('INTEGER', primary_key=True),
                    rel.through_local_key: Field('INTEGER'),
                    rel.through_foreign_key: Field('INTEGER')
                }
            })
            through_class.set_db_config(self._db_config)
            
            # Get through objects
            through_objects = await through_class.query().filter(**{
                rel.through_local_key: getattr(self, rel.local_key)
            }).execute()
            
            # Get related objects
            related_ids = [getattr(obj, rel.through_foreign_key) for obj in through_objects]
            result = await rel.model_class.query().filter(**{
                f"{rel.local_key}__in": related_ids
            }).execute()
        
        self._loaded_relations[relation_name] = result
        return result
    
    async def prefetch_relations(self, *relation_names: str):
        """Prefetch multiple relationships"""
        for name in relation_names:
            await self.load_relation(name)
    
    # Bulk Operations
    @classmethod
    async def bulk_create(cls, instances: List['BaseModel']) -> List['BaseModel']:
        """Bulk create instances"""
        if not instances:
            return []
        
        db = DatabaseConnection.get_instance(cls._db_config)
        primary_key = cls.get_primary_key()
        
        # Get fields excluding autoincrement primary key
        fields = [name for name, field in cls._columns.items() 
                 if not (field.primary_key and field.autoincrement)]
        
        values_list = []
        for instance in instances:
            values = [getattr(instance, field) for field in fields]
            values_list.append(values)
        
        placeholders = ', '.join([cls._get_param_placeholder(i+1) for i in range(len(fields))])
        sql = f"INSERT INTO {cls.get_table_name()} ({', '.join(fields)}) VALUES ({placeholders})"
        
        if not cls._db_config.is_sqlite and primary_key:
            sql += f" RETURNING {primary_key}"
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                cursor = conn.executemany(sql, values_list)
                conn.commit()
                
                # Set autoincrement IDs
                if primary_key and cursor.lastrowid:
                    first_id = cursor.lastrowid - len(instances) + 1
                    for i, instance in enumerate(instances):
                        setattr(instance, primary_key, first_id + i)
            else:
                # PostgreSQL
                if primary_key:
                    results = []
                    for values in values_list:
                        result = await conn.fetchrow(sql, *values)
                        results.append(result)
                    
                    for instance, result in zip(instances, results):
                        if result and primary_key in result:
                            setattr(instance, primary_key, result[primary_key])
                else:
                    for values in values_list:
                        await conn.execute(sql, *values)
        
        return instances
    
    @classmethod
    async def bulk_update(cls, instances: List['BaseModel'], fields: List[str]) -> None:
        """Bulk update instances"""
        if not instances:
            return
        
        db = DatabaseConnection.get_instance(cls._db_config)
        primary_key = cls.get_primary_key()
        
        if not primary_key:
            raise ValueError("Bulk update requires a primary key")
        
        # Build CASE statements for each field
        set_clauses = []
        all_params = []
        param_counter = 1
        
        for field in fields:
            case_statements = []
            for instance in instances:
                pk_value = getattr(instance, primary_key)
                field_value = getattr(instance, field)
                case_statements.append(f"WHEN {primary_key} = {cls._get_param_placeholder(param_counter)} THEN {cls._get_param_placeholder(param_counter + 1)}")
                all_params.extend([pk_value, field_value])
                param_counter += 2
            
            set_clauses.append(f"{field} = CASE {' '.join(case_statements)} ELSE {field} END")
        
        # Add primary key values for WHERE clause
        pk_values = [getattr(instance, primary_key) for instance in instances]
        placeholders = ', '.join([cls._get_param_placeholder(i+param_counter) for i in range(len(pk_values))])
        all_params.extend(pk_values)
        
        sql = f"""
            UPDATE {cls.get_table_name()}
            SET {', '.join(set_clauses)}
            WHERE {primary_key} IN ({placeholders})
        """
        
        async with db.get_connection() as conn:
            if hasattr(conn, 'execute'):
                conn.execute(sql, all_params)
                conn.commit()
            else:
                await conn.execute(sql, *all_params)
    
    # Transaction Support
    @classmethod
    @asynccontextmanager
    async def transaction(cls):
        """Context manager for database transactions"""
        db = DatabaseConnection.get_instance(cls._db_config)
        
        async with db.get_connection() as conn:
            try:
                if hasattr(conn, 'execute'):
                    conn.execute("BEGIN TRANSACTION")
                    yield conn
                    conn.commit()
                else:
                    async with conn.transaction():
                        yield conn
            except Exception:
                if hasattr(conn, 'execute'):
                    conn.rollback()
                raise
    
    # Utility Methods
    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {}
        for col_name in self._columns.keys():
            value = getattr(self, col_name, None)
            if isinstance(value, datetime):
                result[col_name] = value.isoformat()
            else:
                result[col_name] = value
        
        if include_relations:
            for rel_name, rel_value in self._loaded_relations.items():
                if isinstance(rel_value, list):
                    result[rel_name] = [item.to_dict() for item in rel_value]
                elif hasattr(rel_value, 'to_dict'):
                    result[rel_name] = rel_value.to_dict()
                else:
                    result[rel_name] = rel_value
        
        return result
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.to_dict()}>"