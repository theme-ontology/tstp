var g_objStats;
var g_stickyPreview = new Object();


$(document).ready(function () {
    loadObjInfoDataOnReady();
});


function loadObjInfoDataOnReady() 
{
    var fields = g_objFields.join();
    var name = encodeURIComponent(g_objName);

	$('#fieldName').prop('disabled', true); 

    if (g_objType == "theme")
    {
    	$.getJSON(
    		"json.php?type=" + g_objType + "&action=stats&name=" + name,
    		receivedThemeInfoData
    	);
    } 
    else if (g_objType == "story")
    {
        $.getJSON(
            "json.php?type=" + g_objType + "&filter=" + name + "&fields=" + 
                fields + "&slimit=20000&rlimit=1",
            receivedStoryInfoData
        );
    }
}


function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }


// format a theme entry nicely for html
function formatBlobForHTML(txt)
{
    var blockre = /\n\n+/;
    var paragraphs = txt.split(blockre);
    var html = "";

    for (ii = 0; ii < paragraphs.length; ii++)
    {
        var pp = escapeHtml(paragraphs[ii]);

        if (pp.startsWith("Aliases:"))
            pp = "<b>Aliases:</b><BR>" + pp.slice(8);
        if (pp.startsWith("Notes:"))
            pp = "<b>Notes:</b><BR>" + pp.slice(6);
        if (pp.startsWith("Examples:"))
            pp = "<b>Examples:</b><BR>" + pp.slice(9);
        if (pp.startsWith("References:"))
        {
            var lines = pp.slice(12).split("\n");
            pp = "<b>References:</b> ";
            for (jj = 0; jj < lines.length; jj++)
            {
                var line = lines[jj];
                if (line.startsWith("http://") || line.startsWith("https://"))
                {
                    pp += '<BR><A href="' + line + '">' + line + "</A>\n";
                }
            }
        }

        html += "<P class=\"obj-description\">" + pp + "</P>";
    }

    return html;
}


// return only the first paragraph as unformatted text
function firstParagraphText(txt)
{
    var blockre = /\n\n+/;
    var paragraphs = txt.split(blockre);
    return escapeHtml(paragraphs[0]);
}


// create suitable description list items for showing a json object's 
// key=>value pairs
function makeObjectStats(stats)
{
    var html = "";
    var keys = new Array();
    for (var prop in stats) {
        keys.push(prop);
    }
    keys.sort();
    keys.reverse();

    for (var i=0; i<keys.length; i++) {
        var prop = keys[i];
        if (Object.prototype.hasOwnProperty.call(stats, prop)) {
            var val = stats[prop];
            prop = prop.substr(0, 15);
            if (prop == "source" && val.startsWith("/notes")) {
                url = "https://github.com/theme-ontology/theming/blob/master" + val;
                val = '<A href="' + url + '">' + val + '</A>';
            }
            html += '<dt class="col-sm-4 text-right">' + prop + '</dt>';
            html += '<dd class="col-sm-8"><small>' + val + '</small></dd>';
        }
    }
    $("#statslist" + name).html(html);
}



// handle result of ajax query from loadObjInfoDataOnReady
function receivedThemeInfoData(result)
{
    var ok = false;
    var children = [];
    var parents = [];

    try 
    {
        children = result["children"];
        parents = result["parents"];
	    g_objStats = result;
        ok = true;
    }
    catch (err) 
    {
        jalert(result, "Error!");
    }

    if (ok) 
    {
        if (g_objType == "theme")
        {
            var parents_links = [];
            var children_links = [];
            var parents_html = "";
            var children_html = "";
            var childtable = [];
            var description_html = formatBlobForHTML(result.descriptions[g_objName]);

            for (ii = 0; ii < parents.length; ii++)
            {
                th = parents[ii];
                html = ' <A href="theme.php?name=' + th + '">' + th + '</A>';
                parents_links.push(html);
            }
            for (ii = 0; ii < children.length; ii++)
            {
                th = children[ii];
                html = ' <A href="theme.php?name=' + th + '">' + th + '</A>';
                children_links.push(html);
                childtable.push([ th, firstParagraphText(result.descriptions[th]) ])
            }
            if (parents_links.length == 0)
            {
                parents_links.push("&lt;none&gt;");
            }
            if (children_links.length == 0)
            {
                children_links.push("&lt;none&gt;");
            }
            parents_html += parents_links.join(", ");
            children_html += children_links.join(", ");

            $("#div_infobox").css("display", "inline");
            $("#div_parents").html(parents_html);
            $("#div_children").html(children_html);
            $("#div_description").html(description_html);
            $('#loading_message').css('display','none');

            table = $('#children_datatable').DataTable();
            table.clear();
            table.rows.add(childtable);
            table.draw();
    
            makeObjectStats(g_objStats.metas[g_objName]);
        }
    }

}


// handle result of ajax query from loadObjInfoDataOnReady
function receivedStoryInfoData(result)
{
    var ok = false;
    var info = result.data[0];

    try 
    {
        g_objStats = info;
        ok = true;
    }
    catch (err) 
    {
        jalert(result, "Error!");
    }

    if (ok) 
    {
        if (g_objType == "story")
        {
            var title_html = info[1];
            var date_html = info[2];
            var description_html = formatBlobForHTML(info[3]);

            $("#obj_title").html(title_html);
            $("#obj_date").html(date_html);
            $("#div_description").html(description_html);

            makeObjectStats(g_objStats[4]);
        }
    }

}


function loadPreview(frame) {
    frame.attr("src", frame.attr("dsrc"));
}


function showPreview(name) {
    var obj = $("#" + name);
    if (!obj.attr("src")) loadPreview(obj);
    obj.hide();
    obj.show();
}


function hidePreview(name) {
    if (g_stickyPreview[name])
        return
    $("#" + name).hide();
}


function togglePreview(name) {
    if (g_stickyPreview[name]) {
        g_stickyPreview[name] = false;
        hidePreview(name);
    }
    else {
        g_stickyPreview[name] = true;
        showPreview(name)
    }
}


