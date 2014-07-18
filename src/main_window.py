'''
Created on Jun 6, 2014

@author: keisano1
'''

import sys
from PyQt4 import QtGui, QtCore
from machine_widget import MachineWidget
from machine_view import MachineView
from parameter_window import ParameterWindow
from run_selection_window import RunSelectionWindow
import circuit_info
import circuits
import script


class MainWindow(QtGui.QMainWindow):
    '''
    The main window of the UI
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(MainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 500)
        self.setWindowTitle('PyVAFM')

        self.setCentralWidget(MainWidget())

        self.show()


class MainWidget(QtGui.QWidget):

    def __init__(self):
        super(MainWidget, self).__init__()
        self.param_window_style = circuits.machine_param_window_style
        self.parameters = {}
        self.initWidget()
        self.parameter_window = ParameterWindow(self)
        self.run_selection_window = RunSelectionWindow(self)

    def initWidget(self):
        """Initialize the graphical elements of the main widget"""
        # Set up the left area of the UI
        left_area = QtGui.QVBoxLayout()

        # Set up the buttons on the top left of the UI
        button_grid = QtGui.QGridLayout()
        create_button = QtGui.QPushButton("Create Script")
        run_button = QtGui.QPushButton("Create + Run")
        parameter_button = QtGui.QPushButton("Parameters")
        run_selection_button = QtGui.QPushButton("Operations")

        QtCore.QObject.connect(create_button, QtCore.SIGNAL("clicked()"),
                               self.createScript)
        QtCore.QObject.connect(run_button, QtCore.SIGNAL("clicked()"),
                               self.createRun)
        QtCore.QObject.connect(parameter_button, QtCore.SIGNAL("clicked()"),
                               self.showParameters)
        QtCore.QObject.connect(run_selection_button, QtCore.SIGNAL("clicked()"),
                               self.showRunSelection)

        button_grid.addWidget(create_button, 2, 0)
        button_grid.addWidget(run_button, 2, 1)
        button_grid.addWidget(parameter_button, 1, 0)
        button_grid.addWidget(run_selection_button, 1, 1)

        # Set up the tree widget holding the circuits
        tree_widget = QtGui.QTreeWidget(self)
        tree_widget.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                  QtGui.QSizePolicy.Expanding)
        tree_widget.setHeaderLabel("Circuits")
        tree_widget.setDragEnabled(True)
        tree_widget.setFocusPolicy(QtCore.Qt.NoFocus)

        # Load the circuits from circuits.py into the tree_widget
        self.loadCircuits(tree_widget)

        # Set up the graphics view for the machine and set the scene
        graphics_view = MachineView()
        self.machine_widget = MachineWidget(tree_widget, graphics_view)
        graphics_view.setScene(self.machine_widget)

        # Add widgets to the corresponding layouts
        left_area.addLayout(button_grid)
        left_area.addWidget(tree_widget)
        main_layout = QtGui.QHBoxLayout()
        main_layout.addLayout(left_area)
        main_layout.addWidget(graphics_view)
        self.setLayout(main_layout)

    def showParameters(self):
        """Open the main machine parameter window"""
        self.parameter_window.showWindow()

    def showRunSelection(self):
        """Open the run selection window."""
        self.run_selection_window.showWindow()

    def setParameters(self, parameters):
        """Save the machine parameters"""
        for label, value in parameters.iteritems():
            if value is not None:
                self.parameters[label] = value

    def loadCircuits(self, tree_widget):
        """Load all the circuits from the circuits file to the tree_widget"""
        groups = {}
        for group in circuit_info.groups:
            top_item = QtGui.QTreeWidgetItem(tree_widget)
            top_item.setText(0, group)
            top_item.setFlags(top_item.flags() & ~QtCore.Qt.ItemIsDragEnabled
                              & ~QtCore.Qt.ItemIsSelectable)
            groups[group] = top_item
        for name, info in circuits.circuits.iteritems():
            group = info.group
            sub_item = QtGui.QTreeWidgetItem(groups[group])
            sub_item.setText(0, name)

    def createScript(self):
        """Create pyvafm script from the current machine state."""
        print self.parameters
        savefile = QtGui.QFileDialog.getSaveFileName(self, "Save script", "..")
        if not savefile:
            return
        blocks = [""]*5
        with open("formats/machine.format", "r") as f:
            script.createFromFormat(blocks, f, self.parameters)

        # Create script lines for all the circuits
        for circuit in self.machine_widget.circuits:
            print circuit.name
            print circuit.circuit_info.script_format
            if circuit.circuit_info.script_format:
                with open(circuit.circuit_info.script_format, "r") as f:
                    script.createFromFormat(blocks, f, circuit.parameters)
            else:
                raise NotImplementedError("Circuit " + circuit.name +
                      " doesn't have proper script format implemented!")

        # Create script lines for all the inputs and outputs
        for connection in self.machine_widget.connections:
            with open("formats/connect.format", "r") as f:
                output = connection.output.circuit.name+"."+connection.output.name
                input_ = connection.input_.circuit.name+"."+connection.input_.name
                script.createFromFormat(blocks, f, {"output": output,
                                                    "input": input_})

        # Create script lines for the run commands given in run selection tree
        selection_tree = self.run_selection_window.selection_tree
        for i in range(selection_tree.topLevelItemCount()):
            top_item = selection_tree.topLevelItem(i)
            widget = selection_tree.itemWidget(top_item, 0)
            blocks[4] += widget.text() + '\n'

        # Write all the lines to the savefile
        with open(savefile, 'w') as f:
            i = 0
            for block in blocks:
                f.write("'Block #"+str(i)+"'\n")
                f.write(block)
                f.write('\n\n')
                i += 1
        return savefile

    def createRun(self):
        """Create pyvafm script and run the script.
        Currently can only run once and runs from the src folder.
        """
        savefile = self.createScript()
        if savefile:
            with open(str(savefile), 'r') as f:
                exec(f)


def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
