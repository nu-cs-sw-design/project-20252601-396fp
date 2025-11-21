# main.py
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import schemas
import crud
import auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Campus Rental Platform")


# ---------- STATIC UI ----------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


# ---------- AUTH ----------

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(db, user)
    return new_user


@app.post("/login", response_model=schemas.LoginResponse)
def login(login_req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_req.email, login_req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return schemas.LoginResponse(user_id=user.id)


# ---------- LISTINGS ----------

@app.post("/listings/create", response_model=schemas.ListingOut)
def create_listing(
    user_id: int,
    listing_in: schemas.ListingCreate,
    db: Session = Depends(get_db),
):
    owner = db.query(models.User).filter(models.User.id == user_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner user not found")
    listing = crud.create_listing(db, owner_id=user_id, listing_in=listing_in)
    return listing


@app.get("/listings", response_model=List[schemas.ListingOut])
def list_listings(db: Session = Depends(get_db)):
    return crud.get_all_listings(db)


@app.get("/users/{user_id}/listings", response_model=List[schemas.ListingOut])
def get_user_listings(user_id: int, db: Session = Depends(get_db)):
    return crud.get_listings_for_owner(db, user_id)


# ---------- RENTALS ----------

@app.post("/rentals/request", response_model=schemas.RentalOut)
def request_rental(
    rentee_id: int,
    req: schemas.RentalRequestCreate,
    db: Session = Depends(get_db),
):
    rentee = db.query(models.User).filter(models.User.id == rentee_id).first()
    if not rentee:
        raise HTTPException(status_code=404, detail="Rentee user not found")
    try:
        rental = crud.create_rental_request(db, rentee_id=rentee_id, req=req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return rental


@app.get("/rentals/rentee", response_model=List[schemas.RentalOut])
def rentals_for_rentee(rentee_id: int, db: Session = Depends(get_db)):
    return crud.get_rentals_for_rentee(db, rentee_id)


@app.get("/rentals/owner", response_model=List[schemas.RentalOut])
def rentals_for_owner(owner_id: int, db: Session = Depends(get_db)):
    return crud.get_rentals_for_owner(db, owner_id)


@app.post("/rentals/{rental_id}/approve", response_model=schemas.RentalOut)
def approve_rental(rental_id: int, db: Session = Depends(get_db)):
    try:
        rental = crud.approve_rental(db, rental_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rental


@app.post("/rentals/{rental_id}/deny", response_model=schemas.RentalOut)
def deny_rental(rental_id: int, db: Session = Depends(get_db)):
    try:
        rental = crud.deny_rental(db, rental_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rental


@app.post("/rentals/{rental_id}/pickup", response_model=schemas.RentalOut)
def pickup_rental(rental_id: int, db: Session = Depends(get_db)):
    try:
        rental = crud.confirm_pickup(db, rental_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rental


@app.post("/rentals/{rental_id}/return", response_model=schemas.RentalOut)
def return_rental(rental_id: int, db: Session = Depends(get_db)):
    try:
        rental = crud.confirm_return(db, rental_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return rental


# ---------- MESSAGES ----------

@app.post("/messages/send", response_model=schemas.MessageOut)
def send_message(
    sender_id: int,
    msg_in: schemas.MessageCreate,
    db: Session = Depends(get_db),
):
    sender = db.query(models.User).filter(models.User.id == sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    try:
        msg = crud.send_message(db, sender_id=sender_id, msg_in=msg_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return msg


@app.get("/messages/inbox", response_model=List[schemas.MessageOut])
def inbox(user_id: int, db: Session = Depends(get_db)):
    return crud.get_inbox_for_user(db, user_id)


# ---------- NOTIFICATIONS ----------

@app.get("/notifications", response_model=List[schemas.NotificationOut])
def notifications(user_id: int, db: Session = Depends(get_db)):
    return crud.get_notifications_for_user(db, user_id)
