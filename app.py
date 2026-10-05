from flasgger import Swagger

from flask import Flask, jsonify, send_file, request


app = Flask(__name__)

swagger = Swagger(app)

movies = [
    {
        "id": 1,
        "title": "The Matrix",
        "director": "The Wachowskis",
        "year": 1999,
        "watched": True,
    },
    {
        "id": 2,
        "title": "Inception",
        "director": "Christopher Nolan",
        "year": 2010,
        "watched": False,
    },
    {
        "id": 3,
        "title": "Spirited Away",
        "director": "Hayao Miyazaki",
        "year": 2001,
        "watched": True,
    },
]



@app.route("/")
def index():
    return send_file("index.html")



@app.get("/movies")
def get_movies():
    """
    Get all movies (optionally filtered by director)
    ---
    parameters:
      - name: director
        in: query
        type: string
        required: false
        description: Filter movies by exact director name
    responses:
      200:
        description: A list of movies
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              director:
                type: string
              year:
                type: integer
              watched:
                type: boolean
    """
    # 1. Read the ?director=... query parameter (or None if missing)
    director = request.args.get("director")
    print("DEBUG director =", repr(director))
    # 2. Decide what to return
    if director is None:
        # No director filter → return all movies
        result = movies
    else:
        # Director given → filter for exact, case-sensitive matches
        result = []
        for movie in movies:
            if movie["director"] == director:
                result.append(movie)

    # 3. Return the chosen list as JSON
    return jsonify(result)

@app.route("/movies/<int:id>")
def get_movie(id):
    # 1. Try to find the movie with this id
    for movie in movies:
        if movie["id"] == id:
            # 2. If found, return it with 200 OK
            return jsonify(movie), 200

    # 3. If not found, return a 404 JSON error
    return jsonify({
        "error": "Not found",
        "message": "No movie with that id."
    }), 404

@app.route("/movies/<int:id>", methods=["DELETE"])
def delete_movie(id):
    # look for the movie by id
    for movie in movies:
        if movie["id"] == id:
            movies.remove(movie)          # remove from the list
            return "", 204                # 204 No Content, no body

    # if we didn't return inside the loop, it's not found
    return jsonify({
        "error": "Not found",
        "message": "No movie with that id."
    }), 404

@app.route("/movies/body-test", methods=["POST"])
def movies_body_test():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Request body must be JSON with Content-Type: application/json"}), 400

    missing = [field for field in ("title", "year") if field not in data]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    title = data["title"]
    year = data["year"]
    return jsonify({
        "received_title": title,
        "received_year": year
    })

@app.post("/movies")
def create_movie():
    data = request.get_json()

    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body must be JSON."
        }), 400

    required_fields = ["title", "director", "year", "watched"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": "Bad Request",
                "message": f"Field '{field}' is required."
            }), 400

    if not isinstance(data["title"], str):
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'title' must be a string"
        }), 400

    if not isinstance(data["director"], str):
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'director' must be a string."
        }), 400

    if not isinstance(data["year"], int):
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'year' must be a number."
        }), 400

    if not isinstance(data["watched"], bool):
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'watched' must be a boolean."
        }), 400

    if data["title"].strip() == "":
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'title' cannot be empty."
        }), 400

    if data["director"].strip() == "":
        return jsonify({
            "error": "Bad Request",
            "message": "Field 'director' cannot be empty."
        }), 400
    
    # 1. Decide the new id (server-side)
    if movies:
        new_id = max(movie["id"] for movie in movies) + 1
    else:
        new_id = 1

    # 2. Build the new movie from the request body + new_id
    new_movie = {
        "id": new_id,
        "title": data["title"],
        "director": data["director"],
        "year": data["year"],
        "watched": data["watched"],
    }

    # 3. Store it
    movies.append(new_movie)

    # 4. Return it with 201 Created
    return jsonify(new_movie), 201

@app.put("/movies/<int:movie_id>")
def update_movie(movie_id):
    data = request.get_json()

    # 1. find the movie
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404

    # 2. replace fields (but keep id)
    movie["title"] = data["title"]
    movie["director"] = data["director"]
    movie["year"] = data["year"]
    movie["watched"] = data["watched"]

    # 3. return updated movie
    return jsonify(movie), 200

@app.post("/movies/<int:movie_id>/reviews")
def add_review(movie_id):
    # 1. Find the movie
    movie = next((m for m in movies if m["id"] == movie_id), None)
    if movie is None:
        return jsonify({
            "error": "Not Found",
            "message": "Movie not found."
        }), 404

    data = request.get_json()
    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Request body must be JSON."
        }), 400

    required_fields = ["reviewer", "rating", "comment"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": "Bad Request", "message": f"Field '{field}' is required."
            }), 400

    if not isinstance(data["reviewer"], str):
            return jsonify({
                "error": "Bad Request",
                "message": "Field 'reviewer' must be a string"
            }), 400
    
    if not isinstance(data["comment"], str):
            return jsonify({
                "error": "Bad Request",
                "message": "Field 'comment' must be a string."
            }), 400
    
    if not isinstance(data["rating"], int):
            return jsonify({
                "error": "Bad Request",
                "message": "Field 'rating' must be a number."
            }), 400
    

    # 2. Get JSON body (we'll harden this later)
    data = request.get_json() or {}

    # 3. Make sure the movie has a reviews list
    if "reviews" not in movie:
        movie["reviews"] = []

    review = {
        "reviewer": data.get("reviewer"),
        "rating": data.get("rating"),
        "comment": data.get("comment"),
    }

    movie["reviews"].append(review)

    # 4. Return the created review
    return jsonify(review), 201