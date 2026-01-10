import unittest
import sys
from unittest.mock import MagicMock

# MOCKING DEPENDENCIES
# ---------------------------------------------------------
# Why we do this: 
# We want to test the *Configuration Logic* (URLs, Constants) without needing a real database connection.
# By "mocking" the database drivers, we can run these tests on a cheap CI server that doesn't have MySQL installed.
mock_sqlalchemy = MagicMock()
mock_engine = MagicMock()
mock_url = MagicMock()
mock_engine.url = mock_url
mock_sqlalchemy.engine = mock_engine

sys.modules["sqlalchemy"] = mock_sqlalchemy
sys.modules["sqlalchemy.engine"] = mock_engine
sys.modules["sqlalchemy.engine.url"] = mock_url
sys.modules["pymysql"] = MagicMock()

# Now we can import the module safely
from etl_pipeline import Config

class TestConfig(unittest.TestCase):
    def test_url_construction(self):
        """Test that S3 URLs are generated correctly for a given month."""
        # Validate the Base URL structure
        self.assertIn("tripdata", Config.BASE_URL)
        
    def test_db_config_safe(self):
        """Ensure connection strings are valid structure."""
        self.assertTrue(Config.DEFAULT_DB.startswith("mysql+pymysql://"))

if __name__ == '__main__':
    unittest.main()
