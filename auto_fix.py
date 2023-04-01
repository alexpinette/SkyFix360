import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os


# ------------------------------------------------------------------------------  

def preprocess_image(image_path):
  """
      Args:     image_path --> Str: The path to the image file.
      Returns:  img        --> NumPy Array: The preprocessed image as a numpy array.
      Summry:   Preprocesses an image by reading, resizing, and scaling it.
  """
  
  # Read the image from the specified file path
  img = cv2.imread(image_path)
  
  # Resize the image to a standard size of 224x224 pixels
  img = cv2.resize(img, (224, 224))
  
  return img

# ------------------------------------------------------------------------------  

def auto_correct_process(fileName, folder):
  """
      Args:     fileName --> Str  path to the image file.
                folder   --> Str: path to the folder where the model is stored
                
      Returns:  predicted_points --> NumPy Array: of shape (1,2), the predicted horizon line.

      Summary:  Preprocesses the input image, loads the horizon line detection model from the given folder,
                predicts the horizon line and returns the predicted points.
    """
  
  
  # Read the image from file and resize it
  preprocessed_image = preprocess_image(fileName)
  
  # Load the horizon line detection model from the given folder
  modelDir = os.path.join(folder, "horizon_line_model.h5")
  print(modelDir)
  model = tf.keras.models.load_model(modelDir)


  # Preprocess the input image and predict the horizon line
  input_image = np.expand_dims(preprocessed_image, axis=0)
  predicted_points = model.predict(input_image)
  
  # DEBUG print(predicted_points)
  
  # Return the predicted horizon line
  return predicted_points