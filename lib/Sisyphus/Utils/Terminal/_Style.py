#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sisyphus/Utils/Terminal/_Style.py
Copyright (c) 2023 Regents of the University of Minnesota
Author: Alex Wagner <wagn0033@umn.edu>, Dept. of Physics and Astronomy
"""

from Sisyphus.Utils.utils import objectmethod

class Style:
    
    def __init__(self, *args, **kwargs):
        
        # Property names and the private variables containing those properties
        properties = \
        {
            "fg": "_fg", 
            "bg": "_bg", 
            "underline": "_underline", 
            "underscore": "_underscore",
            "overline": "_overline",
            "bold": "_bold", 
            "faint": "_faint", 
            "italic": "_italic", 
            "blink": "_blink", 
            "inverse": "_inverse", 
            "strike": "_strike",
            "large": "_large",
            "wide": "_wide",
        }
        
        for propname, propvar in properties.items():
            setattr(self, propvar, None)
    
        # I think this was expecting "args" to contain style objects,
        # and this was trying to aggregate the properties of the styles
        # that were passed?    
        for arg in args:
            for propname, propvar in properties.items():
                if getattr(arg, propvar, None) is not None:
                    setattr(self, propvar, getattr(arg, propvar))
        
        # The kwargs spell out the desired properties for our new style
        for propname, propvar in properties.items():
            if propname in ("fg", "bg") and propname in kwargs.keys():
                arg = kwargs[propname]
                if type(arg) is str:
                    if arg.lower() in Style.Colors.keys():
                        value = Style.Colors[arg.lower()]
                    elif arg.startswith("#"):
                        if len(arg) == 4:
                            value = tuple(17*int(arg[x:x+1],16) for x in (1, 2, 3))
                        elif len(arg) == 7:
                            value = tuple(int(arg[x:x+2],16) for x in (1, 3, 5))
                    else:
                        value = (0, 0, 0)
                elif type(arg) is int:
                    value = ( (arg & 0xff0000)>>16, (arg & 0xff00)>>8, arg & 0xff)
                elif type(arg) is tuple:
                    value = arg 
                else:
                    value = (0, 0, 0)
                    
                setattr(self, propvar, value)
            else:    
                setattr(self, propvar, kwargs.get(propname, getattr(self, propvar, None)))
   
    #{{{     
    @objectmethod
    def fg(self, color):
        if self is type:
            return Style(fg=color)
        else:
            return Style(self, fg=color)
    
    @objectmethod
    def bg(self, color):
        if self is type:
            return Style(bg=color)
        else:
            return Style(self, bg=color)
    
    @objectmethod
    def underline(self, status=True):
        if self is type:
            return Style(underline=status)
        else:
            return Style(self, underline=status)
    
    @objectmethod
    def underscore(self, status=True):
        if self is type:
            return Style(underscore=status)
        else:
            return Style(self, underscore=status)
    
    @objectmethod
    def overline(self, status=True):
        if self is type:
            return Style(overline=status)
        else:
            return Style(self, overline=status)

    @objectmethod
    def bold(self, status=True):
        if self is type:
            return Style(bold=status)
        else:
            return Style(self, bold=status)
    
    @objectmethod
    def blink(self, status=True):
        if self is type:
            return Style(blink=status)
        else:
            return Style(self, blink=status)
    
    @objectmethod
    def faint(self, status=True):
        if self is type:
            return Style(faint=status)
        else:
            return Style(self, faint=status)
    @objectmethod
    def italic(self, status=True):
        if self is type:
            return Style(italic=status)
        else:
            return Style(self, italic=status)

    @objectmethod
    def strike(self, status=True):
        if self is type:
            return Style(strike=status)
        else:
            return Style(self, strike=status)

    @objectmethod
    def inverse(self, status=True):
        if self is type:
            return Style(inverse=status)
        else:
            return Style(self, inverse=status)
    
    @objectmethod
    def large(self, status=True):
        if self is type:
            return Style(large=status)
        else:
            return Style(self, large=status, wide=not status and self._wide)

    @objectmethod
    def wide(self, status=True):
        if self is type:
            return Style(wide=status)
        else:
            return Style(self, wide=status, large=not status and self._large)
    #}}}    

    Colors = \
    {#{{{
        "aliceblue":            (240, 248, 255),    "antiquewhite":         (250, 235, 215),
        "aqua":                 (  0, 255, 255),    "aquamarine":           (127, 255, 212),
        "azure":                (240, 255, 255),    "beige":                (245, 245, 220),
        "bisque":               ( 55, 228, 196),    "black":                (  0,   0,   0),
        "blanchedalmond":       (255, 235, 205),    "blue":                 (  0,   0, 255),
        "blueviolet":           (138,  43, 226),    "brown":                (165,  42,  42),
        "burlywood":            (222, 184, 135),    "cadetblue":            ( 95, 158, 160),
        "chartreuse":           (127, 255,   0),    "chocolate":            (210, 105,  30),
        "coral":                (255, 127,  80),    "cornflowerblue":       (100, 149, 237),
        "cornsilk":             (255, 248, 220),    "crimson":              (220,  20,  60),
                    
        "cyan":                 (  0, 255, 255),    "darkblue":             (  0,   0, 139),
        "darkcyan":             (  0, 139, 139),    "darkgoldenrod":        (184, 134,  11),
        "darkgray":             (169, 169, 169),    "darkgreen":            (  0, 100,   0),
        "darkgrey":             (169, 169, 169),    "darkkhaki":            (189, 183, 107),
        "darkmagenta":          (139,   0, 139),    "darkolivegreen":       ( 85, 107,  47),       
        "darkorange":           (255, 140,   0),    "darkorchid":           (153,  50, 204),
        "darkred":              (139,   0,   0),    "darksalmon":           (233, 150, 122),
        "darkseagreen":         (143, 188, 143),    "darkslateblue":        ( 72,  61, 139),
        "darkslategray":        ( 47,  79,  79),    "darkslategrey":        ( 47,  79,  79),
        "darkturquoise":        (  0, 206, 209),    "darkviolet":           (148,   0, 211),
        
        "deeppink":             (255,  20, 147),    "deepskyblue":          (  0, 191, 255),
        "dimgray":              (105, 105, 105),    "dimgrey":              (105, 105, 105),
        "dodgerblue":           ( 30, 144, 255),    "firebrick":            (178,  34,  34),
        "floralwhite":          (255, 250, 240),    "forestgreen":          ( 34, 139,  34),
        "fuchsia":              (255,   0, 255),    "gainsboro":            (220, 220, 220),
        "ghostwhite":           (248, 248, 255),    "gold":                 (255, 215,   0),
        "goldenrod":            (218, 165,  32),    "gray":                 (128, 128, 128),
        "green":                (  0, 128,   0),    "greenyellow":          (173, 255,  47),
        "grey":                 (128, 128, 128),    "honeydew":             (240, 255, 240),
        "hotpink":              (255, 105, 180),    "indianred":            (205,  92,  92),
        
        "indigo":               ( 75,   0, 130),    "ivory":                (255, 255, 240),
        "khaki":                (240, 230, 140),    "lavender":             (230, 230, 250),
        "lavenderblush":        (255, 240, 245),    "lawngreen":            (124, 252,   0),
        "lemonchiffon":         (255, 250, 205),    "lightblue":            (173, 216, 230),
        "lightcoral":           (240, 128, 128),    "lightcyan":            (224, 255, 255),
        "lightgoldenrodyellow": (250, 250, 210),    "lightgray":            (211, 211, 211),
        "lightgreen":           (144, 238, 144),    "lightgrey":            (211, 211, 211),
        "lightpink":            (255, 182, 193),    "lightsalmon":          (255, 160, 122),
        "lightseagreen":        ( 32, 178, 170),    "lightskyblue":         (135, 206, 250),
        "lightslategray":       (119, 136, 153),    "lightslategrey":       (119, 136, 153),
        
        "lightsteelblue":       (176, 196, 222),    "lightyellow":          (255, 255, 224),
        "lime":                 (  0, 255,   0),    "limegreen":            ( 50, 205,  50),
        "linen":                (250, 240, 230),    "magenta":              (255,   0, 255),
        "maroon":               (128,   0,   0),    "mediumaquamarine":     (102, 205, 170),
        "mediumblue":           (  0,   0, 205),    "mediumorchid":         (186,  85, 211),
        "mediumpurple":         (147, 112, 219),    "mediumseagreen":       ( 60, 179, 113),
        "mediumslateblue":      (123, 104, 238),    "mediumspringgreen":    (  0, 250, 154),
        "mediumturquoise":      ( 72, 209, 204),    "mediumvioletred":      (199,  21, 133),
        "midnightblue":         ( 25,  25, 112),    "mintcream":            (245, 255, 250),
        "mistyrose":            (255, 228, 225),    "moccasin":             (255, 228, 181),
        
        "navajowhite":          (255, 222, 173),    "navy":                 (  0,   0, 128),
        "oldlace":              (253, 245, 230),    "olive":                (128, 128,   0),
        "olivedrab":            (107, 142,  35),    "orange":               (255, 165,   0),
        "orangered":            (255,  69,   0),    "orchid":               (218, 112, 214),
        "palegoldenrod":        (238, 232, 170),    "palegreen":            (152, 251, 152),
        "paleturquoise":        (175, 238, 238),    "palevioletred":        (219, 112, 147),
        "papayawhip":           (255, 239, 213),    "peachpuff":            (255, 218, 185),
        "peru":                 (205, 133,  63),    "pink":                 (255, 192, 203),
        "plum":                 (221, 160, 221),    "powderblue":           (176, 224, 230),
        "purple":               (128,   0, 128),    "red":                  (255,   0,   0),
        
        "rosybrown":            (188, 143, 143),    "royalblue":            ( 65, 105, 225),
        "saddlebrown":          (139,  69,  19),    "salmon":               (250, 128, 114),
        "sandybrown":           (244, 164,  96),    "seagreen":             ( 46, 139,  87),
        "seashell":             (255, 245, 238),    "sienna":               (160,  82,  45),
        "silver":               (192, 192, 192),    "skyblue":              (135, 206, 235),
        "slateblue":            (106,  90, 205),    "slategray":            (112, 128, 144),
        "slategrey":            (112, 128, 144),    "snow":                 (255, 250, 250),
        "springgreen":          (  0, 255, 127),    "steelblue":            ( 70, 130, 180),
        "tan":                  (210, 180, 140),    "teal":                 (  0, 128, 128),
        "thistle":              (216, 191, 216),    "tomato":               (255,  99,  71),
        
        "turquoise":            ( 64, 224, 208),    "violet":               (238, 130, 238),
        "wheat":                (245, 222, 179),    "white":                (255, 255, 255),
        "whitesmoke":           (245, 245, 245),    "yellow":               (255, 255,   0),
        "yellowgreen":          (154, 205,  50),
    }#}}}
    
    def __call__(self, text):
        opener = ""
        closer = ""
        
        if self._fg is not None:
            r,g,b = self._fg
            opener += f"38;2;{r};{g};{b};"
            closer = "39;" + closer
        if self._bg is not None:
            r,g,b = self._bg
            opener += f"48;2;{r};{g};{b};"
            closer = "49;" + closer
        if self._underline:
            opener += "4;"
            closer = "24;" + closer
        if self._underscore:
            opener += "21;"
            closer = "24;" + closer
        if self._overline:
            opener += "53;"
            closer = "55;" + closer
        if self._bold:
            opener += "1;"
            closer = "22;" + closer
        if self._faint:
            opener += "2;"
            closer = "22;" + closer
        if self._italic:
            opener += "3;"
            closer = "23;" + closer
        if self._blink:
            opener += "5;"
            closer = "25;" + closer
        if self._strike:
            opener += "9;"
            closer = "29;" + closer
        if self._inverse:
            opener += "7;"
            closer = "27;" + closer
        
        if len(opener) > 0:
            # the [:-1] part is to trim off the last semicolon.
            opener = f"\033[{opener[:-1]}m"
            closer = f"\033[{closer[:-1]}m"

        # These have to be handled separately becaunderscoree they are not
        # CSI (i.e. ESC[ ) codes ending with 'm'
        WIDE="\033#6"
        LARGETOP="\033#3"
        LARGEBOTTOM="\033#4"
        if self._wide:
            return f"\033#6{opener}{text}{closer}"
        elif self._large:
            lines = text.split("\n")
            trailing_newline = False
            if len(lines) > 1 and len(lines[-1])==0:
                lines.pop()
                trailing_newline = True
            result = []
            for line in lines:
                result.append(f"{LARGETOP}{line}")
                result.append(f"{LARGEBOTTOM}{line}")
            result = [opener, "\n".join(result), closer]
            if trailing_newline:
                result.append("\n")
            return "".join(result)
            #return  f"{opener}{LARGETOP}{text}\n{LARGEBOTTOM}{text}{closer}"
        else:
            return f"{opener}{text}{closer}"

#Style.ul = Style(ul=True)
#Style.bold = Style(bold=True)
#Style.faint = Style(faint=True)
#Style.blink = Style(blink=True)
#Style.strike = Style(strike=True)
#Style.inverse = Style(inverse=True)
#Style.italic = Style(italic=True)

# Some globally useful styles scripts could use
Style.info = Style()
Style.notice = Style.fg("royalblue")
Style.warning = Style.fg("goldenrod")
Style.error = Style.fg("red")
Style.success = Style.fg("green")

###############################################################################

def highlight(text, substring, *, match_case=False, style=Style.inverse()):

    sub_len = len(substring)

    if match_case:
        cap_text = text
        cap_sub = substring
    else:
        cap_text = text.upper()
        cap_sub = substring.upper()

    parts = []

    last_end = 0
    while True:
        match_start = cap_text.find(cap_sub, last_end)
        if match_start == -1:
            break
        parts.append(text[last_end:match_start])
        next_end = match_start + sub_len
        parts.append(style(text[match_start:next_end]))
        last_end = next_end
    parts.append(text[last_end:]) 

    return "".join(parts)
Style.highlight = highlight

###############################################################################

def fix_emoji_widths(s):
    """If a string contains emojis, fix the ones with bad widths

    I don't know about other terminals, but Windows Terminal messes up
    the widths of some emojis. Some are display 2-characters wide, while
    others are only 1-character wide. Insert an extra space in the 1-char
    emojis, so that it takes up 2 characters.
    """
    return "".join([ c if c not in BAD_WIDTH_CHARS else (c+" ") for c in s ]) 
Style.fix_emoji_widths = fix_emoji_widths

BAD_WIDTH_CHARS = [ 
    chr(c) for c in [
        # 0x1f000
        *[i for i in range(0x1f000, 0x1f100) if i not in (0x1f004, 0x1f0cf)],
        # 0x1f100
        *range(0x1f100, 0x1f18e), 0x1f18f, 0x1f191, *range(0x1f19b, 0x1f1e6),

        # 0x1f200
        *range(0x1f203, 0x1f210), *range(0x1f23c, 0x1f240), *range(0x1f249, 0x1f250),
        *range(0x1f252, 0x1f260), *range(0x1f266, 0x1f300),

        # 0x1f300
        *range(0x1f321, 0x1f32d), 0x1f336, 0x1f37d, *range(0x1f394, 0x1f3a0),
        *range(0x1f3cb, 0x1f3cf), *range(0x1f3d4, 0x1f3e0), *range(0x1f3f1, 0x1f3f4),
        *range(0x1f3f5, 0x1f3f8),

        # 0x1f400
        0x1f441, 0x1f43f, 0x1f4fd, 0x1f4fe,

        # 0x1f500
        *range(0x1f53e, 0x1f54b), 0x1f54f, *range(0x1f568, 0x1f57a),
        *range(0x1f57b, 0x1f595), *range(0x1f597, 0x1f5a4), *range(0x1f5a5, 0x1f5fb),

        # 0x1f600
        *range(0x1f650, 0x1f680), *range(0x1f6c6, 0x1f6cc), 0x1f6cd, 0x1f6ce, 0x1f6cf,
        0x1f6d3, 0x1f6d4, 0x1f6d8, 0x1f6d9, 0x1f6da, 0x1f6db, *range(0x1f6e0, 0x1f6eb),
        *range(0x1f6ed, 0x1f6f4), *range(0x1f6fd, 0x1f700),

        # 0x1f700
        *range(0x1f700, 0x1f7e0), *range(0x1f7ec, 0x1f7f0), *range(0x1f7f1, 0x1f800),

        # 0x1f800
        *range(0x1f800, 0x1f900),

        # 0x1f900
        *range(0x1f900, 0x1f90c), 0x1f93b, 0x1f946,

        # 0x1fa00
        *range(0x1fa00, 0x1fa70), *range(0x1fa7d, 0x1fa80), *range(0x1fa89, 0x1fa90),
        0x1fabe, *range(0x1fac6, 0x1face), *range(0x1fadc, 0x1fae0),
        *range(0x1fae9, 0x1faf0), *range(0x1faf9, 0x1fb00),

        # 0x1fb00 - 0x20000
        # Maybe let's not worry about the rest
        #*range(0x1fb00, 0x20000),
    ]
]

###############################################################################

def main():
    import textwrap

    #print("\033[1;2]\033[4mUnderline\033[0m")
    warn = Style.fg("yellow").bg("green")

    print(warn("yellow on green"))
    print()    
    print(Style.underline()("\033[1;2]underline"))
    print()    
    print(Style.underscore()("underscore"))
    print()    
    print(Style.overline()("overline"))
    print()    
    print(Style.underscore().overline()("underscore-overline"))
    print()    
    print(Style.fg("#336699")("blue"))
    print()    
    print(Style.bg("green")("green"))
    print()    
    
    print(Style.blink(True)("blink"))
    print()    
    print(Style.bold(True)("bold"))
    print()    
    print(Style.faint(True)("faint"))
    print()    

    red = Style.fg("red")
    faintred = red.faint()
    boldred = red.bold()

    print(" ".join([ faintred("faintred"), red("red"), boldred("boldred") ]))
    print()
    print(Style.strike()("strike"))
    print()    
    print(Style.inverse()("inverse"))
    print()    
    print(Style.italic()("italic"))
    print()    
    print(Style.large()("Large"))   
    print()
    print(Style.wide()("Wide"))
    print()
    print(Style.highlight("ABCDE", "BCD", style=Style.fg("tomato").inverse()))
    print()
    multiple = Style.fg("cornflowerblue").underline().overline().large()
    print(multiple("\U0001f600 blue, underlined, overlined, large"))
    print()
 
    s = []
    for colorname in Style.Colors.keys():
        s.append(Style.fg(colorname)(colorname))
        #s.append(colorname)
    text = " ".join(s)
    #print(s)
    #print(text)
    print("\n".join(textwrap.wrap(text, width=300)))

    # note, this isn't all the emojis, but we'll know if the fix worked if
    # we try these
    emojis = \
        [
            "".join([ chr(c) for c in range(x, x+16)]) 
            for x in range(0x1f300, 0x1f400, 0x10) 
        ]
    for line in emojis:
        print(Style.large()(fix_emoji_widths(line)))


if __name__ == "__main__":
    main()

'''

some useful console codes that maybe I'll use in the future:


ESC [ ? 5 h
ESC [ ? 5 l

    Set/Reset reverse video mode ... might be useful to "flash" the screen

ESC ] 0 ; <text> BEL

    Sets the title of the terminal. BEL probably \a or \007

ESC [ n A       Cursor up
ESC [ n B       Cursor down
ESC [ n C       Cursor forward
ESC [ n D       Cursor back
ESC [ n E       Cursor next line
ESC [ n F       Cursor previous line
ESC [ n G       Cursor horizontal absolute
ESC [ n ; m H   Cursor position
ESC [ 0 J       Clear from cursor to end of screen (0 may be omitted)
ESC [ 1 J       Clear from cursor to beginning of screen
ESC [ 2 J       Clear the screen (but not the entire buffer)
ESC [ 3 J       Clear the screen and the buffer
ESC [ 0 K       Erase to end of line (0 may be omitted)
ESC [ 1 K       Erase to beginning of line
ESC [ 2 K       Erase entire line
ESC [ n S       Scroll up
ESC [ n T       Scroll down

ESC [ 6n        Report the cursor position 

ESC # 3         Double-size characters on this line, top half
ESC # 4         Double-size characters on this line, bottom half
ESC # 5         normal-size characters on this line
ESC # 6         Double-wide characters on this line (discard 2nd half of line)























'''
