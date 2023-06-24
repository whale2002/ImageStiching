import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
# 自定义模块
from Stitcher import Stitcher

class ImageStitchingGUI:
  def __init__(self, master):
    self.master = master
    # 设置窗口大小
    self.master.geometry('%dx%d' % (1200, 800))
    self.master.title('图像拼接程序-BJFU秦浩喻')
    # 创建GUI界面
    self.create_gui()
    # 初始化 stitcher
    self.stitcher = Stitcher()

  def create_gui(self):
    # 创建菜单栏
    menubar = Menu(self.master)
    self.master.config(menu=menubar)

    # 创建文件菜单
    filemenu = Menu(menubar, tearoff=0)
    menubar.add_command(label="选择Image 1", command=self.open_image1)
    menubar.add_command(label="选择Image 2", command=self.open_image2)
    menubar.add_command(label="导出结果", command=self.export_image)

    menubar.add_command(label="Exit", command=self.master.quit)

    # 创建拼接按钮
    self.stitch_button = Button(self.master, text="拼接图片", command=self.stitch_image, font=(16))
    self.stitch_button.pack(side='bottom', padx=30, pady=10)

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
      self.img1 = cv2.resize(self.img1, (300, 320))
        
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
      self.img2 = cv2.resize(self.img2, (300, 320))
      self.show_image(self.img2, 1)

  def stitch_image(self):
    # 判断是否已经选择了两张图片
    if hasattr(self, 'img1') and hasattr(self, 'img2'):
      # 进行图像拼接
      (result, vis) = self.stitcher.stitch([self.img1, self.img2], showMatches=True)
      self.result = result

      # 显示拼接后的结果
      self.show_image(self.result, 2)

    else:
      # 提示用户选择两张图片
      messagebox.showwarning('Warning', '请先选择两张图片!')

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
      self.img3_label = Label(self.image_frame, image=img)
      self.img3_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # 保留图像引用，防止被垃圾回收
    if index == 0 or index == 1 or index == 2:
      getattr(self, 'img%d_label' % (index+1)).img = img

  def export_image(self):
    if not hasattr(self, 'result'):
      messagebox.showwarning('Warning', '请先合成图片!')
      return

    # 提示用户选择导出路径
    filepath = filedialog.asksaveasfilename(
      initialdir=".",
      initialfile="result.jpg",
      title="Export Image",
      filetypes=(("JPEG files", "*.jpg"), ("PNG files", "*.png"))
    )

    print(filepath)

    # 判断是否选择了导出路径
    if filepath:
      # 保存拼接后的图片到导出路径
      cv2.imwrite(filepath, self.result)
      messagebox.showinfo('Success', '图片已成功导出！')

if __name__=='__main__':
  root = Tk()

  ImageStitchingGUI(root)

  root.mainloop()