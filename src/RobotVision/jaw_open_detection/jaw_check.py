import cv2
import numpy as np
import logging
from pathlib import Path
import math
import json

class JawDetection:
    def __init__(self, config):
        """
        config: Dictionary chứa các tham số từ file config.json
        """
        self.config = config
        self.center = self.config["mask"]["center"]
        self.dist1 = self.config["distance"]["dist1"]
        self.dist2 = self.config["distance"]["dist2"]

    def detect_open(self, best_triple):
        """
        Hợp nhất cả 2 phương pháp bằng cơ chế biểu quyết
        """
        distances = []
        for c in best_triple:
            xi, yi, rad = c['pos'][0], c['pos'][1], c['rad']
            dis_ = math.sqrt((xi-self.center[0])**2 + (yi-self.center[1])**2)
            # xác định xem nó gần thằng nào
            if dis_ < min(self.dist1, self.dist2):
                distances.append(False)
            elif dis_> max(self.dist1, self.dist2):
                distances.append(True)
            elif abs(dis_ - self.dist1) < abs(dis_ - self.dist2):
                distances.append(True)
            else: distances.append(False)
        if sum(distances) >=2: return True
        else: return False
         
    
        