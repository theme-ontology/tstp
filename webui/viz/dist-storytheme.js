function do_storytheme(svgname)
{
    var URL = '../json.php?action=metathemedata';
    var hist = [[], [], []];
    var maxbin = 0;

    // fetch data and start the behemoth
    d3.request(URL, function(error, response) {
        var data = JSON.parse(response.response);
        var leaf_themes = data[0];
        var count = {};

        for (var i = 0; i < 31; i++)
        {
            hist[0].push(0);
            hist[1].push(0);
            hist[2].push(0);
        }

        function getd(map, item, def) {
            if (!(item in map)) 
                map[item] = def;
            return map[item];
        }

        for (var theme in leaf_themes)
        {
            var theme_uses = leaf_themes[theme];

            for (var idx in theme_uses)
            {
                var entry = theme_uses[idx];
                var wcount = getd(count, entry[0], {});
                var n = getd(wcount, entry[1], 0);
                count[entry[0]][entry[1]] = n < 30 ? n + 1 : n;
            }
        }

        for (var key in count)
        {
            var entry = count[key];
            hist[0][entry["minor"]] += 1;
            hist[1][entry["major"]] += 1;
            hist[2][entry["choice"]] += 1;
        }

        for (var w in hist)
        {
            for (n in hist[w])
            {
                if (hist[w][n] > maxbin)
                    maxbin = hist[w][n];
            }
        }

        window.addEventListener("resize", redraw);
        redraw();
    });

    function redraw()
    {
        var svg = d3.select(svgname);
        var bb = svg.node().getBoundingClientRect();
        var dx = Math.floor((bb.width - 20) / 31);
        var dy = Math.max(1, Math.floor((bb.height - 30) / maxbin));
        var fh = function(d, i) { return dy * d; };
        var fy = function(d, i) { return bb.height - dy * d - 30; };
        var fx = function(j) { 
            return function (d, i) { 
                return 20 + i * dx + (barwidth + 1) * j; 
            }
        };
        var barwidth = dx / 4;
        var dtext = Math.floor(Math.max(1, 100 / dx));
        var ybar = Math.max(1, Math.floor(maxbin / 40) * 10);

        svg.selectAll(".ygrid")
            .data([ ybar ])
            .enter()
                .append("line")
                .attr("class", "ygrid");
        svg.selectAll(".ygrid")
            .attr("x1", 30)
            .attr("y1", fy)
            .attr("x2", bb.width - 10)
            .attr("y2", fy);

        svg.selectAll(".yvalue")
            .data([ ybar ])
            .enter()
                .append("text")
                .attr("class", "yvalue")
        svg.selectAll(".yvalue")
                .attr("x", 20)
                .attr("y", fy)
                .text(function (d, i) { return d; });

        svg.selectAll(".bar0")
            .data(hist[0])
            .enter()
                .append("rect")
                .attr("class", "bar0");
        svg.selectAll(".bar0")
                .attr("x", fx(0))
                .attr("y", fy)
                .attr("width", barwidth)
                .attr("height", fh);

        svg.selectAll(".bar1")
            .data(hist[1])
            .enter().append("rect")
            .attr("class", "bar1");
        svg.selectAll(".bar1")
                .attr("x", fx(1))
                .attr("y", fy)
                .attr("width", barwidth)
                .attr("height", fh);

        svg.selectAll(".bar2")
            .data(hist[2])
            .enter()
                .append("rect")
                .attr("class", "bar2");
        svg.selectAll(".bar2")
                .attr("x", fx(2))
                .attr("y", fy)
                .attr("width", barwidth)
                .attr("height", fh);

        svg.selectAll(".xbin")
            .data(hist[0])
            .enter()
                .append("text")
                .attr("class", "xbin");
        svg.selectAll(".xbin")
                .attr("x", fx(1))
                .attr("y", bb.height - 10)
                .text(function(d, i) { return (i > 0 && i % dtext == 0) ? (i < 30 ? i : "30+") : ""; });                

        svg.selectAll(".ytitle")
            .data([ bb.height ])
            .enter()
                .append("text")
                .attr("class", "ytitle")
                .text("number of stories");
        svg.selectAll(".ytitle")
            .attr("transform", function(d) { 
                return "translate(" + 10 + "," + (d / 2 + 50) + ")rotate(-90)";
            });

    }
}