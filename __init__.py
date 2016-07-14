# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoscopioSearch
                                 A QGIS plugin
 desc
                             -------------------
        begin                : 2016-07-14
        copyright            : (C) 2016 by Walter lorenzetti
        email                : lorenzetti@gis3w.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GeoscopioSearch class from file GeoscopioSearch.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geoscopio_search import GeoscopioSearch
    return GeoscopioSearch(iface)
