

function getQueryVariable(variable)
{
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){
            return decodeURIComponent(pair[1]);
        }
    }
    return(false);
}


function makeThemeLink(data, color = null)
{
    urldata = encodeURIComponent(data);
    pwid = "preview" + data.hashCode();
    href = " href=\"theme.php?name=" + urldata + "\"";
    pwurl = "themestub.php?name=" + urldata;
    iframe = ' \n<iframe id="' + pwid + 
            '" frameborder="0" allowtransparency="true" scrolling="no" class="previewer" dsrc="' + pwurl + '"></iframe>';
    jstags = " onmouseover='showPreview(\"" + pwid + "\")'";
    jstags += " onmouseout='hidePreview(\"" + pwid + "\")'";
    if (color)
    {
        return '<A style="color:' + color + ';"' + href + '>' 
            + data + iframe + '</A>';
    }
    return "<div style=\"position:relative;\"><A " 
        + jstags + href + ">" + data + iframe + "</A></div>";
}


function makeStoryLink(data, color = null)
{
    urldata = encodeURIComponent(data);
    pwid = "preview" + data.hashCode();
    href = " href=\"story.php?name=" + urldata + "\"";
    pwurl = "storystub.php?name=" + urldata;
    iframe = ' \n<iframe id="' + pwid + 
            '" frameborder="0" allowtransparency="true" scrolling="no" class="previewer" dsrc="' + pwurl + '"></iframe>';
    jstags = " onmouseover='showPreview(\"" + pwid + "\")'";
    jstags += " onmouseout='hidePreview(\"" + pwid + "\")'";
    return "<div style=\"position:relative;\"><A " 
        + jstags + href + ">" + data + iframe + "</A></div>";
}


// multiple themes are separated by newlines (once was commas)
function makeThemeLinkList(data, color = null)
{
    html = "";
    parents = data.split("\n");
    for (ii = 0; ii < parents.length; ii++)
    {
        cleanparent = parents[ii].trim();
        if (cleanparent)
        {
            fmtparent = makeThemeLink(cleanparent, color = color);
            html += fmtparent + "\n";
        }
    }
    return html;
}

