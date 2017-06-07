'''
Created on Sep 9, 2013

@author: Mikael
'''
import math
from collections import OrderedDict, defaultdict
from contextlib import contextmanager


class SVG(object):
    
    def __init__(self, prescript = None, unit = "px", style = None):
        self.unit = unit
        self.layers = OrderedDict()
        self.elements = []
        self.style = defaultdict(dict)
        
        if style:
            self.style.update(style)
        if prescript:
            self.custom(prescript)
        
    def __getitem__(self, key):
        if key not in self.layers:
            self.layers[key] = SVG()
            
        return self.layers[key]

    @contextmanager
    def group(self, transform = None, cls = None, style = None, attrs = None):
        """
        Example
        -------
        with svg[layer].group(transform = "rotate(45)"):
            svg[layer].rect(10, 10, 10, 10)
        """
        transform_str = 'transform="%s" ' % transform if transform else ''
        payload = ''.join(transform_str, self._make_payload(cls, style, attrs))

        self.elements.append("""<g %s>""" % payload)
        yield
        self.elements.append("""</g>""")

    def declare_layers(self, names):
        """
        Layers will be in the order they are first used. Use
        this method declare the order of all layers initially
        if that is more convenient.

        Example
        -------
        svg.declare_layers(["foo", "bar"])
        svg["bar"].circle(...)
        svg["foo"].circle(...)
        #: bar is drawn after foo

        Returns
        -------
        self
        """
        for name in names:
            self[name]
        return self

    def marker(
        self,
        m_id,
        svg, 
        viewbox = "0 0 10 10", 
        refx = "0", 
        refy = "3",
        width = "4",
        height = "3",
        **kwargs
    ):
        """
        """
        markerUnits = "strokeWidth",
        orient = "auto",
        kwargs.update(dict(
            viewBox = viewbox, 
            refX = refx, 
            refY = refy,
            markerWidth = width,
            markerHeight = height,
        ))
        kwargs.setdefault("markerUnits", "strokeWidth")
        kwargs.setdefault("orient", "auto")
        payload = " ".join('%s="%s"' % (k, v) for k, v in kwargs.iteritems())

        code = """
            <marker id="%s" %s>
                %s
            </marker>
        """ % (m_id, payload, svg._body_lines())
        self.elements.append(code)
        return self

    def custom(self, svg_code):
        """
        Insert custom svg code in the svg body.

        Example
        -------
        svg.custom('''
            <marker ...>
                <path ... />
            </marker>
        ''')

        Returns
        -------
        self
        """
        self.elements.append(custom)
        return self

    def line(self, x1, y1, x2, y2, cls = None, style = None):
        """
        Draws a line.

        Returns
        -------
        self
        """
        x1, y1, x2, y2 = self._units(x1, y1, x2, y2)
        
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._make_style(style) if style else ''
        
        self.elements.append("""
            <line x1="%s" y1="%s" x2="%s" y2="%s" %s%s/>
        """.strip() % (
            x1, y1, x2, y2, cls_str, style_str
        ))
        return self
        
    def path(self, cmd, cls = None, style = None):
        """
        Draws a path.

        Returns
        -------
        self
        """
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._make_style(style) if style else ''
        cmd_str = ' '.join( str(x) for x in cmd )
        
        self.elements.append("""
            <path d="%s" %s%s/>
        """.strip() % (cmd_str, cls_str, style_str)
        )
        return self

    def polygon(self, pointlist, cls = None, style = None, attrs = None):
        """
        Draws a closed polygon.

        Exammple
        --------
        svg.polygon([(1,1), (1,2), (2,2)], style = { "fill": "#ff0000" })

        Returns
        -------
        self
        """
        payload = self._make_payload(cls, style, attrs)
        pts_str = ' '.join('%s,%s' % (x, y) for x, y in pointlist)
        self.elements.append("""<polygon points="%s" %s/>""" % (pts_str, payload))
        return self
        
    def pie_slice(self, x, y, r, t0, t1, cls = None, style = None):
        tr0 = math.radians(t0)
        tr1 = math.radians(t1)
        
        x0 = x + r * math.cos(tr0)
        y0 = y + r * math.sin(tr0)
        x1 = x + r * math.cos(tr1)
        y1 = y + r * math.sin(tr1)
        
        laf = int(abs(t1 - t0) > 180)
        
        self.path(['M', x, y, 'L', x0, y0, 'A', r, r, 0, laf, 1, x1, y1, 'Z'], cls, style)

    def rect(self, x, y, w, h, cls = None, style = None):
        x, y, w, h = self._units(x, y, w, h)
        
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._make_style(style) if style else ''
        
        self.elements.append("""
            <rect x="%s" y="%s" width="%s" height="%s" %s%s/>
        """.strip() % (
            x, y, w, h, cls_str, style_str
        ))
        
    def rect2(self, x1, y1, x2, y2, cls = None, style = None):
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        x = min(x1, x2)
        y = min(y1, y2)
        
        return self.rect(x, y, w, h, cls, style)
    
    def circle(self, x, y, r, cls = None, style = None):
        x, y, r = self._units(x, y, r)
        
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._make_style(style) if style else ''
        
        self.elements.append("""
            <circle cx="%s" cy="%s" r="%s" %s%s/>
        """.strip() % (
            x, y, r, cls_str, style_str
        ))
        
    def crpolygon(self, x, y, r, n, t0 = 0, cls = None, style = None):
        """
        Draws a convex regular polygon (triangle, square, pentagon, ...)
        centered at x, y with radius r and using n corners.
        """
        t0 = 2 * math.pi * t0 / 360.0
        dt = 2 * math.pi / n 
        pts = []
        
        for idx in xrange(n + 1):
            dx = x + r * math.cos(t0)
            dy = y + r * math.sin(t0)
            t0 += dt
            
            pts.append('M' if idx == 0 else 'Z' if idx == n else 'L')
            pts.append('%s %s' % (dx, dy))
            
        self.path(pts, cls = cls, style = style)
        
    def text(self, x, y, txt, cls = None, style = None, tags = None):
        x, y = self._units(x, y)
        
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._make_style(style) if style else ''
        tag_str = (' '.join( '%s="%s"' % (k, v) for k, v in tags.iteritems() ) + ' ') if tags else ''

        self.elements.append("""
            <text x="%s" y="%s" %s%s%s>%s</text>
        """.strip() % (
            x, y, cls_str, style_str, tag_str, txt
        ))
        
    def _units(self, *args):
        u = self.unit
        return tuple( '%s%s' % (a, u) for a in args )
        
    def _make_style(self, mixed):
        if isinstance(mixed, dict):
            return ' '.join( '%s: %s;' % (k, v) for k, v in mixed.iteritems() )
        return str(mixed)

    def _make_attrs(self, mixed):
        if isinstance(mixed, dict):
            return ''.join('%s="%s" ' % (k, v) for k, v in mixed.iteritems())
        return str(mixed)

    def _make_payload(self, cls, style, attrs):
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._make_style(style) if style else ''
        attr_str = self._make_attrs(attrs) if attrs else ''
        payload = ''.join([attr_str, cls_str, style_str])
        return payload
        
    def _style_lines(self):
        if isinstance(self.style, str):
            yield self.style
        
        else:
            for cls in self.style:
                yield "%s {" % str(cls)
                
                for key, value in self.style[cls].iteritems():
                    yield "    %s: %s;" % (key, value)
    
                yield "}"

    def _body_lines(self):
        for name in self.layers:
            yield '<g id="%s">' % name
            
            for elem in self.layers[name]._body_lines():
                yield '    %s' % elem
                
            yield "</g>"
            
        for elem in self.elements:
            yield "%s" % elem
            
    def make(self, width = 1500.0, height = 1000.0):
        style = list(self._style_lines())
        body = list(self._body_lines())
        
        return make_svg(width, height, style, body)
    
    def write(self, file_name, width = 1500.0, height = 1000.0):
        with open(file_name, 'w+') as fh:
            fh.write(self.make(width, height))
            

def make_svg(width, height, style, body):
    '''
    A standard template for svg images.
    '''
    style = '\n'.join(style) if isinstance(style, list) else style
    body = '\n'.join(body) if isinstance(body, list) else body
    
    style = style.encode('utf-8')
    body = body.encode('utf-8')
    
    style_block = '' if not style else '''<defs>
    
    <style type="text/css"><![CDATA[
%s\n    ]]></style>\n</defs>''' % style
    return '''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%s" height="%s" version="1.1" xmlns="http://www.w3.org/2000/svg">
%s\n%s\n</svg>\n''' % (width, height, style_block, body )


