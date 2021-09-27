import os

PATH = "../examples/configs/"

if not os.path.exists(PATH):
    os.makedirs(PATH)

for obj in os.listdir(PATH):
    if obj.endswith(".ini"):
        try:
            os.remove(PATH+obj)
        except Exception as e:
            print(e)