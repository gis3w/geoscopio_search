"""
/***************************************************************************
 GeoscopioSearch

 This plugin is for Geoscopio users, searching on a Geoscopio form search,
 the results can be added to qgis canvas map. Geoscopio is a service of
 Regione Toscana (Italy authority)
 http://www.regione.toscana.it/-/geoscopio

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

from PyQt4.QtWebKit import QWebPage
from qgis.core import QgsNetworkAccessManager


class WebPage(QWebPage):
    """
    Extention of QWebPage class to add web proxy qgis manager
    """
    def __init__(self, parent=None):
        super(WebPage, self).__init__(parent)

        # add QgsNetworkAccessManager for proxy
        self.setNetworkAccessManager(QgsNetworkAccessManager.instance())
