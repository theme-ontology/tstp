
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

function summarizeThemes(data)
{
    var count = new Proxy({}, {
        get: (target, name) => name in target ? target[name] : 0
    });
    var targets = ["choice", "major", "minor"];
    var remains = 0;
    var parts = [];

    for (let i=0; i<data.length; i++)
    {
        var row = data[i];
        count[row.weight] += 1;
        remains += 1;
    }
    targets.forEach((key) => {
        f = count[key];
        remains -= f;
        if (f) { parts.push(key + ": " + f); }
    });
    if (remains) { parts.push("other: " + remains); }

    return parts.join(", ");
}