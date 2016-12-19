# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoscopioSearchDialog
                                 A QGIS plugin
 desc
                             -------------------
        begin                : 2016-07-14
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Walter lorenzetti
        email                : lorenzetti@gis3w.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic, QtCore
from components.webpage import WebPage

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geoscopio_search_dialog_base.ui'))


class GeoscopioSearchDialog(QtGui.QDialog, FORM_CLASS):

    resized_ev = QtCore.pyqtSignal(int, name='resized')
    closed_ev = QtCore.pyqtSignal(int, name='closed')

    def __init__(self, parent=None):
        """Constructor."""
        super(GeoscopioSearchDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.WEB.setPage(WebPage())
        self.setWindowFlags(QtCore.Qt.Window)

    def resizeEvent(self, event):
        self.resized_ev.emit(1)
        QtGui.QDialog.resizeEvent(self, event)

    def closeEvent(self, event):
        self.closed_ev.emit(1)
        QtGui.QDialog.closeEvent(self, event)
