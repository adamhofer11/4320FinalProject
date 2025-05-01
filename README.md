# Bus Reservation System

A web-based reservation system for managing bus seats for a hackathon trip. Built with Flask and Docker.

## Features

- Interactive seating chart with pricing
- User reservation system
- Admin dashboard with total sales tracking
- Reservation management (view/delete)
- Secure admin authentication

## Prerequisites

- Docker
- Docker Compose (optional)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd bus-reservation-system
```

2. Build and run with Docker:
```bash
docker build -t bus-reservation .
docker run -p 5000:5000 bus-reservation
```

Or run locally:
```bash
pip install -r requirements.txt
python app.py
```

## Usage

1. Access the application at `http://localhost:5000`
2. To make a reservation:
   - Click "Reserve Now"
   - Fill in your details
   - Select a seat from the seating chart
   - Submit the form

3. Admin access:
   - Click "Admin Login"
   - Enter admin credentials
   - View/manage reservations and total sales

## Database

The application uses SQLite with SQLAlchemy ORM. The database file (`reservations.db`) will be created automatically when the application starts.

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── reserve.html
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 