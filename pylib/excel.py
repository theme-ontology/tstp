import xlrd


def xls_sheet_to_memory(filename, sheets='ALL'):
    ''' Read xls file into memory as lists of tuples, as dict of sheets. '''
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
