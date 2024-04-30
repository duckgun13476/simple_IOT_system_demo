from nicegui import ui, app
import threading
import time
from picture_find import find_newest_file
from dashboard.variables.variable import Var

picture = ui.image()

url = Var.MINIO_url


def renews():
    while True:
        new_late = find_newest_file()
        picture.set_source(url + '/usedfor-s-three-test/' + str(new_late))
        time.sleep(3)
        print("update")


app.on_startup(threading.Thread(target=renews, daemon=True).start)  # 3d更新


def change():
    picture.set_source('unlabeled_image.jpg')


ui.button("change", on_click=change)
ui.run(port=3451)
