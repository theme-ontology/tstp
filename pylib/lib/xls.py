import re

# import xlrd/xlwt only locally so that some features may survive 
# if packages are missing


def xls_sheet_to_memory(filename, sheets='ALL'):
    """ 
    Read xls file into memory as lists of tuples, as dict of sheets.
    """
    import pandas as pd
    outdict = {}
    pdict = pd.read_excel(filename, sheet_name=None, header=None, dtype=str, na_filter=False)
    if sheets == 'ALL':
        sheet_names = set(pdict)
    else:
        sheet_names = set([sheets]) if isinstance(sheets, str) else set(sheets)
    for sheetname in pdict:
        if sheetname in sheet_names:
            keystr = str(sheetname)
            allrows = pdict[sheetname].values.tolist()
            outdict[keystr] = allrows
    return outdict


def get_headers(filename, sheetpattern=".*"):
    """
    Return cells in rows with given headers for all sheets in file.
    """
    try:
        sheets = xls_sheet_to_memory(filename)
    except (OSError, KeyError):
        raise IOError("Unable to read excel file")
    results = []
    for sheetname in sheets:
        if re.match(sheetpattern, sheetname):
            sheet = sheets[sheetname]
            if sheet:
                results.append((sheetname, sheet[0]))
            else:
                results.append((sheetname, []))
    return results


def read_xls(filename, headers=None, sheetname=".*"):
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
        if re.match(sheetname, sheet):
            sheetcount += 1
            for idx, row in enumerate(sheets[sheet]):
                if idx == 0:
                    if headers is None:
                        headers = row
                        results.append(row)
                    idxs = []
                    for header in headers:
                        try:
                            idxs.append(row.index(header))
                        except ValueError:
                            raise IOError("Missing Header: '%s', in Sheet '%s', Row %s: %s" % (header, sheet, idx, str(row)))
                    continue
                
                rowcount += 1
                results.append([row[i] for i in idxs])
    
    return results, sheetcount, rowcount


def write_xls(filename, headers, rows, sheetname="data"):
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


def write_themelist(df, filename, columns=None):
    """
    Write a review list of themes and usages given data as a dataframe.
    Args:
        df: A pandas dataframe
        filename: Target filename
    """
    import pandas as pd
    df = df.copy()
    REVIEW_COLS = ["sid", "title", "parents", "theme", "capacity", "weight", "motivation", "DISCUSS", "revised comment",
                   "revised theme", "revised weight", "revised capacity", "tentative action", "discussion thread",
                   "MO notes"]
    REVIEW_COL_WIDTHS = {'weight': 10, 'motivation': 40, 'revised comment': 40, "revised weight": 10,
                         "revised capacity": 10}
    columns = columns or REVIEW_COLS

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    writer = pd.ExcelWriter(filename, engine="xlsxwriter")
    df.to_excel(writer, columns=columns, header=True, index=False, freeze_panes=(1, 1), sheet_name="data")
    workbook = writer.book
    worksheet = writer.sheets['data']
    worksheet.set_default_row(70)
    basic = {
        'text_wrap': True,
        'valign': 'vcenter',
        'align': 'left',
        'border': 1,
        'border_color': '#cccccc',
    }
    revise = dict(basic, **{
        'bg_color': '#ffffcc'
    })
    format_basic = workbook.add_format(basic)
    format_revise = workbook.add_format(revise)

    for idx, colname in enumerate(columns):
        width = REVIEW_COL_WIDTHS.get(colname, 15)
        colc = chr(ord("A") + idx)
        fmt = format_revise if 'revised' in colname else format_basic
        worksheet.set_column('{}:{}'.format(colc, colc), width, fmt)

    writer.save()


