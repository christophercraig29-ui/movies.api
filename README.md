movies.api
A simple RESTful API for managing a movie collection, built with Python and Flask.

Features
List all movies, or filter by director with a query parameter
Get details about a single movie by its ID
Returns data in easy-to-use JSON format
Includes Swagger documentation for all endpoints
Tech Stack
Python
Flask
Swagger
Getting Started
Clone this repo:
git clone https://github.com/yourusername/movies.api.git
cd movies.api
Install dependencies:
pip install flask flasgger
Run the server:
python app.py
Open your browser at http://localhost:5000
Swagger docs are usually at http://localhost:5000/apidocs.

Example Endpoints
GET /movies — List all movies (optionally filter by director)
GET /movies/1 — Get details for movie with ID=1
License
Open-source—feel free to use or adapt!