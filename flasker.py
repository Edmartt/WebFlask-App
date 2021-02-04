import os
from app import create_app
from flask_migrate import Migrate
app=create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate=Migrate(app)


@app.cli.command()
def test():
    """Run the unit tests"""
    import unittest
    tests=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

