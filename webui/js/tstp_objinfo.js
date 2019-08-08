var g_objStats;


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
        }
    }

}
