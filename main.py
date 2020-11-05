from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QSizePolicy, QLineEdit

from photoviewer import PhotoViewer
import database


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        self.viewer.update_selected = self.selected_updated

        # load image button
        self.load_btn = QtWidgets.QPushButton(self)
        self.load_btn.setText('Load image')
        self.load_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.load_btn.setStyleSheet("padding: 20px 15px 20px 15px")
        self.load_btn.clicked.connect(self.load_image)

        # create box button
        self.create_box_btn = QtWidgets.QPushButton(self)
        self.create_box_btn.setText('Create box')
        self.create_box_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.create_box_btn.setStyleSheet("padding: 20px 15px 20px 15px")
        self.create_box_btn.setShortcut("h")
        self.create_box_btn.clicked.connect(self.box_creation_mode)

        # export button
        self.export_btn = QtWidgets.QPushButton(self)
        self.export_btn.setText('Export')
        self.export_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.export_btn.setStyleSheet("padding: 20px 15px 20px 15px")
        self.export_btn.clicked.connect(self.export_polygons)

        vert_left_layout = QtWidgets.QVBoxLayout()
        vert_left_layout.setAlignment(QtCore.Qt.AlignTop)
        vert_left_layout.addWidget(self.load_btn)
        vert_left_layout.addWidget(self.create_box_btn)
        vert_left_layout.addWidget(self.export_btn)


        # Arrange layout
        grid_layout = QtWidgets.QGridLayout(self)
        grid_layout.setColumnStretch(1, 3)

        grid_layout.addLayout(vert_left_layout, 0, 0)
        grid_layout.addWidget(self.viewer, 0, 1)

        vert_right_layout = QtWidgets.QVBoxLayout()
        vert_right_layout.setAlignment(QtCore.Qt.AlignTop)

        poly_edit_layout = QtWidgets.QGridLayout()
        self.id_label = QtWidgets.QLabel()
        self.id_label.setText("id")
        poly_edit_layout.addWidget(self.id_label, 0, 0)

        self.id_txtbox = QLineEdit(self)
        self.id_txtbox.setMaximumWidth(100)
        self.id_txtbox.setValidator(QIntValidator())
        poly_edit_layout.addWidget(self.id_txtbox, 0, 1)

        self.row_label = QtWidgets.QLabel()
        self.row_label.setText("row")
        poly_edit_layout.addWidget(self.row_label, 1, 0)

        self.row_txtbox = QLineEdit(self)
        self.row_txtbox.setMaximumWidth(100)
        poly_edit_layout.addWidget(self.row_txtbox, 1, 1)

        self.col_label = QtWidgets.QLabel()
        self.col_label.setText("col")
        poly_edit_layout.addWidget(self.col_label, 2, 0)

        self.col_txtbox = QLineEdit(self)
        self.col_txtbox.setMaximumWidth(100)
        self.col_txtbox.setValidator(QIntValidator())
        poly_edit_layout.addWidget(self.col_txtbox, 2, 1)

        self.poly_update = QtWidgets.QPushButton()
        self.poly_update.setText('update')
        self.poly_update.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.poly_update.setShortcut("u")
        self.poly_update.clicked.connect(self.update_selected)
        poly_edit_layout.addWidget(self.poly_update, 3, 1)

        vert_right_layout.addLayout(poly_edit_layout)
        grid_layout.addLayout(vert_right_layout, 0, 3)

        vert_left_layout.addStretch()
        vert_right_layout.addStretch()

    def load_image(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'c:/',
                                                          "Image files (*.jpg *.gif *.png *.tiff)")
        pixmap = QtGui.QPixmap(file_name[0])
        self.viewer.set_photo(QtGui.QPixmap(pixmap))

    def box_creation_mode(self):
        self.viewer._box_creation_mode = True
        self.viewer.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.viewer.delete_selected()

    def selected_updated(self, polygons):
        if len(polygons) == 0:
            self.id_txtbox.setText("")
            self.row_txtbox.setText("")
            self.col_txtbox.setText("")
            return
        self.id_txtbox.setText(str(polygons[0].id) if polygons[0].id is not None else "")
        self.row_txtbox.setText(str(polygons[0].row) if polygons[0].row is not None else "")
        self.col_txtbox.setText(str(polygons[0].col) if polygons[0].col is not None else "")

    def update_selected(self):
        for polygon in self.viewer.selected_polygons:
            polygon.id = int(self.id_txtbox.text()) if self.id_txtbox.text() != "" else None
            polygon.row = int(self.row_txtbox.text()) if self.row_txtbox.text() != "" else None
            polygon.col = int(self.col_txtbox.text()) if self.col_txtbox.text() != "" else None

    def export_polygons(self):
        database.create_table("testgravesite")
        for polygon in self.viewer.selection_polygons:
            centroid = polygon.centroid()
            database.add_entry("testgravesite", polygon.id, polygon.row, polygon.col,
                               polygon.polygon_points[0].x(), polygon.polygon_points[0].y(),
                               polygon.polygon_points[1].x(), polygon.polygon_points[1].y(),
                               polygon.polygon_points[2].x(), polygon.polygon_points[2].y(),
                               polygon.polygon_points[3].x(), polygon.polygon_points[3].y(),
                               centroid.x(), centroid.y())

        database.export_table("testgravesite")


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 1000, 600)
    window.show()

    pixmap = QtGui.QPixmap('test_data/graves.png')
    window.viewer.set_photo(QtGui.QPixmap(pixmap))
    sys.exit(app.exec_())
