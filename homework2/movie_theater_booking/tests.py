"""
Unit Tests and Integration Tests for Movie Theater Booking Application
Run with: python -m pytest tests.py -v
Or: python tests.py
"""
import unittest
import json
from datetime import datetime, date
from app import app, db, init_db
from models import Movie, Seat, Booking


class TestConfig:
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'


class BaseTestCase(unittest.TestCase):
    """Base test case with setup and teardown"""
    
    def setUp(self):
        """Set up test fixtures"""
        app.config.from_object(TestConfig)
        self.app = app
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self._create_test_data()
    
    def tearDown(self):
        """Tear down test fixtures"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_data(self):
        """Create sample test data"""
        # Create test movies
        self.movie1 = Movie(
            title="Test Movie 1",
            description="A test movie description",
            release_date=date(2024, 1, 15),
            duration=120
        )
        self.movie2 = Movie(
            title="Test Movie 2",
            description="Another test movie",
            release_date=date(2024, 6, 20),
            duration=90
        )
        db.session.add_all([self.movie1, self.movie2])
        
        # Create test seats
        self.seat1 = Seat(seat_number="A1", is_booked=False)
        self.seat2 = Seat(seat_number="A2", is_booked=False)
        self.seat3 = Seat(seat_number="A3", is_booked=True)  # Already booked
        db.session.add_all([self.seat1, self.seat2, self.seat3])
        
        db.session.commit()
        
        # Create test booking
        self.booking1 = Booking(
            movie_id=self.movie1.id,
            seat_id=self.seat3.id,
            user_name="Test User",
            user_email="test@example.com"
        )
        db.session.add(self.booking1)
        db.session.commit()


# =============================================================================
# UNIT TESTS - Models
# =============================================================================

class TestMovieModel(BaseTestCase):
    """Unit tests for Movie model"""
    
    def test_movie_creation(self):
        """Test movie can be created with all fields"""
        movie = Movie(
            title="New Movie",
            description="New description",
            release_date=date(2025, 1, 1),
            duration=150
        )
        db.session.add(movie)
        db.session.commit()
        
        self.assertIsNotNone(movie.id)
        self.assertEqual(movie.title, "New Movie")
        self.assertEqual(movie.duration, 150)
    
    def test_movie_to_dict(self):
        """Test movie serialization to dictionary"""
        movie_dict = self.movie1.to_dict()
        
        self.assertEqual(movie_dict['title'], "Test Movie 1")
        self.assertEqual(movie_dict['duration'], 120)
        self.assertIn('id', movie_dict)
        self.assertIn('release_date', movie_dict)
    
    def test_movie_repr(self):
        """Test movie string representation"""
        self.assertIn("Test Movie 1", repr(self.movie1))
    
    def test_movie_required_title(self):
        """Test that movie requires a title"""
        movie = Movie(description="No title movie")
        db.session.add(movie)
        
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()


class TestSeatModel(BaseTestCase):
    """Unit tests for Seat model"""
    
    def test_seat_creation(self):
        """Test seat can be created"""
        seat = Seat(seat_number="B1", is_booked=False)
        db.session.add(seat)
        db.session.commit()
        
        self.assertIsNotNone(seat.id)
        self.assertEqual(seat.seat_number, "B1")
        self.assertFalse(seat.is_booked)
    
    def test_seat_to_dict(self):
        """Test seat serialization to dictionary"""
        seat_dict = self.seat1.to_dict()
        
        self.assertEqual(seat_dict['seat_number'], "A1")
        self.assertFalse(seat_dict['is_booked'])
    
    def test_seat_booking_status(self):
        """Test seat booking status can be updated"""
        self.seat1.is_booked = True
        db.session.commit()
        
        updated_seat = Seat.query.get(self.seat1.id)
        self.assertTrue(updated_seat.is_booked)
    
    def test_seat_repr(self):
        """Test seat string representation"""
        self.assertIn("A1", repr(self.seat1))


class TestBookingModel(BaseTestCase):
    """Unit tests for Booking model"""
    
    def test_booking_creation(self):
        """Test booking can be created"""
        booking = Booking(
            movie_id=self.movie2.id,
            seat_id=self.seat2.id,
            user_name="New User",
            user_email="newuser@example.com"
        )
        db.session.add(booking)
        db.session.commit()
        
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.user_name, "New User")
        self.assertIsNotNone(booking.booking_date)
    
    def test_booking_to_dict(self):
        """Test booking serialization to dictionary"""
        booking_dict = self.booking1.to_dict()
        
        self.assertEqual(booking_dict['user_name'], "Test User")
        self.assertEqual(booking_dict['movie_title'], "Test Movie 1")
        self.assertEqual(booking_dict['seat_number'], "A3")
    
    def test_booking_relationships(self):
        """Test booking relationships with movie and seat"""
        self.assertEqual(self.booking1.movie.title, "Test Movie 1")
        self.assertEqual(self.booking1.seat.seat_number, "A3")
    
    def test_booking_repr(self):
        """Test booking string representation"""
        self.assertIn("Test User", repr(self.booking1))


# =============================================================================
# INTEGRATION TESTS - API Endpoints
# =============================================================================

class TestMovieAPI(BaseTestCase):
    """Integration tests for Movie API endpoints"""
    
    def test_get_all_movies(self):
        """Test GET /api/movies returns all movies"""
        response = self.client.get('/api/movies')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
    
    def test_get_single_movie(self):
        """Test GET /api/movies/<id> returns specific movie"""
        response = self.client.get(f'/api/movies/{self.movie1.id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], "Test Movie 1")
    
    def test_get_nonexistent_movie(self):
        """Test GET /api/movies/<id> returns 404 for non-existent movie"""
        response = self.client.get('/api/movies/9999')
        
        self.assertEqual(response.status_code, 404)
    
    def test_create_movie(self):
        """Test POST /api/movies creates a new movie"""
        new_movie = {
            'title': 'Created Movie',
            'description': 'A new movie',
            'release_date': '2025-06-15',
            'duration': 110
        }
        response = self.client.post(
            '/api/movies',
            data=json.dumps(new_movie),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Created Movie')
        self.assertEqual(data['duration'], 110)
    
    def test_create_movie_without_title(self):
        """Test POST /api/movies returns error without title"""
        new_movie = {'description': 'No title movie'}
        response = self.client.post(
            '/api/movies',
            data=json.dumps(new_movie),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_update_movie(self):
        """Test PUT /api/movies/<id> updates a movie"""
        update_data = {'title': 'Updated Title', 'duration': 200}
        response = self.client.put(
            f'/api/movies/{self.movie1.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['duration'], 200)
    
    def test_delete_movie(self):
        """Test DELETE /api/movies/<id> deletes a movie"""
        response = self.client.delete(f'/api/movies/{self.movie2.id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify movie is deleted
        check_response = self.client.get(f'/api/movies/{self.movie2.id}')
        self.assertEqual(check_response.status_code, 404)


class TestSeatAPI(BaseTestCase):
    """Integration tests for Seat API endpoints"""
    
    def test_get_all_seats(self):
        """Test GET /api/seats returns all seats"""
        response = self.client.get('/api/seats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
    
    def test_get_available_seats(self):
        """Test GET /api/seats/available returns only available seats"""
        response = self.client.get('/api/seats/available')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)  # seat1 and seat2 are available
        for seat in data:
            self.assertFalse(seat['is_booked'])
    
    def test_get_single_seat(self):
        """Test GET /api/seats/<id> returns specific seat"""
        response = self.client.get(f'/api/seats/{self.seat1.id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['seat_number'], "A1")
    
    def test_book_available_seat(self):
        """Test POST /api/seats/<id>/book books an available seat"""
        response = self.client.post(f'/api/seats/{self.seat1.id}/book')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_booked'])
    
    def test_book_already_booked_seat(self):
        """Test POST /api/seats/<id>/book returns error for booked seat"""
        response = self.client.post(f'/api/seats/{self.seat3.id}/book')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_release_seat(self):
        """Test POST /api/seats/<id>/release releases a booked seat"""
        response = self.client.post(f'/api/seats/{self.seat3.id}/release')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['is_booked'])


class TestBookingAPI(BaseTestCase):
    """Integration tests for Booking API endpoints"""
    
    def test_get_all_bookings(self):
        """Test GET /api/bookings returns all bookings"""
        response = self.client.get('/api/bookings')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
    
    def test_get_single_booking(self):
        """Test GET /api/bookings/<id> returns specific booking"""
        response = self.client.get(f'/api/bookings/{self.booking1.id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user_name'], "Test User")
    
    def test_create_booking(self):
        """Test POST /api/bookings creates a new booking"""
        new_booking = {
            'movie_id': self.movie1.id,
            'seat_id': self.seat1.id,
            'user_name': 'New Booking User',
            'user_email': 'booking@example.com'
        }
        response = self.client.post(
            '/api/bookings',
            data=json.dumps(new_booking),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['user_name'], 'New Booking User')
        
        # Verify seat is now booked
        seat = Seat.query.get(self.seat1.id)
        self.assertTrue(seat.is_booked)
    
    def test_create_booking_for_booked_seat(self):
        """Test POST /api/bookings returns error for already booked seat"""
        new_booking = {
            'movie_id': self.movie1.id,
            'seat_id': self.seat3.id,  # Already booked
            'user_name': 'Another User'
        }
        response = self.client.post(
            '/api/bookings',
            data=json.dumps(new_booking),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_booking_missing_fields(self):
        """Test POST /api/bookings returns error for missing required fields"""
        new_booking = {'movie_id': self.movie1.id}  # Missing seat_id and user_name
        response = self.client.post(
            '/api/bookings',
            data=json.dumps(new_booking),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_cancel_booking(self):
        """Test DELETE /api/bookings/<id> cancels a booking and releases seat"""
        booking_seat_id = self.booking1.seat_id
        response = self.client.delete(f'/api/bookings/{self.booking1.id}')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify seat is released
        seat = Seat.query.get(booking_seat_id)
        self.assertFalse(seat.is_booked)
    
    def test_get_user_bookings(self):
        """Test GET /api/bookings/user/<name> returns user's bookings"""
        response = self.client.get('/api/bookings/user/Test User')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_name'], 'Test User')


class TestFrontendRoutes(BaseTestCase):
    """Integration tests for frontend template routes"""
    
    def test_index_redirects_to_movies(self):
        """Test / redirects to movie list"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/movies', response.location)
    
    def test_movie_list_page(self):
        """Test /movies returns movie list page"""
        response = self.client.get('/movies')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Movie 1', response.data)
        self.assertIn(b'Test Movie 2', response.data)
    
    def test_seat_booking_page(self):
        """Test /movies/<id>/book returns seat booking page"""
        response = self.client.get(f'/movies/{self.movie1.id}/book')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Movie 1', response.data)
        self.assertIn(b'A1', response.data)
    
    def test_booking_history_page(self):
        """Test /bookings/history returns booking history page"""
        response = self.client.get('/bookings/history')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test User', response.data)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Running Movie Theater Booking Application Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMovieModel))
    suite.addTests(loader.loadTestsFromTestCase(TestSeatModel))
    suite.addTests(loader.loadTestsFromTestCase(TestBookingModel))
    suite.addTests(loader.loadTestsFromTestCase(TestMovieAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestSeatAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestBookingAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestFrontendRoutes))
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 70)


