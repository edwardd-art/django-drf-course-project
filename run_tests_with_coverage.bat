@echo off
echo Running tests with coverage...
coverage run --source='.' manage.py test
coverage report
coverage html
echo HTML report generated in htmlcov/index.html
pause