import pyqtgraph as pg
from PyQt6.QtWidgets import QGraphicsWidget
from PyQt6.QtGui import QFont
from pkgs.common.constants import (
    FontConfig, GraphLabels, RangeValues, ColourValues, Styles)


class MultiAxisGraphWidget(pg.GraphicsLayoutWidget):

    def __init__(self):
        """コンストラクタ

        GraphicalLayoutWidgetを継承
        """
        super().__init__()
        self.show = True
        self.font = QFont(FontConfig.FONT_FAMILY, FontConfig.FONT_SIZE)

        self.plotItem = self.addPlot(row=0, col=0)

        # Curves and ViewBoxes
        self.curves = self.create_curves()
        self.view_boxes = self.create_view_boxes()

        self.add_curves_to_view_boxes()
        self.ax5 = pg.AxisItem(orientation='right')
        self.set_graph_multiple_axis()
        self.set_graph_frame_font()
        self.setup_labels()

        pg.setConfigOptions(antialias=True)

    def create_curves(self):
        """Create and return a list of curves with different colors."""
        return [
            pg.PlotCurveItem(pen=ColourValues.LIGHT_BLUE),
            pg.PlotCurveItem(pen=ColourValues.BLUE),
            pg.PlotCurveItem(pen=ColourValues.GREEN),
            pg.PlotCurveItem(pen=ColourValues.RED),
            pg.PlotCurveItem(pen=ColourValues.YELLOW)
        ]

    def create_view_boxes(self):
        """Create and return a list of view boxes."""
        return [pg.ViewBox() for _ in range(len(self.curves))]

    def add_curves_to_view_boxes(self):
        """Add each curve to its corresponding view box."""
        for curve, view_box in zip(self.curves, self.view_boxes):
            view_box.addItem(curve)

    def set_graph_multiple_axis(self):
        """Set up multiple axes for the graph."""
        self.plotItem.showAxis('right')

        for view_box in self.view_boxes:
            self.plotItem.scene().addItem(view_box)

        self.link_view_boxes()
        self.plotItem.getAxis('left').linkToView(self.view_boxes[0])
        self.plotItem.getAxis('right').linkToView(self.view_boxes[2])
        self.link_view_boxes_to_plot_item()
        self.setup_view_box_range_signals()

        spacer = QGraphicsWidget()
        spacer.setMaximumSize(15, 15)
        self.plotItem.layout.addItem(spacer, 2, 3)
        self.plotItem.layout.addItem(self.ax5, 2, 4)
        self.ax5.linkToView(self.view_boxes[4])
        self.view_boxes[4].setXLink(self.plotItem)
        self.view_boxes[4].sigRangeChanged.connect(
            lambda: self.view_boxes[4].setGeometry(
                self.plotItem.vb.sceneBoundingRect()))

    def link_view_boxes(self):
        """Link view boxes together."""
        self.view_boxes[0].linkView(1, self.view_boxes[1])
        self.view_boxes[2].linkView(1, self.view_boxes[3])

    def link_view_boxes_to_plot_item(self):
        """Link view boxes to the plot item."""
        for view_box in self.view_boxes:
            view_box.setXLink(self.plotItem)

    def setup_view_box_range_signals(self):
        """Set up signals to update view box ranges."""
        for view_box in self.view_boxes:
            view_box.sigRangeChanged.connect(
                lambda vb=view_box: vb.setGeometry(
                    self.plotItem.vb.sceneBoundingRect()))

    def set_graph_frame_font(self):
        """Set font and color for graph axes."""
        self.plotItem.getAxis('bottom').setStyle(tickFont=self.font)
        self.plotItem.getAxis('bottom').setTextPen(ColourValues.WHITE)
        self.plotItem.getAxis('left').setStyle(tickFont=self.font)
        self.plotItem.getAxis('left').setTextPen(ColourValues.WHITE)
        self.plotItem.getAxis('right').setStyle(tickFont=self.font)
        self.plotItem.getAxis('right').setTextPen(ColourValues.WHITE)
        self.ax5.setStyle(tickFont=self.font)
        self.ax5.setTextPen(ColourValues.WHITE)
        self.set_axis_dimensions()

    def set_axis_dimensions(self):
        """Set dimensions for the axes."""
        self.plotItem.getAxis('bottom').setHeight(42)  # 3.5 * 12
        self.plotItem.getAxis('left').setWidth(48)  # 4 * 12
        self.plotItem.getAxis('right').setWidth(51.6)  # 4.3 * 12
        self.ax5.setWidth(72)  # 6 * 12

    def setup_labels(self):
        """Set up labels for the graph axes."""
        self.plotItem.setLabel(
            'left', GraphLabels.FORCE_AX, **Styles.LABEL_STYLE)
        self.plotItem.setLabel(
            'right', GraphLabels.DISP_AX, **Styles.LABEL_STYLE)
        self.plotItem.setLabel(
            'bottom', GraphLabels.TIME_AX, **Styles.LABEL_STYLE)
        self.ax5.setLabel(GraphLabels.SENSOR_AX, **Styles.LABEL_STYLE)

        self.plotItem.setXRange(*RangeValues.X_RANGE, padding=0)

        self.view_boxes[0].setRange(yRange=RangeValues.Y_RANGE1, padding=0)
        self.view_boxes[1].setRange(yRange=RangeValues.Y_RANGE1, padding=0)
        self.view_boxes[2].setRange(yRange=RangeValues.Y_RANGE2, padding=0)
        self.view_boxes[3].setRange(yRange=RangeValues.Y_RANGE2, padding=0)
        self.view_boxes[4].setRange(yRange=RangeValues.Y_RANGE1, padding=0)
