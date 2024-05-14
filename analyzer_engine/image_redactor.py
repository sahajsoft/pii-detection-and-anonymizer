from PIL import Image
from presidio_image_redactor import ImageRedactorEngine

from util.image_util import ImageUtil


class ImageRedactor:
    def __init__(self, image_file):
        self.engine = ImageRedactorEngine()
        self.image_file = image_file

    def detect_pii(self):
        image = ImageUtil.open_image(self.image_file)
        redacted_image = self.engine.redact(image, (255, 192, 203))
        return redacted_image
