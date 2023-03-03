from PySide6.QtWidgets import QWidget, QSizePolicy, QApplication, QVBoxLayout, QGroupBox, QRadioButton, QPushButton, QHBoxLayout, QScrollArea, QLabel

from PySide6.QtGui import QImage, QLinearGradient, QPixmap, QPolygonF, QPainter, QBrush, QColor, QTextDocument, QGradient, QPainterPath, QPen, QTransform, QConicalGradient, QRadialGradient, QFont
from PySide6.QtCore import  QPointF, Qt, Signal,QSize, QLineF, QFile, QSize, QTimer, QCoreApplication
from PySide6.QtOpenGL import QOpenGLPaintDevice
from imports import *
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))    
sys.path.append(os.path.join("\\".join(os.path.dirname(__file__).split("\\")[:-1]), '..'))
sys.path.append(os.path.join("\\".join(os.path.dirname(__file__).split("\\")[:-2]), '..'))
from hoverpoints import HoverPoints
from arthurstyle import ArthurStyle




class ShadeWidget(QWidget):
    ShadeType = 0
    RedShade = 1
    GreenShade = 2
    BlueShade = 3
    ARGBShade = 4
    colorsChanged = Signal()

    
    def __init__(self, type, parent=None):
        super().__init__(parent)

        self.m_shade_type = type
        self.m_shade = QImage()
        self.m_hoverPoints = HoverPoints(self, self.m_shade_type)
        self.m_alpha_gradient = QLinearGradient(0, 0, 0, 0)

        if self.m_shade_type == self.ARGBShade:
            self.pm = QPixmap(20, 20)
            self.pmp = QPainter(self.pm)
            self.pmp.fillRect(0, 0, 10, 10, Qt.lightGray)
            self.pmp.fillRect(10, 10, 10, 10, Qt.lightGray)
            self.pmp.fillRect(0, 10, 10, 10, Qt.darkGray)
            self.pmp.fillRect(10, 0, 10, 10, Qt.darkGray)
            self.pmp.end()
            pal = self.palette()
            pal.setBrush(self.backgroundRole(), QBrush(self.pm))
            self.setAutoFillBackground(True)
            self.setPalette(pal)           
            
        else:
            self.setAttribute(Qt.WA_OpaquePaintEvent)

        points = QPolygonF()
        points.append(QPointF(0, self.sizeHint().height()))
        points.append(QPointF(self.sizeHint().width(), 0))

        self.m_hoverPoints = HoverPoints(self, HoverPoints.ShapeType.CircleShape)
        self.m_hoverPoints.setPoints(points)
        self.m_hoverPoints.setPointLock(0, HoverPoints.LockType.LockToLeft)
        self.m_hoverPoints.setPointLock(1, HoverPoints.LockType.LockToRight)
        self.m_hoverPoints.setSortType(HoverPoints.SortType.XSort)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.m_hoverPoints.pointsChanged["QPolygonF"].connect(self.colorsChanged)
        
    def points(self):        
        
        return self.m_hoverPoints.points()

    def colorAt(self, x):

        self.generateShade()

        pts = self.m_hoverPoints.points()

        for i in range(pts.size()):
            if pts.at(i - 1).x() <= x and pts.at(i).x() >= x:
                l = QLineF(pts.at(i - 1), pts.at(i))
                if not l.dx():
                    continue
                l.setLength(l.length() * ((x - l.x1()) / l.dx()))
                return self.m_shade.pixel(round(min(l.x2(), (self.m_shade.width() -1) )),
                                          round(min(l.y2(), (self.m_shade.height() - 1))))
            
        return 0
        
        

    def setGradientStops(self, stops):
        #Alpha値のみ。

        if self.m_shade_type == self.ARGBShade:
            self.m_alpha_gradient = QLinearGradient(0, 0, self.width(), 0)

            for stop in stops:
                c = stop[1]
                self.m_alpha_gradient.setColorAt(stop[0], QColor(c.red(), c.green(), c.blue()))

            self.m_shade = QImage()
            self.generateShade()
            self.update()

    def paintEvent(self, event):

        self.generateShade()

        p = QPainter(self)
        p.drawImage(0, 0, self.m_shade)
        
        p.setPen(QColor(146, 146, 146))
        p.drawRect(0, 0, self.width() - 1, self.height() - 1)

        p.end()
    
    def sizeHint(self):

        return QSize(150, 40)

    

    def hoverPoints(self):


        return self.m_hoverPoints

    

    
    

    

    def generateShade(self):

        #Widgetをそれぞれ塗りつぶす

        if self.m_shade.isNull() or self.m_shade.size() != self.size():

            if self.m_shade_type == self.ARGBShade:
                

                self.m_shade = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
                self.m_shade.fill(0)

                p = QPainter(self.m_shade)
                p.fillRect(self.rect(), self.m_alpha_gradient)

                p.setCompositionMode(QPainter.CompositionMode_DestinationIn)
                fade = QLinearGradient(0, 0, 0, self.height())
                fade.setColorAt(0, QColor(0, 0, 0, 255))
                fade.setColorAt(1, QColor(0, 0, 0, 0))
                p.fillRect(self.rect(), fade)

            else:
                self.m_shade = QImage(self.size(), QImage.Format_RGB32)
                shade = QLinearGradient(0, 0, 0, self.height())
                shade.setColorAt(1, Qt.black)

                if self.m_shade_type == self.RedShade:
                    shade.setColorAt(0, Qt.red)

                elif self.m_shade_type == self.GreenShade:
                    shade.setColorAt(0, Qt.green)

                else:
                    shade.setColorAt(0, Qt.blue)

                p = QPainter(self.m_shade)
                p.fillRect(self.rect(), shade)


class GradientEditor(QWidget):
 
    gradientStopsChanged = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        vbox = QVBoxLayout(self)
        vbox.setSpacing(1)
        vbox.setContentsMargins(1, 1, 1, 1)

        self.m_red_shade = ShadeWidget(ShadeWidget.RedShade, self)
        self.m_green_shade = ShadeWidget(ShadeWidget.GreenShade, self)
        self.m_blue_shade = ShadeWidget(ShadeWidget.BlueShade, self)
        self.m_alpha_shade = ShadeWidget(ShadeWidget.ARGBShade, self)

        vbox.addWidget(self.m_red_shade)
        vbox.addWidget(self.m_green_shade)
        vbox.addWidget(self.m_blue_shade)
        vbox.addWidget(self.m_alpha_shade)

        self.m_red_shade.colorsChanged.connect(self.pointsUpdated)
        self.m_green_shade.colorsChanged.connect(self.pointsUpdated)
        self.m_blue_shade.colorsChanged.connect(self.pointsUpdated)
        self.m_alpha_shade.colorsChanged.connect(self.pointsUpdated)       


    def x_less_than(self, p1, p2):

        return p1.x() < p2.x()

    def pointsUpdated(self):

        w = self.m_alpha_shade.width()

        stops = []
        points = QPolygonF()
        
        points.append(self.m_red_shade.points())
        points.append(self.m_green_shade.points())
        points.append(self.m_blue_shade.points())
        points.append(self.m_alpha_shade.points())
        
        s = sorted(points, key=lambda p: p.x())
        points = QPolygonF()
        for ss in s:
            points.append(ss)
      

        for i in range(len(points)):
            x = int(points[i].x())

            if i + 1 < len(points) and x == int(points[i + 1].x()):
                continue

    
        
            color = QColor((0x00ff0000& self.m_red_shade.colorAt(x)) >> 16,
                           
                           (0x0000ff00& self.m_green_shade.colorAt(x)) >> 8,
                           
                           (0x000000ff& self.m_blue_shade.colorAt(x)),
                           
                           (0xff000000& self.m_alpha_shade.colorAt(x)) >> 24)

            if (x/w) > 1:
                return
            
            stops.append([x/w, color])
        
        self.m_alpha_shade.setGradientStops(stops)

        self.gradientStopsChanged.emit(stops)

    @staticmethod
    def set_shade_points(points, shade):

        shade.hoverPoints().setPoints(points)
        shade.hoverPoints().setPointLock(0, HoverPoints.LockType.LockToLeft)
        shade.hoverPoints().setPointLock(points.size() - 1, HoverPoints.LockType.LockToRight)
        shade.update()

    def setGradientStops(self, stops):

        pts_red, pts_green, pts_blue, pts_alpha = QPolygonF(), QPolygonF(), QPolygonF(), QPolygonF()

        h_red = self.m_red_shade.height()
        h_green = self.m_green_shade.height()
        h_blue = self.m_blue_shade.height()
        h_alpha = self.m_alpha_shade.height()

        

        for i in range(len(stops)):
            pos = stops[i][0]
        
            color = stops[i][1]
            if not isinstance(color, QColor):

                continue
            pts_red.append(QPointF(pos * self.m_red_shade.width(), h_red - color.red() * h_red/ 255))
            pts_green.append(QPointF(pos * self.m_green_shade.width(), h_green - color.green() * h_green/255))
            pts_blue.append(QPointF(pos * self.m_blue_shade.width(), h_blue - color.blue() * h_blue / 255))
            pts_alpha.append(QPointF(pos * self.m_alpha_shade.width(), h_alpha - color.alpha() * h_alpha / 255))

            

        self.set_shade_points(pts_red, self.m_red_shade)
        self.set_shade_points(pts_green, self.m_green_shade)
        self.set_shade_points(pts_blue, self.m_blue_shade)
        self.set_shade_points(pts_alpha, self.m_alpha_shade)

class GradientWidget(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.m_presetIndex  = 0

        self.setWindowTitle("Gradients")

        self.m_renderer = GradientRenderer()
        
        
        self.setObjectName("Gradient Renderer")
        
        
        

        self.mainContentWidget = QWidget()
        self.mainGroup = QGroupBox(self.mainContentWidget)

        self.mainGroup.setTitle("Gradients")

        self.editorGroup = QGroupBox(self.mainGroup)
        self.editorGroup.setTitle("Color Editor")
        
        self.m_editor = GradientEditor(self.editorGroup)
        self.m_renderer.widget = self
        self.m_renderer.editor = self.m_editor
    

        self.typeGroup = QGroupBox(self.mainGroup)
        self.typeGroup.setTitle("Gradient Type")

        self.m_linearButton = QRadioButton(text="Linear Gradient", parent=self.typeGroup, checkable=True, checked=True)
        self.m_radialButton = QRadioButton(text="Radial Gradient", parent=self.typeGroup, checkable=True)
        self.m_conicalButton = QRadioButton(text="Conical Gradient", parent=self.typeGroup, checkable=True)

        self.spreadGroup = QGroupBox(self.mainGroup)
        self.spreadGroup.setTitle("Spread Method")
        self.m_padSpreadButton = QRadioButton(text="Pad Spread", parent=self.spreadGroup, checkable=True, checked=True)
        self.m_reflectSpreadButton = QRadioButton(text="Reflect Spread", parent=self.spreadGroup, checkable=True)
        self.m_repeatSpreadButton = QRadioButton(text="Repeat Spread", parent=self.spreadGroup, checkable=True)

        self.presetsGroup = QGroupBox(self.mainGroup)
        self.presetsGroup.setTitle("Presets")
        self.prevPresetButton = QPushButton("<", self.presetsGroup)
        self.m_presetButton = QPushButton("(unset)", self.presetsGroup)
        self.nextPresetButton = QPushButton(">", self.presetsGroup)

        self.updatePresetName()

        self.defaultGroup = QGroupBox()
        self.defaultGroup.setTitle("Examples")
        self.default1Button = QPushButton("1")
        self.default2Button = QPushButton("2")
        self.default3Button = QPushButton("3")
        self.default4Button = QPushButton("Reset")

        self.showSourceButton = QPushButton()
        self.showSourceButton.setText("Show Source")

        self.enableOpenGLButton = QPushButton()
        self.enableOpenGLButton.setText("Use OpenGL")
        self.enableOpenGLButton.setCheckable(True)
  

        self.whatsThisButton = QPushButton(checkable=True)
        self.whatsThisButton.setText("What's This?")


        self.mainGroup.setFixedWidth(200)
        
        self.mainGroupLayout = QVBoxLayout(self.mainGroup)
        self.mainGroupLayout.addWidget(self.editorGroup)
        self.mainGroupLayout.addWidget(self.typeGroup)
        self.mainGroupLayout.addWidget(self.spreadGroup)
        self.mainGroupLayout.addWidget(self.presetsGroup)
        self.mainGroupLayout.addWidget(self.defaultGroup)
        self.mainGroupLayout.addStretch(1)
        self.mainGroupLayout.addWidget(self.showSourceButton)
        self.mainGroupLayout.addWidget(self.enableOpenGLButton)
        self.mainGroupLayout.addWidget(self.whatsThisButton)

        self.editorGroupLayout = QVBoxLayout(self.editorGroup)
        self.editorGroupLayout.addWidget(self.m_editor)

        self.typeGroupLayout = QVBoxLayout(self.typeGroup)
        self.typeGroupLayout.addWidget(self.m_linearButton)
        self.typeGroupLayout.addWidget(self.m_radialButton)
        self.typeGroupLayout.addWidget(self.m_conicalButton)

        self.spreadGroupLayout = QVBoxLayout(self.spreadGroup)
        self.spreadGroupLayout.addWidget(self.m_padSpreadButton)
        self.spreadGroupLayout.addWidget(self.m_repeatSpreadButton)
        self.spreadGroupLayout.addWidget(self.m_reflectSpreadButton)

        self.presetsGroupLayout = QHBoxLayout(self.presetsGroup)
        self.presetsGroupLayout.addWidget(self.prevPresetButton)
        self.presetsGroupLayout.addWidget(self.m_presetButton ,1)
        self.presetsGroupLayout.addWidget(self.nextPresetButton)

        self.defaultGroupLayout = QHBoxLayout(self.defaultGroup)
        self.defaultGroupLayout.addWidget(self.default1Button)
        self.defaultGroupLayout.addWidget(self.default2Button)
        self.defaultGroupLayout.addWidget(self.default3Button)
        self.editorGroupLayout.addWidget(self.default4Button)

        self.mainGroup.setLayout(self.mainGroupLayout)

        self.mainContentLayout = QVBoxLayout()
        self.mainContentLayout.addWidget(self.mainGroup)
        self.mainContentWidget.setLayout(self.mainContentLayout)

        self.mainScrollArea = QScrollArea()
        self.mainScrollArea.setWidget(self.mainContentWidget)
        self.mainScrollArea.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.addWidget(self.m_renderer)
        self.mainLayout.addWidget(self.mainScrollArea)

        self.m_editor.gradientStopsChanged.connect(self.m_renderer.setGradientStops)
        self.m_linearButton.clicked[bool].connect(self.m_renderer.setLinearGradient)
 
        
        self.m_radialButton.clicked[bool].connect(self.m_renderer.setRadialGradient)
        
        self.m_conicalButton.clicked[bool].connect(self.m_renderer.setConicalGradient)

        self.m_padSpreadButton.clicked[bool].connect(self.m_renderer.setPadSpread)
        self.m_reflectSpreadButton.clicked[bool].connect(self.m_renderer.setReflectSpread)
        self.m_repeatSpreadButton.clicked[bool].connect(self.m_renderer.setRepeatSpread)

        self.prevPresetButton.clicked.connect(self.setPrevPreset)
        self.m_presetButton.clicked.connect(self.setPreset)
        self.nextPresetButton.clicked.connect(self.setNextPreset)
        
        self.default1Button.clicked.connect(self.setDefault1)
        self.default2Button.clicked.connect(self.setDefault2)
        self.default3Button.clicked.connect(self.setDefault3)
        self.default4Button.clicked.connect(self.setDefault4)

      
        self.showSourceButton.clicked.connect(self.m_renderer.showSource)      
        self.whatsThisButton.clicked[bool].connect(self.m_renderer.hoverPoints().setDisabled)
        self.whatsThisButton.clicked[bool].connect(self.m_renderer.setDescriptionEnabled)
        
        
       
        self.m_renderer.descriptionEnabledChanged[bool].connect(self.m_renderer.hoverPoints().setDisabled)
        
        self.m_renderer.loadSourceFile(":/cpp/gradients.cpp");
        self.m_renderer.loadDescription(":/html/gradients.html");
        QTimer.singleShot(50, self.setDefault1)

    def setGradientRenderer(self, renderer):
        
        self.m_editor.gradientStopsChanged.disconnect(self.m_renderer.setGradientStops)
        self.m_linearButton.clicked[bool].disconnect(self.m_renderer.setLinearGradient)
 
        
        self.m_radialButton.clicked[bool].disconnect(self.m_renderer.setRadialGradient)
        
        self.m_conicalButton.clicked[bool].disconnect(self.m_renderer.setConicalGradient)

        self.m_padSpreadButton.clicked[bool].disconnect(self.m_renderer.setPadSpread)
        self.m_reflectSpreadButton.clicked[bool].disconnect(self.m_renderer.setReflectSpread)
        self.m_repeatSpreadButton.clicked[bool].disconnect(self.m_renderer.setRepeatSpread)


        
        self.m_renderer = renderer

        


        

        self.m_editor.gradientStopsChanged.connect(self.m_renderer.setGradientStops)
        self.m_linearButton.clicked[bool].connect(self.m_renderer.setLinearGradient)
 
        
        self.m_radialButton.clicked[bool].connect(self.m_renderer.setRadialGradient)
        
        self.m_conicalButton.clicked[bool].connect(self.m_renderer.setConicalGradient)

        self.m_padSpreadButton.clicked[bool].connect(self.m_renderer.setPadSpread)
        self.m_reflectSpreadButton.clicked[bool].connect(self.m_renderer.setReflectSpread)
        self.m_repeatSpreadButton.clicked[bool].connect(self.m_renderer.setRepeatSpread)
        

   
    def setPreset(self):

        self.changePresetBy(0)

    def setPrevPreset(self):

        self.changePresetBy(-1)

    def setNextPreset(self):

        self.changePresetBy(1)


    def setDefault1(self):

        self.setDefault(1)

    def setDefault2(self):
        self.setDefault(2)

    def setDefault3(self):

        self.setDefault(3)

    def setDefault4(self):

        self.setDefault(4)

    def setDefault(self, config):

        stops = []
        points = QPolygonF()

        if config == 1:

            stops.append([0.00, QColor.fromRgba(0)])
            stops.append([0.04, QColor.fromRgba(0xff131360)])
            stops.append([0.08, QColor.fromRgba(0xff202ccc)])
            stops.append([0.42, QColor.fromRgba(0xff93d3f9)])
            stops.append([0.51, QColor.fromRgba(0xffb3e6ff)])
            stops.append([0.73, QColor.fromRgba(0xffffffec)])
            stops.append([0.92, QColor.fromRgba(0xff5353d9)])
            stops.append([0.96, QColor.fromRgba(0xff262666)])
            stops.append([1.00, QColor.fromRgba(0)])
            self.m_linearButton.animateClick()
            self.m_repeatSpreadButton.animateClick()

        elif config == 2:

            stops.append([0.00, QColor.fromRgba(0xffffffff)])
            
            stops.append([0.11, QColor.fromRgba(0xfff9ffa0)])
            
            stops.append([0.13, QColor.fromRgba(0xfff9ff99)])
            
            stops.append([0.14, QColor.fromRgba(0xfff3ff86)])
            
            stops.append([0,49, QColor.fromRgba(0xff93b353)])
            
            stops.append([0.87, QColor.fromRgba(0xff264619)])
            
            stops.append([0.96, QColor.fromRgba(0xff0c1306)])
            
            stops.append([1.00, QColor.fromRgba(0)])
   
            self.m_radialButton.animateClick()
            self.m_padSpreadButton.animateClick()


        elif config == 3:

            stops.append([0.00, QColor.fromRgba(0)])
            
            stops.append([0.10, QColor.fromRgba(0xffe0cc73)])
            
            stops.append([0.17, QColor.fromRgba(0xffc6a006)])
            
            stops.append([0.46, QColor.fromRgba(0xff600659)])
            
            stops.append([0.72, QColor.fromRgba(0xff0680ac)])
            
            stops.append([0.92, QColor.fromRgba(0xffb9d9e6)])
            
            stops.append([1.00, QColor.fromRgba(0)])
            
            self.m_conicalButton.animateClick()
            self.m_padSpreadButton.animateClick()

        elif config == 4:

            stops.append([0.00, QColor.fromRgba(0xff000000)])
            
            stops.append([1.00, QColor.fromRgba(0xffffffff)])

        pts = QPolygonF()
        h_off = self.m_renderer.width() / 10
        v_off = self.m_renderer.height() / 8
        pts.append(QPointF(self.m_renderer.width() / 2, self.m_renderer.height() / 2))
        pts.append(QPointF(self.m_renderer.width() / 2 - h_off, self.m_renderer.height() / 2 - v_off))
        self.m_editor.setGradientStops(stops)
        self.m_renderer.hoverPoints().setPoints(pts)
        self.m_renderer.setGradientStops(stops)



    

    def changePresetBy(self, indexOffset):       
        #27, 39, 40, 45, 71, 74, 105, 111, 119, 130, 135, 141　欠番
        falls = [27, 39, 40, 45, 71, 74, 105, 111, 119, 130, 135, 141]
        preset = QGradient.Preset()
        #マッピングは自分で作る必要が出てきた。
        presets = {key:QGradient.Preset(key) for key in range(181) if key not in falls}
    
        presets = {key:presets[key] for num, key in enumerate(presets.keys())}
        
        self.m_presetIndex = min(max(0, self.m_presetIndex  + indexOffset), len(presets ) - 1)
        if self.m_presetIndex == 0:
            self.m_presetIndex = len(presets.values()) - 1
        elif self.m_presetIndex == len(presets.values()) - 1:
            self.m_presetIndex = 1

        try:
            presets[self.m_presetIndex]
        except:
            while True:

                try:
                    self.m_presetIndex += 1
                    presets[self.m_presetIndex]
                except KeyError:
                    
                    continue
                break
            
                
                    
        preset = QGradient.Preset(self.m_presetIndex)
        gradient = QGradient(preset)
  
        if gradient.type() != QGradient.LinearGradient:
            return
        
        linearGradientPointer = QLinearGradient()

        linearGradientPointer.setCoordinateMode(gradient.coordinateMode())
        linearGradientPointer.setSpread(gradient.spread())
        linearGradientPointer.setInterpolationMode(gradient.interpolationMode())
        linearGradientPointer.setStops(gradient.stops())

        objectStopsLine = QLineF(linearGradientPointer.start(), linearGradientPointer.finalStop())

        scaleX = 1.0 if 0.0 < abs(objectStopsLine.dx()) < 0.00001 else (0.8 * self.m_renderer.width() / abs(objectStopsLine.dx()))
        scaleY = 1.0 if 0.0 < abs(objectStopsLine.dy()) < 0.00001 else (0.8 * self.m_renderer.height() / abs(objectStopsLine.dy()))
        logicalStopsLine = QTransform.fromScale(scaleX, scaleY).map(objectStopsLine)
        logicalStopsLine.translate(self.m_renderer.rect().center() - logicalStopsLine.center().toPoint())
        logicalStops = QPolygonF()
        logicalStops.append(logicalStopsLine.p1())
        logicalStops.append(logicalStopsLine.p2())

        self.m_linearButton.animateClick()
        self.m_padSpreadButton.animateClick()
        self.m_editor.setGradientStops(gradient.stops())
        self.m_renderer.hoverPoints().setPoints(logicalStops)
        self.m_renderer.setGradientStops(gradient.stops())
       
        self.updatePresetName()


    def updatePresetName(self):
   
        falls = [27, 39, 40, 45, 71, 74, 105, 111, 119, 130, 135, 141]
        preset = QGradient.Preset()
        #マッピングは自分で作る必要が出てきた。
        presets = {key:QGradient.Preset(key) for key in range(181) if key not in falls}
    
        presets = {key:presets[key] for num, key in enumerate(presets.keys())}
  
        try:
            name = presets[self.m_presetIndex].name

        except KeyError:

            name = presets[self.m_presetIndex+1].name
            self.m_presetIndex += 1
            
        self.m_presetButton.setText(name)

class GradientRenderer(QWidget):

    descriptionEnabledChanged = Signal(bool)

    def __init__(self, parent=None, flags = Qt.WindowFlags()):

        super().__init__(parent, flags)

        self.m_sourceFileName = ""

        self.m_tile = QPixmap(128, 128)
        pt = QPainter(self.m_tile)
        color = QColor(230, 230, 230)
        pt.fillRect(0, 0, 64, 64, color)
        pt.fillRect(64, 64, 64, 64, color)
        pt.end()


        
        self.m_stops = []
        self.m_hoverPoints = HoverPoints(self, HoverPoints.ShapeType.CircleShape)
        self.m_hoverPoints.setPointSize(QSize(15, 15))
        self.m_hoverPoints.setConnectionType(HoverPoints.ConnectionType.NoConnection)
        self.m_hoverPoints.setEditable(False)

        points = QPolygonF()
        points.append(QPointF(10, 10))
        points.append(QPointF(20, 20))

        self.m_hoverPoints.setPoints(points)

        

        self.m_spread = QGradient.PadSpread
        self.m_gradientType = Qt.LinearGradientPattern

        self.m_glWindow = None
        self.m_glWidget = None
        self.m_use_opengl = False
        
        self.m_showDoc = False
        self.m_preferImage = False
   
   

        self.m_foreground = False
        self.m_background = True
        self.m_sorround = False


        



    
    def paintEvent(self, event):

        painter = QPainter(self)

        if self.preferImage() and not self.m_use_opengl:
            if not self.static_image or self.static_image.size() != self.size():
                self.static_image = QImage(self.size(), QImage.Format_RGB32)

            painter.begin(self.static_image)

            o = 10

            bg = self.palette().brush(QPalette.Window)
            painter.fillRect(0, 0, o, o, bg)
            painter.fillRect(self.width() - o, 0, o, o, bg)
            painter.fillRect(0, self.height() - o, o, o, bg)
            painter.fillRect(self.width() - o, self.height() - o, o, o, bg)

        else:
            if self.m_use_opengl and self.m_glWindow.isValid():
                self.m_glWindow.makeCurrent()

                painter.begin(self.m_glWindow)
                painter.fillRect(QRectF(0, 0, self.m_glWindow.width(), self.m_glWindow.height(), self.palette().color(self.backgroundRole())))
            else:
                painter.begin(self)


        painter.setClipRect(event.rect())
        painter.setRenderHint(QPainter.Antialiasing)

        clipPath = QPainterPath()

        r = self.rect()
        left = r.x() + 1
        top = r.y() + 1
        right = r.right()
        bottom = r.bottom()
        radius2 = 8 * 2

        clipPath.moveTo(right - radius2, top)
        clipPath.arcTo(right - radius2, top, radius2, radius2, 90, -90)
        clipPath.arcTo(right - radius2, bottom - radius2, radius2, radius2, 0, -90)
        clipPath.arcTo(left, bottom - radius2, radius2, radius2, 270, -90)
        clipPath.arcTo(left, top, radius2, radius2, 180, -90)

        painter.save()
        painter.setClipPath(clipPath, Qt.IntersectClip)

        painter.drawTiledPixmap(self.rect(), self.m_tile)
        
                                 

        self.paint(painter)

        painter.restore()

        painter.save()
        
        if self.m_showDoc:
            self.paintDescription(painter)

        painter.restore()

        level = 180
        painter.setPen(QPen(QColor(level, level, level), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(clipPath)

        if self.preferImage() and not self.m_use_opengl:

            painter.end()
            painter.begin(self)
            painter.drawImage(event.rect(), self.static_image, event.rect())

        if self.m_use_opengl:
            self.m_glWindow.update()

        painter.end()

        
    def paintDescription(self, painter):

        if not self.m_document:
            return

        pageWidth = max(self.width() - 100, 100)
        pageHeight = max(self.height() - 100,100)

        if pageWidth != self.m_document.pageSize().width():
            self.m_document.setPageSize(QSize(pageWidth, pageHeight))

        textRect = QRect(self.width() / 2 - pageWidth/2,
                         self.height() /2 - pageHeight/2,
                         pageWidth,
                         pageHeight)

        pad = 10

        clearRect = textRect.adjusted(-pad, -pad, pad, pad)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 63))

        shade = 10
        painter.drawRect(clearRect.x() + clearRect.width() + 1,
                         clearRect.y() + shade,
                         shade,
                         clearRect.height() + 1)
        painter.drawRect(clearRect.x() + shade,
                         clearRect.y() + clearRect.height() + 1,
                         clearRect.width() - shade + 1,
                         shade)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.setBrush(QColor(255, 255, 255, 220))
        painter.setPen(Qt.black)
        painter.drawRect(clearRect)

        painter.setClipRegion(textRect, Qt.IntersectClip)
        painter.translate(textRect.topLeft())

        g = QLinearGradient(0, 0, 0, textRect.height())
        g.setColorAt(0, Qt.black)
        g.setColorAt(0.9, Qt.black)
        g.setColorAt(1, Qt.transparent)

        pal = self.palette()
        pal.setBrush(QPalette.Text, g)

        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette = pal
        ctx.clip = QRect(0, 0, textRect.width(), textRect.height())
        self.m_document.documentLayout().draw(painter, ctx)

    def loadSourceFile(self, sourceFile):

        self.m_sourceFileName = sourceFile

    def showSource(self):

        if self.findChild(QTextBrowser):
            return

        contents = ""

        if not self.m_sourceFileName:
            contents = self.tr(f"No source for widget: {self.objectName()}")

        else:
            f = QFile(self.m_sourceFileName)
            if not f.open(QFile.ReadOnly):
                contents = self.tr(f"Could not open file: {self.m_sourceFileName}")
      
            else:
          
                contents = f.readAll()
                out = QTextStream(contents)
                contents = out.readAll()
               
                
        contents = contents.replace("&", "&amp")
        contents = contents.replace("<", "&lt")
        contents = contents.replace(">", "&gt")

        keywords= [
                   "for ", "if ", "switch ", " int ",
                   "#include ", "const", "void ", "uint ",
                   "case ", "double ", "#define ", "static",
                   "new", "this"
                   ]

        for keyword in keywords:
            contents = contents.replace(keyword, "<font color=olive>" + keyword + "</font>")
        contents = contents.replace("(int ", "(<font color=olive><b>int </b></font>")

        ppKeywords = ["#ifdef", "#ifndef", "#if", "#endif", "#else"]


        for keyword in ppKeywords:
            contents = contents.replace("(\\d\\d?)", "<font color=navy>\\1</font>")

        contents = contents.replace("(//.+?)\\n", "<font color=red>\\1</font>\n")
        contents = contents.replace("(\".+?\")", "<font color=green>\\1</font>")

        html = "<html><pre>" + contents + "</pre></html>"

        self.sourceViewer = QTextBrowser()
        self.sourceViewer.setWindowTitle(self.tr("Source: {}".format(self.m_sourceFileName[:-5])))
        self.sourceViewer.setParent(self, Qt.Dialog)
        self.sourceViewer.setAttribute(Qt.WA_DeleteOnClose)
        self.sourceViewer.setLineWrapMode(QTextEdit.NoWrap)
        self.sourceViewer.setHtml(html)
        self.sourceViewer.resize(600, 600)
        self.sourceViewer.show()
        

    def setDescriptionEnabled(self, enabled):

        if self.m_showDoc != enabled:
            self.m_showDoc = enabled
            self.descriptionEnabledChanged.emit(self.m_showDoc)
            self.update()

    def setDescription(self, text):

        self.m_document = QTextDocument(self)

        if isinstance(text, QByteArray):

            out = QTextStream(text, QIODevice.ReadOnly)
            text = out.readAll()
        self.m_document.setHtml(text)
        

    def preferImage(self):

        return self.m_preferImage

    def setPreferImage(self, pi):

        self.m_preferImage = pi

    def resizeEvent(self, e):

        if self.m_glWidget:
            self.m_glWidget.setGeometry(0, 0, e.size().width(), e.size().height())

        QWidget.resizeEvent(self, e)

    def loadDescription(self, fileName):

        textFile = QFile(fileName)
        text = ""

        if not textFile.open(QFile.ReadOnly):
            text = f"Unable to load resource file: {fileName}"
        else:
            text = textFile.readAll()
       

        self.setDescription(text)
        

    def paint(self, painter):
        
        pts = self.m_hoverPoints.points()

        g = QGradient()

        if self.m_gradientType == Qt.LinearGradientPattern:
            g = QLinearGradient(pts.at(0), pts.at(1))
           

        elif self.m_gradientType == Qt.RadialGradientPattern:
            g = QRadialGradient(pts.at(0), min(self.width(), self.height()) / 3.0, pts.at(1))

        else:
            l = QLineF(pts.at(0), pts.at(1))
            angle = QLineF(0, 0, 1, 0).angleTo(l)
            g = QConicalGradient(pts.at(0), angle)
        
        for stop in self.m_stops:
            g.setColorAt(stop[0], stop[1])

        g.setSpread(self.m_spread)

        if self.m_background:

            painter.setBrush(g)
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

        elif self.m_sorround:
            

            pen = painter.pen()
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(200)
            pen.setBrush(g)
            brush = painter.brush()
            brush.setStyle(Qt.NoBrush)
        
            painter.setPen(pen)
            painter.setBrush(brush)

            painter.drawRect(self.rect())

        elif self.m_foreground:

            
            pen = painter.pen()            
            pen.setBrush(g)
            painter.setPen(pen)
           
        
            painter.setFont(self.font())
            
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        

    def sizeHint(self):

        return QSize(400, 400)

    def hoverPoints(self):

        return self.m_hoverPoints

    def mousePressEvent(self, e):

        self.setDescriptionEnabled(False)
        
     
        return super().mousePressEvent(e)

    def setGradientStops(self, stops):

        self.m_stops = stops
        self.update()

    def setPadSpread(self):
        
        self.m_spread = QGradient.PadSpread
        self.update()

    def setRepeatSpread(self):

        self.m_spread = QGradient.RepeatSpread
        self.update()

    def setReflectSpread(self):

        self.m_spread = QGradient.ReflectSpread
        self.update()

    def setLinearGradient(self):

        self.m_gradientType = Qt.LinearGradientPattern
        self.update()

    def setRadialGradient(self):

        self.m_gradientType = Qt.RadialGradientPattern
        self.update()

    def setConicalGradient(self):

        self.m_gradientType = Qt.ConicalGradientPattern
        self.update()





def main():
    
    app = QApplication([]) if QApplication.instance() is None else QApplication.instance()
    w = GradientWidget()
    key = QStyleFactory().create("windows")
    
    a = ArthurStyle(key)
    w.setStyle(a)
    children = w.findChildren(QWidget)
    for child in children:
        
        
        child.setStyle(a)
        child.setAttribute(Qt.WA_AcceptTouchEvents)
    
    w.show()


    
    
    


    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
