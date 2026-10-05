from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.categories import CategoryResponse
from app.schemas.suppliers import SupplierResponse


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    description: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    price: float = Field(default=0.0, ge=0)
    cost: float = Field(default=0.0, ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    min_stock: int = Field(default=0, ge=0)
    unit: str = "unidad"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    description: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    price: float | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    min_stock: int | None = Field(default=None, ge=0)
    unit: str | None = None
    is_active: int | None = None


class ProductResponse(ProductBase):
    id: int
    is_active: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductWithRelations(ProductResponse):
    category: CategoryResponse | None = None
    supplier: SupplierResponse | None = None
