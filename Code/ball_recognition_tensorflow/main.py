import time

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

from ball_recognition_tensorflow.object_detection.utils import label_map_util
from ball_recognition_tensorflow.object_detection.utils import visualization_utils as vis_util

def main():
    start = time.time()
    cam = cv2.VideoCapture(0)
    MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
    MODEL_FILE = MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
    PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
    PATH_TO_LABELS = 'object_detection/data/mscoco_label_map.pbtxt'
    NUM_CLASSES = 90

    # opener = urllib.request.URLopener()
    # opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
    # tar_file = tarfile.open(MODEL_FILE)
    # for file in tar_file.getmembers():
    #     file_name = os.path.basename(file.name)
    #     if 'frozen_inference_graph.pb' in file_name:
    #         tar_file.extract(file, os.getcwd())

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.compat.v1.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=NUM_CLASSES, use_display_name=True
    )
    category_index = label_map_util.create_category_index(categories)

    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                print(
                    "time since last check: {} seconds".format(
                        time.time()-start
                    )
                )
                start = time.time()
                ret, image_np = cam.read()
                # Expand dimensions since the model expects images to have
                # shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = detection_graph.get_tensor_by_name(
                    'image_tensor:0'
                )
                # Each box represents a part of the image where a particular
                # object was detected.
                boxes = detection_graph.get_tensor_by_name(
                    'detection_boxes:0'
                )
                # Each score represent the level of confidence for each of the
                # objects.
                # Score is shown on the result image, together with the class
                # label.
                scores = detection_graph.get_tensor_by_name(
                    'detection_scores:0')
                classes = detection_graph.get_tensor_by_name(
                    'detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name(
                    'num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=1)

                cv2.imshow('object detection',
                           cv2.resize(image_np, (800, 600)))
                if -1 != cv2.waitKey(25) & 0xFF != 255:
                    cv2.destroyAllWindows()
                    break


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)




if __name__ == '__main__':
    main()




# import pathlib
#
# import numpy as np
# import os
# import six.moves.urllib as urllib
# import sys
# import tarfile
# import tensorflow as tf
# import zipfile
#
# from collections import defaultdict
# from io import StringIO
# from matplotlib import pyplot as plt
# from PIL import Image
# from IPython.display import display
#
# from ball_recognition_tensorflow.object_detection.utils import ops as utils_ops
# from ball_recognition_tensorflow.object_detection.utils import label_map_util
# from ball_recognition_tensorflow.object_detection.utils import visualization_utils as vis_util
#
#
# # patch tf1 into `utils.ops`
# utils_ops.tf = tf.compat.v1
#
# # Patch the location of gfile
# tf.gfile = tf.io.gfile
#
#
# def load_model(model_name):
#   base_url = 'http://download.tensorflow.org/models/object_detection/'
#   model_file = model_name + '.tar.gz'
#   model_dir = tf.keras.utils.get_file(
#     fname=model_name,
#     origin=base_url + model_file,
#     untar=True)
#
#   model_dir = pathlib.Path(model_dir)/"saved_model"
#
#   model = tf.saved_model.load(str(model_dir))
#   model = model.signatures['serving_default']
#
#   return model
#
#
# # List of the strings that is used to add correct label for each box.
# PATH_TO_LABELS = 'object_detection/data/mscoco_label_map.pbtxt'
# category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
#
# # If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
# PATH_TO_TEST_IMAGES_DIR = pathlib.Path('object_detection/test_images')
# TEST_IMAGE_PATHS = sorted(list(PATH_TO_TEST_IMAGES_DIR.glob("*.jpg")))
# print(TEST_IMAGE_PATHS)
#
# model_name = 'ssd_mobilenet_v1_coco_2017_11_17'
# detection_model = load_model(model_name)
#
# print(detection_model.inputs)
#
# print(detection_model.output_dtypes)
#
# print(detection_model.output_shapes)
#
#
# def run_inference_for_single_image(model, image):
#     image = np.asarray(image)
#     # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
#     input_tensor = tf.convert_to_tensor(image)
#     # The model expects a batch of images, so add an axis with `tf.newaxis`.
#     input_tensor = input_tensor[tf.newaxis, ...]
#
#     # Run inference
#     output_dict = model(input_tensor)
#
#     # All outputs are batches tensors.
#     # Convert to numpy arrays, and take index [0] to remove the batch dimension.
#     # We're only interested in the first num_detections.
#     num_detections = int(output_dict.pop('num_detections'))
#     output_dict = {key: value[0, :num_detections].numpy()
#                    for key, value in output_dict.items()}
#     output_dict['num_detections'] = num_detections
#
#     # detection_classes should be ints.
#     output_dict['detection_classes'] = output_dict[
#         'detection_classes'].astype(np.int64)
#
#     # Handle models with masks:
#     if 'detection_masks' in output_dict:
#         # Reframe the the bbox mask to the image size.
#         detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
#             output_dict['detection_masks'], output_dict['detection_boxes'],
#             image.shape[0], image.shape[1])
#         detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
#                                            tf.uint8)
#         output_dict[
#             'detection_masks_reframed'] = detection_masks_reframed.numpy()
#
#     return output_dict
#
#
# def show_inference(model, image_path):
#   # the array based representation of the image will be used later in order to prepare the
#   # result image with boxes and labels on it.
#   image_np = np.array(Image.open(image_path))
#   # Actual detection.
#   output_dict = run_inference_for_single_image(model, image_np)
#   # Visualization of the results of a detection.
#   vis_util.visualize_boxes_and_labels_on_image_array(
#       image_np,
#       output_dict['detection_boxes'],
#       output_dict['detection_classes'],
#       output_dict['detection_scores'],
#       category_index,
#       instance_masks=output_dict.get('detection_masks_reframed', None),
#       use_normalized_coordinates=True,
#       line_thickness=8)
#
#   display(Image.fromarray(image_np))
#
#
# for image_path in TEST_IMAGE_PATHS:
#   show_inference(detection_model, image_path)
#
#
# model_name = "mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28"
# masking_model = load_model("mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28")
#
# print(masking_model.output_shapes)
#
# for image_path in TEST_IMAGE_PATHS:
#   show_inference(masking_model, image_path)
