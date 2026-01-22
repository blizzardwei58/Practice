"""
Movie Theater Booking Application - Main Flask Application

This application provides:
- RESTful API endpoints for movies, seats, and bookings
- Beautiful Bootstrap-based frontend for user interactions
- SQLite database for data persistence
"""
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from models import db, Movie, Seat, Booking
from serializers import MovieSerializer, SeatSerializer, BookingSerializer
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration - use environment variables for production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///movie_theater.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
db.init_app(app)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with tables and sample data"""
    with app.app_context():
        db.create_all()
        
        # Add sample data if database is empty
        if Movie.query.count() == 0:
            sample_movies = [
                Movie(
                    title="The Dark Knight",
                    description="Batman faces the Joker in this epic thriller.",
                    release_date=datetime(2008, 7, 18).date(),
                    duration=152
                ),
                Movie(
                    title="Inception",
                    description="A thief who steals corporate secrets through dream-sharing technology.",
                    release_date=datetime(2010, 7, 16).date(),
                    duration=148
                ),
                Movie(
                    title="Interstellar",
                    description="A team of explorers travel through a wormhole in space.",
                    release_date=datetime(2014, 11, 7).date(),
                    duration=169
                ),
                Movie(
                    title="The Matrix",
                    description="A computer programmer discovers the true nature of reality.",
                    release_date=datetime(1999, 3, 31).date(),
                    duration=136
                ),
            ]
            db.session.add_all(sample_movies)
        
        # Add sample seats if database is empty
        if Seat.query.count() == 0:
            rows = ['A', 'B', 'C', 'D', 'E']
            seats_per_row = 8
            for row in rows:
                for num in range(1, seats_per_row + 1):
                    seat = Seat(seat_number=f"{row}{num}")
                    db.session.add(seat)
        
        db.session.commit()
        print("Database initialized with sample data!")


# ============================================================================
# API ROUTES - MOVIES (CRUD Operations)
# ============================================================================

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies - GET /api/movies/"""
    movies = Movie.query.all()
    return jsonify(MovieSerializer.serialize_many(movies))


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Get a specific movie by ID - GET /api/movies/<id>/"""
    movie = Movie.query.get_or_404(movie_id)
    return jsonify(MovieSerializer.serialize(movie))


@app.route('/api/movies', methods=['POST'])
def create_movie():
    """Create a new movie - POST /api/movies/"""
    data = request.get_json()
    
    # Use serializer for validation
    parsed_data, errors = MovieSerializer.deserialize(data or {})
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    movie = Movie(
        title=parsed_data['title'],
        description=parsed_data['description'],
        release_date=parsed_data['release_date'],
        duration=parsed_data['duration'],
        poster=parsed_data['poster']
    )
    
    db.session.add(movie)
    db.session.commit()
    
    return jsonify(MovieSerializer.serialize(movie)), 201


@app.route('/api/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    """Update a movie - PUT /api/movies/<id>/"""
    movie = Movie.query.get_or_404(movie_id)
    data = request.get_json() or {}
    
    if 'title' in data:
        movie.title = data['title']
    if 'description' in data:
        movie.description = data['description']
    if 'release_date' in data:
        movie.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date() if data['release_date'] else None
    if 'duration' in data:
        movie.duration = data['duration']
    if 'poster' in data:
        movie.poster = data['poster']
    
    db.session.commit()
    return jsonify(MovieSerializer.serialize(movie))


@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    """Delete a movie"""
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': 'Movie deleted successfully'})


# ============================================================================
# API ROUTES - SEATS (Availability and Booking)
# ============================================================================

@app.route('/api/seats', methods=['GET'])
def get_seats():
    """Get all seats with their booking status - GET /api/seats/"""
    seats = Seat.query.order_by(Seat.seat_number).all()
    return jsonify(SeatSerializer.serialize_many(seats))


@app.route('/api/seats/available', methods=['GET'])
def get_available_seats():
    """Get only available (not booked) seats - GET /api/seats/available/"""
    seats = Seat.query.filter_by(is_booked=False).order_by(Seat.seat_number).all()
    return jsonify(SeatSerializer.serialize_many(seats))


@app.route('/api/seats/<int:seat_id>', methods=['GET'])
def get_seat(seat_id):
    """Get a specific seat by ID - GET /api/seats/<id>/"""
    seat = Seat.query.get_or_404(seat_id)
    return jsonify(SeatSerializer.serialize(seat))


@app.route('/api/seats/<int:seat_id>/book', methods=['POST'])
def book_seat(seat_id):
    """Book a specific seat - POST /api/seats/<id>/book/"""
    seat = Seat.query.get_or_404(seat_id)
    
    if seat.is_booked:
        return jsonify({'error': 'Seat is already booked'}), 400
    
    seat.is_booked = True
    db.session.commit()
    
    return jsonify(SeatSerializer.serialize(seat))


@app.route('/api/seats/<int:seat_id>/release', methods=['POST'])
def release_seat(seat_id):
    """Release a booked seat - POST /api/seats/<id>/release/"""
    seat = Seat.query.get_or_404(seat_id)
    seat.is_booked = False
    db.session.commit()
    return jsonify(SeatSerializer.serialize(seat))


# ============================================================================
# API ROUTES - BOOKINGS (Book seats and view history)
# ============================================================================

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings - GET /api/bookings/"""
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return jsonify(BookingSerializer.serialize_many(bookings))


@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get a specific booking by ID - GET /api/bookings/<id>/"""
    booking = Booking.query.get_or_404(booking_id)
    return jsonify(BookingSerializer.serialize(booking))


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking - POST /api/bookings/"""
    data = request.get_json()
    
    # Use serializer for validation
    parsed_data, errors = BookingSerializer.deserialize(data or {})
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Check if movie exists
    movie = Movie.query.get(parsed_data['movie_id'])
    if not movie:
        return jsonify({'error': 'Movie not found'}), 404
    
    # Check if seat exists and is available
    seat = Seat.query.get(parsed_data['seat_id'])
    if not seat:
        return jsonify({'error': 'Seat not found'}), 404
    if seat.is_booked:
        return jsonify({'error': 'Seat is already booked'}), 400
    
    # Create booking
    booking = Booking(
        movie_id=parsed_data['movie_id'],
        seat_id=parsed_data['seat_id'],
        user_name=parsed_data['user_name'],
        user_email=parsed_data['user_email'],
        showtime=parsed_data['showtime']
    )
    
    # Mark seat as booked
    seat.is_booked = True
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify(BookingSerializer.serialize(booking)), 201


@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """Cancel a booking and release the seat"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Release the seat
    seat = Seat.query.get(booking.seat_id)
    if seat:
        seat.is_booked = False
    
    db.session.delete(booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking cancelled successfully'})


@app.route('/api/bookings/user/<user_name>', methods=['GET'])
def get_user_bookings(user_name):
    """Get all bookings for a specific user - GET /api/bookings/user/<name>/"""
    bookings = Booking.query.filter_by(user_name=user_name).order_by(Booking.booking_date.desc()).all()
    return jsonify(BookingSerializer.serialize_many(bookings))


# ============================================================================
# TEMPLATE ROUTES (Frontend Views)
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to movie list"""
    return redirect(url_for('movie_list'))


@app.route('/movies')
def movie_list():
    """Display all movies"""
    movies = Movie.query.all()
    return render_template('bookings/movie_list.html', movies=movies)


@app.route('/movies/<int:movie_id>/book')
def seat_booking(movie_id):
    """Display seat booking page for a movie"""
    movie = Movie.query.get_or_404(movie_id)
    seats = Seat.query.order_by(Seat.seat_number).all()
    return render_template('bookings/seat_booking.html', movie=movie, seats=seats)


@app.route('/bookings/history')
def booking_history():
    """Display booking history"""
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('bookings/booking_history.html', bookings=bookings)


@app.route('/bookings/create', methods=['POST'])
def create_booking_form():
    """Handle booking form submission"""
    movie_id = request.form.get('movie_id')
    seat_id = request.form.get('seat_id')
    user_name = request.form.get('user_name')
    user_email = request.form.get('user_email', '')
    showtime = request.form.get('showtime')
    
    # Validate inputs
    if not all([movie_id, seat_id, user_name]):
        return redirect(url_for('seat_booking', movie_id=movie_id))
    
    # Check if seat is available
    seat = Seat.query.get(seat_id)
    if not seat or seat.is_booked:
        return redirect(url_for('seat_booking', movie_id=movie_id))
    
    # Create booking
    booking = Booking(
        movie_id=int(movie_id),
        seat_id=int(seat_id),
        user_name=user_name,
        user_email=user_email,
        showtime=datetime.strptime(showtime, '%Y-%m-%dT%H:%M') if showtime else None
    )
    
    seat.is_booked = True
    db.session.add(booking)
    db.session.commit()
    
    return redirect(url_for('booking_history'))


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# Initialize database when app starts (works with gunicorn too)
with app.app_context():
    db.create_all()
    # Add sample data if database is empty
    if Movie.query.count() == 0:
        init_db()

if __name__ == '__main__':
    # Get port from environment variable or default to 3000
    # Use 0.0.0.0 to make it accessible from outside (required for DevEdu/Render)
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"\n{'='*60}")
    print("Movie Theater Booking Application")
    print(f"{'='*60}")
    print(f"Server running at: http://localhost:{port}")
    print(f"API Endpoints available at: http://localhost:{port}/api/")
    print(f"{'='*60}\n")
    
    app.run(debug=True, host=host, port=port)

