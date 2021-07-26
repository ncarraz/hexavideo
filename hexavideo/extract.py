import torch
import detectron2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

import time
from tqdm import tqdm
import pandas as pd


im = cv2.imread("/content/cam2_08-01-2021__10-59-45_23-59-59__CAM2-part1_Moment.jpg")

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)
outputs = predictor(im)

vid_path = "data/video_1_fps.mp4"
cap = cv2.VideoCapture(vid_path)
N_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
result = pd.DataFrame()

for frame in tqdm(range(N_frames)):
    has_img, img = cap.read()
    if has_img:
        outputs = predictor(img)
        label = outputs["instances"].pred_classes.cpu()
        row = pd.Series(label).value_counts()
        result = result.append(row, ignore_index=True).fillna(0)

result = result.rename(columns={0:"person",2:"car"})
result = result.melt(id_vars="frame", value_vars=["car","person"], var_name="class", value_name="number")
result.to_csv("result.csv")