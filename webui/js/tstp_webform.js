var g_objData;


$(document).ready(function () {
    loadDataOnReady();
});

function jalert(obj, title=null)
{
    msg = JSON.stringify(obj);
    if (title != null)
        msg = title + "\n\n" + msg;
    alert(msg);
}


function loadDataOnReady() 
{
    var fields = g_objFields.join();
    var name = encodeURIComponent(g_objName);

	$('#fieldName').prop('disabled', true); 

	$.getJSON(
		"json.php?type=" + g_objType + "&filter=" + name + "&fields=" + 
            fields + "&slimit=20000&rlimit=1",
		receivedData
	);
}


function receivedData(result)
{
    var ok = false;

    try 
    {
	   g_objData = result["data"][0];
       ok = true;
    }
    catch (err) 
    {
        jalert(result, "Error on Submit!");
    }

    if (ok) 
    {
        $.each(g_objData, function(idx, item)
        {
            f = g_objFields[idx].capitalize();
            $('#field' + f).val(item);
        });
    }

	$('#loading_message').css('display','none');
	$('#hidden_form').css('visibility','visible');
}


function gatherFields(fields, pdata)
{
    var payload = [];

    $.each(fields, function(idx, f)
    {
        var val = $('#field' + f.capitalize()).val();
        var pval = pdata[idx];

        if (val == null || val == pval)
        {

        } else {
            payload.push([f, val]);
        }
    });

    return payload;    
}

function submitData()
{
    var payload = gatherFields(g_objFields, g_objData);

    if (payload.length > 0)
    {
        $('#hidden_form').css('visibility','hidden');
        var filter = g_objFields.join();
        var name = g_objName;

        req = {
            'action'    : 'submit',
            'data'      : payload,
            'filter'    : name,
            'type'      : g_objType,
            'fields'    : g_objFields.join(),
            'slimit'    : 20000,
            'rlimit'    : 1,
        }

        $.ajax({
            url     : 'json.php',
            type    : 'POST',
            data    : req,
            success : function(result) { 
                receivedData(result);
            },
            error   : function(jqXHR, textStatus, errorThrown) {
                msg = "Something went wrong :(\n\n" + textStatus + "\n\n" + errorThrown + "\n";
                alert(msg);
                $('#hidden_form').css('visibility','visible');
            },
        });
    }

}


function submitConnection(defn)
{
    d = g_objDefs[defn];
    
}
