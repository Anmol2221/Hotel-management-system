# Orion Hotel Management System

The Orion Hotel Management System is a web-based platform designed to streamline hotel room management, customer bookings, and administrative tasks for both hotel staff and guests. The system provides an intuitive interface for administrators to manage room availability and customer data, while also allowing customers to register, log in, view their bookings, and make reservations online. This integrated approach ensures efficient, user-friendly management of hotel operations and guest experiences.

---

## Features

### Admin Portal
- Secure admin login
- Dashboard for all admin operations
- Add new customers and bookings
- View room status
- Manage bookings
- View customer details

### Customer Portal
- Customer registration and login
- Dashboard with current booking details
- Book a room if available
- Real-time feedback on booking status
- Logout

### General
- Persistent data storage with SQLite
- Modern, responsive HTML/CSS interface
- Flash messaging for user feedback

---

## Current Status

The user interface and navigation have been fully implemented for both admin and customer perspectives. All pages feature modern, responsive CSS and intuitive navigation.

**Functional HTML Pages:**
- Home Page (index.html): Entry point for the system with navigation to admin and customer login.
- Admin Login Page (admin_login.html): Secure login form for administrators.
- Admin Dashboard (dashboard.html): Central navigation hub for all admin functionalities.
- Add Customer Page (add.html): Form for entering new customer details, with feedback if no rooms are available.
- View Rooms Page (rooms.html): Table displaying room numbers and their current status.
- Manage Bookings Page (manage.html): List of all current bookings with the ability to remove bookings.
- View Customer Details Page (view.html): Table of all customer details and their assigned rooms.
- Customer Login Page (customer_login.html): Secure login form for hotel guests.
- Customer Registration Page (register.html): Registration form for new customers.
- Customer Dashboard (customer_dashboard.html): Personalized dashboard for customers to view bookings and book rooms.

---

## Backend Overview

The backend is developed using Python and Flask. It handles routing, form processing, user authentication for both admins and customers, session management, and flash messaging for real-time feedback. SQLite is used for reliable and efficient data storage.

The backend supports:
- Admin and customer authentication
- Booking logic and room availability checks
- Real-time updates to both admin and customer dashboards
- Secure password storage and session handling

---

## Challenges Faced

- **Routing and Backend Integration:**  
  Ensuring seamless navigation and correct data flow between HTML pages and backend logic was a major challenge, especially as the project expanded to include both admin and customer modules.
- **Database Design and Integration:**  
  Designing the database schema and integrating it with Flask to handle room availability, customer data, and booking status required multiple iterations and careful debugging.
- **Learning HTML and Frontend Development:**  
  Building modern, responsive pages while learning HTML and CSS from scratch added significant complexity, but greatly improved the project’s appearance and usability.

---

## Requirements

- Python 3.x
- Flask

## How to Run

1. Clone or download this repository.
2. (Optional) Create and activate a virtual environment:
