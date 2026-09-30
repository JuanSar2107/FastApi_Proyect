from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ─── Auth ───────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ─── Usuarios ───────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[int] = None


class UserResponse(UserBase):
    id: int
    is_active: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Categorías ─────────────────────────────────────────────────────────────

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Proveedores ────────────────────────────────────────────────────────────

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Productos ──────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    price: float = Field(default=0.0, ge=0)
    cost: float = Field(default=0.0, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    min_stock: int = Field(default=0, ge=0)
    unit: str = "unidad"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    price: Optional[float] = Field(default=None, ge=0)
    cost: Optional[float] = Field(default=None, ge=0)
    min_stock: Optional[int] = Field(default=None, ge=0)
    unit: Optional[str] = None
    is_active: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    is_active: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductWithRelations(ProductResponse):
    category: Optional[CategoryResponse] = None
    supplier: Optional[SupplierResponse] = None


# ─── Movimientos de Inventario ──────────────────────────────────────────────

class MovementCreate(BaseModel):
    product_id: int
    movement_type: str = Field(..., pattern="^(entry|exit|adjustment)$")
    quantity: int = Field(..., gt=0)
    reason: Optional[str] = None


class MovementResponse(BaseModel):
    id: int
    product_id: int
    user_id: Optional[int] = None
    movement_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Reportes ───────────────────────────────────────────────────────────────

class LowStockItem(BaseModel):
    product_id: int
    product_name: str
    sku: str
    current_stock: int
    min_stock: int
    shortage: int


class InventorySummary(BaseModel):
    total_products: int
    total_categories: int
    total_suppliers: int
    total_stock_value: float
    low_stock_count: int
    recent_movements: int
