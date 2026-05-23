import cv2
import json
import math
import argparse
import os
import numpy as np # Thêm numpy để tính mean brightness
from pathlib import Path

class VisionConfigToolWorkpiece:
    def __init__(self, img_path, config_path):
        self.img_orig = cv2.imread(str(img_path))
        if self.img_orig is None:
            raise ValueError("Không thể tải ảnh. Kiểm tra lại đường dẫn!")
        
        self.config_path = Path(config_path)
        self.img_display = self.img_orig.copy()
        
        # Khởi tạo cấu hình mặc định (Thêm workpiece_check)
        self.default_config = {
            "workpiece_check": {
                "center": [],
                "center_roi_radius_px": 0,
                "brightness_threshold": 0,
                "hough_wpc_min_radius": 0,
                "hough_wpc_max_radius": 0,
                "template_path": ""
            }
        }
        self.config = self.default_config.copy()
        self.points = []
        self.mode = None 
        self.window_name = "Vision Comprehensive Tool"
        self.history = []

    def save_history(self):
        """Lưu bản sao của config hiện tại vào lịch sử trước mỗi hành động quan trọng."""
        import copy
        self.history.append(copy.deepcopy(self.config))
        if len(self.history) > 20: # Giới hạn 20 bước quay lại
            self.history.pop(0)

    def load_config(self):
        """Ấn 'l' để load lại config cũ."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            print(f"--- Đã load cấu hình từ {self.config_path} ---")
        else:
            print(f"--- Không tìm thấy file {self.config_path} để load ---")

    def save_config(self):
        # Tự động tính toán các tham số hình học cho phôi dựa trên bán kính đã vẽ
        wpc = self.config["workpiece_check"]
        if wpc["center_roi_radius_px"] > 0:
            r = wpc["center_roi_radius_px"]
            wpc["hough_wpc_min_radius"] = int(r * 0.7)
            wpc["hough_wpc_max_radius"] = int(r * 1.3)
            wpc["hough_wpc_min_dist"] = int(r * 0.5)

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        print(f"--- Đã lưu cấu hình vào {self.config_path} ---")

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.save_history()

            # --- CHẾ ĐỘ MỚI: WORKPIECE (Phím 'W') ---
            if self.mode == 'wpc':
                self.points.append((x, y))
                if len(self.points) == 2:
                    # 1. Tính bán kính từ tâm (điểm 1) đến điểm click (điểm 2)
                    p1, p2 = self.points[0], self.points[1]
                    r = int(math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2))
                    self.config["workpiece_check"]["center"] = self.points[0]
                    # 2. Cập nhật config
                    self.config["workpiece_check"]["center_roi_radius_px"] = r
                    
                    # 3. Tính độ sáng trung bình tại vùng vừa vẽ để gợi ý Threshold
                    img_gray = cv2.cvtColor(self.img_orig, cv2.COLOR_BGR2GRAY)
                    mask = np.zeros(img_gray.shape, dtype=np.uint8)
                    cv2.circle(mask, p1, r, 255, -1)
                    avg_brightness = cv2.mean(img_gray, mask=mask)[0]
                    self.config["workpiece_check"]["brightness_threshold"] = int(avg_brightness)
                    
                    # 4. Tự động cắt và lưu Template (Hốc trống)
                    # Lưu vào thư mục cùng cấp với file config
                    tpl_dir = self.config_path.parent / "templates"
                    tpl_dir.mkdir(exist_ok=True)
                    tpl_path = tpl_dir / f"{self.config_path.stem}_tpl.jpg"
                    
                    roi_tpl = self.img_orig[p1[1]-r:p1[1]+r, p1[0]-r:p1[0]+r]
                    if roi_tpl.size > 0:
                        cv2.imwrite(str(tpl_path), roi_tpl)
                        self.config["workpiece_check"]["template_path"] = str(tpl_path)
                        print(f"--- Đã lưu template tại: {tpl_path} ---")

                    print(f"--- Config WPC: Radius {r}, Brightness {int(avg_brightness)} ---")
                    self.points = []

    def draw_overlay(self):
        self.img_display = self.img_orig.copy()
        h, w = self.img_display.shape[:2]
        
        # Hiển thị điểm đang click dở dang (Real-time feedback)
        for p in self.points:
            cv2.circle(self.img_display, p, 3, (0, 0, 255), -1)
        
        # HIỂN THỊ WORKPIECE CHECK (Màu tím hồng)
        wpc = self.config["workpiece_check"]
        mask_center = self.config["workpiece_check"]["center"]
        if mask_center != [0, 0] and wpc["center_roi_radius_px"] > 0:
            cv2.circle(self.img_display, tuple(mask_center), wpc["center_roi_radius_px"], (255, 0, 255), 2)
            cv2.putText(self.img_display, "WPC ROI", (mask_center[0]+5, mask_center[1]-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        # Menu cập nhật phím 'W'
        menu = "[W]:Workpiece [L]:Load [B]:Back [S]:Save [Q]:Quit"
        curr_mode = f"MODE: {str(self.mode).upper()} | Points: {len(self.points)}"
        cv2.putText(self.img_display, menu, (10, h - 45), 1, 1.2, (255, 255, 255), 2)
        cv2.putText(self.img_display, curr_mode, (10, h - 15), 1, 1.2, (0, 255, 0), 2)

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        while True:
            self.draw_overlay()
            cv2.imshow(self.window_name, self.img_display)
            key = cv2.waitKey(1) & 0xFF
            # if key == ord('r'): self.mode = 'roi'; self.points = []
            # elif key == ord('m'): self.mode = 'mask'; self.points = []
            # elif key == ord('o'): self.mode = 'circle'; self.points = []
            if key == ord('w'): self.mode = 'wpc'; self.points = [] # Phím tắt mới
            # elif key == ord('f'): self.mode = 'ref'; self.points = []
            # ... (Các phím l, b, c, s, q giữ nguyên) ...
            elif key == ord('s'): self.save_config()
            elif key == ord('q'): break
        cv2.destroyAllWindows()