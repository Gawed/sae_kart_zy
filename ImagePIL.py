from PIL import Image as PILImage
import subprocess
import os

class Image:
    def __init__(
            self,
            label: str,  # 对象的名称
            image_path: str,  # 图片路径
            show: bool,  # 是否显示图片
            callback_action: callable = None,  # 点击事件
            dark_light: bool = False,  # 是否适应深色/浅色模式
            **kwargs  # 其他参数
    ):
        self.label = label
        self.show = show
        self.position = (0, 0)
        self.kwargs = kwargs
        self.callback_action = callback_action
        self.dark_light = dark_light
        self.image_path = image_path
        self.image = self.load_image(image_path)  # 加载图片

    def load_image(self, path):
        try:
            img = PILImage.open(path)
            return img
        except FileNotFoundError:
            raise FileNotFoundError(f"无法找到图片文件: {path}")

    def display_image(self):
        if self.image and self.show:
            save_path = "temp_display.png"
            self.image.save(save_path)  # 先保存图片

            # 在终端环境中尝试打开图片
            if subprocess.run(["which", "feh"], capture_output=True).returncode == 0:
                subprocess.run(["feh", save_path])  # 使用 feh 打开
            elif subprocess.run(["which", "display"], capture_output=True).returncode == 0:
                subprocess.run(["display", save_path])  # 使用 ImageMagick 打开
            else:
                print(f"请手动打开 {save_path}")

    def get_size(self):
        return self.image.size if self.image else (0, 0)

    def set_position(self, new_position):
        self.position = new_position

    def change_image(self, new_img_path):
        self.image = self.load_image(new_img_path)
        self.image_path = new_img_path

    def on_click(self, mouse_position):
        if self.callback_action:
            self.callback_action(**self.kwargs, etat="click")

    def on_release(self, mouse_position):
        if self.callback_action:
            self.callback_action(**self.kwargs, etat="release")

