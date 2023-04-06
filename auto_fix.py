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

def correct_horizon_line(image_path, predicted_points):
    # Load the image
    img = cv2.imread(image_path)

    # Reshape the predicted points to the desired shape (10, 2)
    points = np.reshape(predicted_points, (10, 2))

    # Sort the points by their x-coordinates
    sorted_points = sorted(points, key=lambda point: point[0])

    # Identify the source points (the distorted points)
    src_pts = np.array(sorted_points[:4], dtype=np.float32)  # We'll use the first 4 points as source points

    # Calculate the target points (the corrected horizon points)
    target_height = max(src_pts[:, 1]) - min(src_pts[:, 1])
    tgt_pts = np.array([
        [src_pts[0, 0], src_pts[0, 1] - target_height],
        [src_pts[1, 0], src_pts[1, 1] - target_height],
        [src_pts[2, 0], src_pts[2, 1] + target_height],
        [src_pts[3, 0], src_pts[3, 1] + target_height]
    ], dtype=np.float32)

    # Calculate the perspective transformation matrix
    matrix = cv2.getPerspectiveTransform(src_pts, tgt_pts)

    # Apply the perspective transformation to the image
    corrected_img = cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))

    return corrected_img




def visualize_predicted_points(image_path, predicted_points, output_path="visualized_image.png"):
  # Load the image
  img = cv2.imread(image_path)

  # Reshape the predicted points to the desired shape (10, 2)
  points = np.reshape(predicted_points, (10, 2))

  # Draw circles for each predicted point
  for point in points:
      x, y = int(point[0]), int(point[1])
      cv2.circle(img, (x, y), 10, (0, 0, 255), -1)  # Red circle

  # Save the visualized image
  cv2.imwrite(output_path, img)


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
  
  # modelDir = "horizon_line_model.h5"
  # modelDir = os.path.join(folder, "horizon_line_model.h5")

  # print(modelDir)
  currentDir = os.getcwd()
  sep = os.path.sep
  modelDir = currentDir + sep + "horizon_line_model.h5"
  # print(modelDir)

  model = tf.keras.models.load_model(modelDir)


  # Preprocess the input image and predict the horizon line
  input_image = np.expand_dims(preprocessed_image, axis=0)
  predicted_points = model.predict(input_image)
  # print(predicted_points.shape)

  visualize_predicted_points(fileName, predicted_points, output_path="visualized_image.png")

  return predicted_points