'''
Created on Jun 6, 2014

@author: keisano1
'''

from PyQt4 import QtGui, QtCore
from ui_circuit import UICircuit
from ui_IO import UIIO
from ui_connection import UIConnection
import circuits


class MachineWidget(QtGui.QGraphicsScene):
    '''
    classdocs
    '''

    def __init__(self, tree_widget, parent=None):
        '''
        Constructor
        '''
        super(MachineWidget, self).__init__(parent)
        self.tree_widget = tree_widget
        self.xsize = 1000
        self.ysize = 1000
        self.max_size = 2000
        self.circuits = []
        self.connections = []
        self.circuit_index = 1
        self.font_size = 15
        self.new_connection = None
        self.add_circuits = False
        self.initWidget()

    def initWidget(self):
        self.addCircuits()
        self.update()

    def addCircuits(self):
        """Add some circuits to the scene on startup.
        Probably no use in final versions."""
        self.addCircuit("Scanner", 300, 500)
        self.addCircuit("3d Linear Interpolation", 500, 500)
        self.addCircuit("Output", 700, 500)
        # for i in range(1, 10):
        #     x = random.randint(0, self.xsize)
        #     y = random.randint(0, self.ysize)
        #     circuit = UICircuit(x - x%100, y -y%100, random.choice(circuits.circuits.values()), self)
        #     self.circuits.append(circuit)
        #     self.addItem(circuit)
        #     self.circuit_index += 1

    def addCircuit(self, name, x, y):
        """Add a circuit with corresponding name to the scene
        and update the scene.
        """
        circuit = UICircuit(x - x % 100, y - y % 100, circuits.circuits[name], self)
        self.circuits.append(circuit)
        self.addItem(circuit)
        self.circuit_index += 1
        self.update()

    def addDroppedCircuit(self, dropped, pos):
        """Add the dropped circuit to the scene after a dropEvent."""
        name = str(dropped.text(0))
        self.addCircuit(name, pos.x(), pos.y())

    def addClickedCircuit(self, pos):
        """Add circuit selected from the main_window tree_widget
        to the scene. If nothing is selected do nothing.
        """
        item = self.tree_widget.currentItem()
        if item is None:
            return
        name = str(item.text(0))
        if item.parent():
            self.addCircuit(name, pos.x(), pos.y())

    def createNewConnection(self, origin, mouse_pos):
        """Try to create a new connection starting from mouse_pos.
        Throw a ValueError if input under mouse is allready connected.
        Should be called by the input or output at the start of the
        connection.
        """
        try:
            self.new_connection = UIConnection(origin, mouse_pos)
        except ValueError as e:
            print e.message
            return
        self.views()[0].setMouseTracking(True)
        self.addItem(self.new_connection)

    def addConnection(self):
        """Add a new valid connection. Should be called
        by the input or output at the end of connection.
        """
        self.connections.append(self.new_connection)
        self.new_connection = None
        self.views()[0].setMouseTracking(False)

    def deleteNewConnection(self):
        """Delete unconnected new_connextion."""
        if self.new_connection is not None:
            self.removeItem(self.new_connection)
            self.new_connection = None
            self.views()[0].setMouseTracking(False)

    def updateConnections(self):
        """Update paths for all required connections.
        Needed after some move events."""
        for connection in self.connections:
            connection.updatePath()

    def hasIOatPos(self, pos):
        """Check if there's input or output at position pos
        and return True if there is and False otherwise.
        """
        items = self.items(pos)
        for item in items:
            if isinstance(item, UIIO):
                return True
        return False

    def addContextActions(self, menu):
        """Add widget specific context actions to the
        context menu given as parameter.
        """
        clear_all = QtGui.QAction("Clear All", menu)
        QtCore.QObject.connect(clear_all, QtCore.SIGNAL("triggered()"),
                               self.clearAll)

        clear_connections = QtGui.QAction("Clear Connections", menu)
        QtCore.QObject.connect(clear_connections, QtCore.SIGNAL("triggered()"),
                               self.removeConnections)

        menu.addAction(clear_connections)
        menu.addAction(clear_all)

    def clearAll(self):
        """Clear everything from the scene."""
        self.connections = []
        self.circuits = []
        self.clear()
        self.update()

    def removeConnections(self):
        """Clear all connections from the scene."""
        for connection in self.connections:
            self.removeItem(connection)
        self.connections = []
        self.update()

    def removeConnectionsFrom(self, IO):
        """Remove all connections from input or output
        given as parameter.
        """
        for connection in self.connections[:]:
            if connection.input_ == IO or connection.output == IO:
                self.connections.remove(connection)
                self.removeItem(connection)
        self.update()

    def removeConnection(self, connection):
        """Remove the specified connection from the scene."""
        self.connections.remove(connection)
        self.removeItem(connection)

    def removeCircuit(self, circuit):
        """Remove the specified circuit from the scene.
        Also remove all the circuits inputs, outputs and connections
        from the scene.
        """
        for inp in circuit.inputs:
            self.removeConnectionsFrom(inp)
            self.removeItem(inp)
        for outp in circuit.outputs:
            self.removeConnectionsFrom(outp)
            self.removeItem(outp)
        self.circuits.remove(circuit)
        self.removeItem(circuit)
        self.update()

    """def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawBackground(qp)
        self.drawGrid(qp)
        self.drawCircuits(qp)
        qp.end()"""

    def drawBackground(self, qp, rect):
        """Draw the background white and call a grid draw"""
        qp.setPen(QtGui.QColor(255, 255, 255))
        qp.setBrush(QtGui.QColor(255, 255, 255))
        qp.drawRect(rect)
        self.drawGrid(qp, rect)

    def drawGrid(self, qp, rect):
        """Draw a grid with a spacing of 100 to the background."""
        tl = rect.topLeft()
        br = rect.bottomRight()
        solid_pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 4, QtCore.Qt.SolidLine)
        faint_pen = QtGui.QPen(QtGui.QColor(150, 150, 150), 1, QtCore.Qt.SolidLine)
        qp.setPen(faint_pen)
        for x in range(int(tl.x() - tl.x() % 100),
                       int(br.x()), 100):
            for y in range(int(tl.y() - tl.y() % 100),
                           int(br.y()), 100):
                qp.drawLine(int(tl.x()), int(y), int(br.x()), int(y))
                qp.drawLine(int(x), int(tl.y()), int(x), int(br.y()))
        # Draw thicklines to the middle of the scene
        qp.setPen(solid_pen)
        qp.drawLine(int(0.5*self.xsize), int(tl.y()),
                    int(0.5*self.xsize), int(br.y()))
        qp.drawLine(int(tl.x()), int(0.5*self.ysize),
                    int(br.x()), int(0.5*self.ysize))

    def dragEnterEvent(self, event):
        """Accept event for drag & drop to work."""
        event.accept()

    def dragMoveEvent(self, event):
        """Accept event for drag & drop to work."""
        event.accept()

    def dropEvent(self, event):
        """Accept event and add the dropped circuit
        to the scene.
        """
        if event.source() is self.tree_widget:
            event.accept()
            dropped_item = event.source().currentItem()
            self.addDroppedCircuit(dropped_item, event.scenePos())

    def mousePressEvent(self, event):
        """If user is adding circuits try to add circuit to the scene.
        Otherwise call the super function to send signal forward.
        """
        if self.add_circuits and event.button() == QtCore.Qt.LeftButton:
            event.accept()
            self.addClickedCircuit(event.scenePos())
        else:
            super(MachineWidget, self).mousePressEvent(event)
            # If user was trying to create a new connection
            # and clicked something other than input or output
            # destroy the connection. Also non left clicks
            # destroy the connection.
            if (self.new_connection is not None and
               (not self.hasIOatPos(event.scenePos()) or
               event.button() != QtCore.Qt.LeftButton)):
                self.deleteNewConnection()
                print "destroyed connection"

    def mouseMoveEvent(self, event):
        """If user is trying to create a connection update connections
        end point when mouse is moved. Remember to call super.
        """
        super(MachineWidget, self).mouseMoveEvent(event)
        if self.new_connection is not None:
            self.new_connection.updateMousePos(event.scenePos())
            self.update()

    def keyPressEvent(self, event):
        """Set the add_circuits flag to True if user presses down CTRL"""
        if event.key() == QtCore.Qt.Key_Control:
            self.add_circuits = True

    def keyReleaseEvent(self, event):
        """Set the add_circuits flag to False if user releases CTRL"""
        if event.key() == QtCore.Qt.Key_Control:
            self.add_circuits = False

    def contextMenuEvent(self, event):
        """Create a new context menu and open it under mouse"""
        menu = QtGui.QMenu()
        # Insert actions to the menu from all the items under the mouse
        for item in self.items(event.scenePos()):
            item.addContextActions(menu)
        self.addContextActions(menu)
        # Show the menu under mouse
        menu.exec_(event.screenPos())
