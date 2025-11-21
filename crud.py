# crud.py
from datetime import date
from typing import List

from sqlalchemy.orm import Session

from models import User, Listing, Rental, Message, Notification
from schemas import UserCreate, ListingCreate, RentalRequestCreate, MessageCreate
from auth import hash_password


# ---------- USERS ----------
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- LISTINGS ----------
def create_listing(db: Session, owner_id: int, listing_in: ListingCreate) -> Listing:
    listing = Listing(
        owner_id=owner_id,
        title=listing_in.title,
        description=listing_in.description,
        price_per_day=listing_in.price_per_day,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def get_all_listings(db: Session) -> List[Listing]:
    return db.query(Listing).filter(Listing.is_active == True).all()


def get_listings_for_owner(db: Session, owner_id: int) -> List[Listing]:
    return db.query(Listing).filter(Listing.owner_id == owner_id).all()


def get_listing(db: Session, listing_id: int) -> Listing | None:
    return db.query(Listing).filter(Listing.id == listing_id).first()


# ---------- RENTALS ----------
def create_rental_request(db: Session, rentee_id: int, req: RentalRequestCreate) -> Rental:
    listing = get_listing(db, req.listing_id)
    if not listing:
        raise ValueError("Listing not found")

    rental = Rental(
        listing_id=listing.id,
        owner_id=listing.owner_id,
        rentee_id=rentee_id,
        start_date=req.start_date,
        end_date=req.end_date,
        status="pending",
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)

    # Notification to owner
    create_notification(
        db,
        user_id=listing.owner_id,
        type="rental_request",
        content=f"New rental request #{rental.id} for listing '{listing.title}'.",
    )

    return rental


def get_rentals_for_rentee(db: Session, rentee_id: int) -> List[Rental]:
    return db.query(Rental).filter(Rental.rentee_id == rentee_id).all()


def get_rentals_for_owner(db: Session, owner_id: int) -> List[Rental]:
    return db.query(Rental).filter(Rental.owner_id == owner_id).all()


def get_rental(db: Session, rental_id: int) -> Rental | None:
    return db.query(Rental).filter(Rental.id == rental_id).first()


def set_rental_status(db: Session, rental: Rental, status: str) -> Rental:
    rental.status = status
    db.commit()
    db.refresh(rental)
    return rental


def approve_rental(db: Session, rental_id: int) -> Rental:
    rental = get_rental(db, rental_id)
    if not rental:
        raise ValueError("Rental not found")
    rental = set_rental_status(db, rental, "approved")
    create_notification(
        db,
        user_id=rental.rentee_id,
        type="rental_approved",
        content=f"Your rental request #{rental.id} was approved.",
    )
    return rental


def deny_rental(db: Session, rental_id: int) -> Rental:
    rental = get_rental(db, rental_id)
    if not rental:
        raise ValueError("Rental not found")
    rental = set_rental_status(db, rental, "denied")
    create_notification(
        db,
        user_id=rental.rentee_id,
        type="rental_denied",
        content=f"Your rental request #{rental.id} was denied.",
    )
    return rental


def confirm_pickup(db: Session, rental_id: int) -> Rental:
    rental = get_rental(db, rental_id)
    if not rental:
        raise ValueError("Rental not found")
    rental = set_rental_status(db, rental, "active")
    create_notification(
        db,
        user_id=rental.owner_id,
        type="pickup_confirmed",
        content=f"Rentee confirmed pickup for rental #{rental.id}.",
    )
    return rental


def confirm_return(db: Session, rental_id: int) -> Rental:
    rental = get_rental(db, rental_id)
    if not rental:
        raise ValueError("Rental not found")
    rental = set_rental_status(db, rental, "completed")
    create_notification(
        db,
        user_id=rental.owner_id,
        type="return_confirmed",
        content=f"Rental #{rental.id} marked as returned.",
    )
    create_notification(
        db,
        user_id=rental.rentee_id,
        type="rental_completed",
        content=f"Rental #{rental.id} has been completed.",
    )
    return rental


# ---------- MESSAGES ----------
def send_message(db: Session, sender_id: int, msg_in: MessageCreate) -> Message:
    rental = get_rental(db, msg_in.rental_id)
    if not rental:
        raise ValueError("Rental not found")

    msg = Message(
        rental_id=msg_in.rental_id,
        sender_id=sender_id,
        receiver_id=msg_in.receiver_id,
        text=msg_in.text,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    create_notification(
        db,
        user_id=msg_in.receiver_id,
        type="message",
        content=f"New message on rental #{msg.rental_id}.",
    )

    return msg


def get_inbox_for_user(db: Session, user_id: int) -> list[Message]:
    return (
        db.query(Message)
        .filter((Message.sender_id == user_id) | (Message.receiver_id == user_id))
        .order_by(Message.created_at.desc())
        .all()
    )


# ---------- NOTIFICATIONS ----------
def create_notification(db: Session, user_id: int, type: str, content: str) -> Notification:
    notif = Notification(
        user_id=user_id,
        type=type,
        content=content,
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_notifications_for_user(db: Session, user_id: int) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
