
function TSTP_storytheme_data(cb)
{
    var URL = '../json.php?action=metathemedata';

    // fetch data and start the behemoth
    d3.request(URL, function(error, response) {
        var data = JSON.parse(response.response);
        cb(data);
    });
}


function TSTP_storytheme_do(svgname, tooltipname, data)
{
    var hist = [[], [], []];
    var weightdefs = [ "minor", "major", "choice" ];
    var maxbin = 0;

    if (data === null) 
        return TSTP_storytheme_data(function(data) {
            TSTP_storytheme_do(svgname, data);
        });

    init(data);

    function init(data)
    {
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
    }

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

        function makebars(idx) {
            svg.selectAll(".bar" + idx)
                .data(hist[idx])
                .enter()
                    .append("rect")
                    .on('mouseover', function () {
                        d3.select(this).transition().duration(1)
                            .style('fill-opacity', 0.9)
                            .style('filter', 'brightness(75%)');
                        var tt = d3.select(tooltipname);
                        tt.style("visibility", "visible");
                    })
                    .on('mouseout', function () {
                        d3.select(this).transition().duration(100)
                            .style('fill-opacity', 1.0)
                            .style('filter', 'brightness(100%)');
                        var tt = d3.select(tooltipname);
                        tt.style("visibility", "hidden");
                    })
                    .on('mousemove', function (d, i) {
                        var xx = d3.event.pageX;
                        var yy = d3.event.pageY;
                        var tt = d3.select(tooltipname);
                        tt.style("left", xx + "px");
                        tt.style("top", yy + "px");
                        tt.select("#themeweight").text(weightdefs[idx]);
                        tt.select("#numstories").text(d);
                        tt.select("#numthemes").text(i);
                    })
                    .attr("class", "bar" + idx);
            svg.selectAll(".bar" + idx)
                    .attr("x", fx(idx))
                    .attr("y", fy)
                    .attr("width", barwidth)
                    .attr("height", fh);
        }

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

        makebars(0);
        makebars(1);
        makebars(2);

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