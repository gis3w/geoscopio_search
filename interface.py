"""
/***************************************************************************
 JsToQgis
                                 A QGIS plugin
 Porting qgis function to javascript and vice versa
                              -------------------
        begin                : 2014-06-27
        copyright            : (C) 2014-2016 by Walter Lorenzetti - Gis3W
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

import PyQt4
from PyQt4.QtCore import QVariant,QObject,pyqtSlot, pyqtRemoveInputHook
from PyQt4.QtGui import QColor
from qgis.core import *
from qgis.gui import *
import json
import urlparse
from utils import remove_tags

TYPE_MAP = {
    QGis.WKBPoint: 'Point',
    QGis.WKBPoint25D: 'Point',
    QGis.WKBLineString: 'LineString',
    QGis.WKBLineString25D: 'LineString',
    QGis.WKBPolygon: 'Polygon',
    QGis.WKBPolygon25D: 'Polygon',
    QGis.WKBMultiPoint: 'MultiPoint',
    QGis.WKBMultiLineString: 'MultiLineString',
    QGis.WKBMultiLineString25D: 'MultiLineString',
    QGis.WKBMultiPolygon: 'MultiPolygon',
    QGis.WKBMultiPolygon25D: 'MultiPolygon'
}

debug = True

def logQgisConsole(msg,force=False):
    if debug == True or force:
        QgsMessageLog.logMessage(msg,"Debug JSTOQGIS")


class JsToQgis_Interface(QObject):
    
    interchange = {}
    errormessages = {}
    
    def __init__(self,parent=None):
        super(JsToQgis_Interface, self).__init__(parent)
        self.iface = parent
        self.mapCanvas = self.iface.mapCanvas() 
    
    @pyqtSlot(str, result=str)
    def getErrorMessages(self, method):
        '''
        Return error message from self.errormessages dict
        '''
        if method in self.errormessages.keys():
            toRet = json.dumps(self.errormessages[method]);
        else:
            toRet =  "[\"No error message for method '%s'\"]" % method
        return toRet
        
    def setErrorMessages(self, method, error):
        '''
        Set error message for a method
        '''
        if method not in self.errormessages.keys():
            self.errormessages[method] = []
        
        self.errormessages[method].append(error)
        
    @pyqtSlot(result=str)
    def getQgisVersion(self):
        '''
        Return current Qgis Version
        '''
        return QGis.QGIS_VERSION;
    
    @pyqtSlot(result=str)
    def getLayersData(self):
        '''
        Return data from current QGIS registry layers
        '''
        qmlr = QgsMapLayerRegistry.instance()
        res = []
        print qmlr.mapLayers().items()
        for id,l in qmlr.mapLayers().items():
          
            lObj = {}
            lObj['id'] = id
            lObj['name'] = l.name()
            lObj['originalName'] = l.originalName()
            
            lObj['source'] = l.source()
            lObj['type'] = l.type()
            lObj['provider'] = l.providerType()
            uri = QgsDataSourceURI()
            uri.setEncodedUri(l.source())
            if lObj['provider'] == 'wms':
                lObj['url'] = uri.param('url')
                lObj['version'] = uri.param('version')
                lObj['layers'] = uri.param('layers')
                lObj['style'] = uri.param('style')
                lObj['format'] = uri.param('format')
                lObj['crs'] = uri.param('crs')
            elif lObj['provider'] == 'WFS':
                
                up = urlparse.parse_qsl(lObj['source'])
                cont = 0
                for i,t in up:
                    if cont == 0:
                        lObj['url'] = i+'='+t
                    else:
                        lObj[i] = t
                    cont += 1
            else:
                pass
            ext = l.extent()
            lObj['extent'] = [ext.xMinimum(),ext.yMinimum(),ext.xMaximum(),ext.yMaximum()]
            res.append(lObj)
        return json.dumps(res)

    @pyqtSlot(str, str, result=str)
    def getLayer(self, layerid, epsg):
        """
        Get vector layer as geojson
        """

        qmlr = QgsMapLayerRegistry.instance()
        layer = qmlr.mapLayer(layerid)

        jsCrs = QgsCoordinateReferenceSystem(int(epsg), QgsCoordinateReferenceSystem.EpsgCrsId)

        if layer.providerType() not in ['ogc', 'postgres']:
            self.setErrorMessages('getLayer', 'At the moment only ogc provider type layers')
            return False

        error = QgsVectorFileWriter.writeAsVectorFormat(layer, "/tmp/layer_jstoqgis", "utf-8", jsCrs, "GeoJSON")

        if error == QgsVectorFileWriter.NoError:
            file = open("/tmp/layer_jstoqgis.geojson", 'r')
            GeoJSON = file.read()
            file.close()
            return GeoJSON
        else:
            self.setErrorMessages('getLayer', 'Error to export to GeoJSON:{}'.format(error))
            return False
        
    @pyqtSlot(str, str, str)
    def setInterChange(self, field, type, value):
        '''
        A private method for to pass data from QGIS to Js
        '''
        logQgisConsole(' '.join([field,type,value]),True)
        def integer(value):
           return int(value)
        def string(value):
           return str(value)
        def jsoner(value):
           return json.loads(value)
        
        switch = {
                   'int':integer,
                   'str': string,
                   'json': jsoner
                   }
       
        self.interchange[field] = switch[type](value)
        
        
    @pyqtSlot(float, float, float, float, str)
    def zoomToExtent(self, minx, miny, maxx, maxy, epsg):
        '''
        Set extent of qgis map view
        '''
        print 'passa'
        if(not self.mapCanvas):
            print self.iface
            return
        
        jsCrs = QgsCoordinateReferenceSystem(int(epsg),QgsCoordinateReferenceSystem.EpsgCrsId)
        QgisCrs = self.mapCanvas.mapSettings().destinationCrs()
        xform = QgsCoordinateTransform(jsCrs, QgisCrs)
        
        logQgisConsole('minx: ' + str(minx) + '| miny: ' + str(miny) + '| maxx: ' + str(maxx) + '| maxy: ' + str(maxy))
        logQgisConsole(str(type(self.mapCanvas)))
        self.mapCanvas.setExtent(xform.transformBoundingBox(QgsRectangle (minx, miny, maxx, maxy)))
        self.mapCanvas.refresh()
        
    @pyqtSlot(float, float, float, str)
    def zoomToPoint(self, x, y, scale, epsg):
        '''
        Set the center to the map to x,y value and to scale value
        '''
        if(not self.mapCanvas):
            print self.iface
            return
        
        jsCrs = QgsCoordinateReferenceSystem(int(epsg),QgsCoordinateReferenceSystem.EpsgCrsId)
        QgisCrs = self.mapCanvas.mapSettings().destinationCrs()
        xform = QgsCoordinateTransform(jsCrs, QgisCrs)
        
        center = QgsPoint(x,y)
        center = xform.transform(center)
        
        ct = self.mapCanvas.getCoordinateTransform()
        x,y = map(int,list(ct.transform(center.x(),center.y())))
        
        logQgisConsole('ZoomToPoint: x = '+str(x)+'| y = '+str(y))

        self.mapCanvas.zoomWithCenter(x,y,False)
        self.mapCanvas.zoomScale(scale)
        #self.mapCanvas.refresh()
        
    @pyqtSlot(float)
    def zoomToScale(self, scale):
        self.mapCanvas.zoomScale(scale)
        
    @pyqtSlot()
    def zoomIn(self):
        '''
        Execute simple ZoomIn of Qgis API
        '''
        if(not self.mapCanvas):
            print self.iface
            return None
        self.mapCanvas.zoomIn()
        
    @pyqtSlot()
    def zoomOut(self):
        '''
        Execute simple ZoomOut of Qgis API
        '''
        if(not self.mapCanvas):
            print self.iface
            return
        self.mapCanvas.zoomOut()
        
    @pyqtSlot(result=str)
    def getCRS(self):
        '''
        Return current QGIS CRS
        '''
        return self.mapCanvas.mapSettings().destinationCrs().authid()
    
    @pyqtSlot(result=float)
    def getCurrentScale(self):
        '''
        Return current QGIS Map Scale
        '''
        return self.mapCanvas.scale()
    
    @pyqtSlot(float)
    def setScale(self,scale):
        '''
        Set the QGIS Map scale value
        '''
        return self.mapCanvas.zoomScale(scale)

    @pyqtSlot(str)
    def setCRS(self, epsg):
        '''
        Set QGIS current CRS and try to reproject all layers on map
        '''

        #if not self.mapCanvas.hasCrsTransformEnabled():
            #self.mapCanvas.mapSettings().setProjectionsEnabled(True)
        # check if current espg map is different from those submit
        crs = QgsCoordinateReferenceSystem(int(epsg),QgsCoordinateReferenceSystem.EpsgCrsId)
        
        #mapSettings = self.mapCanvas.mapSettings()
        #mapSettings.setDestinationCrs(crs)
        #mapSettings.setMapUnits( crs.mapUnits() if crs.mapUnits() != QGis.UnknownUnit else QGis.Meters )
        self.mapCanvas.setCrsTransformEnabled(True)
        self.mapCanvas.setDestinationCrs(crs)

        self.mapCanvas.refresh()
        
    @pyqtSlot(str, str, str, str, str, str)
    def addWMSLayer(self,legendName,url,layers,format='image/png',crs=None,style=''):
        '''
        Add a WMS layer to QGIS Map registry and show on map
        '''
        
        if not crs:
            crs = self.getCRS()
        
        uri = QgsDataSourceURI()
        uri.setParam("url", url)
        uri.setParamList("layers", layers.split(','))
        uri.setParam("format", format)
        uri.setParam("crs", crs)
        uri.setParam("styles", style)
    
        logQgisConsole(str(uri.encodedUri()))
        
        
        WMS = QgsRasterLayer(str(uri.encodedUri()),legendName,'wms')
        if not WMS.isValid():
            logQgisConsole("Layer failed to load!",True)
            logQgisConsole(WMS.error().summary(),True)
            self.setErrorMessages('addWMSLayer', 'Layer failed to load: '+ WMS.error().summary())
            return False
        QgsMapLayerRegistry.instance().addMapLayer(WMS)
        return True
    
    @pyqtSlot(float, float, str, str, result=str)
    def identifyLayer(self, lon, lat, epsg, layerId):
        '''
        Execute a simple indentify point action on layerId(QGIS) passed and return results of operation
        '''
        # activation layer
        
        jsCrs = QgsCoordinateReferenceSystem(int(epsg),QgsCoordinateReferenceSystem.EpsgCrsId)
        QgisCrs = self.mapCanvas.mapSettings().destinationCrs()
        xform = QgsCoordinateTransform(jsCrs, QgisCrs)
        
        point = QgsPoint(lon,lat)
        point = xform.transform(point)
       
        mapLayer = QgsMapLayerRegistry.instance().mapLayer(layerId)
        logQgisConsole(layerId)
        ci = QgsMapToolIdentify(self.mapCanvas)
        ci.activate()
        
        logQgisConsole('IdentifyLayer '+' X='+ str(point.x()) +'Y='+str(point.y()) )
        
        #transform lon lat to x,y mousepofition
        ct = self.mapCanvas.getCoordinateTransform()
        x,y = map(int,list(ct.transform(point.x(),point.y())))
        
        results = ci.identify(x, y,[mapLayer])        
        ci.deactivate()
        if not results:
            return '[]'
        
        print results;
        
        res = []
        for r in results:
            lObj = {}
            lObj['mLabel'] = r.mLabel
            lObj['mFeature'] = json.loads(r.mFeature.geometry().exportToGeoJSON())
            # adding properties feature
            attrs = r.mFeature.attributes()
            fields = r.mFeature.fields()
            properties = {}
            for idx,fld in enumerate(fields.toList()):
                value = attrs[idx]
                if type(attrs[idx]) == PyQt4.QtCore.QPyNullVariant :
                    value = None
                properties[fld.name()] = value
            lObj['mFeature']['properties'] = properties
            lObj['mAttributes'] = r.mAttributes
            logQgisConsole(str(x)+' '+str(y))
            res.append(lObj)
        return json.dumps(res)
    
    @pyqtSlot(str, str, str, str, bool, result=str)
    def addWKTLayer(self, WKT, legendName, epsg, fields, originalcrs=True):
        '''
        Build a Vector layer from WKT string and adds it to the map canvas
        '''

        # strip html tags
        legendName = remove_tags(legendName)

        # build the geometry
        geom = QgsGeometry.fromWkt(WKT)
        if not isinstance(geom,QgsGeometry):
            self.setErrorMessages('addWKTLayer', 'Check WKT string, probably is not correct!')
            return False

        # trasform geometry id originalcrs is set to False
        if not originalcrs:
            currentCrs = self.mapCanvas.mapSettings().destinationCrs()
            trasform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(int(epsg[5:])), currentCrs)
            geom.transform(trasform)
            epsg = str(currentCrs.authid())
        # check the type
        geomType = geom.type()
        if geomType in (QGis.UnknownGeometry,QGis.NoGeometry):
            self.setErrorMessages('addWKTLayer', 'Qgis said that your WKT is not a valid geometry or is a Unknown geometry')
            return False
        
        # just instance QgsRubberBand or a Vertex if is a polygon / line or a point
        # get the geometry by ogr
        # build fields parameter
        fieldsAttr = json.loads(fields) 
        
        fieldsAttrList = []
        for k,v in fieldsAttr.items():
            if type(v) == str or type(v) == unicode:
                fieldsAttrList.append(k + ':string')
            elif type(v) == float:
                fieldsAttrList.append(k + ':double')
            elif type(v) == int:
                fieldsAttrList.append(k + ':integer')
                
        uriVLayer = TYPE_MAP[geom.wkbType()] + '?crs=' + epsg + '&field=' + '&field='.join(fieldsAttrList)
        logQgisConsole(uriVLayer)
        VLayer = QgsVectorLayer(uriVLayer, legendName, "memory")
        pr = VLayer.dataProvider()
        seg = QgsFeature()
        layerFields = pr.fields()
        seg.setFields(layerFields)
        for k,v in fieldsAttr.items():
            seg.setAttribute(k, v)
        seg.setGeometry(geom)
        pr.addFeatures([seg])
        VLayer.updateExtents() 

        QgsMapLayerRegistry.instance().addMapLayers([VLayer])
        return VLayer.id()
        


class QgisToJs_interface(QObject):
    
    def __init__(self,iface,webview):
        super(QgisToJs_interface, self).__init__(iface)
        self.iface = iface
        self.webview = webview
        
    @pyqtSlot()
    def ZoomToExtent(self):
        ext = self.iface.mapCanvas().extent()
        extent = str(ext.xMinimum()) + "," + str(ext.yMinimum()) + "," + str(ext.xMaximum()) + "," + str(ext.yMaximum())
        cmd = "QJ.ZoomToExtent(" + extent + ")"
        self.webview.WEB.page().mainFrame().evaluateJavaScript(cmd)
        logQgisConsole("EXEC QgisToJs::ZoomToExtent")
        
    @pyqtSlot()
    def ZoomToPoint(self):
        ext = self.iface.mapCanvas().extent()
        extent = str(ext.xMinimum()) + "," + str(ext.yMinimum()) + "," + str(ext.xMaximum()) + "," + str(ext.yMaximum())
        cmd = "QJ.ZoomToExtent(" + extent + ")"
        self.webview.WEB.page().mainFrame().evaluateJavaScript(cmd)
        logQgisConsole("EXEC QgisToJs::ZoomToExtent")
       
    @pyqtSlot() 
    def GetLayersData(self):
        cmd = "QJ.GetLayersData()"
        self.webview.WEB.page().mainFrame().evaluateJavaScript(cmd)
        logQgisConsole("EXEC QgisToJs::GetLayersData")
        
    @pyqtSlot() 
    def GetExtent(self):
        cmd = "QJ.GetExtent()"
        self.webview.WEB.page().mainFrame().evaluateJavaScript(cmd)
        logQgisConsole("EXEC QgisToJs::GeExtent")
        
    @pyqtSlot() 
    def ZoomIn(self):
        cmd = "QJ.ZoomIn()"
        self.webview.WEB.page().mainFrame().evaluateJavaScript(cmd)
        logQgisConsole("EXEC QgisToJs::ZoomIn")
        
    @pyqtSlot() 
    def ZoomOut(self):
        cmd = "QJ.ZoomOut()"
        self.webview.WEB.page().mainFrame().evaluateJavaScript(cmd)
        logQgisConsole("EXEC QgisToJs::ZoomOut")
        
        
        #self.webviewtest.WEB.page().mainFrame().evaluateJavaScript("QJ.ZoomToExtent(" + extent + ")")
