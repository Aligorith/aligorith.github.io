# Accordion/Collapsible Panel widget
# Author: Joshua Leung

import sys

import PyQt5 as pqt
import PyQt5.QtCore as qcore
import PyQt5.QtGui as quic
import PyQt5.QtWidgets as qgui

#####################################
# Panel used in Accordion

class AccordionPane:
	# ctor
	# < title: (str) title of panel
	# < items: ([string]) list of strings to add to this pane
	# < (expandable): (bool) 
	def __init__(self, title, items, expandable=True):
		# store settings for pane
		self.title = title
		self.items = items
		
		self.expandable = expandable
		
		# create the relevant widgets
		self.head = self.make_title_widget()
		self.body = self.make_contents_widget()
		
		# perform appropriate bindings for expandable panels
		if expandable:
			# head <-> body visibility
			self.head.toggled[bool].connect(self.body.setVisible)
			
			# arrow display (need to do initial init)
			#self.head.toggled[bool].connect(self.toggle_icon)
			#self.toggle_icon()
		
	# Add item to pane
	def addItem(self, item):
		self.items.append(item)
		
		
	# Make sure panel is expanded
	def expand(self):
		self.head.setChecked(True)
		
	# Make sure panel is collapsed
	def collapse(self):
		self.head.setChecked(False)
		
	# Returns whether the panel is expanded or not
	def isExpanded(self):
		if self.expandable:
			return self.head.isChecked()
		else:
			return True # always "open"
		
	# Setup UI (internal) ---------------------------------
		
	# Get widget for representing title
	def make_title_widget(self):
		# expandability of widget determines whether it can be toggled/checked
		if self.expandable:
			widget = qgui.QPushButton(self.title)
			widget.setCheckable(True)
		else:
			widget = qgui.QPushButton(self.title)
			#widget.setEnabled(False) # keep background, but make non-clickable
			widget.setFlat(True)
			
		# left-align all text
		widget.setStyleSheet("text-align:left; padding:5px; padding-left:6px;")
			
		return widget
		
	# Get widget showing contents of pane
	# ! This returns a list, since that's what's required for this experiment
	def make_contents_widget(self):
		# create list widget - since that's what's needed for this experiment
		widget = qgui.QListWidget()
		widget.setObjectName("accList: %s" % (self.title))
		
		# add items to list
		for item in self.items:
			itemWidget = qgui.QListWidgetItem(item, widget)
			
		# size/scrolling hacks...
		widget.setResizeMode(qgui.QListView.Adjust)
			
		# unless panel is always expanded, make these default to being closed
		if self.expandable:
			widget.setVisible(False)
		
		return widget
	
	# UI Callbacks -----------------------------------------
	
	# Toggle the icon displayed in the header
	def toggle_icon(self):
		if self.isExpanded():
			self.head.setIcon(qgui.QIcon('icons/expand_open.png'))
		else:
			self.head.setIcon(qgui.QIcon('icons/expand_closed.png'))

#####################################
# Accordion Widget

class AccordionWidget(qgui.QWidget):
	MIN_WIDTH = 300
	
	# ctor
	# < singleOpen: (bool) only a single category can be open at once
	# < fitAllCategories: (bool) all categories must be visible at once
	# < expandablePanels: (bool) whether panels can be expanded
	def __init__(self, singleOpen=True, fitAllCategories=True, expandablePanels=True):
		qgui.QWidget.__init__(self)
		
		# store properties affecting the expansion policy
		self.singleOpen = singleOpen
		self.fitAllCategories = fitAllCategories
		self.expandable = expandablePanels
		
		# internal data model
		self.panels = []     # AccordionPane's
		
		# widget properties
		self.setMinimumWidth(AccordionWidget.MIN_WIDTH + 20)
		self.setContentsMargins(0, 0, 0, 0)
		
	# Panels --------------------------------------------
		
	# add a panel to the accordion
	# < panel: (AccordionPane)
	def addPanel(self, panel):
		self.panels.append(panel)
		
	# add a list of panels
	# < panels: ([AccordionPane])
	def addPanels(self, panels):
		self.panels += panels
		
	# add panels to accordion from a description given as pairs of named tuples
	# < data: ( [(str, [str])] )
	def addData(self, data):
		# create and add the panels
		for title, items in data:
			self.addPanel(AccordionPane(title, items, self.expandable))
	
	# setup panels in accordion
	def setupUI(self):
		# layout manager - vertical list without any gaps
		self.layout = qgui.QGridLayout()
		self.layout.setSpacing(0)
		#self.layout.setMargin(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		
		# add widgets for the current panels
		for i,panel in enumerate(self.panels):
			# get widgets
			head = panel.head
			body = panel.body
			
			# attach to layout
			# - each panel takes 2 rows in layout, but all are in 1 column...
			row = 2 * i
			alignFlag = qcore.Qt.AlignTop
			
			self.layout.addWidget(head, row,   1, alignFlag)
			self.layout.addWidget(body, row+1, 1)
			
			# add additional constraints on extents of panel...
			# FIXME... single-external is collapsed, multi-internal doesn't scroll
			if not self.fitAllCategories:
				# make sure we don't restrict the size
				# - font determines row height... 
				rowHeight = body.fontMetrics().height() + body.fontMetrics().lineSpacing()
				body.setMinimumHeight(body.count() * rowHeight)
				
			
			# hook up events
			head.clicked.connect(self.onPanelClick)
			
		# add dummy padding to force all things together when closed
		# if they all panels could potentially be collapsed at once
		if self.singleOpen == False and self.expandable:
			# - it's size should be the maximum vertical space taken by body widgets
			maxHeight = sum([p.body.height() for p in self.panels])
			width = 0
			
			row = 2 * len(self.panels)
			
			self.tailSpacer = qgui.QSpacerItem(width, maxHeight, vPolicy=qgui.QSizePolicy.Maximum)
			self.layout.addItem(self.tailSpacer, row, 1)
			
		# .....................................
			
		# host everything in a scrollpane if it doesn't need to all fit...
		if not self.fitAllCategories:
			# host everything in a scrollpane
			pnl = qgui.QWidget()
			pnl.setLayout(self.layout)
			pnl.setMinimumWidth(AccordionWidget.MIN_WIDTH)
			
			scrollpane = qgui.QScrollArea()
			scrollpane.setContentsMargins(0, 0, 0, 0)
			scrollpane.setWidgetResizable(True)
			scrollpane.setWidget(pnl)
			
			# host the scrollpane in a layout so that we can host it
			scrollLayout = qgui.QVBoxLayout()
			scrollLayout.setContentsMargins(0, 0, 0, 0)
			scrollLayout.setSpacing(0)
			scrollLayout.addWidget(scrollpane)
			
			self.setLayout(scrollLayout)
		else:
			# use grid layout (with panels) directly
			self.setLayout(self.layout)
		
	# enforce that panels are collapsed properly first
	def validateUI(self):
		# collapse all but first, if only a single item can be open at once
		if self.expandable:
			for i,panel in enumerate(self.panels):
				if i == 0:
					panel.expand()
				else:
					panel.collapse()
	
	# HCI API ----------------------------------------------
	
	# hook up logging utilities
	# < logger: (Logger)
	def attachLogging(self, logger):
		# attach click handlers
		for panel in self.panels:
			panel.head.clicked.connect(logger.click_event)
			
			panel.body.itemDoubleClicked.connect(logger.item_dblClick_event)
			panel.body.itemClicked.connect(logger.item_click_event)
			
	# hook up callbacks
	# < all args are lists of functions to get called
	def attachCallbacks(self, headClick, itemDouble, itemSingle):
		for fn in headClick:
			for panel in self.panels:
				panel.head.clicked.connect(fn)
				
		for fn in itemDouble:
			for panel in self.panels:
				panel.body.itemDoubleClicked.connect(fn)
		
		for fn in itemSingle:
			for panel in self.panels:
				panel.body.itemClicked.connect(fn)
	
	# UI Internals -----------------------------------------
	
	# get the panel with given widget as it's header
	def get_panel_from_header(self, header):
		for i, panel in enumerate(self.panels):
			if panel.head == header:
				return i, panel
		else:
			raise ValueError("Header not found in get_panel_from_header()")
		
	# Event Handling -------------------------------------
	
	# callback for handling panel click behaviour
	def onPanelClick(self):
		# if we only allow a single panel to be open at once, we'll need to do some work here
		if self.singleOpen:
			# get currently active one
			tIndex, target = self.get_panel_from_header(self.sender())
			
			# expand/collapse others
			if target.isExpanded():
				# open - close everything else
				for panel in self.panels:
					if panel != target:
						panel.collapse()
			else:
				# closed - open one above/below us, depending on where this is
				if tIndex == 0:
					if len(self.panels) == 1:
						# keep panel open - it's the only one!
						self.panels[tIndex].expand()
					else:
						# open one after this
						self.panels[tIndex + 1].expand()
				elif tIndex == len(self.panels) - 1:
					# open one before
					self.panels[tIndex - 1].expand()
				else:
					# open one after
					self.panels[tIndex + 1].expand()
		else:
			# size of widget needs recalculation, as number of panels changes
			pass
				
#####################################
# AccordionFactory

# Construct an accordion from a list/dictionary
# < data: ( [(str, [str])] )
def AccordionFactory(singleOpen, fitAllCategories, expandablePanels, data):
	# accordion widget to host all this
	accordion = AccordionWidget(singleOpen, fitAllCategories, expandablePanels)
	
	# create and add the panels
	accordion.addData(data)
		
	# return everything
	return accordion
	

# Parameters for standard accordion types
TYPE_ACCORDION    = 'Accordion'           # (single fixed)
TYPE_COLLAPSIBLES = 'Collapsible Panels'  # (multi scroll)
TYPE_FLAT         = 'Flat Hierarchy'      # (all scroll

TYPE_SINGLESCROLL = 'Single Scrolling'    # (single scroll)
TYPE_MULTIFIXED   = 'Multiple Fixed'      # (multi fixed)

AccordionTypes = {
	# Name : (singleOpen, fitAllCategories, expandablePanels)
	TYPE_ACCORDION     : (True,  True,  True),
	TYPE_COLLAPSIBLES  : (False, False, True),
	TYPE_FLAT          : (False, False, False),
	TYPE_SINGLESCROLL  : (True,  False, True),
	TYPE_MULTIFIXED    : (False, True,  True)
}

# Construct an accordion from a given type
def accordion_from_type(itype, data):	
	# accordion widget to host all this
	singleOpen, fitAllCategories, expandablePanels = AccordionTypes[itype]
	accordion = AccordionWidget(singleOpen, fitAllCategories, expandablePanels)
	
	# create and add the panels
	accordion.addData(data)
		
	# return everything
	return accordion
	
#####################################

# testing
if __name__ == '__main__':
	app = qgui.QApplication(sys.argv)
	
	# setup window
	win = qgui.QMainWindow()
	win.setWindowTitle("Accordion Test Gui")
	
	# create several accordions
	panels = [
		("Category A", ['a', 'b', 'c']),
		("Category B", ['e', 'f', 'g', 'h']),
		("Category C", ['i', 'j']),
		
		("Category D", ['a', 'b', 'c']),
		("Category E", ['e', 'f', 'g', 'h']),
		("Category F", ['i', 'j']),
		("Category G", ['a', 'b', 'c']),
		("Category H", ['e', 'f', 'g', 'h']),
		("Category I", ['i', 'j']),
	]
	
	# list of accordions to make
	accordions = [TYPE_ACCORDION, TYPE_COLLAPSIBLES, TYPE_FLAT]
	#accordions = [TYPE_ACCORDION, TYPE_SINGLESCROLL, TYPE_MULTIFIXED]
	
	# iterate over accordions, adding them to a container
	panel = qgui.QWidget()
	
	hbox = qgui.QHBoxLayout()
	panel.setLayout(hbox)
	
	for itype in accordions:
		# create now
		acc = accordion_from_type(itype, panels)
		
		# set widget state accordingly
		acc.setupUI()
		acc.validateUI()
		
		# add to layout
		hbox.addWidget(acc)
	
	# show all
	win.setCentralWidget(panel)
	win.show()
	
	# execute
	sys.exit(app.exec_())
