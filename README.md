# Đếm sản phẩm trên băng tải

## Features
- Xác định vùng an toàn trên mâm 3 chấu để  robot gắp phôi kim loại ra.

## Tech Stack
- Python 3.12+
- OpenCV
- NumPy

## Project Structure
```
z131_robot_Thai-Nguyen/
    ├── perspective_transform/
    ├── circle_detection/
    ├── edge_detection/
    ├── data/
    ├── utils/
    ├── MvImport/
    ├── capture_image.py
    ├── create_config.py
    ├── get_chuck_angle_mvs.py
    ├── main.py
    ├── requirement.txt
    └── README.md
```

## Installation

### 1. Tạo môi trường ảo
python -m venv .venv  
source .venv/bin/activate             

### 2. Cài đặt thư viện
pip install -r requirements.txt

## Usage

### Bước 1: Chụp ảnh mẫu
Chụp ảnh mẫu từ camera: <br>
``` python capture_image.py --save_dir [Vị trí lưu ảnh sau khi chụp]``` <br>
Màn hình camera hiện lên, căn chỉnh đúng góc đặt camera cố định, ấn "s" để lưu ảnh mẫu, ấn "q" để thoát.
### Bước 2: Thiết lập cấu hình
Bật ảnh mẫu để cấu hình: <br>
``` python create_config.py --image [Đường dẫn ảnh mẫu] --config [Đường dẫn vị trí lưu file config] --detect [Phương pháp xác định góc xoay của mâm: circle hoặc edge]```  
Sau khi ảnh mẫu đã hiện lên, cách cấu hình bao gồm:     
- Vùng làm việc (ROI) của ảnh:  
    - Ấn "r" để vào mode ROI         
    - Ấn 2 điểm ở góc trên bên trái và góc dưới bên phải để thiết lập ROI  
- Mặt nạ (mask) của ảnh và tâm(center) của mâm:  
    - Ấn "m" để vào mode Mask         
    - Ấn 1 điểm chọn làm tâm của mâm  
    - Chọn điểm thứ nhất trên vòng tròn phôi, chọn điểm thứ hai là điểm xa tâm nhất vẫn thuộc mâm  
    - Vùng nằm giữa 2 điểm này chính là khu vực tìm lỗ /cạnh chấu
- Các thông số về lỗ chấu (nếu detect chọn circle):  
    - Ấn "o" để vào mode circle  
    - Ấn một điểm là tâm của lỗ chấu thứ nhất, ấn một điểm nữa phía trong vành lỗ chấu đó để thiết <br>lập bán kính nhỏ nhất mà lỗ chấu có thể có.  
    - Ấn một điểm là tâm của lỗ chấu thứ hai (cùng trên chấu với lỗ thứ nhất), ấn một điểm nữa bên <br>ngoài lỗ chấu đó để thiết lập bán kính lớn nhất mà lỗ chấu có thể có.
- Các thông số về cạnh chấu (nếu detect chọn edge):
    - Ấn "d" để vào mode distance
    - Ấn điểm thứ nhất vào vị trí tâm, ấn điểm thứ hai vào một điểm trên vành trong của phôi hoặc <br>bất kỳ điểm nào mà người dùng ước lượng khoảng cách giữa 2 điểm là khoảng cách từ tâm tới cạnh chấu.
- Đường tham chiếu (Reference):
    - Ấn "f" để vào mode reference. Bước này thiết lập đường tham chiếu để tính góc, chọn 2 điểm <br>mà người dùng muốn, một vector từ điểm đầu tiên -> điểm thứ hai được tạo ra. 
    - Góc của mâm xoay được tính là góc giữa các lỗ/cạnh chấu với vector này. 
- Sau khi đo xong các tham số, ấn "s" để lưu trong file config.json, ấn "q" để thoát chương trình.  
### Bước 3: Tính góc xoay của mâm
``` python main.py --detect [Phương pháp xác định góc xoay: circle hoặc edge] --config [Đường dẫn đến file cấu hình] --save_path [Đường dẫn đến thư mục lưu ảnh kết quả (nếu muốn lưu)] ```

Sau khi máy cnc gửi tín hiệu -> camera chụp ảnh và gửi về máy -> chương trình sẽ tính toán và gửi góc xoay cho robot
