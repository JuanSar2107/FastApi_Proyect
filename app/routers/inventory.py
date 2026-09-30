from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import InventoryMovement, Product, User
from app.schemas import MovementCreate, MovementResponse

router = APIRouter(prefix="/api/inventory", tags=["Inventario"])


@router.post("/movements", response_model=MovementResponse, status_code=201)
def create_movement(
    data: MovementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    previous_stock = product.stock_quantity

    if data.movement_type == "entry":
        new_stock = previous_stock + data.quantity
    elif data.movement_type == "exit":
        new_stock = previous_stock - data.quantity
        if new_stock < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente. Disponible: {previous_stock}",
            )
    elif data.movement_type == "adjustment":
        new_stock = data.quantity
        if new_stock < 0:
            raise HTTPException(status_code=400, detail="El ajuste no puede ser negativo")
    else:
        raise HTTPException(status_code=400, detail="Tipo de movimiento inválido")

    product.stock_quantity = new_stock

    movement = InventoryMovement(
        product_id=data.product_id,
        user_id=current_user.id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        previous_stock=previous_stock,
        new_stock=new_stock,
        reason=data.reason,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/movements", response_model=list[MovementResponse])
def list_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    product_id: int = Query(None),
    movement_type: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(InventoryMovement)
    if product_id:
        query = query.filter(InventoryMovement.product_id == product_id)
    if movement_type:
        query = query.filter(InventoryMovement.movement_type == movement_type)
    return query.order_by(InventoryMovement.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/movements/{movement_id}", response_model=MovementResponse)
def get_movement(
    movement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    movement = db.query(InventoryMovement).filter(InventoryMovement.id == movement_id).first()
    if not movement:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return movement
