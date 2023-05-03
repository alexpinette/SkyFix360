import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os

def preprocess_image(img):
  """
      Args:     image_path --> Str: The path to the image.
      Returns:  img        --> NumPy Array: The preprocessed image as a numpy array.
      Summry:   Preprocesses an image by resizing and scaling it.
  """

  # Resize the image to a standard size of 224x224 pixels
  img = cv2.resize(img, (224, 224))
  img = img.astype('float32') / 255.0

  return img

def visualize_predicted_points(img, predicted_points, output_path="visualized_image.png"):
  """ 
      Args:    image_path --> Str: The path to the input image file.
               predicted_points --> NumPy Array: The predicted horizon line points.
               output_path --> Str: The path to save the visualized image.
      Returns: None
      Summary: This function loads an image from file, visualizes the predicted horizon line by drawing red circles on the predicted points, and saves the visualized image to the output_path.
  """


  # Reshape the predicted points to the desired shape (10, 2)
  points = np.reshape(predicted_points, (10, 2))

  # Draw circles for each predicted point
  for point in points:
      x, y = int(point[0]), int(point[1])
      cv2.circle(img, (x, y), 10, (0, 0, 255), -1)  # Red circle

  # Save the visualized image
  cv2.imwrite(output_path, img)

def auto_correct_process(fileName):
  """
      Args:     fileName --> Str  path to the image file.
      Returns:  predicted_points --> NumPy Array: of shape (1,2), the predicted horizon line.
      Summary:  Preprocesses the input image, loads the horizon line detection model from the given folder,
                predicts the horizon line and returns the predicted points.
  """

  # Read the image from file and resize it
  img = cv2.imread(fileName)
  preprocessed_image = preprocess_image(img)

  modelDir = "horizon_line_modelFINAL.h5"

  model = tf.keras.models.load_model(modelDir)

  input_image = np.expand_dims(preprocessed_image, axis=0)

  predicted_points = model.predict(input_image)

  height, width, _ = img.shape
  predicted_points[0, 0::2] *= width
  predicted_points[0, 1::2] *= height

  visualize_predicted_points(img, predicted_points, output_path="visualized_image.png")

  return predicted_points