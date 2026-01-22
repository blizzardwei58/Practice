"""
Database Models for Movie Theater Booking Application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Movie(db.Model):
    """Movie model - stores movie information"""
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # Duration in minutes
    poster = db.Column(db.String(500), nullable=True)  # Path to poster image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with bookings
    bookings = db.relationship('Booking', backref='movie', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'duration': self.duration,
            'poster': self.poster,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Movie {self.title}>'


class Seat(db.Model):
    """Seat model - stores seat information and booking status"""
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), nullable=False)  # e.g., "A1", "B5"
    is_booked = db.Column(db.Boolean, default=False)
    
    # Relationship with bookings
    bookings = db.relationship('Booking', backref='seat', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'seat_number': self.seat_number,
            'is_booked': self.is_booked
        }
    
    def __repr__(self):
        return f'<Seat {self.seat_number}>'


class Booking(db.Model):
    """Booking model - stores booking information"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)  # Simple user identification
    user_email = db.Column(db.String(100), nullable=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    showtime = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'movie_title': self.movie.title if self.movie else None,
            'seat_id': self.seat_id,
            'seat_number': self.seat.seat_number if self.seat else None,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'showtime': self.showtime.isoformat() if self.showtime else None
        }
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.user_name}>'

