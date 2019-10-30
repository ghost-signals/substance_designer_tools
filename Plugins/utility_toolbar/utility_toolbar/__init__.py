import sd
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdvalueserializer import SDValueSerializer
from functools import partial
import os
from PySide2 import QtCore, QtGui, QtWidgets, QtSvg


DEFAULT_ICON_SIZE = 24


class UtilityToolBar(QtWidgets.QToolBar):

	copy_src_node = None

	def __init__(self, graphViewID, uiMgr):
		super(UtilityToolBar, self).__init__(parent=uiMgr.getMainWindow())

		# Save the graphViewID and uiMgr for later use.
		self.__graphViewID = graphViewID
		self.__uiMgr = uiMgr

		# Add Copy action
		act = self.addAction(self.__loadSvgIcon("param_copy_icon", DEFAULT_ICON_SIZE), "CopyParameters")
		act.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_C))
		act.setToolTip("Copy node parameters")
		act.triggered.connect(self.__onCopyNodeParameters)

		# Add Paste action
		act = self.addAction(self.__loadSvgIcon("param_paste_icon", DEFAULT_ICON_SIZE), "PasteParameters")
		act.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_V))
		act.setToolTip("Paste node parameters")
		act.triggered.connect(self.__onPasteNodeParameters)


	def __onCopyNodeParameters(self):
		# Get the currently selected nodes.
		selection = self.__getSelectedNodes()
		if len(selection) == 1:
			self.copy_src_node = selection[0]


	def __onPasteNodeParameters(self):
		selection = self.__getSelectedNodes()
		if self.copy_src_node != None and len(selection) >= 1:
			
			src_node_label = self.copy_src_node.getDefinition().getLabel()
			props = self.copy_src_node.getDefinition().getProperties(SDPropertyCategory.Input)

			for node in selection:
				if node.getDefinition().getLabel() != src_node_label:
					continue
				
				for prop in props:
					label = prop.getLabel()
					propId = prop.getId()
					
					value = self.copy_src_node.getPropertyValue(prop)
					if value:
						node.setPropertyValue(prop, value)


	def __getSelectedNodes(self):
		# Use our saved graphViewID to retrieve the graph selection.
		return self.__uiMgr.getCurrentGraphSelectionFromGraphViewID(self.__graphViewID)


	def __loadSvgIcon(self, iconName, size):
		currentDir = os.path.dirname(__file__)
		iconFile = os.path.abspath(os.path.join(currentDir, iconName + '.svg'))

		svgRenderer = QtSvg.QSvgRenderer(iconFile)
		if svgRenderer.isValid():
			pixmap = QtGui.QPixmap(QtCore.QSize(size, size))

			if not pixmap.isNull():
				pixmap.fill(QtCore.Qt.transparent)
				painter = QtGui.QPainter(pixmap)
				svgRenderer.render(painter)
				painter.end()

			return QtGui.QIcon(pixmap)

		return None

def onNewGraphViewCreated(graphViewID, uiMgr):
	print(onNewGraphViewCreated)
	# Create our toolbar.
	toolbar = UtilityToolBar(graphViewID, uiMgr)
	
	# Add our toolbar to the graph widget.
	uiMgr.addToolbarToGraphView(
		graphViewID,
		toolbar,
		icon = None,
		tooltip = "Utility Toolbar")


def initializeSDPlugin():
	print("Utility toolbar plugin loaded!")

	# Get the application and UI manager object.
	ctx = sd.getContext()
	app = ctx.getSDApplication()
	uiMgr = app.getQtForPythonUIMgr()

	# Register a callback to know when GraphViews are created.
	uiMgr.registerGraphViewCreatedCallback(partial(onNewGraphViewCreated, uiMgr=uiMgr))
