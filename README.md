# Movie Box Office Prediction System

## Overview

This project involves creating a movie box office prediction system that leverages data on movies, their performances, and user interactions with the system's features. The system uses MongoDB as the database to store and manage data related to movies, their box office performance, users, and feature usage.

## Running the Appliction

python movie_interface.py

## Database Design

The system's database is structured to handle data from various aspects of the movie industry, including movie details, box office performance, user interactions, and feature usage. This is done using a MongoDB database with several collections to store the necessary data.

### Database Name

- **movie_database**

### Collections

1. `movie`
2. `movie_performance`
3. `users`
4. `feature_usage`

---

## Collection Details

### 1. Movie Collection

- **Collection Name**: `movie`
- **Purpose**: Stores information about movies such as their title, director, actors, genre, budget, release year, IMDb score, and description.
- **Document Structure**:

```json
{
    "_id": ObjectId,  // Automatically generated MongoDB ObjectId
    "title": String,  // Movie title
    "director": String,  // Director's name
    "actors": [String],  // List of actor names (up to 3 actors)
    "genre": String,  // Genre of the movie
    "budget": Integer,  // Movie budget (in dollars)
    "release_year": Integer,  // Year of release
    "imdb_score": Float,  // IMDb score
    "description": String  // Description or plot summary (to be updated from IMDb)
}
```

### 2. Movie Performance Collection

- **Collection Name**: `movie_performance`
- **Purpose**: Stores performance data of movies, including box office earnings, earnings breakdown, Oscar and Golden Globes nominations/wins, and performance analysis.
- **Document Structure**:

```json
{
    "_id": ObjectId,  // Automatically generated MongoDB ObjectId
    "movie_id": ObjectId,  // Reference to the movie document in the 'movie' collection
    "final_box_office": Integer,  // Final box office earnings (in dollars)
    "earnings": Integer,  // Total earnings (could represent both domestic and international)
    "oscars_and_golden_globes_nominations": Integer,  // Number of nominations for Oscars/Golden Globes
    "oscars_and_golden_globes_awards": Integer,  // Number of awards won for Oscars/Golden Globes
    "performance": String  // Placeholder for performance comparison (e.g., "N/A")
}
```

### 3. User Collection

- **Collection Name**: `users`
- **Purpose**: Stores basic user information such as username, email, full name, registration date, last login, and preferred language.
- **Document Structure**:

```json
{
    "_id": ObjectId,  // Automatically generated MongoDB ObjectId
    "username": String,  // User's username
    "email": String,  // User's email address
    "full_name": String,  // User's full name
    "registration_date": String,  // Date of registration (in "YYYY-MM-DD" format)
    "last_login": String,  // Date of last login (in "YYYY-MM-DD" format)
    "preferred_language": String  // Preferred language of the user (e.g., "English", "French")
}
```

### 4. Feature Usage Collection

- **Collection Name**: `feature_usage`
- **Purpose**: Stores user interactions with the various features of the system, including the feature name, interaction date, details, and prediction outcomes.
- **Document Structure**:

```json
{
    "_id": ObjectId,  // Automatically generated MongoDB ObjectId
    "user_id": String,  // User's username (referencing the 'users' collection)
    "feature_name": String,  // Name of the feature (e.g., "box_office_prediction")
    "interaction_date": String,  // Date of interaction (in "YYYY-MM-DD" format)
    "interaction_details": String,  // Description of the interaction
    "prediction_outcome": String  // Outcome of the prediction ("success", "failure", or "N/A")
}
```
