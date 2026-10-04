from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from .database import get_db
from . import models, schemas
from sqlalchemy.orm import Session
from .recommendations import load_rules

router = APIRouter(prefix="/api/cart", tags=["cart"])

# In-memory cart for prototype (simulating a session)
CART_SESSION: Dict[int, int] = {}

def calculate_discount(cart_product_names: List[str]):
    rules_df = load_rules()
    if rules_df.empty:
        return 0.0, None, None
        
    best_discount = 0.0
    tier = None
    reason = None
    
    # Check if cart contains any rule's full bundle (antecedent + consequent)
    for _, row in rules_df.iterrows():
        bundle_items = [i.strip() for i in row["antecedents"].split("+")] + [i.strip() for i in row["consequents"].split("+")]
        if all(item in cart_product_names for item in bundle_items):
            conf = row["confidence"]
            lift = row["lift"]
            
            # Apply business logic
            if conf >= 0.70 and lift >= 2.0:
                disc = 0.05
                t = "Very Strong Relationship"
                r = "5% bundle discount applied for buying highly complementary items!"
            elif conf >= 0.50 and lift >= 1.5:
                disc = 0.10
                t = "Strong Relationship"
                r = "10% bundle discount applied!"
            elif conf >= 0.30 and lift >= 1.2:
                disc = 0.15
                t = "Moderate Relationship"
                r = "15% bundle discount applied!"
            else:
                disc = 0.0
                t = None
                r = None
                
            if disc > best_discount:
                best_discount = disc
                tier = t
                reason = r
                
    return best_discount, tier, reason

@router.get("/", response_model=schemas.CartSummary)
def get_cart(db: Session = Depends(get_db)):
    items = []
    subtotal = 0.0
    cart_product_names = []
    
    for product_id, quantity in CART_SESSION.items():
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if product:
            item_subtotal = product.price * quantity
            subtotal += item_subtotal
            cart_product_names.append(product.name)
            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": round(item_subtotal, 2)
            })
            
    discount_pct, tier, reason = calculate_discount(cart_product_names)
    discount_amount = round(subtotal * discount_pct, 2)
    final_total = round(subtotal - discount_amount, 2)
    
    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "discount": discount_amount,
        "final_total": final_total,
        "applied_bundle_tier": tier,
        "savings_reason": reason
    }

@router.post("/add")
def add_to_cart(item: schemas.CartItemAdd, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    CART_SESSION[item.product_id] = CART_SESSION.get(item.product_id, 0) + item.quantity
    return {"message": "Added to cart", "cart_count": sum(CART_SESSION.values())}

@router.put("/update")
def update_cart(item: schemas.CartItemUpdate):
    if item.product_id in CART_SESSION:
        if item.quantity <= 0:
            del CART_SESSION[item.product_id]
        else:
            CART_SESSION[item.product_id] = item.quantity
    return {"message": "Cart updated", "cart_count": sum(CART_SESSION.values())}

@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: int):
    if product_id in CART_SESSION:
        del CART_SESSION[product_id]
    return {"message": "Removed from cart", "cart_count": sum(CART_SESSION.values())}

@router.post("/clear")
def clear_cart():
    CART_SESSION.clear()
    return {"message": "Cart cleared"}

@router.get("/count")
def get_cart_count():
    return {"count": sum(CART_SESSION.values())}

@router.post("/checkout", response_model=schemas.OrderResponse)
def checkout(order_details: schemas.OrderCreate, db: Session = Depends(get_db)):
    if not CART_SESSION:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    cart_summary = get_cart(db)
    
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
        user_id=order_details.user_id
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
    CART_SESSION.clear()
    
    return {"id": order.id, "total": order.total, "message": "Order placed successfully!"}

@router.get("/orders", response_model=List[schemas.FullOrderResponse])
def get_orders(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Order)
    if user_id is not None:
        query = query.filter(models.Order.user_id == user_id)
    orders = query.order_by(models.Order.id.desc()).all()
    return orders

@router.post("/orders/{order_id}/return")
def request_return(order_id: int, return_req: schemas.ReturnRequest, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status in ["Return Requested", "Returned"]:
        raise HTTPException(status_code=400, detail="Return already requested for this order")
    if order.status == "Processing":
        raise HTTPException(status_code=400, detail="Cannot return an order that is still processing")
    order.status = "Return Requested"
    db.commit()
    return {"message": "Return request submitted successfully", "order_id": order_id, "status": order.status}

@router.get("/orders/{order_id}", response_model=schemas.FullOrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
