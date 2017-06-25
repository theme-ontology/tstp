# import xlrd/xlwt only locally so that some features may survive 
# if packages are missing


def xls_sheet_to_memory(filename, sheets='ALL'):
    """ 
    Read xls file into memory as lists of tuples, as dict of sheets.
    """
    import xlrd

    outdict = {}
    book = xlrd.open_workbook(filename)
    
    if sheets == 'ALL':
        sheet_names = set( s.name for s in book.sheets() )
    else:
        sheet_names = set([sheets]) if isinstance(sheets, str) else set(sheets)
        
    for sheet in book.sheets():
        if sheet.name in sheet_names:
            keystr = str(sheet.name)
            allrows = []
            for i in xrange( sheet.nrows ):
                allrows.append( tuple( unicode(cell.value) for cell in sheet.row(i) ) )
            outdict[keystr] = allrows
            
    return outdict


def read_xls(filename, headers):
    """
    Return cells in rows with given headers for all sheets in file.
    """
    sheetcount = 0
    rowcount = 0
    
    try:
        sheets = xls_sheet_to_memory(filename)
    except (OSError, KeyError):
        raise IOError("Unable to read excel file")
    
    results = []
    idxs = []
    
    for sheet in sheets:
        sheetcount += 1
        for idx, row in enumerate(sheets[sheet]):
            if idx == 0:
                idxs = []
                for header in headers:
                    try:
                        idxs.append(row.index(header))
                    except ValueError:
                        raise IOError("Missing header: '%s' in %s" % (header, str(row)))
                continue
            
            rowcount += 1
            results.append([ row[i] for i in idxs ])
    
    return results, sheetcount, rowcount


def write_xls(filename, headers, rows, sheetname = "data"):
    """
    Write an oldfashioned .xls file with a single workbook and given heasers, rows.
    """
    import xlwt

    wb = xlwt.Workbook(encoding='utf-8', style_compression=0)
    ws = wb.add_sheet(sheetname)

    for cc, hh in enumerate(headers):
        ws.write(0, cc, hh)

    for rr, row in enumerate(rows):
        for cc, value in enumerate(row):
            ws.write(rr + 1, cc, value)

    wb.save(filename)

