
from PySide6.QtGui import QPolygonF, QPen, QBrush, QPainterPath, QPainter, QColor
from PySide6.QtCore import  QObject, Qt, Signal, QLineF, QRectF, QSizeF, QPointF, QCoreApplication, QEvent

class HoverPoints(QObject):
    class ShapeType:
        CircleShape = 0
        RectangleShape = 1
        
    class LockType:
        LockToLeft = 0x01
        LockToRight = 0x02
        LockToTop = 0x04
        LockToBottom = 0x08

    class SortType:
        NoSort = 0
        XSort = 1
        YSort = 2

    class ConnectionType:
        NoConnection = 0
        LineConnection = 1
        CurveConnection = 2

    pointsChanged = Signal(QPolygonF)

    def __init__(self, widget, shape):
        super().__init__(widget)

        
        self.m_editable = True
        self.m_enabled = True
        self.m_fingerPointMapping = {}
        self.m_bounds = QRectF()
        self.m_shape = shape
        
        self.m_widget = widget
        self.m_points = QPolygonF()
        
        self.m_shape = shape
        self.m_sortType = self.SortType.NoSort
        self.m_connectionType = self.ConnectionType.CurveConnection

        self.m_locks = []
        self.m_pointSize = QSizeF(11, 11)

        self.m_currentIndex = -1       

        

        self.m_pointPen = QPen(QColor(255, 255, 255, 191), 1)
        self.m_pointBrush = QBrush(QColor(191, 191, 191, 127))
        self.m_connectionPen = QPen(QColor(255, 255, 255, 127), 2)
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_AcceptTouchEvents)

        self.pointsChanged.connect(self.m_widget.update)

      
        

       

        
    def setEnabled(self, enabled):

        if self.m_enabled != enabled:
            self.m_enabled = enabled
            self.m_widget.update()

    def eventFilter(self, object, event):


        if not hasattr(self, "m_widget"):
            #このメンバ変数は存在しているはずだが、何かのきっかけでないといわれる。リサイズ後、別の場所にカーソルを移したときに発生したのが１件。
        
            return False
        
        if (object != self.m_widget) or not self.m_enabled:
            return False
    
        if event.type() == QEvent.MouseButtonPress:
            
            if self.m_fingerPointMapping:
                return True

            me = event
            clickPos = me.position().toPoint()
            index = -1
            
            for i in range(self.m_points.size()):
                path = QPainterPath()
                rect = self.pointBoundingRect(self.m_points.at(i))
                
                if self.m_shape == HoverPoints.ShapeType.CircleShape:
                    path.addEllipse(rect)
                else:
                    path.addRect(rect)

                if path.contains(clickPos):
                    index = i
                    break
  
            if me.button() == Qt.LeftButton:
           
                if index == -1:
                    if not self.m_editable:
                        return False
                    pos = 0
                    if self.m_sortType ==  HoverPoints.SortType.XSort:
                        for i in range(self.m_points.size()):
                            if self.m_points.at(i).x() > clickPos.x():
                                pos = i
                                break
             
                    elif self.m_sortType ==  HoverPoints.SortType.YSort:
                        for i in range(self.m_points.size()):
                            if self.m_points.at(i).y() > clickPos.y():
                                pos = i
                                break
             
                
                    self.m_points.insert(pos, clickPos)    
                    self.m_locks.insert(pos, 0)
                    self.m_currentIndex = pos
                    self.firePointChange()
                    
                else:
                    self.m_currentIndex = index
                    
                return True
            
            elif me.button() == Qt.RightButton:
                if index >= 0 and self.m_editable:
                    if self.m_locks[index] == 0:
                        self.m_locks.remove(self.m_locks[index])
                        self.m_points.remove(index)
                        
                    self.firePointChange()
                    return True
         
        if event.type() == QEvent.MouseButtonRelease:
            if self.m_fingerPointMapping:
                return True
            
            self.m_currentIndex = -1
       
        if event.type() == QEvent.MouseMove:
            if self.m_fingerPointMapping:
                return True
            if self.m_currentIndex >= 0:
                me = event
                self.movePoint(self.m_currentIndex, me.position().toPoint())
                
        if event.type() == QEvent.TouchBegin:
            pass
        
        if event.type() == QEvent.TouchUpdate:

            touchEvent = event
            points = touchEvent.points()
            pointSize = max(self.m_pointSize.width(), slf.m_pointSize.height())
            
            for point in points:
                
                id = point.id()
                if point.state() == QEventPoint.Pressed:
                    mappedPoints = self.m_fingerPointMapping.values()
                    self.activePoints(mappedPoints.begin(), mappedPoints.end())
                    activePoint = -1
                    distance = -1
                    pointsCount = self.m_points.size()
                    activePointCount = activePoints.size()
                    if pointCount == 2 and activePointCount == 1:
                        activePoint = 1 if activePoints.contains(0) else 0
                    else:
                        for i in range(pointsCount):
                            if activePoints.contains(i):
                                continue
                            
                            d = QLineF(point.position(), self.m_points.at(i)).length()
                            
                            if (distance < 0 and 12*pointSize) or d < distance:
                                distance = d
                                activePoint = i
                                
                    if activePoint != -1:
                        self.m_fingerPointMapping.insert(point.id(), activePoint)
                        self.movePoint(activePoint, point.position())
                    break
                
                elif point.state() == QEventPoint.Released:

                    it = self.m_fingerPointMapping.find(id)
                    self.movePoint(it.value(), point.position())
                    self.m_fingerPointMapping.erase(it)

                    break
                
                elif point.state() == QEventPoint.Updated:
                    pointIdx = self.m_fingerPointMapping.value(id, -1)
                    if pointIdx >= 0:
                        self.movePoint(pointIdx, point.position())
                    break
                
                else:
                    
                    break
            if not self.m_fingerPointMapping:
                
                event.ignore()
                return False
            
            return True
   
        if event.type() == QEvent.TouchEnd:
            if not self.m_fingerPointMapping:
                event.ignore()
                return False
            
            return True
        if event.type() == QEvent.Resize:
            e = event
            if e.oldSize().width() <= 0 or e.oldSize().height() <= 0:
                pass
            width , height = 1 if e.oldSize().width() == 0 else e.oldSize().width(),  1 if e.oldSize().height() == 0 else e.oldSize().height()
            stretch_x = e.size().width() / width
            stretch_y = e.size().height() / height
            for i in range(self.m_points.size()):
                p = self.m_points.at(i)
                self.movePoint(i, QPointF(p.x() * stretch_x, p.y() * stretch_y), False)

            self.firePointChange()
            
        if event.type() == QEvent.Paint:
          
            that_widget = self.m_widget
            self.m_widget = None
            QCoreApplication.sendEvent(object, event)
            self.m_widget = that_widget
            self.paintPoints()
            return True
        
        else:
            return False

        return False

   

    def paintPoints(self):

        p = QPainter()
        af = self.m_widget

        
        p.begin(self.m_widget)   
        

        p.setRenderHint(QPainter.Antialiasing)

        if self.m_connectionPen.style() != Qt.NoPen and self.m_connectionType != HoverPoints.ConnectionType.NoConnection:
            p.setPen(self.m_connectionPen)
     
            if self.m_connectionType == HoverPoints.ConnectionType.CurveConnection:
                path = QPainterPath()
            
                if self.m_points.at(0) is not None:
                    
                    path.moveTo(self.m_points.at(0))
                    for i in range(self.m_points.size()):
                        
                        p1 = self.m_points.at(i-1)
                        p2 = self.m_points.at(i)
                        distance = p2.x() - p1.x()

                        path.cubicTo(p1.x() + distance / 2, p1.y(),
                                     p1.x() + distance / 2, p2.y(),
                                     p2.x(), p2.y())
                        p.drawPath(path)
            else:
                p.drawPolyline(self.m_points)
      

        p.setPen(self.m_pointPen)
        p.setBrush(self.m_pointBrush)

        for point in self.m_points:
            bounds = self.pointBoundingRect(point)
            if self.m_shape == HoverPoints.ShapeType.CircleShape:
                p.drawEllipse(bounds)
            else:
                p.drawRect(bounds)

    def bound_point(self, point, bounds, lock):

        p = point
        left = bounds.left()
        right = bounds.right()
        top = bounds.top()
        bottom = bounds.bottom()

        if p.x() < left or (lock& HoverPoints.LockType.LockToLeft):
            p.setX(left)

        elif p.x() > right or (lock&HoverPoints.LockType.LockToRight):
            p.setX(right)

        if p.y() < top or (lock & HoverPoints.LockType.LockToTop):
            p.setY(top)

        elif p.y() > bottom or (lock&HoverPoints.LockType.LockToBottom):
            p.setY(bottom)

        return p

    def setPoints(self, points):       

        if points.size() != self.m_points.size():
            self.m_fingerPointMapping.clear()
        self.m_points.clear()
        for i in range(points.size()):
            self.m_points.append(self.bound_point(points.at(i), self.boundingRect(), 0))
      
        self.m_locks.clear()
        if self.m_points.size() > 0:
            for i in range(self.m_points.size()):
                self.m_locks.append(0)

    def movePoint(self, index, point, emitUpdate=True):

        self.m_points[index] = self.bound_point(point, self.boundingRect(), self.m_locks[index])
        
        if emitUpdate:
            self.firePointChange()
            

    def setDisabled(self, disabled):

        self.setEnabled(not disabled)
        
    
        


    def pointBoundingRect(self, p):

        w = self.m_pointSize.width()
        h = self.m_pointSize.height()
        x = p.x() - w/2
        y = p.y() - h/2

        return QRectF(x, y, w, h)

    
    
    def x_less_than(self, p1, p2):

        return p1.x() < p2.x()

    def y_less_than(self, p1, p2):

        return p1.y() < p2.y()

    
    def firePointChange(self):


  
        if self.m_sortType != HoverPoints.SortType.NoSort:

            oldCurrent = QPointF()
            if self.m_currentIndex != -1:
                oldCurrent = self.m_points[self.m_currentIndex]

            if self.m_sortType == HoverPoints.SortType.XSort:
                s = sorted(self.m_points, key= lambda x: x.x())
                self.m_points = QPolygonF()
                for ss in s:
                    self.m_points.append(ss)
       
            elif self.m_sortType == HoverPoints.SortType.YSort:
                s = sorted(self.m_points, key= lambda y: y.y())
                self.m_points = QPolygonF()
                for ss in s:
                    self.m_points.append(ss)
            if self.m_currentIndex != -1:
                for i in range(self.m_points.size()):
                    if self.m_points[i] == oldCurrent:
                        self.m_currentIndex = i
                        break
                    
        self.pointsChanged.emit(self.m_points)        

        

    def boundingRect(self):

        if self.m_bounds.isEmpty():
            return self.m_widget.rect()
        else:
            return self.m_bounds

    def setBoundingRect(self, rect):

        self.m_bounds = rect

    def points(self):

        return self.m_points    

    

    def setPointSize(self, size):

        self.m_pointSize = size

    def sortType(self):

        return self.m_sortType

    def setSortType(self, sortType):

        self.m_sortType = sortType

    def connectionType(self):

        return self.m_connectionType

    def setConnectionType(self, connectionType):

        self.m_connectionType = connectionType

    def setConnectionPen(self, pen):

        self.m_connectionPen = pen

    def setShapePen(self, pen):

        self.m_pointPen = pen

    def setShapeBrush(self, brush):

        self.m_pointBrush = brush

    def setPointLock(self, pos, lock):


        self.m_locks[pos] = lock

    def setEditable(self, editable):

        self.m_editable = editable

    def editable(self):

        return self.m_editable
    
def main():
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([]) if QApplication.instance() is None else QApplication.instance()

    import sys
    w = QWidget()
    h = HoverPoints(w, HoverPoints.ShapeType.CircleShape)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
