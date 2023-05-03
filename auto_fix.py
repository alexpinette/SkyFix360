import cv2, os
import numpy as np
import tensorflow as tf
from tensorflow import keras
import tensorflow.keras.backend as K

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
  img = img.astype("float32") / 255.0 
  
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

# ------------------------------------------------------------------------------  

def visualize_predicted_points(image_path, predicted_points, output_path="visualized_image.png"):
  """ 
      Args:    image_path --> Str: The path to the input image file.
               predicted_points --> NumPy Array: The predicted horizon line points.
               output_path --> Str: The path to save the visualized image.
      Returns: None
      Summary: This function loads an image from file, visualizes the predicted horizon line by drawing red circles on the predicted points, and saves the visualized image to the output_path.
    """
      
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

# ------------------------------------------------------------------------------  

def auto_correct_process(fileName):
  """
      Args:     fileName --> Str  path to the image file.
      Returns:  predicted_points --> NumPy Array: of shape (1,2), the predicted horizon line.
      Summary:  Preprocesses the input image, loads the horizon line detection model from the given folder,
                predicts the horizon line and returns the predicted points.
    """
  
  # Read the image from file and resize it
  preprocessed_image = preprocess_image(fileName)
  
  # print(modelDir)
  currentDir = os.getcwd()
  sep = os.path.sep
  modelDir = currentDir + sep + "horizon_line_modelFINAL.h5"
  # print(modelDir)

  # model = tf.keras.models.load_model(modelDir)
  model = tf.keras.models.load_model(modelDir, custom_objects={"custom_loss": custom_loss})

  # Preprocess the input image and predict the horizon line
  input_image = np.expand_dims(preprocessed_image, axis=0)
  # predicted_points = model.predict(input_image)

  # Extract patches for the new image
  new_points = [0.5, 0.5] * 10  # Dummy points, will not affect the result
  new_patches = extract_patches(preprocessed_image, new_points)

  predicted_points = model.predict([np.expand_dims(preprocessed_image, axis=0), np.expand_dims(new_patches, axis=0)])

  img = cv2.imread(fileName)
  height, width, _ = img.shape
  predicted_points[0, 0::2] *= width
  predicted_points[0, 1::2] *= height

  visualize_predicted_points(fileName, predicted_points, output_path="visualized_image.png")

  return predicted_points

# ------------------------------------------------------------------------------  

def smoothness_penalty(y_true, y_pred):
    """
        Args:    y_true --> tensor of shape (batch_size, 2*N), where N is the number of points
                            on the horizon line.
                 y_pred --> tensor of shape (batch_size, 2*N), containing the predicted coordinates
                            of the horizon line points.
        Returns: smoothness_penalty --> tensor of shape (), representing the penalty for large differences
                                        between neighboring points.
        Summary: This function calculates the smoothness penalty between the ground truth and predicted horizon
                 line points, in order to encourage smooth predictions. It first calculates the vertical distance
                 between neighboring points for both the ground truth and predicted points. It then computes the
                 mean square difference between these distances and returns it as the smoothness penalty.
    """

  # Calculate the vertical distance between neighboring points
    true_diffs = K.abs(y_true[:, 1::2] - y_true[:, :-1:2])
    pred_diffs = K.abs(y_pred[:, 1::2] - y_pred[:, :-1:2])

    # Penalize large differences between neighboring points
    smoothness_penalty = K.mean(K.square(true_diffs - pred_diffs))
    return smoothness_penalty

# ------------------------------------------------------------------------------  

def custom_loss(y_true, y_pred):
    """
        Args:    y_true --> tensor of shape (batch_size, 2*N), where N is the number of points on the horizon line.
                 y_pred --> tensor of shape (batch_size, 2*N), containing the predicted coordinates of the horizon
                            line points.
        Returns: total_loss --> tensor of shape (), representing the total loss between the ground truth and predicted
                                horizon line points.
        Summary: This function computes the total loss between the ground truth and predicted horizon line points. 
                 It first calculates the mean squared error (MSE) loss between the ground truth and predicted points using 
                 `K.mean(K.square(y_true - y_pred))`. It then computes the smoothness penalty by calling the function
                 `smoothness_penalty` with the ground truth and predicted points as inputs. The weight of the smoothness
                 penalty can be adjusted by changing the coefficient `0.1` in the expression
                 `total_loss = mse_loss + 0.1 * penalty`. This weight controls the influence of the smoothness penalty
                 on the total loss. Finally, the function returns the total loss.
    """
      
    mse_loss = K.mean(K.square(y_true - y_pred))
    penalty = smoothness_penalty(y_true, y_pred)
    
    # You can adjust the weight of the smoothness penalty to control its influence on the total loss
    total_loss = mse_loss + 0.1 * penalty
    return total_loss

# ------------------------------------------------------------------------------  

def extract_patches(image, points, patch_size=32, num_patches=10):
    """
        Args:    image --> NumPy array representing the input image.
                 points --> list of length 2N, where N is the number of points on the horizon line.
                        The list contains the x and y coordinates of each point in the range [0, 1].
                 patch_size --> integer representing the size of the patches to extract. Default value is 32.
                 num_patches --> integer representing the number of patches to extract. Default value is 10.
        Returns: NumPy array of shape (num_patches, patch_size, patch_size, 3), representing the patches
                 extracted from the input image centered at the given points.
        Summary: This function extracts patches from the input image centered at the given points. For each point,
                 a patch is extracted using the given patch_size parameter. The number of patches to extract is
                 controlled by the num_patches.
    """
    patches = []
    for i in range(0, len(points), 2):
        x = int(points[i] * image.shape[1])
        y = int(points[i + 1] * image.shape[0])
        # print(x,y)

        x_min = max(0, x - patch_size // 2)
        x_max = min(image.shape[1], x + patch_size // 2)
        y_min = max(0, y - patch_size // 2)
        y_max = min(image.shape[0], y + patch_size // 2)

        # Adjust patch size for edge cases
        if x_max - x_min < patch_size:
            if x_min == 0:
                x_max = x_min + patch_size
            else:
                x_min = x_max - patch_size
        if y_max - y_min < patch_size:
            if y_min == 0:
                y_max = y_min + patch_size
            else:
                y_min = y_max - patch_size

        # print(f"Point index: {i//2}, Coordinates: ({x}, {y}), Patch position: ({x_min}, {y_min}), ({x_max}, {y_max}), Patch size: ({x_max - x_min}, {y_max - y_min})")

        patch = image[y_min:y_max, x_min:x_max]
        patches.append(patch)

    return np.array(patches)
