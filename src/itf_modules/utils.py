from PyQt5 import QtGui

def set_status_light(widget, status):
    widget.setPixmap(QtGui.QPixmap(f"src/pics/lamp_{status}.png"))