import os


def get_dir_files(dir):
    return os.listdir(dir)


if __name__ == '__main__':
    print(get_dir_files('../static/images/banner'))