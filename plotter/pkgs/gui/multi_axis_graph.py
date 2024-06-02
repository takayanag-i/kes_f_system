import pyqtgraph as pg
from PyQt6.QtWidgets import QGraphicsWidget
from PyQt6.QtGui import QFont

from ..common.constants import FontConfig as fnt, GraphLavels as lvl


class MultiAxisGraphWidget(pg.GraphicsLayoutWidget):

    def __init__(self):
        """コンストラクタ

        GraphicalLayoutWidgetを継承
        """
        super().__init__()
        self.show = True
        self.font = QFont(fnt.FONT_FAMILY, fnt.FONT_SIZE)

        self.plot1 = self.addPlot(row=0, col=0)
        self.curve1 = self.plot1.plot(pen=(221, 238, 255))

        self.curve2 = pg.PlotCurveItem(pen=(153, 221, 255))
        self.curve3 = pg.PlotCurveItem(pen=(181, 255, 20))
        self.curve4 = pg.PlotCurveItem(pen='r')
        self.curve5 = pg.PlotCurveItem(pen='y')

        self.view_box2 = pg.ViewBox()
        self.view_box3 = pg.ViewBox()
        self.view_box4 = pg.ViewBox()
        self.view_box5 = pg.ViewBox()

        self.view_box2.addItem(self.curve2)
        self.view_box3.addItem(self.curve3)
        self.view_box4.addItem(self.curve4)
        self.view_box5.addItem(self.curve5)

        self.ax5 = pg.AxisItem(orientation='right')
        self.set_graph_multiple_axis(
            self.plot1, self.view_box2, self.view_box3, self.view_box4,
            self.view_box5, self.ax5)
        self.set_graph_frame_font(self.plot1, self.ax5)
        self.setup_labels()

        pg.setConfigOptions(antialias=True)

    def set_graph_multiple_axis(self, plot1: pg.PlotItem,
                                view_box2:   pg.ViewBox,
                                view_box3:   pg.ViewBox,
                                view_box4:   pg.ViewBox,
                                view_box5:   pg.ViewBox = None,
                                ax5:         pg.AxisItem = None
                                ):
        plot1.showAxis('right')
        plot1.scene().addItem(view_box2)
        plot1.scene().addItem(view_box3)
        plot1.scene().addItem(view_box4)
        view_box3.linkView(1, view_box4)
        plot1.getAxis('left').linkToView(view_box2)
        plot1.getAxis('right').linkToView(view_box3)
        view_box2.setXLink(plot1)
        view_box2.setYLink(plot1)
        view_box3.setXLink(plot1)
        view_box4.setXLink(plot1)
        view_box2.sigRangeChanged.connect(
            lambda: view_box2.setGeometry(plot1.vb.sceneBoundingRect()))
        view_box3.sigRangeChanged.connect(
            lambda: view_box3.setGeometry(plot1.vb.sceneBoundingRect()))
        view_box4.sigRangeChanged.connect(
            lambda: view_box4.setGeometry(plot1.vb.sceneBoundingRect()))

        if view_box5 is not None and ax5 is not None:
            spacer = QGraphicsWidget()
            spacer.setMaximumSize(15, 15)
            plot1.layout.addItem(spacer, 2, 3)
            plot1.layout.addItem(ax5, 2, 4)
            plot1.scene().addItem(view_box5)
            ax5.linkToView(view_box5)
            view_box5.setXLink(plot1)
            view_box5.sigRangeChanged.connect(
                lambda: view_box5.setGeometry(plot1.vb.sceneBoundingRect()))

    def set_graph_frame_font(self, p1: pg.PlotItem, ax5: pg.AxisItem) -> None:
        p1.getAxis('bottom').setStyle(tickFont=self.font)
        p1.getAxis('bottom').setTextPen('#FFF')
        p1.getAxis('left').setStyle(tickFont=self.font)
        p1.getAxis('left').setTextPen('#FFF')
        p1.getAxis('right').setStyle(tickFont=self.font)
        p1.getAxis('right').setTextPen('#FFF')
        ax5.setStyle(tickFont=self.font)
        ax5.setTextPen('#FFF')
        p1.getAxis('bottom').setHeight(3.5 * 12)
        p1.getAxis('left').setWidth(4 * 12)
        p1.getAxis('right').setWidth(4.3 * 12)
        ax5.setWidth(6 * 12)

    def setup_labels(self) -> None:
        labelstyle = {'color': '#FFF', 'font-size': '12pt'}
        self.plot1.setLabel('left', lvl.FORCE_AX_LAVEL, **labelstyle)
        self.plot1.setLabel('right', lvl.DISP_AX_LAVEL, **labelstyle)
        self.plot1.setLabel('bottom', lvl.TIME_AX_LAVEL, **labelstyle)
        self.ax5.setLabel(lvl.SENSOR_AX_LAVEL, **labelstyle)

        self.plot1.setXRange(0, 50, padding=0)
        self.plot1.setYRange(-0.1, 3.3, padding=0)
        # p1.setRange(yRange = (-10, 10), padding = 0)
        self.view_box2.setRange(yRange=(-0.1, 3.3), padding=0)
        self.view_box3.setRange(yRange=(-10, 10), padding=0)
        self.view_box4.setRange(yRange=(-10, 10), padding=0)
        self.view_box5.setRange(yRange=(-0.1, 3.3), padding=0)
