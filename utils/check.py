follow_img_suffix = ['jpg', 'png']


def check_img_suffix(img_suffix):
    result = False
    if img_suffix in follow_img_suffix:
        result = True
    return result