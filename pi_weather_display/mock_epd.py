from PIL import Image

import os
SHOW_IMAGE = os.environ.get("SHOW_IMAGE", "1") == "1"


class EPD:
    width = 400
    height = 300

    def init(self):
        print("[MOCK] epd.init()")

    def Clear(self):
        print("[MOCK] epd.Clear()")

    def getbuffer(self, image):
        return image

    def display(self, black_img, red_img=None):
        print("[MOCK] Display called.")
        img = Image.new("RGB", black_img.size, "white")
        img.paste(black_img.convert("RGB"))
        if SHOW_IMAGE:
            img.show()

    def sleep(self):
        print("[MOCK] epd.sleep()")

