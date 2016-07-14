from PyQt4.QtWebKit import *
from qgis.core import QgsNetworkAccessManager


class WebPage(QWebPage):
    def __init__(self, logger=None, parent=None):
        super(WebPage, self).__init__(parent)

        # add QgsNetworkAccessManager for proxy
        self.setNetworkAccessManager(QgsNetworkAccessManager.instance())
