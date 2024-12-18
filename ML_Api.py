import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler

def load_model(filename):
    """
    Load a model from a file using pickle.
    
    Args:
    - filename: The path to the file where the model is saved.
    
    Returns:
    - The loaded model.
    """
    try:
        with open(filename, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        return None
    

def load_model_and_resources():
    """
    Load the trained model, feature columns, and scaler from files.

    Args:
    - model_filename (str): The file path to the trained model.
    - features_filename (str): The file path to the feature columns.
    - scaler_filename (str): The file path to the scaler.

    Returns:
    - model (object): The trained model.
    - feature_columns (list): The list of feature columns.
    - scaler (StandardScaler): The scaler used for standardization.
    """
    model = load_model('predict_box_office.pkl')
    feature_columns = load_model('feature_columns.pkl')
    scaler = load_model('scaler.pkl')

    if model and feature_columns and scaler:
        return model, feature_columns, scaler
    else:
        return None, None, None
    


def process_user_input(user_input, feature_columns, scaler):
    """
    Process the user input data, perform necessary transformations and standardization,
    and return the data in a format that can be used for model prediction.

    Args:
    - user_input (dict): User input data containing 'Running time', 'budget', 'Actors Box Office %', 
      'Director Box Office %', 'Oscar and Golden Globes nominations', 'Release year', 'IMDb score'
    - feature_columns (list): List of feature column names, ensuring user input data matches the training data features
    - scaler (StandardScaler): The scaler used to standardize the input data

    Returns:
    - input_scaled (ndarray): Standardized input data, ready for model prediction
    """
    
    # Apply log1p transformation to budget (log transform for budget)
    user_input['log_budget'] = np.log1p(user_input['budget'])

    # Prepare the input data dictionary
    input_data = {
        'Running time': user_input['Running time'],  
        'log_budget': user_input['log_budget'],
        'Actors Box Office %': user_input['Actors Box Office %'],  
        'Director Box Office %': user_input['Director Box Office %'],  
        'Oscar and Golden Globes nominations': user_input['Oscar and Golden Globes nominations'],  
        'Release year': user_input['Release year'],  
        'IMDb score': user_input['IMDb score'],
    }

    # Convert the input data into a DataFrame
    input_df = pd.DataFrame([input_data])

    # Perform one-hot encoding for the directors field (if applicable, based on training data)
    # Assuming 'directors' information is not part of the current user input (since it's not given)
    # So we'll skip director one-hot encoding unless the 'directors' field is part of the model's features
    # Perform one-hot encoding for the actors field
    # If there are multiple actors, handle the one-hot encoding
    # if 'actors' in user_input:
    #     for actor in user_input['actors']:
    #         input_df[f'actor_{actor}'] = 1
    # else:
    #     # No actor data was provided in user_input (fallback mechanism)
    #     pass

    # Ensure all required columns are present in the input data
    input_columns = set(input_df.columns)
    required_columns = set(feature_columns)

    missing_columns = required_columns - input_columns
    for col in missing_columns:
        input_df[col] = 0

    # Align the feature columns to ensure the input data matches the feature columns used in training
    input_df = input_df[feature_columns]

    print(f"Input Data Columns: {input_df.columns}")
    print(f"Feature Columns: {feature_columns}")
    
    # Apply standard scaling to the input data
    input_scaled = scaler.transform(input_df)

    return input_scaled

# def process_user_input(user_input, feature_columns, scaler):
#     """
#     Process the user input data, perform necessary transformations and standardization,
#     and return the data in a format that can be used for model prediction.

#     Args:
#     - user_input (dict): User input data containing 'budget', 'imdb_score', 'directors', 'actors'
#     - feature_columns (list): List of feature column names, ensuring user input data matches the training data features
#     - scaler (StandardScaler): The scaler used to standardize the input data

#     Returns:
#     - input_scaled (ndarray): Standardized input data, ready for model prediction
#     """
    
#     # Apply log1p transformation to budget
#     user_input['log_budget'] = np.log1p(user_input['budget'])

#     # Convert the input data into a DataFrame, mimicking the format of the training data
#     input_df = pd.DataFrame([user_input])

#     # Perform one-hot encoding for the directors field
#     input_df = pd.get_dummies(input_df, columns=['directors'], prefix='director')

#     # Perform one-hot encoding for the actors field
#     input_df['actors'] = input_df['actors'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)
#     input_df = pd.get_dummies(input_df, columns=['actors'], prefix='actor')

#     # Perform one-hot encoding for the genre field
#     input_df = pd.get_dummies(input_df, columns=['genre'], prefix='genre')

#     input_columns = set(input_df.columns)
#     required_columns = set(feature_columns)

#     missing_columns = required_columns - input_columns
#     for col in missing_columns:
#         input_df[col] = 0

#     # Align the feature columns to ensure the input data matches the feature columns used in training
#     input_df = input_df[feature_columns]
        
#     input_scaled = scaler.transform(input_df)

#     return input_scaled


def predict_box_office(model, input_scaled):
    """
    Predict the final box office revenue using a trained model.

    Args:
    - model: The trained machine learning model (e.g., RandomForestRegressor).
    - input_scaled (ndarray): The input data that has been standardized for prediction.

    Returns:
    - predicted_final_box_office (float): The predicted final box office revenue (non-log scale).
    """
    # Predict the log-transformed final box office
    prediction = model.predict(input_scaled)
    print(f"Predicted log-transformed Box Office: {prediction}")

    # Reverse the log transformation to get the actual predicted final box office
    predicted_final_box_office = np.expm1(prediction) 

    
    print(f"Predicted final Box Office: {predicted_final_box_office}")

    return predicted_final_box_office
