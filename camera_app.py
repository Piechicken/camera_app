import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import datetime
import requests
import cv2
import threading

# 创建相册文件夹
def create_album_folder():
    folder_name = "PhotoAlbum"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# 获取地理位置
def get_location():
    try:
        response = requests.get("http://ipinfo.io/json")
        data = response.json()
        city = data.get("city", "Unknown_City")
        return city
    except Exception as e:
        print(f"Error getting location: {e}")
        return "Unknown_City"

# 获取当前时间
def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")

# 保存照片
def save_photo(image, folder_name):
    location = get_location()
    time = get_current_time()
    file_name = f"{time}_{location}.jpg"
    file_path = os.path.join(folder_name, file_name)
    image.save(file_path, format="JPEG")
    print(f"Photo saved: {file_path}")

# 录制视频
def record_video(duration=10):
    global recording, video_writer
    video_writer = None
    file_name = None
    start_time = datetime.datetime.now()
    
    while (datetime.datetime.now() - start_time).seconds < duration:
        ret, frame = cap.read()
        if not ret or not recording:
            break
        
        if video_writer is None:
            height, width, _ = frame.shape
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            file_name = f"{folder_name}/{get_current_time()}_{get_location()}.mp4"
            video_writer = cv2.VideoWriter(file_name, fourcc, 20.0, (width, height))
        
        video_writer.write(frame)
    
    if video_writer:
        video_writer.release()
        print(f"Video saved: {file_name}")
    
    recording = False

# 浏览文件夹中的文件
def browse_files(folder_name):
    file_path = filedialog.askopenfilename(initialdir=folder_name, title="选择文件", filetypes=[("Image files", "*.jpg"), ("Video files", "*.mp4")])
    if file_path:
        if file_path.endswith('.jpg'):
            img = Image.open(file_path)
            img.show()
        elif file_path.endswith('.mp4'):
            cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
            cap = cv2.VideoCapture(file_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cv2.imshow('Video', frame)
                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        break
                else:
                    break
            cap.release()
            cv2.destroyAllWindows()

# 拍摄照片
def take_photo():
    global frame
    if frame is not None:
        save_photo(Image.fromarray(frame), folder_name)

# 开始录制视频
def start_recording():
    global recording
    recording = True
    threading.Thread(target=record_video).start()

# 结束录制视频
def stop_recording():
    global recording
    recording = False

# 更新相机窗口
def update_camera():
    global frame
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(img)
        camera_label.config(image=img_tk)
        camera_label.image = img_tk
    if recording:
        root.after(10, update_camera)
    else:
        root.after(100, update_camera)

# 初始化窗口
root = tk.Tk()
root.title("相机程序")

folder_name = create_album_folder()

# 相机窗口
camera_label = tk.Label(root)
camera_label.pack()

# 控制按钮
btn_take_photo = ttk.Button(root, text="拍摄照片", command=take_photo)
btn_take_photo.pack(side="left", padx=10)

btn_start_recording = ttk.Button(root, text="开始录制", command=start_recording)
btn_start_recording.pack(side="left", padx=10)

btn_stop_recording = ttk.Button(root, text="结束录制", command=stop_recording)
btn_stop_recording.pack(side="left", padx=10)

btn_browse_files = ttk.Button(root, text="浏览文件", command=lambda: browse_files(folder_name))
btn_browse_files.pack(side="left", padx=10)

btn_quit = ttk.Button(root, text="退出", command=quit)
btn_quit.pack(side="left", padx=10)

# 打开摄像头
cap = cv2.VideoCapture(0)
recording = False

# 开始更新相机窗口
update_camera()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
