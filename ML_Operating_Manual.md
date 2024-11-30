### Steps to Call the Model

1. **Import the `ML_Api`**
   - First, you need to import the `ML_Api` file to access the necessary functions.

2. **Call the `load_model_and_resources()` function**
   - This function will return three objects: the trained model, feature columns, and the scaler. Example:
     ```python
     model, features, scaler = load_model_and_resources()
     ```

3. **Prepare the user input**
   - The `user_input` should be in the following format:
     ```python
     user_input = {
         'budget': 20000000,  # Budget of the movie
         'imdb_score': 7.5,   # IMDB score of the movie
         'directors': 'Steven Spielberg',  # Director(s) of the movie
         'actors': ['Tom Hanks', 'Meryl Streep']  # List of actors in the movie
     }
     ```

4. **Call the `process_user_input(user_input, feature_columns, scaler)` function**
   - This function processes the `user_input` and returns the standardized input data (`input_scaled`):
     ```python
     input_scaled = process_user_input(user_input, feature_columns, scaler)
     ```

5. **Call the `predict_box_office(model, input_scaled)` function**
   - This function takes the `model` and `input_scaled` as input and returns the predicted box office value as a float:
     ```python
     predicted_box_office = predict_box_office(model, input_scaled)
     ```
   - The returned value is the predicted box office revenue.

### Example Workflow

```python
# Import the necessary modules from ML_Api.py
from ML_Api import load_model, load_model_and_resources, process_user_input, predict_box_office

# Step 1: Load model, feature columns, and scaler
model, features, scaler = load_model_and_resources()

# Step 2: Define user input
user_input = {
    'budget': 20000000,  
    'imdb_score': 7.5,   
    'directors': 'Steven Spielberg',  
    'actors': ['Tom Hanks', 'Meryl Streep']  
}

# Step 3: Process user input
input_scaled = process_user_input(user_input, features, scaler)

# Step 4: Get predicted box office value
predicted_box_office = predict_box_office(model, input_scaled)

# Step 5: Print the predicted box office
print(f"Predicted Box Office: {predicted_box_office}")
