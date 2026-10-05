from pydantic import BaseModel


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
