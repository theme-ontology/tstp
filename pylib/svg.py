

def make_svg(width, height, style, body):
    '''
    A standard template for svg images.
    '''
    style_block = '' if not style else '''<defs>
    <style type="text/css"><![CDATA[
%s\n    ]]></style>\n</defs>''' % style

    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%s" height="%s" version="1.1" xmlns="http://www.w3.org/2000/svg">
%s\n%s\n</svg>\n''' % (width, height, style_block, body )



