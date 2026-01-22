"""
URL Configuration for Movie Theater Booking Application
Maps URL patterns to view functions
"""

# API Endpoints Overview
# ======================
# 
# Movies API:
#   GET    /api/movies/          - List all movies
#   POST   /api/movies/          - Create a new movie
#   GET    /api/movies/<id>/     - Retrieve a specific movie
#   PUT    /api/movies/<id>/     - Update a specific movie
#   DELETE /api/movies/<id>/     - Delete a specific movie
#
# Seats API:
#   GET    /api/seats/           - List all seats with booking status
#   GET    /api/seats/available/ - List only available seats
#   GET    /api/seats/<id>/      - Get specific seat details
#   POST   /api/seats/<id>/book/ - Book a specific seat
#   POST   /api/seats/<id>/release/ - Release a booked seat
#
# Bookings API:
#   GET    /api/bookings/              - List all bookings
#   POST   /api/bookings/              - Create a new booking
#   GET    /api/bookings/<id>/         - Retrieve a specific booking
#   DELETE /api/bookings/<id>/         - Cancel a booking
#   GET    /api/bookings/user/<name>/  - Get bookings for a specific user
#
# Frontend Routes:
#   GET    /                     - Home page (redirects to movies)
#   GET    /movies/              - Movie listings page
#   GET    /movies/<id>/book/    - Seat booking page for a movie
#   GET    /bookings/history/    - Booking history page
#   POST   /bookings/create/     - Handle booking form submission


def register_routes(app):
    """
    Register all URL routes for the Flask application.
    This function is called from app.py to set up routing.
    """
    from views import (
        # API Views - Movies
        api_get_movies,
        api_get_movie,
        api_create_movie,
        api_update_movie,
        api_delete_movie,
        # API Views - Seats
        api_get_seats,
        api_get_available_seats,
        api_get_seat,
        api_book_seat,
        api_release_seat,
        # API Views - Bookings
        api_get_bookings,
        api_get_booking,
        api_create_booking,
        api_cancel_booking,
        api_get_user_bookings,
        # Frontend Views
        index,
        movie_list,
        seat_booking,
        booking_history,
        create_booking_form
    )
    
    # =========================================================================
    # API Routes - Movies
    # =========================================================================
    app.add_url_rule('/api/movies/', 'api_get_movies', api_get_movies, methods=['GET'])
    app.add_url_rule('/api/movies/', 'api_create_movie', api_create_movie, methods=['POST'])
    app.add_url_rule('/api/movies/<int:movie_id>/', 'api_get_movie', api_get_movie, methods=['GET'])
    app.add_url_rule('/api/movies/<int:movie_id>/', 'api_update_movie', api_update_movie, methods=['PUT'])
    app.add_url_rule('/api/movies/<int:movie_id>/', 'api_delete_movie', api_delete_movie, methods=['DELETE'])
    
    # =========================================================================
    # API Routes - Seats
    # =========================================================================
    app.add_url_rule('/api/seats/', 'api_get_seats', api_get_seats, methods=['GET'])
    app.add_url_rule('/api/seats/available/', 'api_get_available_seats', api_get_available_seats, methods=['GET'])
    app.add_url_rule('/api/seats/<int:seat_id>/', 'api_get_seat', api_get_seat, methods=['GET'])
    app.add_url_rule('/api/seats/<int:seat_id>/book/', 'api_book_seat', api_book_seat, methods=['POST'])
    app.add_url_rule('/api/seats/<int:seat_id>/release/', 'api_release_seat', api_release_seat, methods=['POST'])
    
    # =========================================================================
    # API Routes - Bookings
    # =========================================================================
    app.add_url_rule('/api/bookings/', 'api_get_bookings', api_get_bookings, methods=['GET'])
    app.add_url_rule('/api/bookings/', 'api_create_booking', api_create_booking, methods=['POST'])
    app.add_url_rule('/api/bookings/<int:booking_id>/', 'api_get_booking', api_get_booking, methods=['GET'])
    app.add_url_rule('/api/bookings/<int:booking_id>/', 'api_cancel_booking', api_cancel_booking, methods=['DELETE'])
    app.add_url_rule('/api/bookings/user/<user_name>/', 'api_get_user_bookings', api_get_user_bookings, methods=['GET'])
    
    # =========================================================================
    # Frontend Routes
    # =========================================================================
    app.add_url_rule('/', 'index', index, methods=['GET'])
    app.add_url_rule('/movies/', 'movie_list', movie_list, methods=['GET'])
    app.add_url_rule('/movies/<int:movie_id>/book/', 'seat_booking', seat_booking, methods=['GET'])
    app.add_url_rule('/bookings/history/', 'booking_history', booking_history, methods=['GET'])
    app.add_url_rule('/bookings/create/', 'create_booking_form', create_booking_form, methods=['POST'])
    
    print("✓ All routes registered successfully!")
    return app


