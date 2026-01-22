"""
Serializers for Movie Theater Booking Application
Converts model instances to JSON format and validates input data
"""
from datetime import datetime


class MovieSerializer:
    """Serializer for Movie model"""
    
    @staticmethod
    def serialize(movie):
        """Convert a Movie instance to dictionary/JSON format"""
        return {
            'id': movie.id,
            'title': movie.title,
            'description': movie.description,
            'release_date': movie.release_date.isoformat() if movie.release_date else None,
            'duration': movie.duration,
            'poster': movie.poster,
            'created_at': movie.created_at.isoformat() if movie.created_at else None
        }
    
    @staticmethod
    def serialize_many(movies):
        """Convert a list of Movie instances to list of dictionaries"""
        return [MovieSerializer.serialize(movie) for movie in movies]
    
    @staticmethod
    def deserialize(data):
        """Validate and parse input data for creating/updating a Movie"""
        errors = {}
        
        # Required field validation
        if 'title' not in data or not data['title']:
            errors['title'] = 'Title is required'
        
        # Optional field parsing
        parsed_data = {
            'title': data.get('title', '').strip() if data.get('title') else '',
            'description': data.get('description', '').strip() if data.get('description') else '',
            'duration': None,
            'release_date': None,
            'poster': data.get('poster', '').strip() if data.get('poster') else None
        }
        
        # Duration validation
        if 'duration' in data and data['duration']:
            try:
                parsed_data['duration'] = int(data['duration'])
                if parsed_data['duration'] < 0:
                    errors['duration'] = 'Duration must be a positive number'
            except (ValueError, TypeError):
                errors['duration'] = 'Duration must be a valid integer'
        
        # Release date validation
        if 'release_date' in data and data['release_date']:
            try:
                parsed_data['release_date'] = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
            except ValueError:
                errors['release_date'] = 'Release date must be in YYYY-MM-DD format'
        
        return parsed_data, errors


class SeatSerializer:
    """Serializer for Seat model"""
    
    @staticmethod
    def serialize(seat):
        """Convert a Seat instance to dictionary/JSON format"""
        return {
            'id': seat.id,
            'seat_number': seat.seat_number,
            'is_booked': seat.is_booked
        }
    
    @staticmethod
    def serialize_many(seats):
        """Convert a list of Seat instances to list of dictionaries"""
        return [SeatSerializer.serialize(seat) for seat in seats]
    
    @staticmethod
    def deserialize(data):
        """Validate and parse input data for creating/updating a Seat"""
        errors = {}
        
        if 'seat_number' not in data or not data['seat_number']:
            errors['seat_number'] = 'Seat number is required'
        
        parsed_data = {
            'seat_number': data.get('seat_number', '').strip().upper() if data.get('seat_number') else '',
            'is_booked': bool(data.get('is_booked', False))
        }
        
        return parsed_data, errors


class BookingSerializer:
    """Serializer for Booking model"""
    
    @staticmethod
    def serialize(booking):
        """Convert a Booking instance to dictionary/JSON format"""
        return {
            'id': booking.id,
            'movie_id': booking.movie_id,
            'movie_title': booking.movie.title if booking.movie else None,
            'seat_id': booking.seat_id,
            'seat_number': booking.seat.seat_number if booking.seat else None,
            'user_name': booking.user_name,
            'user_email': booking.user_email,
            'booking_date': booking.booking_date.isoformat() if booking.booking_date else None,
            'showtime': booking.showtime.isoformat() if booking.showtime else None
        }
    
    @staticmethod
    def serialize_many(bookings):
        """Convert a list of Booking instances to list of dictionaries"""
        return [BookingSerializer.serialize(booking) for booking in bookings]
    
    @staticmethod
    def deserialize(data):
        """Validate and parse input data for creating a Booking"""
        errors = {}
        
        # Required field validation
        required_fields = ['movie_id', 'seat_id', 'user_name']
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f'{field.replace("_", " ").title()} is required'
        
        parsed_data = {
            'movie_id': None,
            'seat_id': None,
            'user_name': data.get('user_name', '').strip() if data.get('user_name') else '',
            'user_email': data.get('user_email', '').strip() if data.get('user_email') else '',
            'showtime': None
        }
        
        # Movie ID validation
        if 'movie_id' in data and data['movie_id']:
            try:
                parsed_data['movie_id'] = int(data['movie_id'])
            except (ValueError, TypeError):
                errors['movie_id'] = 'Movie ID must be a valid integer'
        
        # Seat ID validation
        if 'seat_id' in data and data['seat_id']:
            try:
                parsed_data['seat_id'] = int(data['seat_id'])
            except (ValueError, TypeError):
                errors['seat_id'] = 'Seat ID must be a valid integer'
        
        # Showtime validation
        if 'showtime' in data and data['showtime']:
            try:
                parsed_data['showtime'] = datetime.strptime(data['showtime'], '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    parsed_data['showtime'] = datetime.strptime(data['showtime'], '%Y-%m-%d %H:%M')
                except ValueError:
                    errors['showtime'] = 'Showtime must be in YYYY-MM-DDTHH:MM format'
        
        # Email validation (basic)
        if parsed_data['user_email'] and '@' not in parsed_data['user_email']:
            errors['user_email'] = 'Invalid email format'
        
        return parsed_data, errors

