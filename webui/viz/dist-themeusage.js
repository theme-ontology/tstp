
function TSTP_themeusage_data(cb)
{
    var URL = '../json.php?action=metathemedata';

    // fetch data and start the behemoth
    d3.request(URL, function(error, response) {
        var data = JSON.parse(response.response);
        cb(data);
    });
}


function TSTP_themeusage_do(svgname, tooltipname, data)
{
    var DATA = [[], [], []];
    var weightdefs = [ "minor", "major", "choice" ];
    var maxbin = 0;

    if (data === null) 
        return TSTP_themeusage_data(function(data) {
            TSTP_themeusage_do(svgname, data);
        });

    init(data);

    function defaultDict(createValue) {
        return new Proxy(Object.create(null), {
            get(storage, property) {
                if (!(property in storage))
                    storage[property] = createValue(property);
                return storage[property];
            }
        });
    }

    function init(data)
    {
        var leaf_themes = data[0];
        var count = defaultDict(function() { 
            return defaultDict(function() { return 0; }); 
        });

        for (var theme in leaf_themes)
        {
            var theme_uses = leaf_themes[theme];
            var wcount = count[theme];

            for (var idx in theme_uses)
            {
                var entry = theme_uses[idx];
                wcount[entry[1]] += 1;
            }
        }

        for (var theme in count)
        {
            var entry = count[theme];

            for (widx in weightdefs)
            {
                DATA[widx].push([theme, entry[weightdefs[widx]]]);
            }
        }

        for (widx in weightdefs)
        {
            DATA[widx].sort(function(lhs, rhs) { return rhs[1] - lhs[1]; });
            DATA[widx].splice(30);
            maxbin = Math.max(maxbin, DATA[widx][0][1]);
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
        var fh = function(d, i) { return dy * d[1]; };
        var fy = function(d, i) { return bb.height - dy * d[1] - 30; };
        var fx = function(j) { 
            return function (d, i) { 
                return 20 + i * dx + (barwidth + 1) * j; 
            }
        };
        var barwidth = dx / 4;
        var dtext = Math.floor(Math.max(1, 100 / dx));
        var ybar = Math.max(1, Math.floor(maxbin / 40) * 10);

        function mkorder(n) {
            if (n == 1) return "top";
            if (n == 2) return "second";
            if (n == 3) return "third";
            return n + "th"
        }

        function makebars(idx) {
            svg.selectAll(".bar" + idx)
                .data(DATA[idx])
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
                        tt.select("#themename").text(d[0]);
                        tt.select("#themeweight").text(weightdefs[idx]);
                        tt.select("#storycount").text(d[1]);
                        tt.select("#themeorder").text(mkorder(i+1));
                    })
                    .attr("class", "bar" + idx);
            svg.selectAll(".bar" + idx)
                    .attr("x", fx(idx))
                    .attr("y", fy)
                    .attr("width", barwidth)
                    .attr("height", fh);
        }

        svg.selectAll(".ygrid")
            .data([ ["", ybar] ])
            .enter()
                .append("line")
                .attr("class", "ygrid");
        svg.selectAll(".ygrid")
            .attr("x1", 18)
            .attr("y1", fy)
            .attr("x2", bb.width - 10)
            .attr("y2", fy);

        svg.selectAll(".yvalue")
            .data([ ["", ybar] ])
            .enter()
                .append("text")
                .attr("class", "yvalue")
        svg.selectAll(".yvalue")
                .attr("x", 18)
                .attr("y", fy)
                .text(function (d, i) { return d[1]; });

        makebars(0);
        makebars(1);
        makebars(2);

        svg.selectAll(".xbin")
            .data(DATA[0])
            .enter()
                .append("text")
                .attr("class", "xbin");
        svg.selectAll(".xbin")
                .attr("x", fx(1))
                .attr("y", bb.height - 10)
                .text(function(d, i) { return (i % dtext == 0) ? (i + 1) : ""; });

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

