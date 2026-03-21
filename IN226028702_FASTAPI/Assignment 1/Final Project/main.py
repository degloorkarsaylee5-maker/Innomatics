from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import math

# ──────────────────────────────────────────────
# Q1 — App init + GET /
# ──────────────────────────────────────────────
app = FastAPI(title="SpeedRide Car Rentals API")


@app.get("/")
def welcome():
    return {"message": "Welcome to SpeedRide Car Rentals"}


# ──────────────────────────────────────────────
# Q2 — In-memory cars list
# ──────────────────────────────────────────────
cars = [
    {"id": 1, "model": "Swift",      "brand": "Maruti",  "type": "Hatchback", "price_per_day": 1200, "fuel_type": "Petrol",   "is_available": True},
    {"id": 2, "model": "City",       "brand": "Honda",   "type": "Sedan",     "price_per_day": 1800, "fuel_type": "Petrol",   "is_available": True},
    {"id": 3, "model": "Creta",      "brand": "Hyundai", "type": "SUV",       "price_per_day": 2500, "fuel_type": "Diesel",   "is_available": True},
    {"id": 4, "model": "Nexon EV",   "brand": "Tata",    "type": "SUV",       "price_per_day": 2200, "fuel_type": "Electric", "is_available": True},
    {"id": 5, "model": "Camry",      "brand": "Toyota",  "type": "Luxury",    "price_per_day": 4500, "fuel_type": "Petrol",   "is_available": True},
    {"id": 6, "model": "Baleno",     "brand": "Maruti",  "type": "Hatchback", "price_per_day": 1100, "fuel_type": "Petrol",   "is_available": False},
    {"id": 7, "model": "Fortuner",   "brand": "Toyota",  "type": "SUV",       "price_per_day": 3800, "fuel_type": "Diesel",   "is_available": True},
    {"id": 8, "model": "Model 3",    "brand": "Tesla",   "type": "Luxury",    "price_per_day": 8000, "fuel_type": "Electric", "is_available": True},
]

car_id_counter = 9  # next id for newly added cars


@app.get("/cars")
def get_all_cars():
    available = [c for c in cars if c["is_available"]]
    return {
        "total": len(cars),
        "available_count": len(available),
        "cars": cars,
    }


# ──────────────────────────────────────────────
# Q4 — In-memory rentals list
# ──────────────────────────────────────────────
rentals = []
rental_counter = 1


@app.get("/rentals")
def get_all_rentals():
    return {"total": len(rentals), "rentals": rentals}


# ──────────────────────────────────────────────
# Q5 — GET /cars/summary  (must be above /cars/{car_id})
# ──────────────────────────────────────────────
@app.get("/cars/summary")
def get_cars_summary():
    type_breakdown: dict = {}
    fuel_breakdown: dict = {}
    for car in cars:
        type_breakdown[car["type"]] = type_breakdown.get(car["type"], 0) + 1
        fuel_breakdown[car["fuel_type"]] = fuel_breakdown.get(car["fuel_type"], 0) + 1

    prices = [c["price_per_day"] for c in cars]
    cheapest = min(cars, key=lambda c: c["price_per_day"]) if cars else None
    priciest = max(cars, key=lambda c: c["price_per_day"]) if cars else None

    return {
        "total_cars": len(cars),
        "available_count": sum(1 for c in cars if c["is_available"]),
        "breakdown_by_type": type_breakdown,
        "breakdown_by_fuel_type": fuel_breakdown,
        "cheapest_car_per_day": cheapest,
        "most_expensive_car_per_day": priciest,
    }


# ──────────────────────────────────────────────
# Q15 — GET /cars/unavailable  (fixed route — before /{car_id})
# ──────────────────────────────────────────────
@app.get("/cars/unavailable")
def get_unavailable_cars():
    unavailable = [c for c in cars if not c["is_available"]]
    return {"total": len(unavailable), "cars": unavailable}


# ──────────────────────────────────────────────
# Q16 — GET /cars/search
# ──────────────────────────────────────────────
@app.get("/cars/search")
def search_cars(keyword: str = Query(..., min_length=1)):
    kw = keyword.lower()
    matches = [
        c for c in cars
        if kw in c["model"].lower()
        or kw in c["brand"].lower()
        or kw in c["type"].lower()
    ]
    return {"total_found": len(matches), "cars": matches}


# ──────────────────────────────────────────────
# Q17 — GET /cars/sort
# ──────────────────────────────────────────────
VALID_SORT_FIELDS = {"price_per_day", "brand", "type"}


@app.get("/cars/sort")
def sort_cars(sort_by: str = "price_per_day", order: str = "asc"):
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Choose from: {', '.join(VALID_SORT_FIELDS)}",
        )
    if order not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    reverse = order == "desc"
    sorted_cars = sorted(cars, key=lambda c: c[sort_by], reverse=reverse)
    return {"sort_by": sort_by, "order": order, "cars": sorted_cars}


# ──────────────────────────────────────────────
# Q18 — GET /cars/page
# ──────────────────────────────────────────────
@app.get("/cars/page")
def paginate_cars(page: int = Query(default=1, ge=1), limit: int = Query(default=3, ge=1)):
    total = len(cars)
    total_pages = math.ceil(total / limit) if total else 1
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "cars": cars[start:end],
    }


# ──────────────────────────────────────────────
# Q10 — GET /cars/filter
# ──────────────────────────────────────────────
def filter_cars_logic(
    car_list,
    type: Optional[str] = None,
    brand: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
):
    result = car_list
    if type is not None:
        result = [c for c in result if c["type"].lower() == type.lower()]
    if brand is not None:
        result = [c for c in result if c["brand"].lower() == brand.lower()]
    if fuel_type is not None:
        result = [c for c in result if c["fuel_type"].lower() == fuel_type.lower()]
    if max_price is not None:
        result = [c for c in result if c["price_per_day"] <= max_price]
    if is_available is not None:
        result = [c for c in result if c["is_available"] == is_available]
    return result


@app.get("/cars/filter")
def filter_cars(
    type: Optional[str] = None,
    brand: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
):
    result = filter_cars_logic(cars, type, brand, fuel_type, max_price, is_available)
    return {"total": len(result), "cars": result}


# ──────────────────────────────────────────────
# Q20 — GET /cars/browse (combined)
# ──────────────────────────────────────────────
@app.get("/cars/browse")
def browse_cars(
    keyword: Optional[str] = None,
    type: Optional[str] = None,
    fuel_type: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
    sort_by: str = "price_per_day",
    order: str = "asc",
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1),
):
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Choose from: {', '.join(VALID_SORT_FIELDS)}",
        )
    if order not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    result = list(cars)

    # 1. Keyword search
    if keyword:
        kw = keyword.lower()
        result = [
            c for c in result
            if kw in c["model"].lower()
            or kw in c["brand"].lower()
            or kw in c["type"].lower()
        ]

    # 2. Filters
    result = filter_cars_logic(result, type=type, fuel_type=fuel_type,
                               max_price=max_price, is_available=is_available)

    # 3. Sort
    result = sorted(result, key=lambda c: c[sort_by], reverse=(order == "desc"))

    # 4. Paginate
    total = len(result)
    total_pages = math.ceil(total / limit) if total else 1
    start = (page - 1) * limit
    paginated = result[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total_matched": total,
        "total_pages": total_pages,
        "filters_applied": {
            "keyword": keyword,
            "type": type,
            "fuel_type": fuel_type,
            "max_price": max_price,
            "is_available": is_available,
        },
        "sort_by": sort_by,
        "order": order,
        "cars": paginated,
    }


# ──────────────────────────────────────────────
# Q3 — GET /cars/{car_id}
# ──────────────────────────────────────────────
def find_car(car_id: int):
    """Q7 helper — find a car by id or return None."""
    for car in cars:
        if car["id"] == car_id:
            return car
    return None


@app.get("/cars/{car_id}")
def get_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    return car


# ──────────────────────────────────────────────
# Q7 — Cost calculation helper
# ──────────────────────────────────────────────
def calculate_rental_cost(price_per_day: int, days: int, insurance: bool, driver_required: bool):
    """
    Q7 + Q9: Calculates full cost breakdown.
    - 7–14 days → 15% discount on base
    - 15+ days  → 25% discount on base
    - insurance  → +₹500/day
    - driver     → +₹800/day
    """
    base_cost = price_per_day * days

    if days >= 15:
        discount_pct = 25
    elif days >= 7:
        discount_pct = 15
    else:
        discount_pct = 0

    discount_amount = round(base_cost * discount_pct / 100)
    discounted_base = base_cost - discount_amount

    insurance_cost = 500 * days if insurance else 0
    driver_cost = 800 * days if driver_required else 0
    total_cost = discounted_base + insurance_cost + driver_cost

    return {
        "base_cost": base_cost,
        "discount_percent": discount_pct,
        "discount_amount": discount_amount,
        "discounted_base": discounted_base,
        "insurance_cost": insurance_cost,
        "driver_cost": driver_cost,
        "total_cost": total_cost,
    }


# ──────────────────────────────────────────────
# Q6 + Q9 — Pydantic model for rental request
# ──────────────────────────────────────────────
class RentalRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    car_id: int = Field(..., gt=0)
    days: int = Field(..., gt=0, le=30)
    license_number: str = Field(..., min_length=8)
    insurance: bool = False
    driver_required: bool = False  # Q9


# ──────────────────────────────────────────────
# Q8 + Q9 — POST /rentals
# ──────────────────────────────────────────────
@app.post("/rentals", status_code=201)
def create_rental(req: RentalRequest):
    global rental_counter

    car = find_car(req.car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car with id {req.car_id} not found")
    if not car["is_available"]:
        raise HTTPException(status_code=400, detail=f"Car '{car['model']}' is not available")

    cost = calculate_rental_cost(car["price_per_day"], req.days, req.insurance, req.driver_required)

    rental = {
        "rental_id": rental_counter,
        "customer_name": req.customer_name,
        "license_number": req.license_number,
        "car_id": car["id"],
        "car_model": car["model"],
        "car_brand": car["brand"],
        "days": req.days,
        "insurance": req.insurance,
        "driver_required": req.driver_required,
        "status": "active",
        **cost,
    }

    car["is_available"] = False
    rentals.append(rental)
    rental_counter += 1
    return rental


# ──────────────────────────────────────────────
# Q11 — POST /cars  (add a new car)
# ──────────────────────────────────────────────
class NewCar(BaseModel):
    model: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    type: str = Field(..., min_length=2)
    price_per_day: int = Field(..., gt=0)
    fuel_type: str = Field(..., min_length=2)
    is_available: bool = True


@app.post("/cars", status_code=201)
def add_car(new_car: NewCar):
    global car_id_counter

    # Reject duplicate model+brand combos
    for car in cars:
        if (car["model"].lower() == new_car.model.lower()
                and car["brand"].lower() == new_car.brand.lower()):
            raise HTTPException(
                status_code=400,
                detail=f"Car '{new_car.brand} {new_car.model}' already exists",
            )

    car_dict = {
        "id": car_id_counter,
        "model": new_car.model,
        "brand": new_car.brand,
        "type": new_car.type,
        "price_per_day": new_car.price_per_day,
        "fuel_type": new_car.fuel_type,
        "is_available": new_car.is_available,
    }
    cars.append(car_dict)
    car_id_counter += 1
    return car_dict


# ──────────────────────────────────────────────
# Q12 — PUT /cars/{car_id}
# ──────────────────────────────────────────────
@app.put("/cars/{car_id}")
def update_car(
    car_id: int,
    price_per_day: Optional[int] = Query(default=None, gt=0),
    is_available: Optional[bool] = None,
):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")

    if price_per_day is not None:
        car["price_per_day"] = price_per_day
    if is_available is not None:
        car["is_available"] = is_available

    return {"message": "Car updated successfully", "car": car}


# ──────────────────────────────────────────────
# Q13 — DELETE /cars/{car_id}
# ──────────────────────────────────────────────
@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")

    active = [r for r in rentals if r["car_id"] == car_id and r["status"] == "active"]
    if active:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete car {car_id} — it has an active rental (rental_id={active[0]['rental_id']})",
        )

    cars.remove(car)
    return {"message": f"Car {car_id} deleted successfully"}


# ──────────────────────────────────────────────
# Q14 — GET /rentals/{rental_id}  +  POST /return/{rental_id}
# ──────────────────────────────────────────────
def find_rental(rental_id: int):
    for r in rentals:
        if r["rental_id"] == rental_id:
            return r
    return None


@app.get("/rentals/{rental_id}")
def get_rental(rental_id: int):
    rental = find_rental(rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail=f"Rental with id {rental_id} not found")
    return rental


@app.post("/return/{rental_id}")
def return_car(rental_id: int):
    rental = find_rental(rental_id)
    if not rental:
        raise HTTPException(status_code=404, detail=f"Rental with id {rental_id} not found")
    if rental["status"] == "returned":
        raise HTTPException(status_code=400, detail=f"Rental {rental_id} is already returned")

    rental["status"] = "returned"

    car = find_car(rental["car_id"])
    if car:
        car["is_available"] = True

    return {"message": "Car returned successfully", "rental": rental}


# ──────────────────────────────────────────────
# Q15 — GET /rentals/active  +  GET /rentals/by-car/{car_id}
# ──────────────────────────────────────────────
@app.get("/rentals/active")
def get_active_rentals():
    active = [r for r in rentals if r["status"] == "active"]
    return {"total": len(active), "rentals": active}


@app.get("/rentals/by-car/{car_id}")
def get_rentals_by_car(car_id: int):
    car = find_car(car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car with id {car_id} not found")
    history = [r for r in rentals if r["car_id"] == car_id]
    return {"car_id": car_id, "total": len(history), "rentals": history}


# ──────────────────────────────────────────────
# Q19 — GET /rentals/search  |  /rentals/sort  |  /rentals/page
# ──────────────────────────────────────────────
VALID_RENTAL_SORT = {"total_cost", "days"}


@app.get("/rentals/search")
def search_rentals(customer_name: str = Query(..., min_length=1)):
    kw = customer_name.lower()
    matches = [r for r in rentals if kw in r["customer_name"].lower()]
    return {"total_found": len(matches), "rentals": matches}


@app.get("/rentals/sort")
def sort_rentals(sort_by: str = "total_cost", order: str = "asc"):
    if sort_by not in VALID_RENTAL_SORT:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Choose from: {', '.join(VALID_RENTAL_SORT)}",
        )
    if order not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    sorted_rentals = sorted(rentals, key=lambda r: r[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "rentals": sorted_rentals}


@app.get("/rentals/page")
def paginate_rentals(page: int = Query(default=1, ge=1), limit: int = Query(default=3, ge=1)):
    total = len(rentals)
    total_pages = math.ceil(total / limit) if total else 1
    start = (page - 1) * limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "rentals": rentals[start:start + limit],
    }