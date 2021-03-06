import os
import sys
import numpy as np
import tensorflow as tf
import pandas as pd
from mrcnn import utils
import mrcnn.model as modellib
import worker
import datetime

ROOT_DIR = os.path.abspath("../../")
sys.path.append(ROOT_DIR)  # To find local version of the library

MODEL_DIR = os.path.join(ROOT_DIR, "logs")
config = worker.WorkerConfig()

class InferenceConfig(config.__class__):
    # Run detection on one image at a time
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
def compute_batch_ap(image_ids):
    APs = []
    for image_id in image_ids:
        # Load image
        image, image_meta, gt_class_id, gt_bbox, gt_mask = \
            modellib.load_image_gt(dataset, config,
                                   image_id, use_mini_mask=False)
        # Run object detection
        results = model.detect([image], verbose=0)
        # Compute AP
        r = results[0]
        AP, precisions, recalls, overlaps = \
            utils.compute_ap(gt_bbox, gt_class_id, gt_mask,
                             r['rois'], r['class_ids'], r['scores'], r['masks'])
        print(image_id, AP)
        APs.append(AP)
    return APs
def loop_weight(length,path):
    weights_path = path
    weights_path = weights_path+ "%04d" % (length+1) +'.h5'
    print("Loading weights ", weights_path)
    model.load_weights(weights_path, by_name=True)
    image_ids = np.random.choice(dataset.image_ids, 30, replace=False, p=None)
    APs = compute_batch_ap(dataset.image_ids)
    print(APs)
    print("mAP @ IoU=50: ", np.mean(APs))
    return np.mean(APs)
def save_data(data, path):
    # 字典中的key值即为csv中列名
    dataframe = pd.DataFrame(data)
    # 将DataFrame存储为csv,index表示是否显示行名，default=True
    dataframe.to_csv(path, index=False,header=False)

def detect_input(str):
    test = '/\\'
    for i in str:
        if i in test:
            return str
    else:
        return  '../drive/My Drive/silhouette_weight/'+ str

str = input('Please enter the dataset: \n'
            'WorkerData, player')
wpath = input('Please enter the test weights set:')
wpath = detect_input(wpath)
opath = input('Please enter the output path:')
opath = detect_input(opath)

config = InferenceConfig()
config.display()
TEST_MODE = "inference"
# with tf.device("/gpu:0"):
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR,
                              config=config)
# Load validation dataset
dataset = worker.WorkerDataset()
dataset.load_worker(str, "test")#Test for gitignore
dataset.prepare()
print("Images: {}\nClasses: {}".format(len(dataset.image_ids), dataset.class_names))

# *****************************************************silhouette
# weight_amount = 150
# output = np.zeros(weight_amount)
# w_path = '../drive/My Drive/silhouette_weight/worker_silhouette/mask_rcnn_worker_'
# for i in range(weight_amount):
#     output[i] = loop_weight(i,w_path)
# save_data(output,'../drive/My Drive/silhouette_weight/player_performance_silhouette.csv')
# *****************************************************stick
ISOTIMEFORMAT = '%Y%m%d%H%M%S'
theTime = datetime.datetime.now().strftime(ISOTIMEFORMAT)
output_path = opath + theTime +'.csv'
print('Output path: ' + output_path)

weight_amount = 150
output = np.zeros(weight_amount)

w_path = wpath+'/mask_rcnn_worker_'
for i in range(weight_amount):
    output[i] = loop_weight(i,w_path)

save_data(output,output_path)