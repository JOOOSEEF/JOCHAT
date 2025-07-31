import pytest
from backend.run import create_app

def test_app_creation():
    app = create_app()
    assert app.name == 'flask.app'
