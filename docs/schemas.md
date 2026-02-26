# Schema Validation

Learn how to define and use schemas to validate LLM response structure.

## 📋 What are Schemas?

Schemas define the expected structure of your LLM responses. They ensure that:

- ✅ Required fields are present
- ✅ Fields have correct data types
- ✅ Values meet constraints (length, range, pattern)
- ✅ No unexpected fields are included

trustguard uses **Pydantic** for schema validation, giving you powerful, fast, and type-safe validation.

## 🏗️ Base Schema

All schemas inherit from `BaseResponse`:

```python
from pydantic import BaseModel, ConfigDict
from trustguard.schemas import BaseResponse

class MySchema(BaseResponse):
    """My custom schema."""
    
    # Define your fields
    field1: str
    field2: int
    field3: Optional[float] = None
    
    # Configure schema behavior
    model_config = ConfigDict(
        extra="forbid",           # Don't allow extra fields
        validate_assignment=True,  # Validate on attribute assignment
        str_strip_whitespace=True, # Strip whitespace from strings
        frozen=False,              # Allow mutation after creation
        populate_by_name=True,     # Allow populating by field name
    )
```

## 📦 GenericResponse

The built-in `GenericResponse` schema works for most use cases:

```python
from trustguard.schemas import GenericResponse

# Fields:
# - content: str (required)
# - sentiment: "positive"|"neutral"|"negative" (required)
# - tone: str (required)
# - is_helpful: bool (required)
# - confidence: Optional[float] (optional)

# Use directly
guard = TrustGuard(schema_class=GenericResponse)

# Or extend it
class CustomResponse(GenericResponse):
    custom_field: str
    timestamp: datetime
```

## 🎨 Creating Custom Schemas

### Basic Example

```python
from pydantic import Field, field_validator
from trustguard.schemas import BaseResponse
from datetime import datetime
from typing import List, Optional

class BlogPost(BaseResponse):
    """Schema for blog post generation."""
    
    title: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Blog post title"
    )
    
    content: str = Field(
        ...,
        min_length=100,
        max_length=5000,
        description="Main content"
    )
    
    tags: List[str] = Field(
        default=[],
        max_length=10,
        description="Post tags"
    )
    
    reading_time_minutes: Optional[int] = Field(
        None,
        ge=1,
        le=60,
        description="Estimated reading time"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags are lowercase and unique."""
        if v:
            # Make lowercase
            v = [tag.lower() for tag in v]
            # Remove duplicates
            v = list(dict.fromkeys(v))
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Ensure title doesn't start with lowercase."""
        if v and v[0].islower():
            raise ValueError('Title should start with capital letter')
        return v
```

### Advanced Example

```python
from pydantic import Field, field_validator, model_validator
from trustguard.schemas import BaseResponse
from enum import Enum
from typing import List, Optional, Union
import re

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EngineeringResponse(BaseResponse):
    """Schema for engineering system responses."""
    
    # Basic fields
    component: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="System component name"
    )
    
    status: str = Field(
        ...,
        pattern="^(operational|degraded|failed|maintenance)$",
        description="Component status"
    )
    
    # Numeric fields with constraints
    pressure_psi: float = Field(
        ...,
        ge=0,
        le=5000,
        description="Pressure in PSI"
    )
    
    temperature_c: float = Field(
        ...,
        ge=-50,
        le=1000,
        description="Temperature in Celsius"
    )
    
    vibration_mms: float = Field(
        ...,
        ge=0,
        le=100,
        description="Vibration in mm/s"
    )
    
    # Complex fields
    readings: List[dict] = Field(
        default=[],
        max_length=100,
        description="Sensor readings"
    )
    
    risk_level: RiskLevel = Field(
        default=RiskLevel.LOW,
        description="Assessed risk level"
    )
    
    is_safe: bool = Field(
        ...,
        description="Safety status"
    )
    
    recommended_actions: List[str] = Field(
        default=[],
        description="Recommended actions"
    )
    
    metadata: dict = Field(
        default={},
        description="Additional metadata"
    )
    
    @field_validator('pressure_psi')
    @classmethod
    def validate_pressure(cls, v):
        """Custom pressure validation."""
        if v > 2000:
            raise ValueError(f"Critical pressure: {v} PSI exceeds 2000 PSI limit")
        if v < 0:
            raise ValueError("Pressure cannot be negative")
        return v
    
    @field_validator('temperature_c')
    @classmethod
    def validate_temperature(cls, v):
        """Custom temperature validation."""
        if v > 500:
            raise ValueError(f"Critical temperature: {v}°C exceeds 500°C limit")
        if v < -50:
            raise ValueError("Temperature below minimum operating range")
        return v
    
    @model_validator(mode='after')
    def validate_safety(self):
        """Cross-field validation."""
        # If pressure is high, risk level should be at least MEDIUM
        if self.pressure_psi > 1500 and self.risk_level == RiskLevel.LOW:
            raise ValueError("High pressure requires at least MEDIUM risk level")
        
        # If status is failed, is_safe should be False
        if self.status == "failed" and self.is_safe:
            raise ValueError("Failed component cannot be safe")
        
        return self
    
    @field_validator('recommended_actions')
    @classmethod
    def validate_actions(cls, v):
        """Validate recommended actions."""
        if v:
            # Check for duplicates
            if len(v) != len(set(v)):
                raise ValueError("Recommended actions must be unique")
            
            # Check each action
            for action in v:
                if len(action) < 5:
                    raise ValueError(f"Action too short: {action}")
                if not re.match(r'^[a-zA-Z0-9\s\-_]+$', action):
                    raise ValueError(f"Action contains invalid characters: {action}")
        
        return v
```

## 🔧 Field Types and Validation

### Basic Field Types

```python
from pydantic import Field
from typing import Optional, List, Dict, Union, Literal

class ExampleSchema(BaseResponse):
    # String fields
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Numeric fields
    count: int = Field(..., ge=0, le=100)
    price: float = Field(..., gt=0, multiple_of=0.01)
    
    # Boolean
    is_active: bool = Field(..., description="Active status")
    
    # Lists
    tags: List[str] = Field(default=[], max_length=10)
    scores: List[float] = Field(..., min_length=1, max_length=5)
    
    # Dictionaries
    metadata: Dict[str, Union[str, int]] = Field(default={})
    
    # Literal (specific values)
    status: Literal["draft", "published", "archived"] = Field(...)
    
    # Enums (alternative to Literal)
    from enum import Enum
    class Color(str, Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"
    
    color: Color = Field(...)
```

### Field Constraints

| Constraint | Description | Example |
|------------|-------------|---------|
| `min_length` | Minimum string length | `min_length=1` |
| `max_length` | Maximum string length | `max_length=100` |
| `pattern` | Regex pattern | `pattern=r'^\d{3}-\d{2}-\d{4}$'` |
| `ge` | Greater than or equal | `ge=0` |
| `gt` | Greater than | `gt=0` |
| `le` | Less than or equal | `le=100` |
| `lt` | Less than | `lt=100` |
| `multiple_of` | Multiple of value | `multiple_of=0.01` |
| `min_items` | Minimum list items | `min_items=1` |
| `max_items` | Maximum list items | `max_items=10` |
| `unique_items` | Unique list items | `unique_items=True` |

### Validators

#### Field Validators

```python
from pydantic import field_validator

class UserSchema(BaseResponse):
    email: str
    age: int
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        """Validate age range."""
        if v < 0:
            raise ValueError('Age cannot be negative')
        if v > 150:
            raise ValueError('Age exceeds reasonable limit')
        return v
```

#### Model Validators

```python
from pydantic import model_validator

class DateRangeSchema(BaseResponse):
    start_date: datetime
    end_date: datetime
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validate that end_date is after start_date."""
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        return self
```

## 🚀 Using Schemas with TrustGuard

### Basic Usage

```python
from trustguard import TrustGuard
from trustguard.schemas import GenericResponse

# Use built-in schema
guard = TrustGuard(schema_class=GenericResponse)

# Validate response
result = guard.validate(response_json)
```

### Custom Schema

```python
from trustguard import TrustGuard
from myapp.schemas import MyCustomSchema

# Use custom schema
guard = TrustGuard(schema_class=MyCustomSchema)

# Validate
result = guard.validate(response_json)

if result.is_approved:
    # Access validated data
    data = result.data
    print(data.custom_field)
    print(data.timestamp)
```

### Schema Inheritance

```python
from trustguard.schemas import GenericResponse

class ExtendedResponse(GenericResponse):
    """Extend GenericResponse with additional fields."""
    
    extra_field: str
    metadata: dict = {}
    
    @field_validator('extra_field')
    @classmethod
    def validate_extra(cls, v):
        if len(v) < 3:
            raise ValueError('extra_field too short')
        return v

# Use extended schema
guard = TrustGuard(schema_class=ExtendedResponse)
```

## 📊 Common Schema Patterns

### 1. API Response Schema

```python
class APIResponse(BaseResponse):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: int = Field(..., ge=100, le=599)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @model_validator(mode='after')
    def validate_response(self):
        """Ensure data/error consistency."""
        if self.success and self.error:
            raise ValueError("Cannot have both success and error")
        if not self.success and not self.error:
            raise ValueError("Failed response must have error message")
        return self
```

### 2. Paginated Results

```python
class PaginatedResponse(BaseResponse):
    items: List[dict]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    has_more: bool
    next_page: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_pagination(self):
        """Validate pagination logic."""
        max_page = (self.total + self.page_size - 1) // self.page_size
        if self.page > max_page:
            raise ValueError(f"Page {self.page} exceeds max page {max_page}")
        
        self.has_more = self.page < max_page
        self.next_page = self.page + 1 if self.has_more else None
        return self
```

### 3. Form Validation

```python
class FormData(BaseResponse):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    age: int = Field(..., ge=18, le=120)
    terms_accepted: bool = Field(..., description="Must accept terms")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Check password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Check that passwords match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
```

## 🎯 Best Practices

### 1. Keep Schemas Focused

```python
# Good - focused on one purpose
class UserProfile(BaseResponse):
    name: str
    email: str
    bio: Optional[str]

# Bad - trying to do too much
class EverythingResponse(BaseResponse):
    user_data: dict
    product_data: dict
    order_data: dict
    # ... too many responsibilities
```

### 2. Use Descriptive Field Names

```python
# Good
class ProductResponse(BaseResponse):
    product_name: str
    unit_price: float
    quantity_in_stock: int

# Bad
class ProductResponse(BaseResponse):
    n: str  # What is 'n'?
    p: float  # Price? Profit?
    q: int  # Quantity? Quality?
```

### 3. Provide Clear Error Messages

```python
@field_validator('email')
@classmethod
def validate_email(cls, v):
    if '@' not in v:
        raise ValueError('Email must contain @ symbol')  # Clear message
    if '.' not in v.split('@')[-1]:
        raise ValueError('Email domain must contain dot')  # Clear message
    return v
```

### 4. Use Enums for Fixed Values

```python
from enum import Enum

class Status(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class DocumentResponse(BaseResponse):
    status: Status  # Clear that only these values are allowed
    title: str
```

### 5. Validate Early, Validate Often

```python
class UserInput(BaseResponse):
    email: str
    age: int
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        # Validate format immediately
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        # Validate range immediately
        if v < 0 or v > 150:
            raise ValueError('Invalid age')
        return v
```

## 🚨 Common Errors and Solutions

### 1. Missing Required Field

```python
# Error: Field required
result = guard.validate('{"content": "test"}')
print(result.log)  # "Schema Error: 3 validation errors..."

# Solution: Include all required fields
valid = {
    "content": "test",
    "sentiment": "neutral",
    "tone": "professional",
    "is_helpful": true
}
```

### 2. Wrong Field Type

```python
# Error: Input should be a valid boolean
invalid = '{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":"yes"}'

# Solution: Use correct type
valid = '{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":true}'
```

### 3. Constraint Violation

```python
# Error: String should have at least 1 character
invalid = '{"content":"","sentiment":"neutral","tone":"professional","is_helpful":true}'

# Solution: Meet constraints
valid = '{"content":"test","sentiment":"neutral","tone":"professional","is_helpful":true}'
```

## 📚 Related Topics

- [Core Concepts](concepts.md) - How validation works
- [Rules System](rules.md) - Fast deterministic checks
- [Judge System](judges.md) - AI-powered validation
- [API Reference](api.md) - Complete API documentation
- [Examples](examples.md) - Real-world examples

## 🔧 Advanced Topics

### Dynamic Schemas

```python
from pydantic import create_model

def create_dynamic_schema(fields: dict):
    """Create schema dynamically."""
    return create_model(
        'DynamicSchema',
        __base__=BaseResponse,
        **{name: (typ, ...) for name, typ in fields.items()}
    )

# Usage
fields = {
    'name': (str, ...),
    'age': (int, ...),
    'email': (str, ...)
}
DynamicSchema = create_dynamic_schema(fields)
```

### Schema Composition

```python
class Address(BaseResponse):
    street: str
    city: str
    zip_code: str

class User(BaseResponse):
    name: str
    email: str
    address: Address  # Nested schema
    preferences: dict

class Order(BaseResponse):
    user: User  # Reuse User schema
    items: List[dict]
    total: float
```

## 📖 Summary

- **Schemas** define expected response structure
- **Pydantic** provides powerful validation
- **Field constraints** ensure data quality
- **Validators** enable custom logic
- **Inheritance** promotes code reuse
- **Early validation** catches errors quickly

Remember: Good schemas = reliable applications!
## 📈 What's Next?


- Explore the [Judge System](judges.md) - Use any model as a judge
- Check out [Examples](examples.md) - See real-world use cases
- Read the [API Reference](api.md) - Detailed documentation

## 🆘 Getting Help

- [GitHub Issues](https://github.com/Dr-Mo-Khalaf/trustguard/issues)
- [Discussions](https://github.com/Dr-Mo-Khalaf/trustguard/discussions)