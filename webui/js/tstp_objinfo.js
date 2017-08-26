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


function receivedObjInfoData(result)
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
            var parents_html = "Parents: ";
            var children_html = "Children: ";

            for (ii = 0; ii < parents.length; ii++)
            {
                th = parents[ii];
                html = ' <A href="theme.php?name=' + th + '">' + th + '</A>';
                parents_links.push(html);
            }
            console.log(children);
            for (ii = 0; ii < children.length; ii++)
            {
                th = children[ii];
                html = ' <A href="theme.php?name=' + th + '">' + th + '</A>';
                children_links.push(html);
            }
            parents_html += parents_links.join(", ") + ".";
            children_html += children_links.join(", ") + ".";

            $("#div_infobox").css("display", "inline");
            $("#div_parents").html(parents_html);
            $("#div_children").html(children_html);
        }
    }

}

