from PIL import Image
img = Image.open('ui/assets/logo.jpg')
img.save('ui/assets/logo.ico', format='ICO', sizes=[(256, 256)])
