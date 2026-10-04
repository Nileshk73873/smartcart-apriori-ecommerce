from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from .database import get_db
from . import models, schemas
from .auth import get_current_user, get_optional_current_user
from sqlalchemy.orm import Session
from .recommendations import load_rules
from src.discount import calculate_bundle_discount

router = APIRouter(prefix="/api/cart", tags=["cart"])

# In-memory per-user / per-session carts
USER_CARTS: Dict[str, Dict[int, int]] = {}


def get_cart_key(
    user: Optional[models.User] = Depends(get_optional_current_user),
    session_id: Optional[str] = Header(None, alias="session-id"),
    x_session_id: Optional[str] = Header(None, alias="x-session-id"),
) -> str:
    if user:
        return f"user_{user.id}"
    sid = x_session_id or session_id
    if sid:
        return f"guest_{sid}"
    return "guest_default"


def get_user_cart(cart_key: str) -> Dict[int, int]:
    return USER_CARTS.setdefault(cart_key, {})


def calculate_discount(cart_items_data: List[Dict[str, Any]]):
    """
    Calculate bundle discount using src.discount.calculate_bundle_discount.
    Discount applies strictly to the line totals of items in the matched bundle.
    """
    rules_df = load_rules()
    if rules_df.empty or not cart_items_data:
        return 0.0, None, None

    cart_product_names = {item["name"] for item in cart_items_data}
    best_discount_amount = 0.0
    best_tier = None
    best_reason = None

    for _, row in rules_df.iterrows():
        bundle_items = [i.strip() for i in str(row["antecedents"]).split("+")] + [
            i.strip() for i in str(row["consequents"]).split("+")
        ]
        # Full bundle must be present in the cart
        if all(item in cart_product_names for item in bundle_items):
            conf = float(row["confidence"])
            lift = float(row["lift"])
            disc_info = calculate_bundle_discount(confidence=conf, lift=lift)
            disc_pct = disc_info["discount_pct"] / 100.0

            if disc_pct > 0:
                # Apply discount ONLY to the line totals of products in the matched bundle
                bundle_line_total = sum(
                    item["subtotal"] for item in cart_items_data if item["name"] in bundle_items
                )
                discount_amount = round(bundle_line_total * disc_pct, 2)

                if discount_amount > best_discount_amount:
                    best_discount_amount = discount_amount
                    best_tier = disc_info["tier"]
                    best_reason = disc_info["rationale"]

    return best_discount_amount, best_tier, best_reason


@router.get("/", response_model=schemas.CartSummary)
def get_cart(cart_key: str = Depends(get_cart_key), db: Session = Depends(get_db)):
    cart_dict = get_user_cart(cart_key)
    items = []
    subtotal = 0.0
    cart_items_data = []

    for product_id, quantity in list(cart_dict.items()):
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if product:
            item_subtotal = round(product.price * quantity, 2)
            subtotal += item_subtotal
            cart_items_data.append({
                "product": product,
                "name": product.name,
                "quantity": quantity,
                "subtotal": item_subtotal
            })
            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": item_subtotal
            })

    discount_amount, tier, reason = calculate_discount(cart_items_data)
    subtotal = round(subtotal, 2)
    final_total = round(max(0.0, subtotal - discount_amount), 2)

    return {
        "items": items,
        "subtotal": subtotal,
        "discount": discount_amount,
        "final_total": final_total,
        "applied_bundle_tier": tier,
        "savings_reason": reason
    }


@router.post("/add")
def add_to_cart(
    item: schemas.CartItemAdd,
    cart_key: str = Depends(get_cart_key),
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_dict = get_user_cart(cart_key)
    cart_dict[item.product_id] = cart_dict.get(item.product_id, 0) + item.quantity
    return {"message": "Added to cart", "cart_count": sum(cart_dict.values())}


@router.put("/update")
def update_cart(item: schemas.CartItemUpdate, cart_key: str = Depends(get_cart_key)):
    cart_dict = get_user_cart(cart_key)
    if item.product_id in cart_dict:
        if item.quantity <= 0:
            del cart_dict[item.product_id]
        else:
            cart_dict[item.product_id] = item.quantity
    return {"message": "Cart updated", "cart_count": sum(cart_dict.values())}


@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: int, cart_key: str = Depends(get_cart_key)):
    cart_dict = get_user_cart(cart_key)
    if product_id in cart_dict:
        del cart_dict[product_id]
    return {"message": "Removed from cart", "cart_count": sum(cart_dict.values())}


@router.post("/clear")
def clear_cart(cart_key: str = Depends(get_cart_key)):
    cart_dict = get_user_cart(cart_key)
    cart_dict.clear()
    return {"message": "Cart cleared"}


@router.get("/count")
def get_cart_count(cart_key: str = Depends(get_cart_key)):
    cart_dict = get_user_cart(cart_key)
    return {"count": sum(cart_dict.values())}


@router.post("/checkout", response_model=schemas.OrderResponse)
def checkout(
    order_details: schemas.OrderCreate,
    cart_key: str = Depends(get_cart_key),
    user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    cart_dict = get_user_cart(cart_key)
    if not cart_dict:
        raise HTTPException(status_code=400, detail="Cart is empty")

    cart_summary = get_cart(cart_key=cart_key, db=db)
    user_id = user.id if user else order_details.user_id

    order = models.Order(
        customer_name=order_details.customer_name,
        email=order_details.email,
        address=order_details.address,
        city=order_details.city,
        postal_code=order_details.postal_code,
        subtotal=cart_summary["subtotal"],
        discount=cart_summary["discount"],
        total=cart_summary["final_total"],
        status="Processing",
        user_id=user_id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart_summary["items"]:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["product"].price
        )
        db.add(order_item)

    db.commit()
    cart_dict.clear()

    return {"id": order.id, "total": order.total, "message": "Order placed successfully!"}


@router.get("/orders", response_model=List[schemas.FullOrderResponse])
def get_orders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.id.desc())
        .all()
    )
    return orders


@router.post("/orders/{order_id}/return")
def request_return(
    order_id: int,
    return_req: schemas.ReturnRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to return this order")
    if order.status in ["Return Requested", "Returned"]:
        raise HTTPException(status_code=400, detail="Return already requested for this order")
    if order.status == "Processing":
        raise HTTPException(status_code=400, detail="Cannot return an order that is still processing")
    order.status = "Return Requested"
    db.commit()
    return {"message": "Return request submitted successfully", "order_id": order_id, "status": order.status}


@router.get("/orders/{order_id}", response_model=schemas.FullOrderResponse)
def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order

