#!/usr/bin/env python
'''
Contains code to render a script object.
'''

import matplotlib
import matplotlib.pyplot as pyplot

class Plot(object):
    '''An object representing a single set of axis'''
    def __init__(self, script):
        self.figure = pyplot.figure(figsize=(8, 8))
        self.axis = self.figure.add_subplot(1, 1, 1)
        self.script = script
        self.render_script()
        
    def center_origin(self):
        '''Adjusts the axis so that they're centered at the origin.'''
        self.axis.spines['right'].set_color('none')
        self.axis.spines['top'].set_color('none')
        self.axis.xaxis.set_ticks_position('bottom')
        self.axis.spines['bottom'].set_position(('data', 0))
        self.axis.yaxis.set_ticks_position('left')
        self.axis.spines['left'].set_position(('data', 0))
        
    def add_axis_labels(self):
        '''Correctly formats the tick labels based on the script object'''
        def fix(string):
            if string.startswith('.'):
                string = '0' + string
            if string.endswith('.'):
                string = string + '0'
            return string
        x_format_func = lambda x, pos: fix(('%F' % x).strip('0'))
        y_format_func = lambda y, pos: fix(('%F' % y).strip('0')) + 'i' if y != 0 else ''
        x_formatter = matplotlib.ticker.FuncFormatter(x_format_func)
        y_formatter = matplotlib.ticker.FuncFormatter(y_format_func)
        
        x_locator = matplotlib.ticker.MultipleLocator(self.script.xinterval)
        y_locator = matplotlib.ticker.MultipleLocator(self.script.yinterval)
        
        self.axis.xaxis.set_major_formatter(x_formatter)
        self.axis.xaxis.set_major_locator(x_locator)
        self.axis.yaxis.set_major_formatter(y_formatter)
        self.axis.yaxis.set_major_locator(y_locator)
        
        self.axis.set_xlim(*self.script.xrange)
        self.axis.set_ylim(*self.script.yrange)
            
    def render_script(self):
        '''Places the points, lines, circles, and text on the script.'''
        for point, color in self.script.points:
            self.axis.scatter([point.x], [point.y], color=color)
        
        for line, color in self.script.lines:
            x1, y1 = line[0]()
            x2, y2 = line[1]()
            self.axis.add_line(pyplot.Line2D([x1, x2], [y1, y2], color=color))
        
        for rad, color in self.script.circles:
            circle = pyplot.Circle(
                (0, 0), radius=rad, edgecolor=color, facecolor='none')
            self.axis.add_patch(circle)
            
        for coords, text, color in self.script.text:
            pyplot.text(coords.x, coords.y, text, color=color)
        
        self.center_origin()
        self.add_axis_labels()
        
    def show(self):
        '''Makes a window appear showing the axis. This is a blocking call:
        the script pauses until the window is closed.'''
        pyplot.show()
        