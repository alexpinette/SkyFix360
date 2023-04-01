import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import os

def preprocess_image(image_path):
  img = cv2.imread(image_path)
  img = cv2.resize(img, (224, 224))
  # img = img.astype('float32') / 255.0
  return img

def auto_correct_process(fileName, folder):
  # image_path = 'images/R0011130.JPG'
  preprocessed_image = preprocess_image(fileName)
  
  modelDir = os.path.join(folder, "horizon_line_model.h5")
  print(modelDir)
  model = tf.keras.models.load_model(modelDir)

  input_image = np.expand_dims(preprocessed_image, axis=0)
  predicted_points = model.predict(input_image)
  # print(predicted_points)
  return predicted_points