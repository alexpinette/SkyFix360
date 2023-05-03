import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os

def preprocess_image(img):
  img = cv2.resize(img, (224, 224))
  img = img.astype('float32') / 255.0
  return img

def visualize_predicted_points(img, predicted_points, output_path="visualized_image.png"):

  # Reshape the predicted points to the desired shape (10, 2)
  points = np.reshape(predicted_points, (10, 2))

  # Draw circles for each predicted point
  for point in points:
      x, y = int(point[0]), int(point[1])
      cv2.circle(img, (x, y), 10, (0, 0, 255), -1)  # Red circle

  # Save the visualized image
  cv2.imwrite(output_path, img)

def auto_correct_process(fileName):

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