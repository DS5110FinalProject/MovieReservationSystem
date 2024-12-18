### Steps to Call the Model

1. **Import the necessary libraries**
   ```python
   import numpy as np
   import pandas as pd
   import pickle
   from sklearn.preprocessing import StandardScaler
   ```

2. **Import the `ML_Api`**
   - First, you need to import the `ML_Api` file to access the necessary functions.

3. **Call the `load_model_and_resources()` function**
   - This function will return three objects: the trained model, feature columns, and the scaler. Example:
     ```python
     model, features, scaler = load_model_and_resources()
     ```

4. **Prepare the user input**
   - The `user_input` should be in the following format:
     ```python
     user_input = {
        'Running time': 144,  
        'budget': 50000000,
        'Actors Box Office %': 50,  
        'Director Box Office %': 69.23,  
        'Oscar and Golden Globes nominations': 0,  
        'Release year': 2016,  
        'IMDb score': 7.4,
    }
     ```

5. **Call the `process_user_input(user_input, feature_columns, scaler)` function**
   - This function processes the `user_input` and returns the standardized input data (`input_scaled`):
     ```python
     input_scaled = process_user_input(user_input, feature_columns, scaler)
     ```

6. **Call the `predict_box_office(model, input_scaled)` function**
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
    'Running time': 144,  
    'budget': 50000000,
    'Actors Box Office %': 50,  
    'Director Box Office %': 69.23,  
    'Oscar and Golden Globes nominations': 0,  
    'Release year': 2016,  
    'IMDb score': 7.4,
}

# Step 3: Process user input
input_scaled = process_user_input(user_input, features, scaler)

# Step 4: Get predicted box office value
predicted_box_office = predict_box_office(model, input_scaled)

# Step 5: Print the predicted box office
print(f"Predicted Box Office: {predicted_box_office}")
