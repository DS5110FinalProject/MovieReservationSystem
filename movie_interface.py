from pymongo import MongoClient
import pprint

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["movie_database"]

# Pretty printer for clean output
pp = pprint.PrettyPrinter(indent=4)

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
    sort_option = input("Choose an attribute to sort by (1-4): ")
    sort_order = input("Sort order (1 for ascending, -1 for descending): ")

    # Map user input to sorting keys
    sort_key_map = {
        "1": "release_year",
        "2": "imdb_score",
        "3": "title",
        "4": "budget"
    }
    sort_key = sort_key_map.get(sort_option, "release_year")  # Default to release_year
    sort_order = int(sort_order) if sort_order in ["1", "-1"] else -1  # Default to descending

    movies = db.movie.find(query).sort(sort_key, sort_order)

    # Display the movies
    print("\nMovies:")
    print(f"{'Title':<30} {'Director':<20} {'Genre':<10} {'Year':<5} {'IMDB':<5}")
    print("-" * 75)
    for movie in movies:
        print(f"{movie['title']:<30} {movie['director']:<20} {movie['genre']:<10} {movie['release_year']:<5} {movie['imdb_score']:<5}")


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
    sort_option = input("Choose an attribute to sort by (1-4): ")
    sort_order = input("Sort order (1 for ascending, -1 for descending): ")

    # Map user input to sorting keys
    sort_key_map = {
        "1": "release_year",
        "2": "imdb_score",
        "3": "title",
        "4": "budget"
    }
    sort_key = sort_key_map.get(sort_option, "title")  # Default to title
    sort_order = int(sort_order) if sort_order in ["1", "-1"] else 1  # Default to ascending

    movies = db.movie.find(query).sort(sort_key, sort_order)

    # Display the movies
    print("\nSearch Results:")
    print(f"{'Title':<30} {'Director':<20} {'IMDB Score':<10} {'Year':<5}")
    print("-" * 70)
    for movie in movies:
        print(f"{movie['title']:<30} {movie['director']:<20} {movie['imdb_score']:<10} {movie['release_year']:<5}")


def view_movie_performance():
    """View top 5 movies by final box office."""
    performances = db.movie_performance.aggregate([
        { "$lookup": {
            "from": "movie",
            "localField": "movie_id",
            "foreignField": "_id",
            "as": "movie_details"
        }},
        { "$unwind": "$movie_details" },
        { "$sort": { "final_box_office": -1 } },
        { "$limit": 5 }
    ])
    
    print("\nTop 5 Movies by Final Box Office:")
    print(f"{'Title':<30} {'Box Office':<15} {'Earnings':<15} {'Performance':<10}")
    print("-" * 70)
    for performance in performances:
        movie_title = performance['movie_details']['title']
        box_office = performance['final_box_office']
        earnings = performance['earnings']
        perf = performance['performance']
        print(f"{movie_title:<30} {box_office:<15} {earnings:<15} {perf:<10}")

def show_active_users():
    """Display active users."""
    users = db.users.find({"last_login": {"$gte": "2024-11-01"}})
    
    print("\nActive Users:")
    print(f"{'Username':<15} {'Last Login':<20} {'Language':<10}")
    print("-" * 50)
    for user in users:
        print(f"{user['username']:<15} {user['last_login']:<20} {user['preferred_language']:<10}")

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
    print(f"Movie added with ID: {result.inserted_id}")

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
    print(f"Movie '{title}' updated successfully.")


def delete_movie():
    """Delete a movie by title."""
    title = input("Enter the title of the movie to delete: ")
    result = db.movie.delete_one({"title": title})
    if result.deleted_count > 0:
        print(f"Movie '{title}' deleted.")
    else:
        print("Movie not found.")

def menu():
    """Main CLI menu."""
    while True:
        print("\nWelcome to MovieDB CLI!")
        print("1. Filter movies")
        print("2. Search movies")
        print("3. View movie performance")
        print("4. User analytics")
        print("5. Add a movie")
        print("6. Update a movie")
        print("7. Delete a movie")
        print("8. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            list_movies()
        elif choice == "2":
            search_movies()
        elif choice == "3":
            view_movie_performance()
        elif choice == "4":
            user_analytics()
        elif choice == "5":
            add_movie()
        elif choice == "6":
            update_movie()
        elif choice == "7":
            delete_movie()
        elif choice == "8":
            print("Exiting CLI. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

# Run the CLI
if __name__ == "__main__":
    menu()
