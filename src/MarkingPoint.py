import matplotlib
from Misc import *



class MarkingPoint():
    """
    Displayed object on the GUI, that visualizes the selected marking point.

    This class contains the functionality to display a marking point on the GUI. From technical point of view a
    matplotlib.lines.Line2D object, that simply draws the char X on top of the whole GUI, is used.
    """

    def __init__(self, origAxes: matplotlib.axes._axes.Axes, origFigure: matplotlib.figure.Figure,
        position: list[float] = [ 0.0, 0.0 ], color: str = "r", lineWidth: float = 25.0):
        """
        The MarkingPoint constructor.

        https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html the section "Colors" contains all
        supported colors.

        Args:
            origAxes:   Original axes of the matplotlib.pyplot. Usually matplotlib.pyplot.gca()
            origFigure: Original figure of the matplotlib.pyplot. Usually matplotlib.pyplot.gcf()
            position:   Initial position
            color:      Initial color of the drawn char
            lineWidth:  Width of the char

        Raises:
            TypeError, ValueError
        """
        is_Type(origAxes, matplotlib.axes._axes.Axes)
        is_Type(origFigure, matplotlib.figure.Figure)
        is_Type(color, str)
        is_Type(lineWidth, float)
        has_List_Type(position, float)
        self.__origAxes = origAxes
        self.__origFigure = origFigure
        self.__line2D = self.__origAxes.plot(position[0], position[1], color + "X", linewidth=lineWidth)[0]
        self.__line2D.set_antialiased(False)
        
# ---------------------------------------------------------------------------------------------------------------------

    def set_Position(self, newX: float, newY: float) -> None:
        """
        Sets the new position.

        Args:
            newX:   New X position
            newY:   New Y position

        Raises:
            TypeError, ValueError
        """
        is_Type(newX, float)
        is_Type(newY, float)
        is_Valid_Coordinate(newX)
        is_Valid_Coordinate(newY)
        self.__line2D.set_xdata([ newX ])
        self.__line2D.set_ydata([ newY ])
        
# ---------------------------------------------------------------------------------------------------------------------

    def get_Position(self) -> list[float]:
        """
        Gets the current position.

        Returns:
            Array with X and Y coordinate

        Raises:
            TypeError, ValueError
        """
        x = float(self.__line2D.get_xdata()[0])
        y = float(self.__line2D.get_ydata()[0])
        is_Valid_Coordinate(x)
        is_Valid_Coordinate(y)
        return is_Type_R([ x, y ], list)
    
# ---------------------------------------------------------------------------------------------------------------------

    def show(self) -> None:
        """
        Shows the char on the GUI.
        """
        self.__line2D.set_visible(True)
        
# ---------------------------------------------------------------------------------------------------------------------

    def hide(self) -> None:
        """
        Hides the char on the GUI.
        """
        self.__line2D.set_visible(False)