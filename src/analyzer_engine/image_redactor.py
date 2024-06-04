from PIL import Image
from presidio_image_redactor import ImageRedactorEngine

from util.image_util import ImageUtil


class ImageRedactor:
    def __init__(self):
        self.engine = ImageRedactorEngine()

    def detect_pii(self, image_file):
        image = ImageUtil.open_image(image_file)
        redacted_image = self.engine.redact(image, (255, 192, 203))
        return redacted_image
