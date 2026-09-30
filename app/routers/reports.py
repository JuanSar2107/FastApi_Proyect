from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Category, InventoryMovement, Product, Supplier, User
from app.schemas import InventorySummary, LowStockItem

router = APIRouter(prefix="/api/reports", tags=["Reportes"])


@router.get("/low-stock", response_model=list[LowStockItem])
def low_stock_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    products = (
        db.query(Product)
        .filter(Product.is_active == 1)
        .filter(Product.stock_quantity <= Product.min_stock)
        .all()
    )
    return [
        LowStockItem(
            product_id=p.id,
            product_name=p.name,
            sku=p.sku,
            current_stock=p.stock_quantity,
            min_stock=p.min_stock,
            shortage=p.min_stock - p.stock_quantity,
        )
        for p in products
    ]


@router.get("/summary", response_model=InventorySummary)
def inventory_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == 1).scalar()
    total_categories = db.query(func.count(Category.id)).scalar()
    total_suppliers = db.query(func.count(Supplier.id)).scalar()
    total_stock_value = db.query(func.sum(Product.stock_quantity * Product.cost)).filter(
        Product.is_active == 1
    ).scalar() or 0.0
    low_stock_count = (
        db.query(func.count(Product.id))
        .filter(Product.is_active == 1)
        .filter(Product.stock_quantity <= Product.min_stock)
        .scalar()
    )
    recent_movements = db.query(func.count(InventoryMovement.id)).scalar()

    return InventorySummary(
        total_products=total_products,
        total_categories=total_categories,
        total_suppliers=total_suppliers,
        total_stock_value=round(total_stock_value, 2),
        low_stock_count=low_stock_count,
        recent_movements=recent_movements,
    )
