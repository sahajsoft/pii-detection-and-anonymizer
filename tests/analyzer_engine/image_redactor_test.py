from unittest import TestCase

from analyzer_engine.image_redactor import ImageRedactor
import os

OUTPUT_DIR = "output"


class ImageRedactorTest(TestCase):

    def setUp(self) -> None:
        self.img_red = ImageRedactor()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(OUTPUT_DIR)

    def test_detects_pii_in_image_successfully(self):
        image = self.img_red.detect_pii("./data/ocr_text.png")
        image.save("./output/modified.png")
        self.assertTrue(os.path.isfile("./output/modified.png"))
