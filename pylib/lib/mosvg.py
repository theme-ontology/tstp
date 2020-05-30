# -*- coding: utf-8 -*-
'''
Created on Sep 9, 2013
@author: Mikael Onsjö

MIT License

Copyright (c) 2019 odinlake

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import math
from collections import OrderedDict, defaultdict
from contextlib import contextmanager


class SVG(object):
    def __init__(self, style=None, unit="px"):
        """
        Represents an SVG image that is built up piece by piece. Provides
        a variety of convenience API.

        Example
        -------
        svg = SVG({'circle': {'fill': 'red'}})
        svg.circle(100, 100, 50).write("foo.svg", 200, 200)
        """
        self._meta = SVGHelper(self)
        self.layers = OrderedDict()
        self.style = defaultdict(dict)
        self.stock = SVGStockObjects
        self.unit = unit
        self.defs = []
        self.elements = []
        self.masks = {}
        self.add_style(style or {})

    def __getitem__(self, key):
        if key not in self.layers:
            self.layers[key] = SVG()
        return self.layers[key]

    def add_style(self, style, keepdefault=False):
        """
        Add styles to this svg definition.
        
        Parameters
        ----------
        style: {str=>{str=>str}} 
            A dictionary of dictionaries that defines css styles.
        keepdefault: bool
            If True, do not overwrite any keys already present.
        """
        for key, styledict in style.items():
            target = self.style[key]
            for k, v in styledict.items():
                if keepdefault:
                    target.setdefault(k, v)
                else:
                    target[k] = v
        return self

    @contextmanager
    def group(self, transform=None, cls=None, style=None, attrs=None):
        """
        Example
        -------
        with svg[layer].group(transform = "rotate(45)"):
            svg[layer].rect(10, 10, 10, 10)
        """
        transform_str = 'transform="%s" ' % transform if transform else ''
        payload = ''.join([transform_str, self._meta.make_payload(cls, style, attrs)])
        self.elements.append("""<g %s>""" % payload)
        yield
        self.elements.append("""</g>""")

    @contextmanager
    def clip(self, name=None, attrs=None):
        """
        Draw within a clipping mask. The maks may be defined within the first context
        then reused later on.

        Example
        -------
        with svg[layer].clip("clipid") as mask:
            mask.circle(100, 100, 50)
            svg[layer].circle(50, 50, 100)
        with svg[layer].clip("clipid"):
            svg[layer].circle(150, 150, 100)
        """
        if name is None:
            while name is None or name in self.masks:
                name = "__auto__clip%d" % idx
                idx += 1
        if name not in self.masks:
            self.masks[name] = SVG()
        with self.group(style={"clip-path": "url(#%s)" % name}, attrs=attrs):
            yield self.masks[name]

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

    def marker(self, m_id, svg, scale=1, viewbox=(-10, -10, 20, 20), refx=1, refy=0, width=10, height=10, **kwargs):
        """
        Defines an SVG marker that can later be used as, for example, arrow heads.
        """
        kwargs.update(dict(
            viewBox=" ".join(map(str, viewbox)),
            refX=refx,
            refY=refy,
            markerWidth=width * scale,
            markerHeight=height * scale,
        ))
        kwargs.setdefault("markerUnits", "strokeWidth")
        kwargs.setdefault("orient", "auto")
        payload = " ".join('%s="%s"' % (k, v) for k, v in kwargs.items())
        body = '\n'.join(svg.meta.body_lines())
        code = """<marker id="%s" %s>\n%s\n</marker>""" % (m_id, payload, body)
        self.defs.append(code)
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
        self.elements.append(svg_code)
        return self

    def line(self, x1, y1, x2, y2, markers=(None, None), cls=None, style=None, attrs=None):
        """
        Draws a line.

        Returns
        -------
        self
        """
        if any(markers):
            attrs = dict(attrs or {})
        if markers[0]:
            attrs['marker-start'] = 'url(#%s)' % markers[0]
        if markers[1]:
            attrs['marker-end'] = 'url(#%s)' % markers[1]
        x1, y1, x2, y2 = self._meta.units(x1, y1, x2, y2)
        payload = self._meta.make_payload(cls, style, attrs)
        self.elements.append("""
            <line x1="%s" y1="%s" x2="%s" y2="%s" %s/>
        """.strip() % (
            x1, y1, x2, y2, payload,
        ))
        return self

    def path(self, cmd, cls=None, style=None):
        """
        Draws a path.

        Returns
        -------
        self
        """
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._meta.make_style(style) if style else ''
        cmd_str = ' '.join(str(x) for x in cmd)
        self.elements.append("""
            <path d="%s" %s%s/>
        """.strip() % (cmd_str, cls_str, style_str))
        return self

    def polygon(self, pointlist, cls=None, style=None, attrs=None):
        """
        Draws a closed polygon from a list of points.

        Exammple
        --------
        svg.polygon([(1,1), (1,2), (2,2)], style = { "fill": "#ff0000" })

        Returns
        -------
        self
        """
        payload = self._meta.make_payload(cls, style, attrs)
        pts_str = ' '.join('%s,%s' % (x, y) for x, y in pointlist)
        self.elements.append("""<polygon points="%s" %s/>""" % (pts_str, payload))
        return self

    def polyline(self, pointlist, cls=None, style=None, attrs=None):
        """
        Draws an open "polyline" from a list of points.

        Exammple
        --------
        svg.polygon([(1,1), (1,2), (2,2)], style = { "fill": "#ff0000" })

        Returns
        -------
        self
        """
        payload = self._meta.make_payload(cls, style, attrs)
        pts_str = ' '.join('%s,%s' % (x, y) for x, y in pointlist)
        self.elements.append("""<polyline points="%s" %s/>""" % (pts_str, payload))
        return self

    def pie_slice(self, x, y, r, t0, t1, cls=None, style=None):
        """
        Draw circular pie-slice from circle center, radius, and angle interval.
        """
        tr0 = math.radians(t0)
        tr1 = math.radians(t1)
        x0 = x + r * math.cos(tr0)
        y0 = y + r * math.sin(tr0)
        x1 = x + r * math.cos(tr1)
        y1 = y + r * math.sin(tr1)
        laf = int(abs(t1 - t0) > 180)
        self.path(['M', x, y, 'L', x0, y0, 'A', r, r, 0, laf, 1, x1, y1, 'Z'], cls, style)
        return self

    def rect(self, x, y, w, h, cls=None, style=None):
        """
        Draws a rectangle by a corner coordinate, width, and height.

        :param x:
        :param y:
        :param w:
        :param h:
        :param cls:
        :param style:
        :return:
        """
        x, y, w, h = self._meta.units(x, y, w, h)
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._meta.make_style(style) if style else ''
        self.elements.append("""
            <rect x="%s" y="%s" width="%s" height="%s" %s%s/>
        """.strip() % (
            x, y, w, h, cls_str, style_str
        ))

    def rect2(self, x1, y1, x2, y2, cls=None, style=None):
        """
        Draws a rectangle from the coordinates of two diagonally
        opposite corners.

        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param cls:
        :param style:
        :return:
        """
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        x = min(x1, x2)
        y = min(y1, y2)
        return self.rect(x, y, w, h, cls, style)

    def circle(self, x, y, r, cls=None, style=None):
        """
        Draws a circle centered at (x, y) with radius r.

        :param x:
        :param y:
        :param r:
        :param cls:
        :param style:
        :return:
        """
        x, y, r = self._meta.units(x, y, r)
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._meta.make_style(style) if style else ''
        self.elements.append("""
            <circle cx="%s" cy="%s" r="%s" %s%s/>
        """.strip() % (
            x, y, r, cls_str, style_str
        ))
        return self

    def crpolygon(self, x, y, r, n, t0=0, cls=None, style=None):
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
        self.path(pts, cls=cls, style=style)

    def text(self, x, y, txt, cls=None, style=None, tags=None, linespacing=10, valign=1.0):
        """
        Draws text at a coordinate.

        :param x:
        :param y:
        :param txt:
        :param cls:
        :param style:
        :param tags:
        :return:
        """
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self._meta.make_style(style) if style else ''
        tag_str = (' '.join('%s="%s"' % (k, v) for k, v in tags.items()) + ' ') if tags else ''
        lines = txt.split("\n")
        hh = linespacing * len(lines)
        y -= (hh - linespacing) * valign
        for line in lines:
            xx, yy = self._meta.units(x, y)
            self.elements.append("""
                <text x="%s" y="%s" %s%s%s>%s</text>
            """.strip() % (
                xx, yy, cls_str, style_str, tag_str, line
            ))
            y += linespacing
        return self

    def xychart(self, x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax, baseline_reference=None):
        """
        Create a simple plot area with x/y axes.

        Returns
        -------
        An SVGPlot component object on which data can be more easily plotted.
        """
        plot = SVGPlot(self, x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax, baseline_reference=baseline_reference)
        self.elements.append(plot)
        return plot

    def make(self, width=1500.0, height=1000.0):
        """
        Return SVG code as a utf-8 encoded string/binary.
        """
        return self._meta.template1(width, height).encode('utf-8')

    def write(self, file_name, width=1500.0, height=1000.0):
        """
        Write SVG code to a text file.
        """
        with open(file_name, 'wb+') as fh:
            fh.write(self.make(width, height))

    def finalize(self):
        """
        Used by subclasses that need to do something final before rendering.
        """
        return self


class SVGPlot(SVG):
    iid = 0

    #: set this to approximate font-height if you wish text to be aligned using such
    #: an approximation instead of CSS alignment-baseline property (which IE doesn't support)
    #:      baseline_reference = None

    def __init__(self, parent, x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax, name="plot", baseline_reference=None):
        dx = x2 - x1
        dy = y2 - y1
        dxv = float(xvmax - xvmin)
        dyv = float(yvmax - yvmin)
        self.name = name
        self.geom = (x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax)
        self.v2x = lambda v: x1 + (v - xvmin) / dxv * dx
        self.v2y = lambda v: y2 - (v - yvmin) / dyv * dy
        self.plotcmds = []
        self._plotstack = None
        self._finalized = False
        self._baseline_reference = baseline_reference
        super(SVGPlot, self).__init__(unit=parent.unit, style=self.default_style())
        self._config = dict(self.default_config())
        self._iid = SVGPlot.iid
        SVGPlot.iid += 1

    def config(self, cfg):
        """
        Update the general plot configuration.
        """
        self._config.update(cfg)
        return self

    def getcfg(self, key, default=None):
        """
        Get a config parameter.
        """
        return self._config.get(key, default)

    def default_config(self):
        """
        A simple default plot configuration.
        """
        return {
            "xtype": "scalar",
            "ytype": "scalar",
            "xtick-delta": 50, 
            "ytick-delta": 20, 
            "xtick-format": '{:g}', 
            "ytick-format": '{:g}',
        }

    def default_style(self):
        """
        A simple default plot style.
        """
        bref = self._baseline_reference
        dd = {
            '': {
            },
            "text": {
                "font": "10px sans-serif",
            },            
            "rect.plotarea": {
                "fill": "none",
                "stroke": "black",
            },
            "line.axis": {
                "stroke": "black"
            },
            "line.tick": {
                "stroke": "black"
            },
            "text.axis": {
                "fill": "black",
            },
            "text.xtick": {
                "text-anchor": "middle",
            },
            "text.ytick": {
                "text-anchor": "end",
            },
            "line.grid": {
                "stroke": "#888888",
                "stroke-opacity": 0.5,
                "stroke-dasharray": "1 1",
            },
            ".dataline": {
                "fill": "none",
            },
            ".datapoint": {
                "stroke": "#ffffff",
            },
            ".datapointlabel": {
                "text-anchor": "middle",
            },
            ".datapointlabelmarker": {
                "stroke": "none",
                "fill": "#000000",
            },
        }
        # because IE sucks user may want to override this for a crappier method
        if bref is None:
            dd["text.xtick"].update({
                "alignment-baseline": "text-before-edge",
                "dominant-baseline": "text-before-edge",
            })
            dd["text.ytick"].update({
                "alignment-baseline": "central",
                "dominant-baseline": "central",
            })

        n = "." + self.name
        p = n + " "
        return {(p + k if k else n) : v for k, v in dd.items()}

    def finalize(self):
        """
        Used by subclasses that need to do something final before rendering.
        """
        if not self._finalized:
            self._do_plot()
            super(SVGPlot, self).finalize()
            self._finalized = True
        return self

    def get_ticks(self, dim="x"):
        """
        """
        (x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax) = self.geom
        axis_type = self.getcfg(dim + "type", "scalar")
        delta = self.getcfg(dim + "tick-delta", 50)
        if dim.startswith("x"):
            vmin, vmax = xvmin, xvmax
            dv = float(xvmax - xvmin)
            nn = max(2, int((x2 - x1) / delta))
        else:
            vmin, vmax = yvmin, yvmax
            dv = float(yvmax - yvmin)
            nn = max(2, int((y2 - y1) / delta))
        if axis_type == 'scalar':
            ticksv = self._meta.float_tick_locations(vmin, vmax, dv / nn)
        elif axis_type == 'enum':
            c, f = math.ceil, math.floor
            ticksv = range(int(c(vmin)), int(f(vmax)) + 1, int(c(dv / nn)))

        return ticksv

    def plotarea(self):
        """
        Draw the grid/axes and ticks.
        """
        (x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax) = self.geom
        dxv = float(xvmax - xvmin)
        dyv = float(yvmax - yvmin)
        v2x = self.v2x
        v2y = self.v2y
        xticksv = self.get_ticks("x")
        yticksv = self.get_ticks("y")
        xtick_fmt = self.getcfg("xtick-format")
        ytick_fmt = self.getcfg("ytick-format")

        bref = self._baseline_reference
        xtickoffsety = 0 if bref is None else int(bref)
        ytickoffsety = 0 if bref is None else int(bref / 3)

        with self.group(cls=self.name):
            self.rect2(x1, y1, x2, y2, cls='plotarea')
            self.line(x1, y2, x2, y2, cls='axis xaxis')
            self.line(x1, y1, x1, y2, cls='axis yaxis')
            for xtv in xticksv:
                xr = (xtv - xvmin) / dxv
                xx = x1 + (x2 - x1) * xr
                xx = round(v2x(xtv))
                self.line(xx, y2, xx, y2 + 3, cls='tick xtick')
                self.line(xx, y1, xx, y2, cls='grid xgrid')
                self.text(xx, y2 + 3 + xtickoffsety, xtick_fmt.format(xtv), cls='tick xtick')
            for ytv in yticksv:
                yr = (ytv - yvmin) / dyv
                yy = y1 + (y2 - y1) * yr
                yy = round(v2y(ytv))
                self.line(x1, yy, x1 - 3, yy, cls='tick ytick')
                self.line(x1, yy, x2, yy, cls='grid ygrid')
                self.text(x1 - 5, yy + ytickoffsety, ytick_fmt.format(ytv), cls='tick ytick')

        return self

    @contextmanager
    def stack(self):
        self._plotstack = []
        yield self
        stack, self._plotstack = self._plotstack, None
        basedata = None
        for args, kwargs in stack:
            data = list(args[0])
            ys = data[1]
            if basedata is None:
                baseyv = kwargs['baseyv']
                basedata = kwargs['basedata'] or [ baseyv for _ in ys ]
            kwargs['basedata'] = basedata
            ys = [ y + by for (y, by) in zip(ys, basedata) ]
            data[1] = ys
            args = (data,) + args[1:]
            self.plot(*args, **kwargs)
            basedata = ys

    def plot(self, data, basedata=None, shape="bar", baseyv=0.0, cls=None, style=None):
        args = (data,)
        kwargs = dict(basedata=basedata, shape=shape, baseyv=baseyv, cls=cls, style=style)
        if self._plotstack is not None:
            self._plotstack.append((args, kwargs))
        else:
            self.plotcmds.append((args, kwargs))

    def _do_plot(self):
        v2x = self.v2x
        v2y = self.v2y
        (x1, y1, x2, y2, xvmin, xvmax, yvmin, yvmax) = self.geom
        clipid = "plotdata{}".format(self._iid)

        with self.clip(clipid) as mask:
            mask.rect2(x1 + 1, y1 + 1, x2, y2)

        with self.group(cls=self.name):
            for args, kwargs in self.plotcmds:
                data = args[0]
                baseyv = kwargs['baseyv']
                basedata = kwargs['basedata']
                shape = kwargs['shape']
                cls = kwargs['cls']
                style = kwargs['style']
                pre = (xvmin, baseyv, baseyv)
                post = (xvmax, baseyv, baseyv)
                xs, ys = data[:2]
                baseys = [ basedata[i] if basedata else baseyv for i in range(len(xs)) ]
                linepts = []
                ptiter = self._meta.iter_segments([xs, ys, baseys], pre, post)

                with self.clip(clipid):
                    for idx, (d0, d1, d2) in enumerate(ptiter):
                        xx, yy, yb = v2x(d1[0]), v2y(d1[1]), v2y(d1[2])
                        px, nx = v2x(d0[0]), v2x(d2[0])
                        yb = max(min(yb, y2), y1)
                        lx = (xx + px) / 2 if idx > 0 else px
                        rx = (xx + nx) / 2 if idx < len(xs) - 1 else nx
                        linepts.append((xx, yy))

                        if shape == "bar":
                            self.rect2(lx, yy, rx, yb, cls="databar "+cls, style=style)

                    if shape in ("line", "area"):
                        self.polyline(linepts, cls="dataline "+cls, style=style)
                    if shape in ("line", "area", "scatter"):
                        for x, y in linepts:
                            self.circle(x, y, 3, cls="datapoint "+cls, style=style)
                        if len(data) > 2 and data[-1] and isinstance(data[-1][0], str):
                            for (x, y), label in zip(linepts, data[-1]):
                                if label:
                                    self.text(x, y-3, label, cls="datapointlabel " + cls, style=style)
                                    self.circle(x, y, 1, cls="datapointlabelmarker "+cls, style=style)


class SVGStockObjects(object):
    @classmethod
    def arrowhead(cls, base = 20 / 3 ** 0.5, height = 10):
        """
        Creates an arrow head pointing rightwards of given base and height 
        with centre base-line at origo. The default parameter yields an
        equilateral triangle.
        """
        svg = SVG()
        b2, h = base / 2, height
        svg.path(["M 0", -b2, "L", h, "0 L 0", b2, "z", ])
        return svg


class SVGHelper(object):
    def __init__(self, parent):
        self.parent = parent

    def iter_segments(self, data, pre=None, post=None):
        """
        Plot helper to iterate over the 3-point segments of a curve.
        To plot points, for example, simply "draw" the second item in
        each tuple yielded. To draw line you might "draw" the first-
        -to-second item whenever they are not None, etc. To draw a "bar"
        you might want all three items.
        """
        pre = pre or [None for _ in data]
        post = post or [None for _ in data]
        prev = None
        for dp in zip(*data):
            if prev is not None:
                yield prev + (dp,)
                prev = (prev[1], dp)
            else:
                prev = (pre, dp)
        if prev is not None:
            yield prev + (post,)

    def float_tick_locations(self, vmin, vmax, vdelta):
        """
        Plot helper to choose "nice" locations for ticks.
        """
        locations = []
        vrange = vmax - vmin
        delta = 10 ** math.floor(math.log10(vdelta))
        while delta > vdelta:
            delta /= 10.0
        while delta * 10 < vdelta:
            delta *= 10
        decimals = int(-math.floor(math.log10(delta)))
        for dm in [ 1, 2, 5, 10 ]:
            if delta * dm >= vdelta:
                delta *= dm
                break
        if vrange > 2 * delta:
            vvmin = round(vmin, decimals)
            vvmax = round(vmax, decimals)
            vv = vvmin
            while vv <= vmax:
                locations.append(vv)
                vv += delta
        if len(locations) > 2:
            return locations
        return [vmin, vmax]

    def units(self, *args):
        """
        Helper to add svg units to coordinate given as any python type.
        """
        u = self.parent.unit
        return tuple('%s%s' % (a, u) for a in args)

    def make_style(self, mixed):
        """
        Create an svg style (attribute-value) string from a python dict.
        """
        if isinstance(mixed, dict):
            return ' '.join('%s: %s;' % (k, v) for k, v in mixed.items())
        return str(mixed)

    def make_attrs(self, mixed):
        """
        Create an svg attributes string from a python dict.
        """
        if isinstance(mixed, dict):
            return ''.join('%s="%s" ' % (k, v) for k, v in mixed.items())
        return str(mixed)

    def make_payload(self, cls, style, attrs):
        """
        Create a string of the attributes for an svg element.
        """
        cls_str = 'class="%s" ' % cls if cls else ''
        style_str = 'style="%s" ' % self.make_style(style) if style else ''
        attr_str = self.make_attrs(attrs) if attrs else ''
        payload = ''.join([attr_str, cls_str, style_str])
        return payload

    def iter_svgs(self):
        """
        Iterate through the various svg component objects.
        """
        for name in self.parent.layers:
            yield name, self.parent.layers[name]
        for elem in self.parent.elements:
            if isinstance(elem, SVG):
                yield None, elem

    def style_lines(self):
        """
        Iterate through the svg css style lines defined by this object.
        """
        self.parent.finalize()
        for name, svg in self.iter_svgs(): # recurse here
            for line in svg._meta.style_lines():
                yield line
        if isinstance(self.parent.style, str):
            yield self.parent.style
        else:
            for cls in self.parent.style:
                yield "%s {" % str(cls)
                for key, value in self.parent.style[cls].items():
                    yield "    %s: %s;" % (key, value)
                yield "}"

    def defs_lines(self):
        """
        Iterate through the additional svg defs section lines defined by this object.
        """
        self.parent.finalize()
        for name, svg in self.iter_svgs(): # recurse here
            for line in svg._meta.defs_lines():
                yield line
        for line in self.parent.defs:
            yield line
        for name, svg in self.parent.masks.items():
            yield """<clipPath id="%s">""" % name
            for line in svg._meta.body_lines():
                yield line
            yield """</clipPath>"""

    def body_lines(self):
        """
        Iterate through the svg body lines defined by this object.
        """
        self.parent.finalize()
        for name, svg in self.iter_svgs(): # recurse here
            if name:
                yield '<g id="%s">' % name
            for line in svg._meta.body_lines():
                yield line
            if name:
                yield "</g>"
        for elem in self.parent.elements:
            if isinstance(elem, SVG):
                pass
            else:
                yield "%s" % elem

    def template1(self, width, height):
        """
        A standard template for svg images.
        """
        style = '\n'.join(self.style_lines())
        defs = '\n'.join(self.defs_lines())
        body = '\n'.join(self.body_lines())
        defs_block = '' if not (style or defs) else '''<defs>
    <style type="text/css"><![CDATA[
%s\n    ]]></style>\n%s\n</defs>''' % (style, defs)
        txt = '''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%s" height="%s" version="1.1" xmlns="http://www.w3.org/2000/svg">
%s\n%s\n</svg>\n''' % (width, height, defs_block, body)
        return txt

