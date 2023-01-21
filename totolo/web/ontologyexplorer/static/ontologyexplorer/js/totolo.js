
function makeThemeLink(data, color = null)
{
    urldata = encodeURIComponent(data);
    if (color)
    {
        return '<A style="color:' + color + ';" href="/theme/' + urldata + '">' + data + '</A>';
    }
    return "<A href=\"/theme/" + urldata + "\">" + data + "</A>";
}


function makeThemeLinkList(data, color = null)
{
    html = "<ul>";
    parents = data.split(", ");
    for (ii = 0; ii < parents.length; ii++)
    {
        cleanparent = parents[ii].trim();
        if (cleanparent)
        {
            fmtparent = makeThemeLink(cleanparent, color = color);
            html += "<li>" + fmtparent + "</li>\n";
        }
    }
    html += "</ul>";
    return html;
}


function makeStoryLink(data, color = null)
{
    urldata = encodeURIComponent(data);
    if (color)
    {
        return '<A style="color:' + color + ';" href="/story/' + urldata + '">' + data + '</A>';
    }
    return "<A href=\"/story/" + urldata + "\">" + data + "</A>";
}


function makeStoryLinkList(data, color = null)
{
    html = "";
    parents = data.split("\n");
    for (ii = 0; ii < parents.length; ii++)
    {
        cleanparent = parents[ii].trim();
        if (cleanparent)
        {
            fmtparent = makeStoryLink(cleanparent, color = color);
            html += fmtparent + "\n";
        }
    }
    return html;
}

