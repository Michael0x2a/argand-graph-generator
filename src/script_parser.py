#!/usr/bin/env python
'''
Contains code to parse the scripting file and convert it into an object the 
renderer can use.
'''

from __future__ import division

import math # used inside eval
import re

import errors
        
class ParserException(Exception): 
    '''A generic exception used to represent all the different types of 
    errors this parser is meant to handle.'''
    pass
    
class OverridingSymbolError(ParserException): 
    '''Called when the user tries to define an already-existing variable.'''
    pass
    
class FetchingNonexistantSymbolError(ParserException): 
    '''Called when the user tries to use a non-existant variable.'''
    pass
    
class ImproperCoordinateError(ParserException): 
    '''Called when a malformed coordinate is encountered.'''
    pass
    
class WrongNumberOfCommasError(ParserException): 
    '''Called when there are too many commas'''
    pass
    
class WrongNumberOfArgumentsError(ParserException): 
    '''Called when a command gets an incorrect number of arguments.'''
    pass
    
class UnknownCommandError(ParserException): 
    '''Called when an unknown command is used.'''
    pass
    
class InvalidColorError(ParserException): 
    '''Called when an invalid color is encountered.'''
    pass
    
class InvalidExpressionError(ParserException): 
    '''Called when the parser encounters a math expression that Python's 
    "eval" cannot handle.'''
    pass
    
class SymbolTable(object):
    '''An object representing all the variables in a script.'''
    def __init__(self):
        self.table = {}
        
    def add(self, name, expression):
        '''Adds an expression under the given name, and throws an exception 
        when trying to overwrite an already existing variable.'''
        if name not in self.table:
            self.table[name] = expression
        else:
            error = 'Overwriting point {0} with {1}'.format(name, expression)
            raise OverridingSymbolError(error)
        
    def fetch(self, name):
        '''Gets the expression registered under a given name. Raises an 
        exception if the variable has not been defined.'''
        if name in self.table:
            return self.table[name]
        else:
            error = 'Referring to nonexistant point {0}'.format(name)
            raise FetchingNonexistantSymbolError(error)
    
class Coordinate(object):
    '''Represents a coordinate/complex number on the argand plane'''
    def __init__(self):
        self.x = 0
        self.y = 0
        
    def imaginary(self, expression):
        '''Converts an imaginary number into a coordinate'''
        self.x = expression.real
        self.y = expression.imag
        return self
        
    def cartesian(self, x, y):
        '''Converts a cartesian coordinate into a coordinate object'''
        self.x = x
        self.y = y
        return self
        
    def __call__(self):
        '''Returns the coordinates as a tuple.'''
        return (self.x, self.y)
        
    def __repr__(self):
        return 'C({0}, {1})'.format(self.x, self.y)
        
VALID_COLORS = [
'AliceBlue',      'BlueViolet',      'Cyan',            'Darkorange',     
'AntiqueWhite',   'Brown',           'DarkBlue',        'DarkOrchid',     
'Aqua',           'BurlyWood',       'DarkCyan',        'DarkRed',        
'Aquamarine',     'CadetBlue',       'DarkGoldenRod',   'DarkSalmon',     
'Azure',          'Chartreuse',      'DarkGray',        'DarkSeaGreen',   
'Beige',          'Chocolate',       'DarkGrey',        'DarkSlateBlue',  
'Bisque',         'Coral',           'DarkGreen',       'DarkSlateGray',  
'Black',          'CornflowerBlue',  'DarkKhaki',       'DarkSlateGrey',  
'BlanchedAlmond', 'Cornsilk',        'DarkMagenta',     'DarkTurquoise',  
'Blue',           'Crimson',         'DarkOliveGreen',  'DarkViolet',     

'DeepPink',      'GhostWhite',   'Indigo',        'LightGoldenRodYellow',
'DeepSkyBlue',   'Gold',         'Ivory',         'LightGray',           
'DimGray',       'GoldenRod',    'Khaki',         'LightGrey',           
'DimGrey',       'Gray',         'Lavender',      'LightGreen',          
'DodgerBlue',    'Grey',         'LavenderBlush', 'LightPink',           
'FireBrick',     'Green',        'LawnGreen',     'LightSalmon',         
'FloralWhite',   'GreenYellow',  'LemonChiffon',  'LightSeaGreen',       
'ForestGreen',   'HoneyDew',     'LightBlue',     'LightSkyBlue',        
'Fuchsia',       'HotPink',      'LightCoral',    'LightSlateGray',      
'Gainsboro',     'IndianRed',    'LightCyan',     'LightSlateGrey',      

'LightSteelBlue',    'LightSteelBlue',   'MediumPurple',      'NavajoWhite',  
'LightYellow',       'LightYellow',      'MediumSeaGreen',    'Navy',         
'Lime',              'Lime',             'MediumSlateBlue',   'OldLace',      
'LimeGreen',         'LimeGreen',        'MediumSpringGreen', 'Olive',        
'Linen',             'Linen',            'MediumTurquoise',   'OliveDrab',    
'Magenta',           'Magenta',          'MediumVioletRed',   'Orange',       
'Maroon',            'Maroon',           'MidnightBlue',      'OrangeRed',    
'MediumAquaMarine',  'MediumAquaMarine', 'MintCream',         'Orchid',       
'MediumBlue',        'MediumBlue',       'MistyRose',         'PaleGoldenRod',
'MediumOrchid',      'MediumOrchid',     'Moccasin',          'PaleGreen',    

 'PaleTurquoise', 'RosyBrown',   'SlateBlue',   'Turquoise',
 'PaleVioletRed', 'RoyalBlue',   'SlateGray',   'Violet',
 'PapayaWhip',    'SaddleBrown', 'SlateGrey',   'Wheat',
 'PeachPuff',     'Salmon',      'Snow',        'White',
 'Peru',          'SandyBrown',  'SpringGreen', 'WhiteSmoke',
 'Pink',          'SeaGreen',    'SteelBlue',   'Yellow',
 'Plum',          'SeaShell',    'Tan',         'YellowGreen',
 'PowderBlue',    'Sienna',      'Teal',
 'Purple',        'Silver',      'Thistle',
 'Red',           'SkyBlue',     'Tomato']

VALID_COLORS = [COLOR.lower() for COLOR in VALID_COLORS]
                                                                      

class Script(object):
    '''An object representing a complete script object, and all the 
    instructions needed to draw a graph'''
    def __init__(self, text):
        self.xrange = (-1.0, 1.0)
        self.xinterval = 0.2
        self.yrange = (-1.0, 1.0)
        self.yinterval = 0.2
        self.points = []
        self.lines = []
        self.text = []
        self.circles = []
        
        self.symbol_table = SymbolTable()
        self.parse_text(text)
    
    def parse_text(self, text):
        '''Runs through each line of the text and parses it.'''
        for lineno, raw_line in enumerate(text):
            line = raw_line.strip()
            line = self.discard_comments(line)
            if line == '':
                continue
            try:
                command, args, color = self.split_line(line)
                self.switch(command, args, color)
            except ParserException as ex:
                error = 'Error at line {0}: "{1}"\n{2}'.format(
                    lineno + 1, raw_line, str(ex))
                errors.error(error)
            
    def discard_comments(self, line):
        '''Removes comments from a line.'''
        return line.partition(r'%')[0].strip()
        
    def split_line(self, line):
        '''Extracts the command, arguments, and the optional color from 
        a line.'''
        command = None
        args = []
        char_buffer = []
        color = None
        outside_brackets = True
        color_mode = False
        
        for char in line.strip():
            if char == ' ' and command is None:
                command = ''.join(char_buffer)
                char_buffer = []
                continue
            elif char == ',' and outside_brackets:
                args.append(''.join(char_buffer).strip())
                char_buffer = []
                continue
            elif char == '[':
                outside_brackets = False
            elif char == ']':
                outside_brackets = True
            elif char == '"' and outside_brackets:
                outside_brackets = False
            elif char == '"' and not outside_brackets:
                outside_brackets = True
            elif char == '!' and outside_brackets:
                color_mode = True
                args.append(''.join(char_buffer).strip())
                char_buffer = []
                continue
            char_buffer.append(char)
        if color_mode:
            color = ''.join(char_buffer).strip()
        else:
            args.append(''.join(char_buffer).strip())
        if color is not None:
            color = color.lower()
        if command is None:
            command = args[0]
            args = []
            
        self.validate_color(color)
        
        return command, args, color
        
    def validate_color(self, color):
        '''Takes a color, and checks to see if it's a valid English color
        or hex color.'''
        is_html_color = color in VALID_COLORS
        # delay evaluation by making it a lambda.
        is_hex = lambda : re.match(r'\#[0-9a-f]{6}', color) is not None
        if color is not None and not is_html_color and not is_hex():
            error = ''.join([
                '"{0}" is not a valid color.\nSee ',
                'http://www.w3schools.com/html/html_colornames.asp ',
                'for a list of all valid colors, or use hex colors.'])
            raise InvalidColorError(error.format(color))
        
    def switch(self, command, args, color_):
        '''Switches to the appropriate method given the command.'''
        try:
            getattr(self, 'set_{0}'.format(command))(args, color=color_)
        except AttributeError:
            error = 'Unknown command found: {0}'.format(command)
            raise UnknownCommandError(error)
            
    def guard_args(self, name, args, target):
        '''Checks if there are too many arguments for a given command.'''
        if len(args) != target:
            error = ''.join(['The "{0}" command requires {1} value(s).', 
                'You have {2} value(s).\n',
                'Did you remember to add a comma?'])
            error = error.format(name, target, len(args))
            raise WrongNumberOfArgumentsError()
            
    def set_xrange(self, args, color=None):
        '''Sets the min and max x-axis size in a graph'''
        self.guard_args('xrange', args, 2)
        self.xrange = (float(args[0]), float(args[1]))
        
    def set_yrange(self, args, color=None):
        '''Sets the min and max y-axis size in a graph'''
        self.guard_args('yrange', args, 2)
        self.yrange = (float(args[0]), float(args[1]))
        
    def set_xinterval(self, args, color=None):
        '''Sets the interval between the ticks on the x-axis'''
        self.guard_args('xinterval', args, 1)
        self.xinterval = float(args[0])
        
    def set_yinterval(self, args, color=None):
        '''Sets the interval between the ticks on the y-axis'''
        self.guard_args('yinterval', args, 1)
        self.yinterval = float(args[0])
        
    def set_variable(self, args, color=None):
        '''Sets a variable'''
        self.guard_args('variable', args, 2)
        self.symbol_table.add(args[0], self.convert_number(args[1]))
        
    def set_point(self, args, color=None):
        '''Draws a point at the given coord and of the given color'''
        self.guard_args('point', args, 1)
        coord = self.convert_number(args[0])
        self.points.append((coord, color))
    
    def set_line(self, args, color=None):
        '''Draws a line between the given two coords and of the given color'''
        
        self.guard_args('line', args, 2)
        coords = self.convert_number(args[0]), self.convert_number(args[1])
        self.lines.append((coords, color))
    
    def set_text(self, args, color=None):
        '''Writes text at the given coordinate and of the given color'''
        self.guard_args('text', args, 2)
        coord = self.convert_number(args[0])
        text = args[1].strip()[1:-1]
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')
        if color is None:
            color = 'black'
        self.text.append((coord, text, color))
    
    def set_circle(self, args, color=None):
        '''Adds a circle of a given radius and color centered 
        around the origin.'''
        self.guard_args('circle', args, 1)
        radius = float(args[0])
        self.circles.append((radius, color))
            
    def clean_number(self, raw_number):
        '''Takes an input expression (as a string), transforms it into a valid 
        Python expression, and evals it.'''
        number = raw_number.replace('^', '**')
        number = number.replace('i', '1j')
        number = number.replace('p1j', 'math.pi')
        number = number.replace('sqrt', 'math.sqrt')
        try:
            number = eval(number.strip()) # Yes, this is evil, but whatever.
        except Exception: # Also evil, but whatever.
            error = 'Invalid Expression: {0}'.format(raw_number)
            raise InvalidExpressionError(error)
        return number
            
    def convert_number(self, arg):
        '''Converts a string representing a number, in the form of either a 
        coordinate or a complex number, into a valid Coordinate object'''
        arg = arg.strip()
        if arg.startswith('['):
            if not arg.endswith(']'):
                error = 'Coordinate {0} is missing a close bracket "]"'.format(arg)
                raise ImproperCoordinateError(error)
            arg = arg[1:-1]
            args = [self.clean_number(a) for a in arg.split(',')]
            if len(args) < 2:
                error = 'Coordinate {0} is missing a comma'.format(arg)
                raise WrongNumberOfCommasError(error)
            elif len(args) > 2:
                error = 'Coordinate {0} has too many commas'.format(arg)
                raise WrongNumberOfCommasError(error)
            return Coordinate().cartesian(args[0], args[1])
        if arg.startswith('@'):
            return self.symbol_table.fetch(arg[1:])
        else:
            return Coordinate().imaginary(self.clean_number(arg))
        
        
    