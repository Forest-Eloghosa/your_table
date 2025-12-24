# YourTable - Minimal Core ERD

This ERD represents the essential database schema for YourTable, focusing on core functionality for restaurant booking, menu management, and reviews.



```
Table users {
  id int [pk]
  username varchar [unique]
  email varchar [unique]
  password varchar
  first_name varchar
  last_name varchar
}

Table restaurant {
  id int [pk]
  name varchar [unique]
  slug varchar [unique]
  description text
  address varchar
  phone varchar
}

Table menu_category {
  id int [pk]
  name varchar
  description text
  slug varchar [unique]
}

Table menu_item {
  id int [pk]
  category_id int [ref: > menu_category.id]
  name varchar
  slug varchar [unique]
  description text
  price decimal(6,2)
  image varchar
  allergens varchar
  is_active boolean
}

Table booking {
  id int [pk]
  user_id int [ref: > users.id]
  restaurant_id int [ref: > restaurant.id]
  date datetime
  guests int
  special_requests text
  is_deleted boolean
  deleted_at datetime
  created_at datetime
}

Table booking_status {
  id int [pk]
  booking_id int [ref: > booking.id, unique]
  status varchar
  updated_at datetime
}

Table booking_history {
  id int [pk]
  booking_pk int
  user_id int [ref: > users.id, null]
  action varchar
  timestamp datetime
  data json
}

Table review {
  id int [pk]
  user_id int [ref: > users.id, null]
  guest_name varchar
  rating smallint
  comment text
  image varchar
  created_at datetime
}
```

## Schema Overview

### Core Tables:

**users** — Django's authentication table
- Stores login credentials and user profile info
- Referenced by bookings, reviews, and booking_history

**restaurant** — Single or multiple restaurant locations
- Stores restaurant details (name, address, contact)
- Referenced by bookings

**menu_category** — Menu organization
- Groups menu items by category (Starters, Mains, Desserts, etc.)
- Referenced by menu_item

**menu_item** — Individual dishes/items
- Price, description, allergen info, availability
- Linked to category via FK

**booking** — User reservations
- Links user to restaurant with date/time/guest count
- Soft-delete support (is_deleted flag)
- Special requests for dietary/accessibility needs

**booking_status** — Booking lifecycle
- Tracks pending → confirmed → completed/canceled
- One-to-one with booking (unique constraint)

**booking_history** — Audit trail
- Records create/update/delete events on bookings
- Supports user activity tracking (as seen in Profile page)

**review** — Customer feedback
- Supports authenticated and anonymous reviews
- Rating (1-5), comment, optional image
- Linked to user (nullable for guest reviews)

---

## Key Design Decisions

1. **Soft Deletes**: Bookings use `is_deleted` flag to preserve history instead of hard deletion
2. **Audit Trail**: `booking_history` tracks all changes for user transparency
3. **Status Tracking**: Separate `booking_status` table for clean status management
4. **Anonymous Reviews**: `user_id` nullable on reviews; `guest_name` for non-authenticated users
5. **No Direct Table Assignment**: Removed `table` from initial ERD as it's not actively used in current features
6. **Allergen Support**: `allergens` field on menu items for accessibility

---

## Relationships Summary

```
users ──→ booking
users ──→ booking_history
users ──→ review
restaurant ──→ booking
restaurant ──→ menu_category
menu_category ──→ menu_item
booking ──→ booking_status (1:1)
booking ──→ booking_history (1:many)
```


