import datetime
import os.path
import sqlite3
import webbrowser
from os import getcwd, startfile

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

from fetch_video_info import fetch_window
from main_window import add_to_cl_window, copy_move
from misc_files import common_vars, check_for_db
from settings import settings_window
from video_entry import entry_screen

# TODO: Detail view -- if e.g. video is selected from Editor Username dropdown, another editor is clicked, and then you click the Edit Video button, AMVT crashes


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		check_for_db.check_for_db()
		self.init_window()

	def init_window(self, sel_filters=None):
		"""
		:param sel_filters: a list [a, b, c] where:
			a = sub-DB dropdown current index
			b = filter dropdown current index
			c = selected item in filter list widget (if None, nothing is selected)
		"""
		# Instance attributes defined outside __init__ -- known weak warnings here, decided to do it this way because
		# I'm too lazy to restructure the code here to avoid this error, and this is a hacky fix to make updating
		# MainWindow possible when Settings window is closed.

		# SQLite connections
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()
		video_db_conn = sqlite3.connect(common_vars.video_db())
		video_db_cursor = video_db_conn.cursor()

		# Misc variables
		leftWidth = 270
		rightWidth = 340
		settings_cursor.execute('SELECT path_to_db FROM db_settings')
		currentWorkingDB = settings_cursor.fetchone()[0]
		settings_cursor.execute('SELECT value FROM search_settings WHERE setting_name = ?', ('view_type',))
		self.viewType = settings_cursor.fetchone()[0]
		self.leftSideVidIDs = []
		self.rightSideVidIDs = []

		# Layout initialization
		self.vLayoutMaster = QtWidgets.QVBoxLayout()
		self.hLayoutTopBar = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_L = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_L.setAlignment(QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_Ctr = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_Ctr.setAlignment(QtCore.Qt.AlignCenter)
		self.hLayoutTopBar_R = QtWidgets.QHBoxLayout()
		self.hLayoutTopBar_R.setAlignment(QtCore.Qt.AlignRight)

		self.hLayoutCenter = QtWidgets.QHBoxLayout()
		self.vLayoutLeftBar = QtWidgets.QVBoxLayout()
		self.hLayoutDView = QtWidgets.QHBoxLayout()
		self.hLayoutDViewMaster = QtWidgets.QHBoxLayout()
		self.vLayoutDView = QtWidgets.QVBoxLayout()
		self.gridDHeader = QtWidgets.QGridLayout()
		self.gridDView_L = QtWidgets.QGridLayout()
		self.gridDView_L.setAlignment(QtCore.Qt.AlignTop)
		self.gridDView_R = QtWidgets.QGridLayout()
		self.gridDView_R.setAlignment(QtCore.Qt.AlignTop)
		self.gridRightBar = QtWidgets.QGridLayout()
		self.gridRightBar.setAlignment(QtCore.Qt.AlignLeft)

		# Top bar - L
		self.boldFont = QtGui.QFont()
		self.boldFont.setBold(True)
		self.boldFont.setPixelSize(20)
		self.addVideoBtn = QtWidgets.QPushButton('+')
		self.addVideoBtn.setFont(self.boldFont)
		self.addVideoBtn.setFixedSize(40, 40)
		self.addVideoBtn.setToolTip('Add new video to database')

		self.fetchDateIcon = QtGui.QIcon(getcwd() + '/icons/fetch_data_icon.png')
		self.fetchDataButton = QtWidgets.QPushButton()
		self.fetchDataButton.setIcon(self.fetchDateIcon)
		self.fetchDataButton.setIconSize(QtCore.QSize(25, 25))
		self.fetchDataButton.setFixedSize(40, 40)
		self.fetchDataButton.setToolTip('Download video data by editor profile or YouTube channel')

		self.custListIcon = QtGui.QIcon(getcwd() + '/icons/cl-icon.png')
		self.custListBtn = QtWidgets.QPushButton()
		self.custListBtn.setIcon(self.custListIcon)
		self.custListBtn.setIconSize(QtCore.QSize(25, 25))
		self.custListBtn.setFixedSize(40, 40)
		self.custListBtn.setToolTip('Manage custom lists')
		
		# Top bar - Ctr
		self.listViewIcon = QtGui.QIcon(getcwd() + '/icons/list-view-icon.png')
		self.listViewBtn = QtWidgets.QPushButton()
		self.listViewBtn.setFixedSize(40, 40)
		self.listViewBtn.setIcon(self.listViewIcon)
		self.listViewBtn.setIconSize(QtCore.QSize(25, 25))
		self.listViewBtn.setToolTip('List view')

		self.detailViewIcon = QtGui.QIcon(getcwd() + '/icons/detail-view-icon.png')
		self.detailViewBtn = QtWidgets.QPushButton()
		self.detailViewBtn.setFixedSize(40, 40)
		self.detailViewBtn.setIcon(self.detailViewIcon)
		self.detailViewBtn.setIconSize(QtCore.QSize(30, 30))
		self.detailViewBtn.setToolTip('Detail view')

		if self.viewType == 'L':
			self.listViewBtn.setDown(True)
			self.detailViewBtn.setDown(False)
		else:
			self.listViewBtn.setDown(False)
			self.detailViewBtn.setDown(True)

		# Top bar - R
		self.settingsIcon = QtGui.QIcon(getcwd() + '/icons/settings-icon.png')
		self.settingsBtn = QtWidgets.QPushButton()
		self.settingsBtn.setFixedSize(40, 40)
		self.settingsBtn.setIcon(self.settingsIcon)
		self.settingsBtn.setIconSize(QtCore.QSize(25, 25))
		self.settingsBtn.setToolTip('AMV Tracker settings')

		self.statsIcon = QtGui.QIcon(getcwd() + '/icons/stats-icon.png')
		self.statsBtn = QtWidgets.QPushButton()
		self.statsBtn.setFixedSize(40, 40)
		self.statsBtn.setIcon(self.statsIcon)
		self.statsBtn.setIconSize(QtCore.QSize(25, 25))
		self.statsBtn.setToolTip('Database stats and analytics')

		self.updateBtn = QtWidgets.QPushButton(u'\u2191')
		self.updateBtn.setFont(self.boldFont)
		self.updateBtn.setFixedSize(40, 40)
		self.updateBtn.setToolTip('Check for update')

		# Mid: left bar
		self.scrollWidget_L = QtWidgets.QWidget()
		self.scrollArea_L = QtWidgets.QScrollArea()
		self.scrollArea_L.setFixedWidth(leftWidth)

		self.largeFont = QtGui.QFont()
		self.largeFont.setPixelSize(14)

		self.subDBLabel = QtWidgets.QLabel()
		self.subDBLabel.setText('Sub-DB:')
		self.subDBLabel.setFont(self.largeFont)
		self.subDBList = [k for k, v in common_vars.sub_db_lookup().items()]
		self.subDBDrop = QtWidgets.QComboBox()
		self.subDBDrop.setFont(self.largeFont)
		for subdb in self.subDBList:
			self.subDBDrop.addItem(subdb)

		self.basicFiltersLabel = QtWidgets.QLabel()
		self.basicFiltersLabel.setText('Filter by:')
		self.basicFiltersLabel.setFont(self.largeFont)
		self.basicFiltersList = ['Studio', 'Year released', 'Star rating', 'Video footage', 'Song artist', 'Song genre',
								 'Video length', 'My rating', 'Notable videos', 'Favorited videos',
								 'Date added to database', 'Custom list', 'Editor username',
								 'Video footage (single source only)']
		self.basicFiltersList.sort()
		# TODO: Change index below to 0 for final release
		self.basicFiltersList.insert(1, 'Show all')
		self.basicFiltersDrop = QtWidgets.QComboBox()
		for item in self.basicFiltersList:
			self.basicFiltersDrop.addItem(item)
		self.basicFiltersDrop.setFixedWidth(230)
		self.basicFiltersDrop.setFont(self.largeFont)
		self.basicFiltersDrop.setMaxVisibleItems(15)

		self.basicFilterListWid = QtWidgets.QListWidget()
		self.basicFilterListWid.setFixedSize(230, 550)

		if sel_filters:
			self.subDBDrop.setCurrentIndex(sel_filters[0])
			self.basicFiltersDrop.setCurrentIndex(sel_filters[1])

		self.vLayoutLeftBar.addWidget(self.subDBLabel)
		self.vLayoutLeftBar.addWidget(self.subDBDrop)
		self.vLayoutLeftBar.addSpacing(15)
		self.vLayoutLeftBar.addWidget(self.basicFiltersLabel)
		self.vLayoutLeftBar.addWidget(self.basicFiltersDrop)
		self.vLayoutLeftBar.addWidget(self.basicFilterListWid)

		# Mid: left bar - stats window
		self.gridLayoutStats = QtWidgets.QGridLayout()
		self.gridLayoutStats.setColumnMinimumWidth(0, 200)
		self.scrollWidgetStats = QtWidgets.QWidget()
		self.scrollAreaStats = QtWidgets.QScrollArea()

		self.statsLabelFont = QtGui.QFont()
		self.statsLabelFont.setPixelSize(14)
		self.statsLabelFont.setUnderline(True)
		self.statsWidLabel = QtWidgets.QLabel()
		self.statsWidLabel.setText('Stats for displayed videos')
		self.statsWidLabel.setFont(self.statsLabelFont)
		self.gridLayoutStats.addWidget(self.statsWidLabel, 0, 0, 1, 5)

		self.numVideosTitle = QtWidgets.QLabel()
		self.numVideosTitle.setText('# of videos: ')
		self.numVideosLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.numVideosTitle, 1, 0)
		self.gridLayoutStats.addWidget(self.numVideosLabel, 1, 2, 1, 3)

		self.oldestVideoTitle = QtWidgets.QLabel()
		self.oldestVideoTitle.setText('Oldest video released: ')
		self.oldestVideoLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.oldestVideoTitle, 2, 0)
		self.gridLayoutStats.addWidget(self.oldestVideoLabel, 2, 2, 1, 3)

		self.newestVideoTitle = QtWidgets.QLabel()
		self.newestVideoTitle.setText('Newest video released: ')
		self.newestVideoLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.newestVideoTitle, 3, 0)
		self.gridLayoutStats.addWidget(self.newestVideoLabel, 3, 2, 1, 3)

		self.avgMyRatingTitle = QtWidgets.QLabel()
		self.avgMyRatingTitle.setText('Average my rating score: ')
		self.avgMyRatingLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.avgMyRatingTitle, 4, 0)
		self.gridLayoutStats.addWidget(self.avgMyRatingLabel, 4, 2, 1, 3)

		self.avgStarRatingTitle = QtWidgets.QLabel()
		self.avgStarRatingTitle.setText('Average star rating score: ')
		self.avgStarRatingLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.avgStarRatingTitle, 5, 0)
		self.gridLayoutStats.addWidget(self.avgStarRatingLabel, 5, 2, 1, 3)

		self.longestVidTitle = QtWidgets.QLabel()
		self.longestVidTitle.setText('Longest video is: ')
		self.longestVidLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.longestVidTitle, 6, 0)
		self.gridLayoutStats.addWidget(self.longestVidLabel, 6, 2, 1, 3)

		self.shortestVidTitle = QtWidgets.QLabel()
		self.shortestVidTitle.setText('Shortest video is: ')
		self.shortestVidLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.shortestVidTitle, 7, 0)
		self.gridLayoutStats.addWidget(self.shortestVidLabel, 7, 2, 1, 3)

		self.avgDurationTitle = QtWidgets.QLabel()
		self.avgDurationTitle.setText('Average duration is: ')
		self.avgDurationLabel = QtWidgets.QLabel()
		self.gridLayoutStats.addWidget(self.avgDurationTitle, 8, 0)
		self.gridLayoutStats.addWidget(self.avgDurationLabel, 8, 2, 1, 3)

		self.scrollWidgetStats.setLayout(self.gridLayoutStats)
		self.scrollAreaStats.setWidget(self.scrollWidgetStats)
		self.vLayoutLeftBar.addWidget(self.scrollAreaStats)

		# Mid: center
		self.searchTable = QtWidgets.QTableWidget()
		if self.viewType == 'D':
			self.searchTable.setMinimumWidth(350)
			self.searchTable.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		self.init_table()

		# Mid: Detail view
		dViewHeaderInd = 0
		dViewVertInd_L = 0
		dViewVertInd_R = 0
		self.medLargeText = QtGui.QFont()
		self.medLargeText.setPixelSize(13)
		self.headerText = QtGui.QFont()
		self.headerText.setPixelSize(22)
		self.headerText.setBold(True)

		self.scrollWidget_dview = QtWidgets.QWidget()
		self.scrollArea_dview = QtWidgets.QScrollArea()
		self.scrollArea_dview.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

		## Detail view: Header
		self.thumbLabel = QtWidgets.QLabel()
		self.thumbLabel.setFixedSize(640, 360)
		self.thumbPixmap = QtGui.QPixmap(getcwd() + '\\thumbnails\\no_thumb.jpg')
		self.thumbLabel.setPixmap(self.thumbPixmap.scaled(self.thumbLabel.size(), QtCore.Qt.KeepAspectRatio))
		self.gridDHeader.addWidget(self.thumbLabel, dViewHeaderInd, 0, 2, 4, alignment=QtCore.Qt.AlignCenter)
		dViewHeaderInd += 1

		self.gridDHeader.setRowMinimumHeight(dViewHeaderInd, 10)
		dViewHeaderInd += 1

		self.editorVideoTitleLabel = QtWidgets.QLabel()
		self.editorVideoTitleLabel.setWordWrap(True)
		self.editorVideoTitleLabel.setText('')
		self.editorVideoTitleLabel.setFont(self.headerText)
		self.gridDHeader.addWidget(self.editorVideoTitleLabel, dViewHeaderInd, 0, 1, 4)
		dViewHeaderInd += 1

		self.gridDHeader.setRowMinimumHeight(dViewHeaderInd, 10)
		dViewHeaderInd += 1

		self.middleRibbonHLayout = QtWidgets.QHBoxLayout()
		self.middleRibbonHLayout.setAlignment(QtCore.Qt.AlignLeft)

		self.editBtnIcon = QtGui.QIcon(getcwd() + '/icons/edit-icon.png')
		self.editButton = QtWidgets.QPushButton()
		self.editButton.setToolTip('Edit video info')
		self.editButton.setFixedSize(40, 40)
		self.editButton.setIcon(self.editBtnIcon)
		self.editButton.setIconSize(QtCore.QSize(25, 25))
		self.editButton.setDisabled(True)
		self.middleRibbonHLayout.addWidget(self.editButton)

		self.viewBtnIcon = QtGui.QIcon(getcwd() + '/icons/play-icon.png')
		self.viewButton = QtWidgets.QPushButton()
		self.viewButton.setToolTip('Play local video file')
		self.viewButton.setFixedSize(40, 40)
		self.viewButton.setIcon(self.viewBtnIcon)
		self.viewButton.setIconSize(QtCore.QSize(25, 25))
		self.viewButton.setDisabled(True)
		self.middleRibbonHLayout.addWidget(self.viewButton)

		self.YTBtnIcon = QtGui.QIcon(getcwd() + '/icons/yt-icon.png')
		self.YTButton = QtWidgets.QPushButton()
		self.YTButton.setToolTip('Go to video on YouTube (if URL has been provided)')
		self.YTButton.setFixedSize(40, 40)
		self.YTButton.setIcon(self.YTBtnIcon)
		self.YTButton.setIconSize(QtCore.QSize(25, 25))
		self.YTButton.setDisabled(True)
		self.middleRibbonHLayout.addWidget(self.YTButton)
		self.middleRibbonHLayout.addSpacing(10)

		self.editCLIcon = QtGui.QIcon(getcwd() + '\\icons\\edit-cl-icon.png')
		self.editCLButton = QtWidgets.QPushButton()
		self.editCLButton.setToolTip('Add/remove from custom lists')
		self.editCLButton.setFixedSize(40, 40)
		self.editCLButton.setIcon(self.editCLIcon)
		self.editCLButton.setIconSize(QtCore.QSize(30, 30))
		self.editCLButton.setDisabled(True)
		self.middleRibbonHLayout.addSpacing(30)
		self.middleRibbonHLayout.addWidget(self.editCLButton, alignment=QtCore.Qt.AlignRight)

		self.copyIcon = QtGui.QIcon(getcwd() + '\\icons\\copy-icon.png')
		self.copyButton = QtWidgets.QPushButton()
		self.copyButton.setToolTip('Copy video to another sub-DB')
		self.copyButton.setFixedSize(40, 40)
		self.copyButton.setIcon(self.copyIcon)
		self.copyButton.setIconSize(QtCore.QSize(25, 25))
		self.copyButton.setDisabled(True)
		self.middleRibbonHLayout.addWidget(self.copyButton, alignment=QtCore.Qt.AlignRight)

		self.moveIcon = QtGui.QIcon(getcwd() + '\\icons\\move-icon.png')
		self.moveButton = QtWidgets.QPushButton()
		self.moveButton.setToolTip('Move video to another sub-DB')
		self.moveButton.setFixedSize(40, 40)
		self.moveButton.setIcon(self.moveIcon)
		self.moveButton.setIconSize(QtCore.QSize(25, 25))
		self.moveButton.setDisabled(True)
		self.middleRibbonHLayout.addWidget(self.moveButton, alignment=QtCore.Qt.AlignRight)

		self.deleteIcon = QtGui.QIcon(getcwd() + '\\icons\\delete_icon.png')
		self.deleteButton = QtWidgets.QPushButton()
		self.deleteButton.setToolTip('Delete this video from AMV Tracker')
		self.deleteButton.setFixedSize(40, 40)
		self.deleteButton.setIcon(self.deleteIcon)
		self.deleteButton.setIconSize(QtCore.QSize(25, 25))
		self.deleteButton.setDisabled(True)
		self.middleRibbonHLayout.addWidget(self.deleteButton, alignment=QtCore.Qt.AlignRight)

		self.vertFrame1 = QtWidgets.QFrame()
		self.vertFrame1.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
		self.vertFrame1.setLineWidth(0)
		self.vertFrame1.setMidLineWidth(1)
		self.middleRibbonHLayout.addWidget(self.vertFrame1)
		self.middleRibbonHLayout.addSpacing(10)

		self.dateAddedLabel = QtWidgets.QLabel()
		self.dateAddedLabel.setText('Date added:\n')
		self.dateAddedLabel.setFont(self.medLargeText)
		self.middleRibbonHLayout.addWidget(self.dateAddedLabel)
		self.middleRibbonHLayout.addSpacing(10)

		self.vertFrame2 = QtWidgets.QFrame()
		self.vertFrame2.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
		self.vertFrame2.setLineWidth(0)
		self.vertFrame2.setMidLineWidth(1)
		self.middleRibbonHLayout.addWidget(self.vertFrame2)
		self.middleRibbonHLayout.addSpacing(10)

		self.numPlaysLabel = QtWidgets.QLabel()
		self.numPlaysLabel.setText('# of plays:\n')
		self.numPlaysLabel.setToolTip('Only counts times the local video file\nhas been played from AMV Tracker')
		self.numPlaysLabel.setFont(self.medLargeText)
		self.middleRibbonHLayout.addWidget(self.numPlaysLabel)
		self.middleRibbonHLayout.addSpacing(10)

		self.playCountLayout = QtWidgets.QVBoxLayout()
		self.playCountIncreaseBtn = QtWidgets.QPushButton(u'\u25B2')
		self.playCountIncreaseBtn.setFixedSize(15, 15)
		self.playCountIncreaseBtn.setToolTip('Increase play count')
		self.playCountIncreaseBtn.setDisabled(True)
		self.playCountDecreaseBtn = QtWidgets.QPushButton(u'\u25BC')
		self.playCountDecreaseBtn.setFixedSize(15, 15)
		self.playCountDecreaseBtn.setToolTip('Decrease play count')
		self.playCountDecreaseBtn.setDisabled(True)

		self.playCountLayout.addWidget(self.playCountIncreaseBtn)
		self.playCountLayout.addWidget(self.playCountDecreaseBtn)
		self.middleRibbonHLayout.addLayout(self.playCountLayout)
		self.middleRibbonHLayout.addSpacing(10)

		self.vertFrame3 = QtWidgets.QFrame()
		self.vertFrame3.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
		self.vertFrame3.setLineWidth(0)
		self.vertFrame3.setMidLineWidth(1)
		self.middleRibbonHLayout.addWidget(self.vertFrame3)
		self.middleRibbonHLayout.addSpacing(10)

		self.vidIDLabel = QtWidgets.QLabel()
		self.vidIDLabel.setText('AMV Tracker video ID:\n')
		self.vidIDLabel.setFont(self.medLargeText)
		self.middleRibbonHLayout.addWidget(self.vidIDLabel)
		"""self.middleRibbonHLayout.addSpacing(10)

		self.vertFrame4 = QtWidgets.QFrame()
		self.vertFrame4.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
		self.vertFrame4.setLineWidth(0)
		self.vertFrame4.setMidLineWidth(1)
		self.middleRibbonHLayout.addWidget(self.vertFrame4)
		self.middleRibbonHLayout.addSpacing(10)

		self.dViewSubDBLabel = QtWidgets.QLabel()
		self.dViewSubDBLabel.setText('Sub-DB:\n')
		self.dViewSubDBLabel.setFont(self.medLargeText)
		self.middleRibbonHLayout.addWidget(self.dViewSubDBLabel)"""

		# self.gridDHeader.addLayout(self.middleRibbonHLayout, dViewHeaderInd, 0, 1, 3)

		dViewHeaderInd += 1

		## Detail view: Left grid
		# TODO: Widgets overlap if too much info is provided
		self.pseudoLabel = QtWidgets.QLabel()
		self.pseudoLabel.setWordWrap(True)
		self.pseudoLabel.setText('Primary editor pseudonym(s): ')
		self.pseudoLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.pseudoLabel, dViewVertInd_L, 0, 1, 3, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_L += 1

		self.addlEditorsLabel = QtWidgets.QLabel()
		self.addlEditorsLabel.setWordWrap(True)
		self.addlEditorsLabel.setText('Additional editors: ')
		self.addlEditorsLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.addlEditorsLabel, dViewVertInd_L, 0, 1, 3, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_L += 1

		self.studioLabel = QtWidgets.QLabel()
		self.studioLabel.setWordWrap(True)
		self.studioLabel.setText('Studio: ')
		self.studioLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.studioLabel, dViewVertInd_L, 0, 1, 3, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_L += 1

		self.releaseDateLabel = QtWidgets.QLabel()
		self.releaseDateLabel.setText('Release date: ')
		self.releaseDateLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.releaseDateLabel, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.gridDView_L.setRowMinimumHeight(dViewVertInd_L, 10)
		dViewVertInd_L += 1

		self.starRatingHLayout = QtWidgets.QHBoxLayout()
		self.starRatingHLayout.setAlignment(QtCore.Qt.AlignLeft)
		self.starRatingLabel = QtWidgets.QLabel()
		self.starRatingLabel.setText('Star rating: ')
		self.starRatingLabel.setFont(self.medLargeText)
		self.starRatingHLayout.addWidget(self.starRatingLabel)

		self.starRatingImg = QtWidgets.QLabel()
		self.starRatingImg.setFixedWidth(70)
		self.starPixmap = QtGui.QPixmap('F:\\Python\\AMV Tracker\\icons\\stars-00.png')
		self.starRatingImg.setPixmap(self.starPixmap.scaled(self.starRatingImg.size(), QtCore.Qt.KeepAspectRatio))
		self.starRatingHLayout.addWidget(self.starRatingImg)
		self.gridDView_L.addLayout(self.starRatingHLayout, dViewVertInd_L, 0)
		dViewVertInd_L += 1

		self.myRatingLabel = QtWidgets.QLabel()
		self.myRatingLabel.setText('My rating: ')
		self.myRatingLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.myRatingLabel, dViewVertInd_L, 0, 1, 2)
		dViewVertInd_L += 1

		self.favHLayout = QtWidgets.QHBoxLayout()
		self.favHLayout.setAlignment(QtCore.Qt.AlignLeft)
		self.favLabel = QtWidgets.QLabel()
		self.favLabel.setText('Favorite: ')
		self.favLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.favLabel, dViewVertInd_L, 0, 1, 2)

		self.favImg = QtWidgets.QLabel()
		self.favImg.setFixedWidth(15)
		self.favPixmap = QtGui.QPixmap(getcwd() + '\\icons\\' + 'checkbox_empty_icon.png')
		self.favImg.setPixmap(self.favPixmap.scaled(self.favImg.size(), QtCore.Qt.KeepAspectRatio))
		self.favHLayout.addWidget(self.favImg)
		self.gridDView_L.addLayout(self.favHLayout, dViewVertInd_L, 0)
		dViewVertInd_L += 1

		self.notableHLayout = QtWidgets.QHBoxLayout()
		self.notableHLayout.setAlignment(QtCore.Qt.AlignLeft)
		self.notableLabel = QtWidgets.QLabel()
		self.notableLabel.setText('Notable: ')
		self.notableLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.notableLabel, dViewVertInd_L, 0, 1, 2)

		self.notableImg = QtWidgets.QLabel()
		self.notableImg.setFixedWidth(15)
		self.notablePixmap = QtGui.QPixmap(getcwd() + '\\icons\\' + 'checkbox_empty_icon.png')
		self.notableImg.setPixmap(self.notablePixmap.scaled(self.notableImg.size(), QtCore.Qt.KeepAspectRatio))
		self.notableHLayout.addWidget(self.notableImg)
		self.gridDView_L.addLayout(self.notableHLayout, dViewVertInd_L, 0)
		dViewVertInd_L += 1

		self.gridDView_L.setRowMinimumHeight(dViewVertInd_L, 10)
		dViewVertInd_L += 1

		self.durLabel = QtWidgets.QLabel()
		self.durLabel.setText('Duration: ')
		self.durLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.durLabel, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.artistLabel = QtWidgets.QLabel()
		self.artistLabel.setWordWrap(True)
		self.artistLabel.setText('Song artist: ')
		self.artistLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.artistLabel, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.songLabel = QtWidgets.QLabel()
		self.songLabel.setWordWrap(True)
		self.songLabel.setText('Song title: ')
		self.songLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.songLabel, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.songGenreLabel = QtWidgets.QLabel()
		self.songGenreLabel.setWordWrap(True)
		self.songGenreLabel.setText('Song genre: ')
		self.songGenreLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.songGenreLabel, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.videoFtgLabel = QtWidgets.QLabel()
		self.videoFtgLabel.setText('List of video footage:')
		self.videoFtgLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.videoFtgLabel, dViewVertInd_L, 0, 1, 2)
		dViewVertInd_L += 1

		self.videoFtgListWid = QtWidgets.QListWidget()
		self.videoFtgListWid.setFixedSize(300, 120)
		self.gridDView_L.addWidget(self.videoFtgListWid, dViewVertInd_L, 0, 1, 6)
		dViewVertInd_L += 1

		self.gridDView_L.setRowMinimumHeight(dViewVertInd_L, 10)
		dViewVertInd_L += 1

		self.tags1Label = QtWidgets.QLabel()
		self.tags1Label.setWordWrap(True)
		self.tags1Label.setText('Tags: ')
		# self.tags1Label.hide()
		self.tags1Label.setFixedWidth(300)
		self.tags1Label.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.tags1Label, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.tags2Label = QtWidgets.QLabel()
		self.tags2Label.setWordWrap(True)
		# self.tags2Label.hide()
		self.tags2Label.setFixedWidth(300)
		self.tags2Label.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.tags2Label, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.tags3Label = QtWidgets.QLabel()
		self.tags3Label.setWordWrap(True)
		# self.tags3Label.hide()
		self.tags3Label.setFixedWidth(300)
		self.tags3Label.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.tags3Label, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.tags4Label = QtWidgets.QLabel()
		self.tags4Label.setWordWrap(True)
		# self.tags4Label.hide()
		self.tags4Label.setFixedWidth(300)
		self.tags4Label.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.tags4Label, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.tags5Label = QtWidgets.QLabel()
		self.tags5Label.setWordWrap(True)
		# self.tags5Label.hide()
		self.tags5Label.setFixedWidth(300)
		self.tags5Label.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.tags5Label, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.tags6Label = QtWidgets.QLabel()
		self.tags6Label.setWordWrap(True)
		# self.tags6Label.hide()
		self.tags6Label.setFixedWidth(300)
		self.tags6Label.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.tags6Label, dViewVertInd_L, 0, 1, 3)
		dViewVertInd_L += 1

		self.gridDView_L.setRowMinimumHeight(dViewVertInd_L, 10)
		dViewVertInd_L += 1

		self.contestsLabel = QtWidgets.QLabel()
		self.contestsLabel.setText('Contests entered:')
		self.contestsLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.contestsLabel, dViewVertInd_L, 0, 1, 2)
		dViewVertInd_L += 1

		self.contestsText = QtWidgets.QTextEdit()
		self.contestsText.setFixedSize(300, 120)
		self.contestsText.setReadOnly(True)
		self.gridDView_L.addWidget(self.contestsText, dViewVertInd_L, 0, 1, 6)
		dViewVertInd_L += 1

		self.awardsLabel = QtWidgets.QLabel()
		self.awardsLabel.setText('Awards won:')
		self.awardsLabel.setFont(self.medLargeText)
		self.gridDView_L.addWidget(self.awardsLabel, dViewVertInd_L, 0, 1, 2)
		dViewVertInd_L += 1

		self.awardsText = QtWidgets.QTextEdit()
		self.awardsText.setFixedSize(300, 120)
		self.awardsText.setReadOnly(True)
		self.gridDView_L.addWidget(self.awardsText, dViewVertInd_L, 0, 1, 6)
		dViewVertInd_L += 1

		## Details view: Right grid
		self.vidDescLabel = QtWidgets.QLabel()
		self.vidDescLabel.setText('Video description:')
		self.vidDescLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.vidDescLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.vidDescText = QtWidgets.QTextEdit()
		self.vidDescText.setFixedSize(400, 300)
		self.vidDescText.setReadOnly(True)
		self.gridDView_R.addWidget(self.vidDescText, dViewVertInd_R, 0, 1, 6, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.gridDView_R.setRowMinimumHeight(dViewVertInd_R, 10)
		dViewVertInd_R += 1

		self.commentsLabel = QtWidgets.QLabel()
		self.commentsLabel.setText('Personal comments:')
		self.commentsLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.commentsLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.commentsText = QtWidgets.QTextEdit()
		self.commentsText.setFixedSize(400, 200)
		self.commentsText.setReadOnly(True)
		self.gridDView_R.addWidget(self.commentsText, dViewVertInd_R, 0, 1, 6, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.gridDView_R.setRowMinimumHeight(dViewVertInd_R, 10)
		dViewVertInd_R += 1

		self.videoLinksLabel = QtWidgets.QLabel()
		self.videoLinksLabel.setText('Video links:')
		self.videoLinksLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.videoLinksLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.ytLinkLabel = QtWidgets.QLabel()
		self.ytLinkLabel.setOpenExternalLinks(True)
		self.ytLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.ytLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.amvOrgLinkLabel = QtWidgets.QLabel()
		self.amvOrgLinkLabel.setOpenExternalLinks(True)
		self.amvOrgLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.amvOrgLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.amvnewsLinkLabel = QtWidgets.QLabel()
		self.amvnewsLinkLabel.setOpenExternalLinks(True)
		self.amvnewsLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.amvnewsLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.otherLinkLabel = QtWidgets.QLabel()
		self.otherLinkLabel.setOpenExternalLinks(True)
		self.otherLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.otherLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.gridDView_R.setRowMinimumHeight(dViewVertInd_R, 10)
		dViewVertInd_R += 1
		
		self.profileLinksLabel = QtWidgets.QLabel()
		self.profileLinksLabel.setText('Editor profile links:')
		self.profileLinksLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.profileLinksLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.ytChannelLinkLabel = QtWidgets.QLabel()
		self.ytChannelLinkLabel.setOpenExternalLinks(True)
		self.ytChannelLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.ytChannelLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.amvOrgProfileLinkLabel = QtWidgets.QLabel()
		self.amvOrgProfileLinkLabel.setOpenExternalLinks(True)
		self.amvOrgProfileLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.amvOrgProfileLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.amvnewsProfileLinkLabel = QtWidgets.QLabel()
		self.amvnewsProfileLinkLabel.setOpenExternalLinks(True)
		self.amvnewsProfileLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.amvnewsProfileLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		self.otherProfileLinkLabel = QtWidgets.QLabel()
		self.otherProfileLinkLabel.setOpenExternalLinks(True)
		self.otherProfileLinkLabel.setFont(self.medLargeText)
		self.gridDView_R.addWidget(self.otherProfileLinkLabel, dViewVertInd_R, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
		dViewVertInd_R += 1

		# Mid: right bar
		self.scrollWidget_R = QtWidgets.QWidget()
		self.scrollArea_R = QtWidgets.QScrollArea()
		self.scrollArea_R.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.scrollArea_R.setFixedWidth(rightWidth)

		self.largeUndFont = QtGui.QFont()
		self.largeUndFont.setPixelSize(14)
		self.largeUndFont.setUnderline(True)

		self.addFilterButton = QtWidgets.QPushButton('Add filter')
		self.addFilterButton.setFixedWidth(125)
		self.addFilterButton.setFont(self.largeFont)
		self.gridRightBar.addWidget(self.addFilterButton, 0, 0, 1, 2)

		self.filterOperatorDrop = QtWidgets.QComboBox()
		self.filterOperatorDrop.setFixedWidth(150)
		self.filterOperatorDrop.setFont(self.largeFont)
		self.filterOperatorDrop.addItem('Match ALL criteria')
		self.filterOperatorDrop.addItem('Match ANY criteria')
		self.gridRightBar.addWidget(self.filterOperatorDrop, 1, 0, 1, 2)

		self.filterLabelList = [QtWidgets.QLabel() for x in range(0, 6)]
		self.exclLabelList = [QtWidgets.QCheckBox('EXCLUDE') for x in range(0, 6)]
		self.filterTextEditList = [QtWidgets.QTextEdit() for x in range(0, 6)]
		self.removeFilterList = [QtWidgets.QPushButton('X') for x in range(0, 6)]

		self.gridRightBar.setRowMinimumHeight(2, 30)

		loopIndex = 0
		for ind in range(3, 15, 2):
			self.filterLabelList[loopIndex].setText('Filter {}'.format(loopIndex + 1))
			self.filterLabelList[loopIndex].setFont(self.largeUndFont)
			self.filterLabelList[loopIndex].setDisabled(True)
			self.exclLabelList[loopIndex].setDisabled(True)
			self.filterTextEditList[loopIndex].setFixedSize(170, 60)
			self.filterTextEditList[loopIndex].setReadOnly(True)
			self.filterTextEditList[loopIndex].setDisabled(True)
			self.removeFilterList[loopIndex].setFixedWidth(20)
			self.removeFilterList[loopIndex].setToolTip('Remove filter')
			self.removeFilterList[loopIndex].setDisabled(True)

			self.gridRightBar.addWidget(self.filterLabelList[loopIndex], ind, 0)
			self.gridRightBar.addWidget(self.exclLabelList[loopIndex], ind + 1, 0)
			self.gridRightBar.addWidget(self.filterTextEditList[loopIndex], ind + 1, 1, alignment=QtCore.Qt.AlignLeft)
			self.gridRightBar.addWidget(self.removeFilterList[loopIndex], ind + 1, 2)

			loopIndex += 1

		self.gridRightBar.setRowMinimumHeight(15, 30)

		self.filterLogicLabel = QtWidgets.QLabel()
		self.filterLogicLabel.setText('Filter logic')
		self.filterLogicLabel.setFont(self.largeUndFont)
		self.gridRightBar.addWidget(self.filterLogicLabel, 16, 0)

		self.filterLogicText = QtWidgets.QTextEdit()
		self.filterLogicText.setReadOnly(True)
		self.filterLogicText.setFixedSize(280, 60)
		self.gridRightBar.addWidget(self.filterLogicText, 17, 0, 1, 2)

		self.gridRightBar.setRowMinimumHeight(18, 30)

		self.applyFilters = QtWidgets.QPushButton('Apply filters')
		self.applyFilters.setFont(self.largeFont)
		self.applyFilters.setFixedSize(150, 40)
		self.applyFilters.setDisabled(True)
		self.gridRightBar.addWidget(self.applyFilters, 19, 0, 1, 3, alignment=QtCore.Qt.AlignCenter)

		# Bottom bar
		self.cwdLabel = QtWidgets.QLabel()
		self.cwdLabel.setText('Current working database: ' + currentWorkingDB)

		# Top layout size restriction
		self.leftWidget = QtWidgets.QWidget()
		self.leftWidget.setLayout(self.hLayoutTopBar_L)
		self.leftWidget.setFixedWidth(leftWidth)

		self.rightWidget = QtWidgets.QWidget()
		self.rightWidget.setLayout(self.hLayoutTopBar_R)
		self.rightWidget.setFixedWidth(rightWidth)

		# Set layouts
		self.hLayoutTopBar_L.addWidget(self.addVideoBtn, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_L.addWidget(self.fetchDataButton, alignment=QtCore.Qt.AlignLeft)
		# self.hLayoutTopBar_L.addWidget(self.custListBtn, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_Ctr.addWidget(self.listViewBtn, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_Ctr.addWidget(self.detailViewBtn, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar_R.addWidget(self.settingsBtn, alignment=QtCore.Qt.AlignRight)
		self.hLayoutTopBar_R.addWidget(self.statsBtn, alignment=QtCore.Qt.AlignRight)
		self.hLayoutTopBar_R.addWidget(self.updateBtn, alignment=QtCore.Qt.AlignRight)
		self.hLayoutTopBar.addWidget(self.leftWidget, alignment=QtCore.Qt.AlignLeft)
		self.hLayoutTopBar.addLayout(self.hLayoutTopBar_Ctr)
		self.hLayoutTopBar.addWidget(self.rightWidget, alignment=QtCore.Qt.AlignRight)

		self.hLayoutDViewMaster.addLayout(self.gridDView_L)
		self.hLayoutDViewMaster.addSpacing(20)
		self.hLayoutDViewMaster.addLayout(self.gridDView_R)

		self.scrollWidget_L.setLayout(self.vLayoutLeftBar)
		self.scrollArea_L.setWidget(self.scrollWidget_L)
		self.scrollWidget_dview.setLayout(self.hLayoutDViewMaster)
		self.scrollArea_dview.setWidget(self.scrollWidget_dview)
		self.scrollWidget_R.setLayout(self.gridRightBar)
		self.scrollArea_R.setWidget(self.scrollWidget_R)

		self.hLayoutCenter.addWidget(self.scrollArea_L, alignment=QtCore.Qt.AlignLeft)
		if self.viewType == 'D':
			self.vLayoutDView.addLayout(self.gridDHeader)
			self.vLayoutDView.addLayout(self.middleRibbonHLayout)
			self.hLayoutDView.addWidget(self.scrollArea_dview, 1)
			self.vLayoutDView.addLayout(self.hLayoutDView)

			self.hLayoutCenter.addWidget(self.searchTable, alignment=QtCore.Qt.AlignLeft)
			self.hLayoutCenter.addLayout(self.vLayoutDView)
			self.hLayoutCenter.setStretch(2, 1)
		else:
			self.hLayoutCenter.addWidget(self.searchTable)
		self.hLayoutCenter.addWidget(self.scrollArea_R, alignment=QtCore.Qt.AlignRight)

		self.vLayoutMaster.addLayout(self.hLayoutTopBar)
		self.vLayoutMaster.addLayout(self.hLayoutCenter)
		self.vLayoutMaster.addWidget(self.cwdLabel, alignment=QtCore.Qt.AlignRight)

		# Populate table
		self.basic_filter_dropdown_clicked()

		# Signals / slots
		self.addVideoBtn.clicked.connect(self.add_video_pushed)
		self.fetchDataButton.clicked.connect(self.fetch_info_pushed)
		self.listViewBtn.clicked.connect(lambda: self.change_view_type('L'))
		self.detailViewBtn.clicked.connect(lambda: self.change_view_type('D'))

		self.settingsBtn.clicked.connect(self.settings_button_pushed)

		self.subDBDrop.currentIndexChanged.connect(self.basic_filter_dropdown_clicked)
		self.basicFiltersDrop.currentIndexChanged.connect(self.basic_filter_dropdown_clicked)
		self.basicFilterListWid.itemClicked.connect(self.filter_set_1)
		self.searchTable.cellClicked.connect(lambda: self.table_cell_clicked(
			int(self.searchTable.currentRow()), int(self.searchTable.currentColumn()),
			self.searchTable.item(self.searchTable.currentRow(), 0).text()))

		self.editButton.clicked.connect(self.edit_entry)
		self.viewButton.clicked.connect(lambda: self.play_video(common_vars.sub_db_lookup()[self.subDBDrop.currentText()],
																self.searchTable.item(self.searchTable.currentRow(), 0).text()
																))
		self.YTButton.clicked.connect(lambda: self.go_to_link(common_vars.sub_db_lookup()[self.subDBDrop.currentText()],
																self.searchTable.item(self.searchTable.currentRow(), 0).text(),
															  'video_youtube_url'))
		self.editCLButton.clicked.connect(lambda: self.add_to_cust_list(
			self.searchTable.item(self.searchTable.currentRow(), 0).text()))
		self.copyButton.clicked.connect(lambda: self.copy_btn_pushed(
			self.searchTable.item(self.searchTable.currentRow(), 0).text(), self.subDBDrop.currentText(), True))
		self.moveButton.clicked.connect(lambda: self.copy_btn_pushed(
			self.searchTable.item(self.searchTable.currentRow(), 0).text(), self.subDBDrop.currentText(), False))
		self.deleteButton.clicked.connect(lambda: self.delete_video(
			common_vars.sub_db_lookup()[self.subDBDrop.currentText()],
			self.searchTable.item(self.searchTable.currentRow(), 0).text()))
		self.playCountIncreaseBtn.clicked.connect(lambda: self.change_play_count(1))
		self.playCountDecreaseBtn.clicked.connect(lambda: self.change_play_count(-1))

		if sel_filters:
			if sel_filters[2]:
				self.basicFilterListWid.item(sel_filters[2]).setSelected(True)
				self.basicFilterListWid.setCurrentItem(self.basicFilterListWid.item(sel_filters[2]))
				self.filter_set_1()

		# Widget
		self.mainWid = QtWidgets.QWidget()
		self.mainWid.setLayout(self.vLayoutMaster)
		self.setCentralWidget(self.mainWid)
		self.setWindowTitle('AMV Tracker')

		video_db_conn.close()
		settings_conn.close()

	def add_video_pushed(self):
		self.add_video = entry_screen.VideoEntry()
		self.add_video.show()

	def fetch_info_pushed(self):
		self.fetch_window = fetch_window.FetchWindow()
		self.fetch_window.show()

	def change_view_type(self, view_type):
		settings_conn = sqlite3.connect(common_vars.settings_db())
		settings_cursor = settings_conn.cursor()

		if (view_type == 'L' and self.listViewBtn.isDown()) or (view_type == 'D' and self.detailViewBtn.isDown()):
			pass
		else:
			if view_type == 'L':
				self.listViewBtn.setDown(True)
				self.detailViewBtn.setDown(False)

			else:
				self.listViewBtn.setDown(False)
				self.detailViewBtn.setDown(True)

			settings_cursor.execute('UPDATE search_settings SET value = ? WHERE setting_name = "view_type"', (view_type,))
			settings_conn.commit()

			if self.basicFilterListWid.selectedItems():
				sel_item_ind = self.basicFilterListWid.currentRow()
			else:
				sel_item_ind = None
			self.init_window(sel_filters=[self.subDBDrop.currentIndex(), self.basicFiltersDrop.currentIndex(),
										  sel_item_ind])

		settings_conn.close()

	def settings_button_pushed(self):
		if self.basicFilterListWid.selectedItems():
			sel_item_ind = self.basicFilterListWid.currentRow()
		else:
			sel_item_ind = None

		self.settings_screen = settings_window.SettingsWindow()
		self.settings_screen.window_closed.connect(lambda: self.init_window(sel_filters=[self.subDBDrop.currentIndex(),
																						 self.basicFiltersDrop.currentIndex(),
																						 sel_item_ind]))
		self.settings_screen.show()

	def init_table(self):
		init_tab_sett_conn = sqlite3.connect(common_vars.settings_db())
		init_tab_sett_cursor = init_tab_sett_conn.cursor()
		init_tab_sett_cursor.execute('SELECT value FROM search_settings WHERE setting_name = ?', ('view_type',))
		view_type = init_tab_sett_cursor.fetchone()[0]
		init_tab_sett_cursor.execute('SELECT field_name_display, displ_order, col_width FROM search_field_lookup WHERE '
									 'visible_in_search_view = 1')

		header_bold_font = QtGui.QFont()
		header_bold_font.setBold(True)

		field_data = init_tab_sett_cursor.fetchall()
		field_data.sort(key=lambda x: int(x[1]))
		table_header_dict = {x[0]: x[2] for x in field_data}
		table_header_dict['Edit entry'] = 70
		table_header_dict['Watch'] = 60
		table_header_dict['Delete'] = 60
		if view_type == 'L':
			table_header_list = [x[0] for x in field_data]
			table_header_list.insert(1, 'Edit entry')
			table_header_list.insert(2, 'Watch')
			table_header_list.insert(3, 'Delete')
		else:
			table_header_list = ['Video ID', 'Editor name / Video title']

		self.searchTable.setColumnCount(len(table_header_list))
		self.searchTable.setHorizontalHeaderLabels(table_header_list)
		for ind in range(0, len(table_header_list)):
			if view_type == 'L':
				self.searchTable.setColumnWidth(ind, table_header_dict[
					self.searchTable.horizontalHeaderItem(ind).text()])
			else:
				self.searchTable.setColumnWidth(1, 300)
		self.searchTable.setColumnHidden(0, True)  # Hide VidID column
		self.searchTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.searchTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.searchTable.horizontalHeader().setFont(header_bold_font)
		self.searchTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

		init_tab_sett_conn.close()

	def basic_filter_dropdown_clicked(self):
		self.basicFilterListWid.clear()

		bf_drop_conn = sqlite3.connect(common_vars.video_db())
		bf_drop_cursor = bf_drop_conn.cursor()

		bf_drop_sub_db_friendly = self.subDBDrop.currentText()
		bf_drop_sub_db_internal = common_vars.sub_db_lookup()[bf_drop_sub_db_friendly]
		filter_text = self.basicFiltersDrop.currentText()

		bf_drop_cursor.execute('SELECT video_id FROM {}'.format(bf_drop_sub_db_internal))
		self.leftSideVidIDs = self.rightSideVidIDs = [x[0] for x in bf_drop_cursor.fetchall()]

		if filter_text == 'Show all':
			list_wid_pop = []
			self.filter_set_1()
		elif filter_text == 'Custom list':
			list_wid_pop = [k for k, v in common_vars.custom_list_lookup().items()]
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Date added to database':
			list_wid_pop = ['Today', 'Yesterday', 'Last 7 days', 'Last 30 days', 'Last 60 days', 'Last 90 days',
							'Last 6 months', 'Last 12 months', 'Last 24 months']

		elif filter_text == 'Editor username':
			bf_drop_cursor.execute('SELECT primary_editor_username FROM {}'.format(bf_drop_sub_db_internal))
			editors = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in editors for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Year released':
			bf_drop_cursor.execute('SELECT release_date FROM {}'.format(bf_drop_sub_db_internal))
			dates = bf_drop_cursor.fetchall()
			list_wid_pop = list(set([y[:4] for x in dates for y in x]))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort()
			list_wid_pop.insert(0, 'Unknown')
			list_wid_pop.insert(0, 'Not specified')

		elif filter_text == 'Favorited videos':
			list_wid_pop = ['Marked as favorite', 'Not marked as favorite']

		elif filter_text == 'My rating':
			list_wid_pop = [str(rat * 0.5) for rat in range(0, 21)]
			list_wid_pop.insert(0, 'Unrated')

		elif filter_text == 'Notable videos':
			list_wid_pop = ['Marked as notable', 'Not marked as notable']

		elif filter_text == 'Song artist':
			bf_drop_cursor.execute('SELECT song_artist FROM {}'.format(bf_drop_sub_db_internal))
			artists = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in artists for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Song genre':
			bf_drop_cursor.execute('SELECT song_genre FROM {}'.format(bf_drop_sub_db_internal))
			song_genres = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in song_genres for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Star rating':
			list_wid_pop = ['Unrated or 0.0', '0.50 - 1.99', '2.00 - 2.49', '2.50 - 2.99', '3.00 - 3.49', '3.50 - 3.99',
							'4.00 - 4.49', '4.50 - 5.00']

		elif filter_text == 'Studio':
			bf_drop_cursor.execute('SELECT studio FROM {}'.format(bf_drop_sub_db_internal))
			studios = bf_drop_cursor.fetchall()
			list_wid_pop = list(set(y for x in studios for y in x))
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif 'Video footage' in filter_text:
			list_wid_pop = []
			bf_drop_cursor.execute('SELECT video_footage FROM {}'.format(bf_drop_sub_db_internal))
			for ftg_tup in bf_drop_cursor.fetchall():
				for ftg_grp in list(ftg_tup):
					for ftg in ftg_grp.split('; '):
						if ftg not in list_wid_pop:
							list_wid_pop.append(ftg)
			if '' in list_wid_pop:
				list_wid_pop.remove('')
			list_wid_pop.sort(key=lambda x: x.casefold())

		elif filter_text == 'Video length':
			list_wid_pop = [str(x * 30) + ' - ' + str(((x + 1) * 30) - 1) + ' sec' for x in range(0, 14)]
			list_wid_pop.append('420+ sec')
			list_wid_pop.insert(0, 'Not specified')

		else:
			list_wid_pop = []

		for item in list_wid_pop:
			self.basicFilterListWid.addItem(item)

		bf_drop_conn.close()

	def filter_set_1(self):
		bf_conn = sqlite3.connect(common_vars.video_db())
		bf_cursor = bf_conn.cursor()

		bf_sel_subdb_friendly = self.subDBDrop.currentText()
		bf_sel_subdb_internal = common_vars.sub_db_lookup()[bf_sel_subdb_friendly]
		vidids_list = []
		filtered_vidids_1 = []
		filter_by_text = self.basicFiltersDrop.currentText()
		sel_filter = ''

		if filter_by_text == 'Show all':
			bf_cursor.execute('SELECT video_id FROM {}'.format(bf_sel_subdb_internal))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])
		else:
			sel_filter = self.basicFilterListWid.currentItem().text()

		if filter_by_text == 'Custom list':
			bf_cursor.execute('SELECT vid_ids FROM custom_lists WHERE list_name = ?', (sel_filter,))
			filtered_vidids_1 = bf_cursor.fetchall()[0][0].split('; ')

		elif filter_by_text == 'Date added to database':
			today = datetime.date.today()
			bf_cursor.execute('SELECT video_id, date_entered FROM {}'.format(bf_sel_subdb_internal))
			for tup in bf_cursor.fetchall():
				if tup[1] != '':
					ent_date_list = [int(x) for x in tup[1].split('/')]
					ent_date = datetime.date(ent_date_list[0], ent_date_list[1], ent_date_list[2])
					delta = today - ent_date
					vidids_list.append((tup[0], delta.days))

			for vid in vidids_list:
				if (sel_filter == 'Today' and vid[1] == 0) or \
						(sel_filter == 'Yesterday' and vid[1] == 1) or \
						(sel_filter == 'Last 7 days' and vid[1] <= 7) or \
						(sel_filter == 'Last 30 days' and vid[1] <= 30) or \
						(sel_filter == 'Last 60 days' and vid[1] <= 60) or \
						(sel_filter == 'Last 90 days' and vid[1] <= 90) or \
						(sel_filter == 'Last 6 months' and vid[1] <= 180) or \
						(sel_filter == 'Last 12 months' and vid[1] <= 365) or \
						(sel_filter == 'Last 24 months' and vid[1] <= 730):
					filtered_vidids_1.append(vid[0])

		elif filter_by_text == 'Editor username':
			bf_cursor.execute('SELECT video_id FROM {} WHERE primary_editor_username = ? OR '
							  'primary_editor_pseudonyms LIKE ? OR addl_editors LIKE ?'.format(bf_sel_subdb_internal),
							  (sel_filter, sel_filter, sel_filter))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Favorited videos':
			if sel_filter == 'Marked as favorite':
				fav = 1
			else:
				fav = 0
			bf_cursor.execute('SELECT video_id FROM {} WHERE favorite = ?'.format(bf_sel_subdb_internal), (fav,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'My rating':
			if sel_filter == 'Unrated':
				mr_inp_text = ''
			else:
				mr_inp_text = sel_filter
			bf_cursor.execute('SELECT video_id FROM {} WHERE my_rating = ?'.format(bf_sel_subdb_internal),
							  (mr_inp_text,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Notable videos':
			if sel_filter == 'Marked as notable':
				notable = 1
			else:
				notable = 0
			bf_cursor.execute('SELECT video_id FROM {} WHERE notable = ?'.format(bf_sel_subdb_internal), (notable,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Song artist' or filter_by_text == 'Song genre' or filter_by_text == 'Studio' or \
				filter_by_text == 'Video footage (single source only)':
			if filter_by_text == 'Video footage (single source only)':
				column_name = 'video_footage'
			else:
				column_name = filter_by_text.lower().replace(' ', '_')
			bf_cursor.execute('SELECT video_id FROM {} WHERE {} = ?'.format(bf_sel_subdb_internal, column_name),
							  (sel_filter,))
			for vidid_tup in bf_cursor.fetchall():
				filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Star rating':
			if sel_filter == 'Unrated or 0.0':
				bf_cursor.execute('SELECT video_id FROM {} WHERE star_rating = "" or star_rating = 0.0'
								  .format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])
			else:
				star_rat_rng = [float(x) for x in sel_filter.split(' - ')]
				bf_cursor.execute('SELECT video_id, star_rating FROM {} WHERE star_rating != ""'
								  .format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					if star_rat_rng[0] <= float(vidid_tup[1]) <= star_rat_rng[1]:
						filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Video footage':
			bf_cursor.execute('SELECT video_id, video_footage FROM {}'.format(bf_sel_subdb_internal))
			for vidid_tup in bf_cursor.fetchall():
				for ftg in vidid_tup[1].split('; '):
					if sel_filter == ftg:
						filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Video length':
			if sel_filter == 'Not specified':
				bf_cursor.execute('SELECT video_id FROM {} WHERE video_length = ""'.format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])

			else:
				bf_cursor.execute('SELECT video_id, video_length FROM {} WHERE video_length != ""'
								  .format(bf_sel_subdb_internal))
				if sel_filter == '420+ sec':
					for vidid_tup in bf_cursor.fetchall():
						if int(vidid_tup[1]) >= 420:
							filtered_vidids_1.append(vidid_tup[0])
				else:
					dur_rng = [int(x) for x in sel_filter[:-4].split(' - ')]
					for vidid_tup in bf_cursor.fetchall():
						if dur_rng[0] <= vidid_tup[1] <= dur_rng[1]:
							filtered_vidids_1.append(vidid_tup[0])

		elif filter_by_text == 'Year released':
			if sel_filter == 'Not specified':
				bf_cursor.execute('SELECT video_id FROM {} WHERE release_date = "" AND release_date_unknown = 0'
								  .format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])
			elif sel_filter == 'Unknown':
				bf_cursor.execute(
					'SELECT video_id FROM {} WHERE release_date_unknown = 1'.format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					filtered_vidids_1.append(vidid_tup[0])
			else:
				bf_cursor.execute('SELECT video_id, release_date FROM {}'.format(bf_sel_subdb_internal))
				for vidid_tup in bf_cursor.fetchall():
					if sel_filter == vidid_tup[1][:4]:
						filtered_vidids_1.append(vidid_tup[0])

		bf_conn.close()
		self.leftSideVidIDs = filtered_vidids_1
		self.populate_table(self.leftSideVidIDs, self.rightSideVidIDs)

	def populate_table(self, inp_vidids_1, inp_vidids_2):
		self.searchTable.setRowCount(0)
		final_vidid_list = list(set(inp_vidids_1) & set(inp_vidids_2))
		sub_db = common_vars.sub_db_lookup()[self.subDBDrop.currentText()]
		pop_table_db_conn = sqlite3.connect(common_vars.video_db())
		pop_table_db_cursor = pop_table_db_conn.cursor()
		pop_table_settings_conn = sqlite3.connect(common_vars.settings_db())
		pop_table_settings_cursor = pop_table_settings_conn.cursor()

		pop_table_settings_cursor.execute('SELECT value FROM search_settings WHERE setting_name = ?', ('view_type',))
		view_type = pop_table_settings_cursor.fetchone()[0]

		pop_table_settings_cursor.execute('SELECT value FROM search_settings WHERE setting_name = ?',
										  ('min_sec_check',))
		min_sec_check = pop_table_settings_cursor.fetchone()[0]

		pop_table_settings_cursor.execute('SELECT field_name_internal, displ_order FROM search_field_lookup WHERE '
										  'visible_in_search_view = 1')
		field_lookup_dict = dict(
			(x[0], x[1] + 3) if x[1] != 0 else (x[0], x[1]) for x in pop_table_settings_cursor.fetchall())

		edit_icon = QtGui.QIcon(getcwd() + '/icons/edit-icon.png')
		watch_icon = QtGui.QIcon(getcwd() + '/icons/play-icon.png')
		delete_icon = QtGui.QIcon(getcwd() + '/icons/delete_icon.png')
		checkbox_empty_icon = QtGui.QIcon(getcwd() + '/icons/checkbox_empty_icon.png')
		checkbox_checked_icon = QtGui.QIcon(getcwd() + '/icons/checkbox_checked_icon.png')

		matching_vids = []
		for vidid in final_vidid_list:
			pop_table_db_cursor.execute('SELECT primary_editor_username FROM {} WHERE video_id = ?'.format(sub_db),
										(vidid,))
			matching_vids.append(pop_table_db_cursor.fetchone())
		matching_vid_check = [x for x in matching_vids if x is not None]

		self.searchTable.setSortingEnabled(False)
		if matching_vid_check:  # If there is at least one result in the sub-db
			if view_type == 'L':
				for row in range(0, len(final_vidid_list)):
					self.searchTable.insertRow(row)
					for field, col in field_lookup_dict.items():
						query = 'SELECT {} FROM {} '.format(field, sub_db)
						pop_table_db_cursor.execute(query + 'WHERE video_id = ?', (final_vidid_list[row],))
						temp_val = pop_table_db_cursor.fetchall()[0][0]

						pop_table_db_cursor.execute('SELECT local_file FROM {} WHERE video_id = ?'.format(sub_db),
													(final_vidid_list[row],))
						loc_file_check = pop_table_db_cursor.fetchall()[0][0]
						if loc_file_check != '':
							loc_file_pop = True
						else:
							loc_file_pop = False

						# Populating edit icon
						edit_icon_item = QtWidgets.QTableWidgetItem()
						edit_icon_item.setIcon(edit_icon)
						edit_icon_to_insert = QtWidgets.QTableWidgetItem(edit_icon_item)
						self.searchTable.setItem(row, 1, edit_icon_to_insert)

						# Populating play local video icon
						if loc_file_pop:
							watch_icon_item = QtWidgets.QTableWidgetItem()
							watch_icon_item.setIcon(watch_icon)
							watch_icon_to_insert = QtWidgets.QTableWidgetItem(watch_icon_item)
							self.searchTable.setItem(row, 2, watch_icon_to_insert)

						# Populating delete icon
						delete_icon_item = QtWidgets.QTableWidgetItem()
						delete_icon_item.setIcon(delete_icon)
						delete_icon_to_insert = QtWidgets.QTableWidgetItem(delete_icon_item)
						self.searchTable.setItem(row, 3, delete_icon_to_insert)

						# Populating table with data from db file
						if temp_val is None or temp_val == '':
							val_to_insert = QtWidgets.QTableWidgetItem('')
						else:
							if field == 'star_rating' or field == 'my_rating' or field == 'play_count' or \
									field == 'sequence':
								val_to_insert = QtWidgets.QTableWidgetItem()
								val_to_insert.setTextAlignment(QtCore.Qt.AlignCenter)
								val_to_insert.setData(QtCore.Qt.DisplayRole, temp_val)
							elif field == 'video_length':
								val_to_insert = QtWidgets.QTableWidgetItem()
								val_to_insert.setTextAlignment(QtCore.Qt.AlignCenter)
								if min_sec_check == '1':
									mod_val = str(int(temp_val) // 60) + ' min ' + str(int(temp_val) % 60) + ' sec'
									val_to_insert.setData(QtCore.Qt.DisplayRole, mod_val)
								else:
									val_to_insert.setData(QtCore.Qt.DisplayRole, temp_val)
							elif field == 'favorite' or field == 'notable':
								check_empty_item = QtWidgets.QTableWidgetItem()
								check_empty_item.setIcon(checkbox_empty_icon)
								check_empty_item_to_insert = QtWidgets.QTableWidgetItem(check_empty_item)

								checked_item = QtWidgets.QTableWidgetItem()
								checked_item.setIcon(checkbox_checked_icon)
								checked_item_to_insert = QtWidgets.QTableWidgetItem(checked_item)

								if temp_val == 0:
									val_to_insert = check_empty_item_to_insert
								else:
									val_to_insert = checked_item_to_insert
							else:
								val_to_insert = QtWidgets.QTableWidgetItem(str(temp_val))

						self.searchTable.setItem(row, col, val_to_insert)

			else:
				for row in range(0, len(final_vidid_list)):
					self.searchTable.insertRow(row)

					v_id = final_vidid_list[row]
					pop_table_db_cursor.execute('SELECT primary_editor_username, video_title FROM {} WHERE video_id = ?'
												.format(sub_db), (v_id,))
					ed_title_tup = pop_table_db_cursor.fetchall()[0]
					ed_title_str = ed_title_tup[0] + ' - ' + ed_title_tup[1]

					for col in range(0, 2):
						v_id_item = QtWidgets.QTableWidgetItem(v_id)
						ed_title_item = QtWidgets.QTableWidgetItem(ed_title_str)
						if col == 0:
							self.searchTable.setItem(row, col, v_id_item)
						else:
							self.searchTable.setItem(row, col, ed_title_item)

		self.searchTable.setSortingEnabled(True)
		if view_type == 'L':
			self.searchTable.sortByColumn(field_lookup_dict['video_title'], QtCore.Qt.AscendingOrder)
			self.searchTable.sortByColumn(field_lookup_dict['primary_editor_username'], QtCore.Qt.AscendingOrder)
		else:
			self.searchTable.sortByColumn(1, QtCore.Qt.AscendingOrder)

		# Populate stats box
		self.numVideosLabel.setText('')
		self.oldestVideoLabel.setText('')
		self.newestVideoLabel.setText('')
		self.avgMyRatingLabel.setText('')
		self.avgStarRatingLabel.setText('')
		self.longestVidLabel.setText('')
		self.shortestVidLabel.setText('')
		self.avgDurationLabel.setText('')

		num_vids = '{:,}'.format(len(final_vidid_list))
		self.numVideosLabel.setText(num_vids)

		all_rel_dates = []
		for v_id in final_vidid_list:
			pop_table_db_cursor.execute('SELECT release_date FROM {} WHERE release_date IS NOT NULL AND video_id = ?'
										.format(sub_db), (v_id,))
			all_rel_dates.append(pop_table_db_cursor.fetchone()[0])
		rel_date_list = [x for x in all_rel_dates if x != '']
		rel_date_list.sort()
		if len(rel_date_list) > 0:
			self.oldestVideoLabel.setText(rel_date_list[0])
			self.newestVideoLabel.setText(rel_date_list[-1])
		else:
			self.oldestVideoLabel.setText('N/A')
			self.newestVideoLabel.setText('N/A')

		my_rating_list = []
		for v_id in final_vidid_list:
			pop_table_db_cursor.execute('SELECT my_rating FROM {} WHERE my_rating IS NOT NULL AND my_rating != "" AND '
										'video_id = ?'.format(sub_db), (v_id,))
			my_rating_list.append(pop_table_db_cursor.fetchone())
		my_rating_list_cleaned = [x[0] for x in my_rating_list if x is not None]
		if len(my_rating_list_cleaned) > 0:
			avg_my_rating = str(round(sum(my_rating_list_cleaned) / len(my_rating_list_cleaned), 2))
		else:
			avg_my_rating = 'N/A'
		self.avgMyRatingLabel.setText(avg_my_rating)

		star_rating_list = []
		for v_id in final_vidid_list:
			pop_table_db_cursor.execute(
				'SELECT star_rating FROM {} WHERE star_rating IS NOT NULL AND star_rating != "" '
				'AND star_rating != 0 AND video_id = ?'.format(sub_db), (v_id,))
			star_rating_list.append(pop_table_db_cursor.fetchone())
		star_rating_list_cleaned = [x[0] for x in star_rating_list if x is not None]
		if len(star_rating_list_cleaned) > 0:
			avg_star_rating = str(round(sum(star_rating_list_cleaned) / len(star_rating_list_cleaned), 2))
		else:
			avg_star_rating = 'N/A'
		self.avgStarRatingLabel.setText(avg_star_rating)

		all_durations = []
		for v_id in final_vidid_list:
			pop_table_db_cursor.execute('SELECT video_length FROM {} WHERE video_length IS NOT NULL AND '
										'video_length != "" AND video_length != 0 AND video_id = ?'.format(sub_db),
										(v_id,))
			all_durations.append(pop_table_db_cursor.fetchone())
		all_durations_cleaned = [x[0] for x in all_durations if x is not None]
		all_durations_cleaned.sort()
		if len(all_durations_cleaned) > 0:
			shortest_duration = str(int(all_durations_cleaned[0] / 60)) + ' min ' + str(
				int(all_durations_cleaned[0] % 60)) + ' sec'
			longest_duration = str(int(all_durations_cleaned[-1] / 60)) + ' min ' + str(
				int(all_durations_cleaned[-1] % 60)) + ' sec'
			avg_duration = str(int(sum(all_durations_cleaned) / len(all_durations_cleaned) / 60)) + ' min ' + \
						   str(int(sum(all_durations_cleaned) / len(all_durations_cleaned) % 60)) + ' sec'
		else:
			shortest_duration = 'N/A'
			longest_duration = 'N/A'
			avg_duration = 'N/A'
		self.shortestVidLabel.setText(shortest_duration)
		self.longestVidLabel.setText(longest_duration)
		self.avgDurationLabel.setText(avg_duration)

		pop_table_db_conn.close()
		pop_table_settings_conn.close()

	def update_col_width(self):
		pass
		# TODO: Write this method (update_col_width)

	def table_cell_clicked(self, row, col, vidid):
		cell_clicked_db_conn = sqlite3.connect(common_vars.video_db())
		cell_clicked_db_cursor = cell_clicked_db_conn.cursor()
		cell_clicked_settings_conn = sqlite3.connect(common_vars.settings_db())
		cell_clicked_settings_cursor = cell_clicked_settings_conn.cursor()
		cell_clicked_settings_cursor.execute('SELECT value FROM search_settings WHERE setting_name = ?', ('view_type',))
		view_type = cell_clicked_settings_cursor.fetchone()[0]
		subdb = common_vars.sub_db_lookup()[self.subDBDrop.currentText()]

		if view_type == 'L':  # For List view
			if col == 1:
				self.edit_entry()

			if col == 2:
				cell_clicked_db_cursor.execute('SELECT local_file FROM {} WHERE video_id = ?'.format(subdb), (vidid,))
				file_path = cell_clicked_db_cursor.fetchone()[0].replace('\\', '/')
				if file_path != '':
					self.play_video(subdb, vidid)
				else:
					no_file_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'No local file specified',
														'You have not specified a local file path for this video. Please\n'
														'go to the video profile to add a local file path.')
					no_file_msg.exec_()

			if col == 3:
				self.delete_video(subdb, vidid)

		else:  # For Detail view
			self.videoFtgListWid.clear()
			vid_dict = common_vars.get_all_vid_info(subdb, vidid)

			if vid_dict['vid_thumb_path'] == '' or not os.path.exists(vid_dict['vid_thumb_path']):
				self.thumbPixmap = QtGui.QPixmap(getcwd() + '\\thumbnails\\no_thumb.jpg')
			else:
				self.thumbPixmap = QtGui.QPixmap(vid_dict['vid_thumb_path'])
			self.thumbLabel.setPixmap(self.thumbPixmap.scaled(self.thumbLabel.size(), QtCore.Qt.KeepAspectRatio))

			self.editButton.setEnabled(True)
			self.editCLButton.setEnabled(True)
			self.copyButton.setEnabled(True)
			self.moveButton.setEnabled(True)
			self.deleteButton.setEnabled(True)
			self.playCountIncreaseBtn.setEnabled(True)
			self.playCountDecreaseBtn.setEnabled(True)

			if vid_dict['local_file'] == '':
				self.viewButton.setDisabled(True)
			else:
				self.viewButton.setEnabled(True)

			if vid_dict['video_youtube_url'] == '':
				self.YTButton.setDisabled(True)
			else:
				self.YTButton.setEnabled(True)

			self.editorVideoTitleLabel.setText('{} - {}'.format(vid_dict['primary_editor_username'],
																vid_dict['video_title']))
			self.dateAddedLabel.setText('Date added:\n{}'.format(vid_dict['date_entered']))
			self.numPlaysLabel.setText('# of plays:\n{}'.format(str(vid_dict['play_count'])))
			self.vidIDLabel.setText('AMV Tracker video ID:\n{}'.format(vidid))
			self.pseudoLabel.setText('Primary editor pseudonym(s): {}'.format(vid_dict['primary_editor_pseudonyms']))
			self.addlEditorsLabel.setText('Additional editors: {}'.format(vid_dict['addl_editors']))
			self.studioLabel.setText('Studio: {}'.format(vid_dict['studio']))

			if vid_dict['release_date_unknown'] == 1:
				rel_date = 'Unknown'
			else:
				rel_date = vid_dict['release_date']
			self.releaseDateLabel.setText('Release date: {}'.format(rel_date))

			if vid_dict['star_rating'] == 0.0 or vid_dict['star_rating'] == '':
				star_icon = 'stars-00.png'
				star_tt = 'No rating'
			else:
				star_tt = str(vid_dict['star_rating'])
				if 0 < vid_dict['star_rating'] <= 0.74:
					star_icon = 'stars-05.png'
				elif 0.74 < vid_dict['star_rating'] <= 1.24:
					star_icon = 'stars-10.png'
				elif 1.24 < vid_dict['star_rating'] <= 1.74:
					star_icon = 'stars-15.png'
				elif 1.74 < vid_dict['star_rating'] <= 2.24:
					star_icon = 'stars-20.png'
				elif 2.24 < vid_dict['star_rating'] <= 2.74:
					star_icon = 'stars-25.png'
				elif 2.74 < vid_dict['star_rating'] <= 3.24:
					star_icon = 'stars-30.png'
				elif 3.24 < vid_dict['star_rating'] <= 3.74:
					star_icon = 'stars-35.png'
				elif 3.74 < vid_dict['star_rating'] <= 4.24:
					star_icon = 'stars-40.png'
				elif 4.24 < vid_dict['star_rating'] <= 4.74:
					star_icon = 'stars-45.png'
				else:
					star_icon = 'stars-50.png'
			self.starPixmap = QtGui.QPixmap(getcwd() + '\\icons\\' + star_icon)
			self.starRatingImg.setPixmap(self.starPixmap.scaled(self.starRatingImg.size(), QtCore.Qt.KeepAspectRatio))
			self.starRatingImg.setToolTip(star_tt)

			if vid_dict['my_rating'] == '':
				my_rating = 'My rating: Not rated'
			else:
				my_rating = 'My rating: {} / 10'.format(str(vid_dict['my_rating']))
			self.myRatingLabel.setText(my_rating)

			if vid_dict['favorite'] == 0:
				fav_box = 'checkbox_empty_icon.png'
			else:
				fav_box = 'checkbox_checked_icon.png'
			self.favPixmap = QtGui.QPixmap(getcwd() + '\\icons\\' + fav_box)
			self.favImg.setPixmap(self.favPixmap.scaled(self.favImg.size(), QtCore.Qt.KeepAspectRatio))
			
			if vid_dict['notable'] == 0:
				notable_box = 'checkbox_empty_icon.png'
			else:
				notable_box = 'checkbox_checked_icon.png'
			self.notablePixmap = QtGui.QPixmap(getcwd() + '\\icons\\' + notable_box)
			self.notableImg.setPixmap(self.notablePixmap.scaled(self.notableImg.size(), QtCore.Qt.KeepAspectRatio))

			if vid_dict['video_length'] == 0 or vid_dict['video_length'] == '':
				vid_len = 'Not specified'
			else:
				vid_len = str(int(vid_dict['video_length'] / 60)) + ' min ' + str(int(vid_dict['video_length'] % 60)) + \
						  ' sec'
			self.durLabel.setText('Video duration: ' + vid_len)

			if vid_dict['song_artist'] == '':
				song_artist = 'Not specified'
			else:
				song_artist = vid_dict['song_artist']
			self.artistLabel.setText('Song artist: {}'.format(song_artist))

			if vid_dict['song_title'] == '':
				song_title = 'Not specified'
			else:
				song_title = vid_dict['song_title']
			self.songLabel.setText('Song title: {}'.format(song_title))

			if vid_dict['song_genre'] == '':
				song_genre = 'Not specified'
			else:
				song_genre = vid_dict['song_genre']
			self.songGenreLabel.setText('Song genre: {}'.format(song_genre))

			if vid_dict['video_footage'] == '':
				ftg_list = []
			else:
				ftg_list = vid_dict['video_footage'].split('; ')

			for ftg in ftg_list:
				self.videoFtgListWid.addItem(ftg)

			cell_clicked_settings_cursor.execute('SELECT field_name_internal, field_name_display FROM '
												 'search_field_lookup WHERE in_use = 1 AND tag_field = 1')
			tags_tup_list = cell_clicked_settings_cursor.fetchall()

			tags_list = []
			for tup in tags_tup_list:
				cell_clicked_db_cursor.execute('SELECT {} FROM {} WHERE video_id = ?'.format(tup[0], subdb), (vidid,))
				tags_list.append((tup[1], cell_clicked_db_cursor.fetchone()[0]))
			tag_wid_list = [self.tags1Label, self.tags2Label, self.tags3Label, self.tags4Label, self.tags5Label,
							self.tags6Label]

			for wid in tag_wid_list:
				wid.hide()

			for i in range(len(tags_list)):
				"""text_len = len(tags_list[i][0][7:]) + len(tags_list[i][1]) + 2
				num_rows = int(text_len / 45) + 1
				print(tags_list[i][0][7:], num_rows)"""
				if tags_list[i][1] is not None:
					tag_wid_list[i].setText('<u>{}</u>'.format(tags_list[i][0][7:]) + ': ' + tags_list[i][1])
					tag_wid_list[i].show()

			self.contestsText.setText(vid_dict['contests_entered'])
			self.awardsText.setText(vid_dict['awards_won'])
			self.vidDescText.setText(vid_dict['video_description'])
			self.commentsText.setText(vid_dict['comments'])

			self.ytLinkLabel.clear()
			if vid_dict['video_youtube_url'] != '' and vid_dict['video_youtube_url'] is not None:
				self.ytLinkLabel.show()
				self.ytLinkLabel.setText(
					'<a href="{}">YouTube</a>'.format(vid_dict['video_youtube_url']))
			else:
				self.ytLinkLabel.hide()

			self.amvOrgLinkLabel.clear()
			if vid_dict['video_org_url'] != '' and vid_dict['video_org_url'] is not None:
				self.amvOrgLinkLabel.show()
				self.amvOrgLinkLabel.setText('<a href="{}">a-m-v.org</a>'.format(vid_dict['video_org_url']))
			else:
				self.amvOrgLinkLabel.hide()

			self.amvnewsLinkLabel.clear()
			if vid_dict['video_amvnews_url'] != '' and vid_dict['video_amvnews_url'] is not None:
				self.amvnewsLinkLabel.show()
				self.amvnewsLinkLabel.setText('<a href="{}">amvnews</a>'.format(vid_dict['video_amvnews_url']))
			else:
				self.amvnewsLinkLabel.hide()

			self.otherLinkLabel.clear()
			if vid_dict['video_other_url'] != '' and vid_dict['video_other_url'] is not None:
				self.otherLinkLabel.show()
				self.otherLinkLabel.setText(
					'<a href="{}">Other</a>'.format(vid_dict['video_other_url']))
			else:
				self.otherLinkLabel.hide()

			self.ytChannelLinkLabel.clear()
			if vid_dict['editor_youtube_channel_url'] != '' and vid_dict['editor_youtube_channel_url'] is not None:
				self.ytChannelLinkLabel.show()
				self.ytChannelLinkLabel.setText(
					'<a href="{}">YouTube</a>'.format(vid_dict['editor_youtube_channel_url']))
			else:
				self.ytChannelLinkLabel.hide()

			self.amvOrgProfileLinkLabel.clear()
			if vid_dict['editor_org_profile_url'] != '' and vid_dict['editor_org_profile_url'] is not None:
				self.amvOrgProfileLinkLabel.show()
				self.amvOrgProfileLinkLabel.setText(
					'<a href="{}">a-m-v.org</a>'.format(vid_dict['editor_org_profile_url']))
			else:
				self.amvOrgProfileLinkLabel.hide()

			self.amvnewsProfileLinkLabel.clear()
			if vid_dict['editor_amvnews_profile_url'] != '' and vid_dict['editor_amvnews_profile_url'] is not None:
				self.amvnewsProfileLinkLabel.show()
				self.amvnewsProfileLinkLabel.setText(
					'<a href="{}">amvnews</a>'.format(vid_dict['editor_amvnews_profile_url']))
			else:
				self.amvnewsProfileLinkLabel.hide()

			self.otherProfileLinkLabel.clear()
			if vid_dict['editor_other_profile_url'] != '' and vid_dict['editor_other_profile_url'] is not None:
				self.otherProfileLinkLabel.show()
				self.otherProfileLinkLabel.setText(
					'<a href="{}">Other</a>'.format(vid_dict['editor_other_profile_url']))
			else:
				self.otherProfileLinkLabel.hide()

		cell_clicked_db_conn.commit()
		cell_clicked_db_conn.close()

	def edit_entry(self):
		vidid = self.searchTable.item(self.searchTable.currentRow(), 0).text()
		subdb = common_vars.sub_db_lookup()[self.subDBDrop.currentText()]

		edit_screen = entry_screen.VideoEntry(edit_entry=True, inp_vidid=vidid, inp_subdb=subdb)
		edit_screen.show()

	def play_video(self, subdb, vidid):
		play_vid_conn = sqlite3.connect(common_vars.video_db())
		play_vid_cursor = play_vid_conn.cursor()

		play_vid_cursor.execute('SELECT local_file FROM {} WHERE video_id = ?'.format(subdb), (vidid,))
		f_path = play_vid_cursor.fetchone()[0]

		try:
			startfile(f_path)
			play_vid_cursor.execute('SELECT play_count FROM {} WHERE video_id = ?'.format(subdb),
										   (vidid,))
			curr_play_ct = play_vid_cursor.fetchone()[0]
			play_vid_cursor.execute('UPDATE {} SET play_count = ? WHERE video_id = ?'.format(subdb),
										   (curr_play_ct + 1, vidid))
			self.numPlaysLabel.setText('# of plays:\n{}'.format(str(curr_play_ct + 1)))
			
		except:
			file_not_found_msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'File not found',
													   'Local file not found. Please check the file path in the\n'
													   'video\'s AMV Tracker profile.')
			file_not_found_msg.exec_()

		play_vid_conn.commit()
		play_vid_conn.close()

	def go_to_link(self, subdb, vidid, field):
		go_to_link_conn = sqlite3.connect(common_vars.video_db())
		go_to_link_cursor = go_to_link_conn.cursor()

		go_to_link_cursor.execute('SELECT {} FROM {} WHERE video_id = ?'.format(field, subdb), (vidid,))
		url = go_to_link_cursor.fetchone()[0]

		if url != '' and url is not None:
			webbrowser.open(url)
		else:
			no_url_error = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'No URL',
												 'The requested URL has not been provided for this video. Please\n'
												 'edit the video information and add the URL.')
			no_url_error.exec_()

		go_to_link_conn.close()

	def add_to_cust_list(self, vidid):
		self.add_win = add_to_cl_window.AddToCustList(vidid)
		self.add_win.show()

	def copy_btn_pushed(self, vidid, subdb, copy):
		self.copy_win = copy_move.CopyMoveWindow(vidid, subdb, copy=copy)
		self.copy_win.show()
		self.copy_win.move_completed.connect(lambda: self.delete_video(common_vars.sub_db_lookup()[subdb], vidid,
																	   bypass_warning=True))

	def delete_video(self, subdb, vidid, bypass_warning=False):
		subdb_friendly = common_vars.sub_db_lookup(reverse=True)[subdb]
		del_vid_conn = sqlite3.connect(common_vars.video_db())
		del_vid_cursor = del_vid_conn.cursor()

		if not bypass_warning:
			delete_warning = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Delete video',
												   'Ok to remove video from sub-DB [{}]?\nThis cannot be undone.'.format(subdb_friendly),
												   QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
			response = delete_warning.exec_()
		else:
			response = QtWidgets.QMessageBox.Yes

		if response == QtWidgets.QMessageBox.Yes:
			# Delete row from SQLite table
			del_vid_cursor.execute('DELETE FROM {} WHERE video_id = ?'.format(subdb), (vidid,))

			# Delete vidid from Custom Lists
			vidid_exists_elsewhere = False
			for k, v in common_vars.sub_db_lookup().items():
				if v != subdb:
					del_vid_cursor.execute('SELECT video_title FROM {} WHERE video_id = ?'.format(v), (vidid,))
					if del_vid_cursor.fetchone() is not None:
						vidid_exists_elsewhere = True

			if not vidid_exists_elsewhere:
				del_vid_cursor.execute('SELECT cl_id, vid_ids FROM custom_lists WHERE vid_ids LIKE "%{}%"'.format(vidid))
				cl_tups = del_vid_cursor.fetchall()
				for tup in cl_tups:
					id_list = tup[1].split('; ')
					id_list.remove(vidid)
					id_str = '; '.join(id_list)
					del_vid_cursor.execute('UPDATE custom_lists SET vid_ids = ? WHERE cl_id = ?', (id_str, tup[0]))
					del_vid_conn.commit()

			# Remove thumbnail if it is not in use in another sub-db
			thumb_file = getcwd() + '\\thumbnails\\{}.jpg'.format(vidid)
			if not vidid_exists_elsewhere and os.path.exists(thumb_file):
				os.remove(thumb_file)

			del_vid_conn.commit()

			if not bypass_warning:
				vid_deleted = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Video deleted',
													'This video has been removed from {}.'.format(subdb_friendly))
				vid_deleted.exec_()

			if self.basicFilterListWid.selectedItems():
				sel_item_ind = self.basicFilterListWid.currentRow()
			else:
				sel_item_ind = None
			self.init_window(sel_filters=[self.subDBDrop.currentIndex(), self.basicFiltersDrop.currentIndex(),
										  sel_item_ind])

		del_vid_conn.close()

	def change_play_count(self, dir):
		play_count_conn = sqlite3.connect(common_vars.video_db())
		play_count_cursor = play_count_conn.cursor()
		subdb = common_vars.sub_db_lookup()[self.subDBDrop.currentText()]
		vidid = self.searchTable.item(self.searchTable.currentRow(), 0).text()

		play_count_cursor.execute('SELECT play_count FROM {} WHERE video_id = ?'.format(subdb), (vidid,))
		new_play_count = play_count_cursor.fetchone()[0] + dir

		if new_play_count < 0:
			new_play_count = 0

		play_count_cursor.execute('UPDATE {} SET play_count = ? WHERE video_id = ?'.format(subdb),
								  (new_play_count, vidid))
		self.numPlaysLabel.setText('# of plays:\n{}'.format(str(new_play_count)))

		play_count_conn.commit()
		play_count_conn.close()
