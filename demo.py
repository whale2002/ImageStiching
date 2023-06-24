import cv2
import numpy as np 
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
# import opencv-contrib-python

class ImageStitchingGUI: 
  def __init__(self, master): 
    self.master = master
    self.master.geometry('%dx%d' % (1200, 800))#设置窗口大小
    self.master.title('Image Stitching')
    # 创建GUI界面
    self.create_gui()

  def create_gui(self):
      # 创建菜单栏
      menubar = Menu(self.master)
      self.master.config(menu=menubar)

      # 创建文件菜单
      filemenu = Menu(menubar, tearoff=0)
      filemenu.add_command(label="Open Image 1", command=self.open_image1)
      filemenu.add_command(label="Open Image 2", command=self.open_image2)

      filemenu.add_separator()

      filemenu.add_command(label="Exit", command=self.master.quit)

      menubar.add_cascade(label="添加图片", menu=filemenu)

      # 创建拼接按钮
      self.stitch_button = Button(self.master, text="拼接图片", command=self.stitch_image)
      self.stitch_button.pack(side='bottom')

      # 创建图像显示区域
      self.image_frame = Frame(self.master)
      self.image_frame.pack(side='top', padx=10, pady=10)

  def open_image1(self):
      # 打开文件对话框，选择图片1
      filepath = filedialog.askopenfilename(
          initialdir=".",
          title="Select Image 1",
          filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("all files", "*.*"))
      )

      print(filepath)

      if filepath:
          self.img1 = cv2.imread(filepath)
          self.img1 = cv2.resize(self.img1, (300, 200))
          
          self.show_image(self.img1, 0)

  def open_image2(self):
      # 打开文件对话框，选择图片2
      filepath = filedialog.askopenfilename(
          initialdir=".",
          title="Select Image 2",
          filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("all files", "*.*"))
      )

      print(filepath)

      if filepath:
          self.img2 = cv2.imread(filepath)
          self.img2 = cv2.resize(self.img2, (300, 200))
          self.show_image(self.img2, 1)

  def stitch_image(self):
      # 判断是否已经选择了两张图片
      if hasattr(self, 'img1') and hasattr(self, 'img2'):
          # 计算单应性矩阵
          H = self.get_homo(self.img1, self.img2)
          # 进行图像拼接
          result_image = self.stitch_images(self.img1, self.img2, H)
          # 显示拼接后的结果
          self.show_image(result_image, 2)
      else:
          # 提示用户选择两张图片
          messagebox.showwarning('Warning', 'Please select two images first!')

  def get_homo(self, img1, img2):
      # 创建特征转换对象
      sift = cv2.xfeatures2d.SIFT_create()
      # 通过特征转换对象获得特征点和描述子
      k1, d1 = sift.detectAndCompute(img1, None)    # k1为特征点，d1为描述子
      k2, d2 = sift.detectAndCompute(img2, None)
      # 创建特征匹配
      # 进行特征匹配
      bf = cv2.BFMatcher()  # 采用暴力特征匹配
      matches = bf.knnMatch(d1, d2, k=2)    # 匹配特征点

      verify_ratio = 0.8  # 过滤
      verify_matches = []
      for m1, m2 in matches:  # m1,m2之间的距离越小越好，小于0.8认为有效，大于0.8无效
          if m1.distance < 0.8 * m2.distance:
              verify_matches.append(m1)

      # 最小匹配数
      min_matches = 8
      if len(verify_matches) > min_matches:
          img1_pts = []
          img2_pts = []
          for m in verify_matches:
              img1_pts.append(k1[m.queryIdx].pt)  # 图像1的坐标特征点
              img2_pts.append(k2[m.trainIdx].pt)  # 图像2的坐标特征点
          img1_pts = np.float32(img1_pts).reshape(-1, 1, 2)    # 适应findHomography的格式
          img2_pts = np.float32(img2_pts).reshape(-1, 1, 2) 
          H, mask =  cv2.findHomography(img1_pts, img2_pts, cv2.RANSAC, 5.0)  # 获取单应性矩阵
          return H
      else:
          messagebox.showerror('Error', 'Not enough matches!')
          return None

  def stitch_images(self, img1, img2, H):
      # 获得每张图片的4个角点
      h1, w1 = img1.shape[:2]
      h2, w2 = img2.shape[:2]
      img1_dims = np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2)
      img2_dims = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
      # 图像变换
      img1_transform = cv2.perspectiveTransform(img1_dims, H)
      result_dims = np.concatenate((img2_dims, img1_transform), axis=0)   # 横向拼接，主要是为了求出图像的最大值最小值
      [x_min, y_min] = np.int32(result_dims.min(axis=0).ravel() - 0.5)
      [x_max, y_max] = np.int32(result_dims.max(axis=0).ravel() + 0.5)
      # 平移的距离
      transform_dist = [-x_min, -y_min]
      transform_array = np.array([[1, 0, transform_dist[0]],
                                  [0, 1, transform_dist[1]],
                                  [0, 0, 1]])
      # 投影变换
      result_img = cv2.warpPerspective(img1, transform_array.dot(H), (x_max - x_min, y_max - y_min))
      result_img[transform_dist[1]:transform_dist[1] + h2, transform_dist[0]:transform_dist[0] + w2] = img2
      return result_img

  def show_image(self, img, index):
    # 将OpenCV图像转换为PIL图像
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)

    # 显示图像
    if index == 0:
        self.img1_label = Label(self.image_frame, image=img)
        self.img1_label.grid(row=0, column=0, padx=10, pady=10)
    elif index == 1:
        self.img2_label = Label(self.image_frame, image=img)
        self.img2_label.grid(row=0, column=1, padx=10, pady=10)
    elif index == 2:
        self.result_label = Label(self.image_frame, image=img)
        self.result_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # 保留图像引用，防止被垃圾回收
    if index == 0 or index == 1:
        getattr(self, 'img%d_label' % (index+1)).img = img

if __name__=='__main__':
  root = Tk() 

  app = ImageStitchingGUI(root)

  root.mainloop()