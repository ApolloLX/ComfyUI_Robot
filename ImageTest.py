from PIL import Image

def add_comment_to_jpg(input_image_path, output_image_path, comment):
    # 打开图像文件
    img = Image.open(input_image_path)

    # 确保备注信息是字符串类型
    if not isinstance(comment, str):
        comment = str(comment)

    # 保存图像为 JPG 文件，并嵌入备注信息
    img.save(output_image_path, "JPEG", comment=comment)

    print(f"Image saved with comment: {comment}")

def read_comment_from_jpg(image_path):
    # 打开保存的 JPG 文件
    img = Image.open(image_path)

    # 读取备注信息
    comment = img.info.get("comment")

    if comment:
        print(f"Comment found: {comment}")
    else:
        print("No comment found.")

# 主函数
def main():
    # 输入图像文件路径
    input_image_path = "H:\\tmp\\image_1.png"  # 替换为你的图像文件路径

    # 输出 JPG 文件路径
    output_image_path = "H:\\tmp\\imageA_1.jpg"  # 替换为你想要保存的 JPG 文件路径

    # 备注信息
    comment = "This is a comment string saved in the JPG file."

    # 添加备注信息并保存图像
    add_comment_to_jpg(input_image_path, output_image_path, comment)

    # 读取备注信息
    read_comment_from_jpg(output_image_path)

if __name__ == "__main__":
    main()
