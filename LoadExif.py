from PIL import Image

# 打开图像文件
img = Image.open("H:\\TMP\\AAA.jpg")

# 显示图像属性
print("Format:", img.format)
print("Mode:", img.mode)
print("Size:", img.size)
print("Width:", img.width)
print("Height:", img.height)
print("Info:", img.info)

# 显示图像
img.show()

# 调整图像大小
resized_img = img.resize((200, 200))
resized_img.show()

# 旋转图像
rotated_img = img.rotate(45)
rotated_img.show()

# 裁剪图像
cropped_img = img.crop((50, 50, 150, 150))
cropped_img.show()

# 转换图像模式
gray_img = img.convert("L")
gray_img.show()

# 获取像素值
pixel_value = img.getpixel((100, 100))
print("Pixel value at (100, 100):", pixel_value)

# 获取 EXIF 数据
exif_data = img.getexif()
print("EXIF data:", exif_data)
