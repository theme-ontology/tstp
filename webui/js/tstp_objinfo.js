var g_objStats;


$(document).ready(function () {
    loadObjInfoDataOnReady();
});


function loadObjInfoDataOnReady() 
{
    var fields = g_objFields.join();
    var name = encodeURIComponent(g_objName);

	$('#fieldName').prop('disabled', true); 

	$.getJSON(
		"json.php?type=" + g_objType + "&action=stats&name=" + name,
		receivedObjInfoData
	);
}


function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }


function formatBlobForHTML(txt)
{
    var blockre = /\n\n+/;

    paragraphs = txt.split(blockre);
    html = "";

    console.log(txt);
    console.log(paragraphs);

    for (ii = 0; ii < paragraphs.length; ii++)
    {
        var pp = escapeHtml(paragraphs[ii]);

        if (pp.startsWith("Example:"))
            pp = "<b>Example:</b> " + pp.slice(9);
        if (pp.startsWith("References:"))
        {
            var lines = pp.slice(12).split("\n");
            pp = "<b>References:</b> ";
            for (jj = 0; jj < lines.length; jj++)
            {
                var line = lines[jj];
                if (line.startsWith("http://") || line.startsWith("https://"))
                {
                    pp += ' <A href="' + line + '">' + line + "</A>\n";
                }
            }
        }

        html += "<P>" + pp + "</P>";
    }

    return html;
}


function receivedObjInfoData(result)
{
    var ok = false;
    var children = [];
    var parents = [];

    console.info(result);

    try 
    {
        children = result["children"];
        parents = result["parents"];
        description = "";

        for (var k in result["descriptions"]) {
            description = result["descriptions"][k];
            break;
        }

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
            var parents_html = "<b>Parents:</b> ";
            var children_html = "<b>Children:</b> ";
            var childtable = [];

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
                childtable.push([ th, result.descriptions[th] ])
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
            description_html = formatBlobForHTML(description);

            $("#div_infobox").css("display", "inline");
            $("#div_parents").html(parents_html);
            $("#div_children").html(children_html);
            $("#div_description").html(description_html);

            table = $('#children_datatable').DataTable();
            table.clear();
            table.rows.add(childtable);
            table.draw();

        }
    }

}

