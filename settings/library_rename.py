import PyQt5.QtWidgets as QtWidgets


class RenameWindow(QtWidgets.QMainWindow):
	def __init__(self, inp_text):
		super(RenameWindow, self).__init__()

		self.inp_text = inp_text

		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayout = QtWidgets.QHBoxLayout()

		self.label = QtWidgets.QLabel()

