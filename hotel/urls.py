# hotel/urls.py
# This file maps all URL paths to their corresponding view functions.
# It replaces the URL routing logic from the CustomHandler in main.py.

from django.urls import path
from hotel import views

urlpatterns = [
    # ── Page Routes (HTML Templates) ──
    path("", views.housekeeping_page, name="home"),
    path("housekeeping", views.housekeeping_page, name="housekeeping"),
    path("loyalty", views.loyalty_page, name="loyalty"),
    path("staff", views.staff_page, name="staff"),
    path("guest-registration", views.guest_registration_page, name="guest-registration"),
    path("room-booking", views.room_booking_page, name="room-booking"),
    path("checkin-checkout", views.checkin_checkout_page, name="checkin-checkout"),

    # ── API GET Endpoints ──
    path("api/data", views.api_get_all_data, name="api-data"),
    path("api/guest-registration/meta", views.api_guest_meta, name="api-guest-meta"),
    path("api/room-booking/meta", views.api_booking_meta, name="api-booking-meta"),
    path("api/loyalty/member", views.api_loyalty_lookup, name="api-loyalty-lookup"),

    # ── API POST Endpoints ──
    path("api/rooms/update", views.api_update_room, name="api-update-room"),
    path("api/loyalty/redeem", views.api_redeem_reward, name="api-redeem-reward"),
    path("api/loyalty/add-points", views.api_add_points, name="api-add-points"),
    path("api/staff/add", views.api_add_staff, name="api-add-staff"),
    path("api/staff/edit-role", views.api_edit_staff_role, name="api-edit-role"),
    path("api/staff/toggle-status", views.api_toggle_staff_status, name="api-toggle-status"),
    path("api/guest-registration/create", views.api_create_guest, name="api-create-guest"),
    path("api/room-booking/availability", views.api_room_availability, name="api-room-availability"),
    path("api/room-booking/create", views.api_create_reservation, name="api-create-reservation"),
    path("api/checkin-checkout/lookup", views.api_lookup_reservation, name="api-lookup-reservation"),
    path("api/checkin-checkout/checkin", views.api_checkin, name="api-checkin"),
    path("api/checkin-checkout/checkout", views.api_checkout, name="api-checkout"),
    path("api/checkin-checkout/rooms-available", views.api_rooms_available_count, name="api-rooms-available"),
]