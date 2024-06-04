from PIL import Image


class ImageUtil:
    def save_image(self):
        pass

    @staticmethod
    def open_image(image_name):
        try:
            img = Image.open(image_name, mode="r")
            return img
        except Exception as e:
            print(f"Error opening image: {e}")
            return None
