
function TSTP_themeusage2_data(cb)
{
    var URL = '../json.php?action=metathemedata';

    // fetch data and start the behemoth
    d3.request(URL, function(error, response) {
        var data = JSON.parse(response.response);
        cb(data);
    });
}


function TSTP_themeusage2_do(svgname, tooltipname, data)
{
    var DATA = [[], [], []];
    var weightdefs = [ "minor", "major", "choice" ];
    var maxbin = 0;
    var redrawcount = 0;
    var BINS = 10;

    if (data === null) 
        return TSTP_themeusage_data(function(data) {
            TSTP_themeusage_do(svgname, data);
        });

    init(data);
    window.addEventListener("resize", schedule_redraw);
    redraw();

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
        var count2 = defaultDict(function() { 
            return defaultDict(function() { return 0; }); 
        });

        for (var ii=0; ii <= BINS; ii++)
        {
            DATA[0].push(0);
            DATA[1].push(0);
            DATA[2].push(0);
        }

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
                var theme_timesused_asweight = entry[weightdefs[widx]];
                theme_timesused_asweight = (theme_timesused_asweight > BINS) ? BINS : theme_timesused_asweight;
                DATA[widx][theme_timesused_asweight] += 1;
            }
        }

        for (var ii=0; ii <= BINS; ii++)
        {
            maxbin = Math.max(DATA[0][ii], maxbin);
            maxbin = Math.max(DATA[1][ii], maxbin);
            maxbin = Math.max(DATA[2][ii], maxbin);
        }
        console.log(maxbin, BINS);
    }

    function schedule_redraw()
    {
        redrawcount += 1;
        setTimeout(function() { redraw_once(); }, 100)
    }

    function redraw_once()
    {
        redrawcount -= 1;
        if (redrawcount == 0) 
            redraw();
    }

    function redraw()
    {
        var svg = d3.select(svgname);
        var bb = svg.node().getBoundingClientRect();
        var dx = Math.floor((bb.width - 20) / (BINS + 1));
        var dy = Math.max(0.0001, (bb.height - 30.0) / maxbin);
        var fh = function(d, i) { return dy * d; };
        var fy = function(d, i) { return bb.height - dy * d - 30; };
        var fx = function(j) { 
            return function (d, i) { 
                return 30 + i * dx + (barwidth + 1) * j; 
            }
        };
        var barwidth = dx / 4;
        var dtext = Math.floor(Math.max(1, 100 / dx));
        var ybar = Math.max(1, Math.floor(maxbin / 40) * 10);

        console.log(dx, dy * ybar, ybar, maxbin);

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
                        tt.select("#numthemes").text(d);
                        tt.select("#themeweight").text(weightdefs[idx]);
                        if (i == BINS) 
                            tt.select("#numstories").text(i + " or more");
                        else
                            tt.select("#numstories").text(i);
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
            .attr("x1", 26)
            .attr("y1", fy)
            .attr("x2", bb.width - 10)
            .attr("y2", fy);

        svg.selectAll(".yvalue")
            .data([ ybar ])
            .enter()
                .append("text")
                .attr("class", "yvalue")
        svg.selectAll(".yvalue")
                .attr("x", 26)
                .attr("y", fy)
                .text(function (d, i) { return d; });

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
                .text(function(d, i) { 
                    if (i == BINS) return i + "+";
                    return (i % dtext == 0) ? (i) : ""; 
                });

        svg.selectAll(".ytitle")
            .data([ bb.height ])
            .enter()
                .append("text")
                .attr("class", "ytitle")
                .text("number of themes");
        svg.selectAll(".ytitle")
            .attr("transform", function(d) { 
                return "translate(" + 10 + "," + (d / 2 + 50) + ")rotate(-90)";
            });

    }

}

