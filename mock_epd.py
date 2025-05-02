from PIL import Image

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
        img.show()

    def sleep(self):
        print("[MOCK] epd.sleep()")

