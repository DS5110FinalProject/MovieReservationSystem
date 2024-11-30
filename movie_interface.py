import bcrypt
import pprint
from pymongo import MongoClient
from ML_Api import load_model_and_resources, process_user_input, predict_box_office
import warnings
from sklearn.exceptions import InconsistentVersionWarning
import numpy as np
from datetime import datetime


# MongoDB connection 
client = MongoClient("mongodb://localhost:27017/")
db = client["movie_database"]

pp = pprint.PrettyPrinter(indent=4)

def signup():
    """Signup a new user."""
    print("\n--- Signup ---")
    username = input("Enter a username: ")
    existing_user = db.users.find_one({"username": username})
    if existing_user:
        print("Username already exists. Please choose a different username.")
        return None

    password = input("Enter a password: ")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    role = input("Enter role (admin/regular): ").lower()
    if role not in ["admin", "regular"]:
        print("Invalid role. Defaulting to 'regular'.")
        role = "regular"

    db.users.insert_one({
        "username": username,
        "password": hashed_password,
        "role": role
    })
    print("User registered successfully! Please login to continue.")


def login():
    """Login an existing user."""
    print("\n--- Login ---")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    user = db.users.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        print("Invalid username or password. Please try again.")
        return None

    # Update the last_login field to the current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": current_date}})

    print(f"Welcome, {username}!")
    return user

def list_movies():
    """List all movies or filter by multiple criteria."""
    genres = db.movie.distinct("genre")
    print("\nAvailable Genres:")
    print(", ".join(genres))  # Display genres as a comma-separated list

    # Filters
    genre = input("Enter genre to filter by (or press Enter for all): ")
    min_year = input("Enter minimum release year (or press Enter to skip): ")
    max_year = input("Enter maximum release year (or press Enter to skip): ")
    min_score = input("Enter minimum IMDB score (or press Enter to skip): ")

    query = {}
    if genre:
        query["genre"] = {"$regex": f"^{genre}$", "$options": "i"}
    if min_year:
        query["release_year"] = {"$gte": int(min_year)}
    if max_year:
        query["release_year"] = query.get("release_year", {})
        query["release_year"]["$lte"] = int(max_year)
    if min_score:
        query["imdb_score"] = {"$gte": float(min_score)}

    # Sorting Options
    print("\nSort Options:")
    print("1. Release Year")
    print("2. IMDB Score")
    print("3. Title")
    print("4. Budget")
    print("5. Box Office")  
    sort_option = input("Choose an attribute to sort by (1-5): ")
    sort_order = input("Sort order (1 for ascending, -1 for descending): ")

    # Map
    sort_key_map = {
        "1": "release_year",
        "2": "imdb_score",
        "3": "title",
        "4": "budget",
        "5": "performance.final_box_office"
    }
    sort_key = sort_key_map.get(sort_option, "release_year")  # Default to release_year
    sort_order = int(sort_order) if sort_order in ["1", "-1"] else -1  # Default to descending

    # Limit the number of results
    limit = input("Enter the maximum number of results to display (or press Enter for no limit): ")
    limit = int(limit) if limit.isdigit() else None

    # Aggregation to join with `movie_performance`, sort, and limit
    pipeline = [
        {"$match": query},
        {"$lookup": {
            "from": "movie_performance",
            "localField": "_id",
            "foreignField": "movie_id",
            "as": "performance"
        }},
        {"$unwind": {"path": "$performance", "preserveNullAndEmptyArrays": True}},
        {"$sort": {sort_key: sort_order}}
    ]
    if limit:  # if the user specifies a limit
        pipeline.append({"$limit": limit})

    movies = db.movie.aggregate(pipeline)

    # Display the movies
    print("\nMovies:")
    print(f"{'Title':<50} {'Director':<20} {'Cast':<60} {'Genre':<10} {'Year':<5} {'IMDB':<5} {'Box Office':<15}")
    print("-" * 160)
    for movie in movies:
        box_office = movie.get("performance", {}).get("final_box_office", "N/A")
        actors = ", ".join(movie.get("actors", []))
        print(f"{movie['title']:<50} {movie['director']:<20} {actors:<60} {movie['genre']:<10} {movie['release_year']:<5} {movie['imdb_score']:<5} {box_office:<15}")



def search_movies():
    """Search movies by title and sort results."""
    title = input("Enter part of the movie title: ")
    query = {"title": {"$regex": title, "$options": "i"}}

    # Sorting Options
    print("\nSort Options:")
    print("1. Release Year")
    print("2. IMDB Score")
    print("3. Title")
    print("4. Budget")
    print("5. Box Office")  
    sort_option = input("Choose an attribute to sort by (1-5): ")
    sort_order = input("Sort order (1 for ascending, -1 for descending): ")

    # Map 
    sort_key_map = {
        "1": "release_year",
        "2": "imdb_score",
        "3": "title",
        "4": "budget",
        "5": "performance.final_box_office"
    }
    sort_key = sort_key_map.get(sort_option, "title")  # Default to title
    sort_order = int(sort_order) if sort_order in ["1", "-1"] else 1  # Default to ascending

    # Limit the number of results
    limit = input("Enter the maximum number of results to display (or press Enter for no limit): ")
    limit = int(limit) if limit.isdigit() else None

    # Aggregation to join with `movie_performance` and sort
    pipeline = [
        {"$match": query},
        {"$lookup": {
            "from": "movie_performance",
            "localField": "_id",
            "foreignField": "movie_id",
            "as": "performance"
        }},
        {"$unwind": {"path": "$performance", "preserveNullAndEmptyArrays": True}},
        {"$sort": {sort_key: sort_order}}
    ]
    if limit:  # if the user specifies a limit
        pipeline.append({"$limit": limit})

    movies = db.movie.aggregate(pipeline)
    # Display the movies
    print("\nSearch Results:")
    print(f"{'Title':<50} {'Director':<20} {'Genre':<15} {'Cast':<60} {'IMDB Score':<10} {'Year':<5} {'Box Office':<15}")
    print("-" * 160)
    for movie in movies:
        box_office = movie.get("performance", {}).get("final_box_office", "N/A")
        actors = ", ".join(movie.get("actors", []))
        genre = movie.get("genre", "N/A")
        print(f"{movie['title']:<50} {movie['director']:<20} {genre:<15} {actors:<60} {movie['imdb_score']:<10} {movie['release_year']:<5} {box_office:<15}")

def show_active_users():
    """Display active users."""
    users = db.users.find({"last_login": {"$gte": "2024-11-01"}}).sort("last_login", -1)
    
    print("\nActive Users:")
    print(f"{'Username':<15} {'Last Login':<20} {'Language':<10}")
    print("-" * 50)
    for user in users:
        language = user.get("preferred_language", "English") 
        print(f"{user['username']:<15} {user['last_login']:<20} {language:<10}")

def show_feature_usage():
    """Display most used features."""
    features = db.feature_usage.aggregate([
        { "$group": { "_id": "$feature_name", "usage_count": { "$sum": 1 } } },
        { "$sort": { "usage_count": -1 } }
    ])
    
    print("\nMost Used Features:")
    print(f"{'Feature Name':<20} {'Usage Count':<10}")
    print("-" * 30)
    for feature in features:
        print(f"{feature['_id']:<20} {feature['usage_count']:<10}")

def user_analytics():
    """View active users and feature usage."""
    print("\n1. View active users")
    print("2. View most used features")
    choice = input("Choose an option: ")
    
    if choice == "1":
        show_active_users()
    elif choice == "2":
        show_feature_usage()
    else:
        print("Invalid choice.")

def add_movie():
    """Add a new movie."""
    title = input("Title: ")
    director = input("Director: ")
    genre = input("Genre: ")
    budget = int(input("Budget: "))
    release_year = int(input("Release Year: "))
    imdb_score = float(input("IMDB Score: "))
    actors = input("Actors (comma-separated): ").split(",")
    final_box_office = int(input("Final Box Office (or 0 if not available): "))

    # Insert the movie into the `movie` collection
    movie = {
        "title": title,
        "director": director,
        "actors": actors,
        "genre": genre,
        "budget": budget,
        "release_year": release_year,
        "imdb_score": imdb_score,
        "description": "N/A"
    }
    result = db.movie.insert_one(movie)
    movie_id = result.inserted_id

    # Insert the box office data into the `movie_performance` collection
    performance = {
        "movie_id": movie_id,
        "final_box_office": final_box_office,
        "oscars_and_golden_globes_nominations": 0,
        "oscars_and_golden_globes_awards": 0,
        "performance": "N/A"
    }
    db.movie_performance.insert_one(performance)

    print(f"Movie added with ID: {movie_id}")


def update_movie():
    """Update a movie's details."""
    title = input("Enter the title of the movie to update: ")
    movie = db.movie.find_one({"title": {"$regex": f"^{title}$", "$options": "i"}})
    if not movie:
        print("Movie not found.")
        return

    print("Leave fields blank to keep current values.")
    new_title = input(f"New title ({movie['title']}): ") or movie['title']
    new_director = input(f"New director ({movie['director']}): ") or movie['director']
    new_genre = input(f"New genre ({movie['genre']}): ") or movie['genre']
    new_budget = input(f"New budget ({movie['budget']}): ")
    new_budget = int(new_budget) if new_budget else movie['budget']
    new_year = input(f"New release year ({movie['release_year']}): ")
    new_year = int(new_year) if new_year else movie['release_year']
    new_score = input(f"New IMDB score ({movie['imdb_score']}): ")
    new_score = float(new_score) if new_score else movie['imdb_score']

    # Update movie details in the `movie` collection
    db.movie.update_one(
        {"_id": movie["_id"]},
        {"$set": {
            "title": new_title,
            "director": new_director,
            "genre": new_genre,
            "budget": new_budget,
            "release_year": new_year,
            "imdb_score": new_score
        }}
    )

    # Update box office data in the `movie_performance` collection
    performance = db.movie_performance.find_one({"movie_id": movie["_id"]})
    if performance:
        new_box_office = input(f"New box office ({performance['final_box_office']}): ")
        new_box_office = int(new_box_office) if new_box_office else performance["final_box_office"]
        db.movie_performance.update_one(
            {"movie_id": movie["_id"]},
            {"$set": {"final_box_office": new_box_office}}
        )
    else:
        # Add new box office data if it doesn't exist
        new_box_office = int(input("Enter final box office (or 0 if not available): "))
        db.movie_performance.insert_one({
            "movie_id": movie["_id"],
            "final_box_office": new_box_office,
            "oscars_and_golden_globes_nominations": 0,
            "oscars_and_golden_globes_awards": 0,
            "performance": "N/A"
        })

    print(f"Movie '{title}' updated successfully, including box office data.")



def delete_movie():
    """Delete a movie by title."""
    title = input("Enter the title of the movie to delete: ")
    result = db.movie.delete_one({"title": title})
    if result.deleted_count > 0:
        print(f"Movie '{title}' deleted.")
    else:
        print("Movie not found.")

def predict_movie_box_office():
    """Predict the box office of a movie based on user inputs or database data."""
    print("\n--- Predict Movie Box Office ---")

    # Suppress warnings
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", message="DataFrame is highly fragmented")

    # Load model, feature columns, and scaler
    try:
        model, features, scaler = load_model_and_resources()
    except Exception as e:
        print(f"Error loading model resources: {e}")
        return

    # Choose input source
    print("\n1. Use a movie from the database")
    print("2. Enter a new movie manually")
    choice = input("Choose an option (1 or 2): ")

    if choice == "1":
        # Select a movie from the database
        title = input("Enter the title of the movie to predict: ")
        movie = db.movie.find_one({"title": {"$regex": f"^{title}$", "$options": "i"}})
        if not movie:
            print("Movie not found in the database.")
            return

        # Create the user input dictionary from the database data
        user_input = {
            'budget': movie.get("budget", 0),
            'imdb_score': movie.get("imdb_score", 0),
            'directors': movie.get("director", "Unknown"),
            'actors': movie.get("actors", []),
            'genre': movie.get("genre", "Unknown"),
        }
    elif choice == "2":
        # Enter a new movie manually
        try:
            budget = int(input("Enter the movie's budget (e.g., 20000000): "))
            imdb_score = float(input("Enter the movie's IMDB score (e.g., 7.5): "))
            directors = input("Enter the movie's director(s) (e.g., Christopher Nolan): ")
            actors = input("Enter the movie's actors (comma-separated, e.g., Tom Hanks, Meryl Streep): ").split(',')
            genre = input("Enter the movie's genre (e.g., Action): ")

            user_input = {
                'budget': budget,
                'imdb_score': imdb_score,
                'directors': directors,
                'actors': [actor.strip() for actor in actors],
                'genre': genre,
            }
        except ValueError as ve:
            print(f"Invalid input: {ve}")
            return
    else:
        print("Invalid choice. Please try again.")
        return

    # Process user input
    try:
        input_scaled = process_user_input(user_input, features, scaler)
    except Exception as e:
        print(f"Error processing user input: {e}")
        return

    # Predict
    try:
        predicted_box_office = predict_box_office(model, input_scaled)
        if isinstance(predicted_box_office, np.ndarray):
            predicted_box_office = float(predicted_box_office[0])
        print(f"\nPredicted Box Office Revenue: ${predicted_box_office:,.2f}")
    except Exception as e:
        print(f"Error predicting box office: {e}")


def menu():
    """Main CLI menu with login/signup."""
    while True:
        print("\nWelcome to MovieDB CLI!")
        print("1. Login")
        print("2. Signup")
        print("3. Exit")

        choice = input("Choose an option: ")
        if choice == "1":
            user = login()
            if user:
                main_menu(user)  # Proceed to the main menu after successful login
        elif choice == "2":
            signup()  # Redirect to signup and then back to login
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


def main_menu(user):
    """CLI menu for logged-in users."""
    while True:
        print("\n--- Main Menu ---")
        print("1. Filter movies")
        print("2. Search movies")
        print("3. User analytics")
        print("4. Predict movie box office")  # New option

        # Admin-only options
        if user["role"] == "admin":
            print("5. Add a movie")
            print("6. Update a movie")
            print("7. Delete a movie")

        print("8. Logout")
        
        choice = input("Choose an option: ")

        if choice == "1":
            list_movies()
        elif choice == "2":
            search_movies()
        elif choice == "3":
            user_analytics()
        elif choice == "4":
            predict_movie_box_office()  # Call the new function
        elif choice == "5" and user["role"] == "admin":
            add_movie()
        elif choice == "6" and user["role"] == "admin":
            update_movie()
        elif choice == "7" and user["role"] == "admin":
            delete_movie()
        elif choice == "8":
            print("Logging out...")
            break
        else:
            print("Invalid choice or insufficient permissions. Try again.")



# Run the CLI
if __name__ == "__main__":
    menu()
