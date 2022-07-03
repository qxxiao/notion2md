import os


# 确保在执行的时候导入此文件
exported_dir = "notion2md_files"
# root_dir = os.getcwd()  # as root directory: absolute path
root_dir = os.curdir  # as root directory: relative path


image_count = 0
file_count = 0
file_last_btype = 0

# ! 更新 root_dir 首页写入位置
root_dir = os.path.join(root_dir, exported_dir)

if not os.path.exists(root_dir):
    os.makedirs(root_dir)
else:
    print("exported_dir already exists: {}".format(root_dir))
    # exit(1)
os.chdir(root_dir)
cur_dir = os.curdir  # . = current directory
# print(cur_dir)
# print(os.path.dirname(cur_dir))
