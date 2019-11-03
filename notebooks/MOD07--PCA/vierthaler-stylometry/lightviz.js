

var margin = {top: 100, right: 200, bottom: 100, left: 200},
    width = window.innerWidth - margin.left - margin.right,
    height = window.innerHeight - margin.top - margin.bottom;

// set the active category type
var color = d3.scaleOrdinal(colorDictionaries[activecatnum]);

var drawData = true;
var drawLoadings = false;
var showLabels = false;
var showGrid = false;
// load in the data and transform it
// get the value, category, and label types
let categoryValues = {}
for (let i = 0; i < categoryTypes.length; i++){
    categoryValues[categoryTypes[i]] = new Set();
}

window.onload = function(){

for (i = 0; i < data.length; i++){
    data[i].size = 2.5;
    for (j = 0; j < labels[i].length; j ++){
        data[i][j] = labels[i][j];
    }
}


var chartArea = d3.select("#dataviz").append("div")
    .style("position","relative")
    .style("float","left")
    .style("left", margin.left+"px")
    .style("top", margin.top+"px");

let canvas = chartArea.append("canvas")
    .classed("vizlayer",true)
    .style("position","absolute")
    .call(d3.zoom().scaleExtent([.1, 50])
    .on("zoom", zoom))
    .attr('width', width)
    .attr('height', height)
    .style("width",width+"px")
    .style("height",height+"px");

var context = canvas.node().getContext("2d");

let fontsize = 18;
context.font= fontsize+"px Open Sans";


var currenttransform = d3.zoomIdentity;

var svg = d3.select("#dataviz").append("svg")
    .classed("overlay",true)
    .style("position","absolute")
    .attr("width", 2*width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.select("#dataviz").append("svg")
    .style("position","relative")
    .attr("width", 0)
    .attr("height", height + margin.top + margin.bottom)
    .style("pointer-events", "none")
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


var x = d3.scaleLinear()
    .range([0, width]);
var y = d3.scaleLinear()
    .range([height, 0]);
var xScale = d3.scaleLinear()
    .range([0, width]);
var yScale = d3.scaleLinear()
    .range([height, 0]);

var xAxis = d3.axisBottom(x);
var yAxis = d3.axisLeft(y);
var x2Axis = d3.axisBottom(x);
var y2Axis = d3.axisLeft(y);


// set the domains of the default values (the first two value types)
var boundData = {x:0, y:1, xString:valueTypes[0], 
                    yString:valueTypes[1]};

var activeCatType = categoryTypes[activecatnum]

labels.forEach(function(d){
    categoryValues[activeCatType].add(d[activecatnum])
})

var activeCategories = categoryValues[activeCatType]


x.domain(d3.extent(data, function(d) { return d[valueTypes[0]]; })).nice();
y.domain(d3.extent(data, function(d) { return d[valueTypes[1]]; })).nice();
xScale.domain(d3.extent(data, function(d) { return d[valueTypes[0]]; })).nice();
yScale.domain(d3.extent(data, function(d) { return d[valueTypes[1]]; })).nice();


var gX = svg.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
var gY = svg.append("g")
    .attr("class", "axis axis--y")
    .call(yAxis);

var g2X = svg.append("g")
    .attr("class", "axis axis--x")
    .call(x2Axis);

var g2Y = svg.append("g")
    .attr("class", "axis axis--y")
    .attr("transform", "translate("+width+",0)")
    .call(y2Axis);


// var graphTitle = svg.append("text")
//   .attr("x", width + 40)
//   .attr("y", margin.top)
//   .attr("font-size",32)
//   .text("Scatter Plot (PCA)")

var xLabel = svg.append("text")
    .attr("x",width/2)
    .attr("y",height +40)
    .attr("font-size",18)
    .attr("text-anchor","middle")
    .text(boundData.xString);

var yLabel = svg.append("text")
    .attr("x",0-40)
    .attr("y",height/2)
    .attr("font-size",18)
    .attr("text-anchor","middle")
    .attr("transform", "rotate(-90,-40,"+height/2+")")
    .text(boundData.yString);



draw(currenttransform, "transform",d3.zoomIdentity);

function zoom() {

    xScale = d3.event.transform.rescaleX(x);
    yScale = d3.event.transform.rescaleY(y);
    
    // update axes
    gX.call(xAxis.scale(xScale));
    gY.call(yAxis.scale(yScale));
    g2X.call(xAxis.scale(xScale));
    g2Y.call(yAxis.scale(yScale));
    context.clearRect(0, 0, width, height);
    currenttransform = d3.event.transform
    draw(currenttransform,"transform",d3.event.transform);
}

function draw(transform, operation=null,inputvalue=null) {
    context.fillStyle = '#fff';
    context.fillRect(0, 0, width, height);
    context.font= fontsize+"px Open Sans"
    
    var i = -1, n = data.length;
    context.beginPath();

    if (showGrid) {
        xline = inputvalue.apply([0,y(0)])
        yline = inputvalue.apply([x(0),0])
        context.beginPath();
        context.moveTo(0,xline[1])
        context.lineTo(width,xline[1])
        context.strokeStyle="#222"
        context.stroke();
        context.beginPath();
        context.moveTo(yline[0],height)
        context.lineTo(yline[0],0)
        context.strokeStyle="#222"
        context.stroke();

    }


    while (++i < n) {
    
        var da = []
        

        for (let j = 0; j<valueTypes.length;j++){
            da.push(data[i][valueTypes[j]])
        }
    
        //Use x scale because of transform
        if (operation == "transform"){
        if (boundData.x == -1) {
            var usex = 0
        } else {
            var usex = da[boundData.x]
        }
        if (boundData.y == -1){
            var usey = 0;
        } else {
            var usey = da[boundData.y]
        }
        
        var d = [x(usex), y(usey)];
        d = inputvalue.apply(d);
        

        } else if (operation == "transition") {
        var d = [xScale(data[i].startx), yScale(data[i].starty)]
        } else {
        if (boundData.x == -1) {
            var usex = 0
        } else {
            var usex = da[boundData.x]
        }
        if (boundData.y == -1){
            var usey = 0;
        } else {
            var usey = da[boundData.y]
        }
        var d = [xScale(usex), yScale(usey)]
        }
        data[i].px = d[0]
        data[i].py = d[1]
        
        data[i].c = color(data[i][activecatnum])
        
        
        
        
        
    
    }
    

    
    if (drawData){
        
        var i = -1, n = data.length-1;
        
        while (i++ < n){
        
        if (data[i].size > 0) {
        
            if (activeCategories.has(data[i][activecatnum])){
            context.moveTo(data[i].px,data[i].py);
            
            context.fillStyle = data[i].c;
            
            
            context.beginPath();
            context.arc(data[i].px,data[i].py, 4, 0, 2 * Math.PI);
            context.fill();
            context.closePath();
            
            
            if (transform.k > 2 || showLabels == true){
                context.fillText(data[i][activelabelnum],data[i].px+4,data[i].py-4)
            }
            }
        }
        }
        
    }

    
    if (drawLoadings) {

        var i = -1, n = loadings.length -1;
        while (i++ < n){
        var da = []
        
        for (j = 0; j < valueTypes.length; j++){
            da.push(loadings[i][1][valueTypes[j]])
        }
        
        currenttext = loadings[i][0]
        if (operation == "transform"){
            var d = [x(da[boundData.x]), y(da[boundData.y])]
            d = inputvalue.apply(d);
        } else if (operation == "transition") {
            var d = [xScale(loadingsdata[i].startx), yScale(loadingsdata[i].starty)]
        } else {
            var d = [xScale(da[boundData.x]), yScale(da[boundData.y])]
        }
        
        context.fillStyle="black";
        context.fillText(currenttext,d[0],d[1])

        }
    }
    context.closePath();
    }

var colorselect = svg.selectAll(".colorselect")
    .data(limitedCategories)
    .enter().append("g")
    .attr("transform", function(d, i) { var adjust = (i*50)+height/14;return "translate(0," + adjust + ")"; });

var colorr = colorselect.append("rect")
    .attr("x", width + 60)
    .attr("width", 80)
    .attr("height", 40)
    .attr("rx", 4)
    .attr("ry", 4)
    .attr("class", "colorselect")
    .attr("id", function(d,i){return i})
    .style("pointer-events","auto")
    .on("click", function(d){setCategory(d);});

function setCategory(input){
    activecatnum =categoryTypes.indexOf(input)
    activeCatType = input
    activeCategories = categoryValues[activeCatType]
    console.log(categoryValues, activecatnum, activeCatType)
    labels.forEach(function(d){
        categoryValues[activeCatType].add(d[activecatnum])
    })
    color = d3.scaleOrdinal(colorDictionaries[activecatnum])
    draw(currenttransform, "transform", currenttransform)
    svg.selectAll(".legend").remove()
    legend = svg.selectAll(".legend")
    .data(color.domain())
    .enter().append("g")
    .attr("class", "legend")
    .attr("transform", function(d, i) { var adjust = (i*20)+20;return "translate(0," + adjust + ")"; });
    
    lrect = legend.append("rect")
    .attr("x", width - 46)
    .attr("width", 18)
    .attr("height", 18)
    .attr("id",function(d,i){return i})
    .style("fill", color)
    .style("pointer-events","auto")
    .on("click", function(d,i){toggleItem(d,i)});

legend.append("text")
    .attr("x", width - 52)
    .attr("y", 9)
    .attr("dy", ".35em")
    .style('font-size', "12px")
    .style("text-anchor", "end")
    .text(function(d) { return d; });
    
    function toggleItem(d,i){
    referenceitem = d3.select(lrect._groups[0][i])
    if (activeCategories.has(d)) {
        activeCategories.delete(d);
        referenceitem.style("stroke",color(d))
                .style("stroke-opacity","1.0")
                .style("fill-opacity","0.0");
    } else {
        activeCategories.add(d)
        console.log(activeCategories)
        referenceitem.style("fill",color(d))
                    .style("fill-opacity","1.0")
                    .style("stroke-opacity","0.0")
        };
    draw(currenttransform);
    }
    
}

colorselect.append("text")
    .attr("x", width+100)
    .attr("y", 26)
    .style("text-anchor","middle")
    .style('font-size',"18px")
    .style('text-transform', 'capitalize')
    .attr("class", "colortext")
    .text(function(d) { return d; });
    

var legend = svg.selectAll(".legend")
    .data(color.domain())
    .enter().append("g")
    .attr("class", "legend")
    .attr("transform", function(d, i) { var adjust = (i*20)+20;return "translate(0," + adjust + ")"; });
    
var lrect = legend.append("rect")
    .attr("x", width - 46)
    .attr("width", 18)
    .attr("height", 18)
    .attr("id",function(d,i){return i})
    .style("fill", color)
    .style("pointer-events","auto")
    .on("click", function(d,i){toggleItem(d,i)});

legend.append("text")
    .attr("x", width - 52)
    .attr("y", 9)
    .attr("dy", ".35em")
    .style('font-size', "12px")
    .style("text-anchor", "end")
    .text(function(d) { return d; });
    
    function toggleItem(d,i){
    var referenceitem = d3.select(lrect._groups[0][i])
    if (activeCategories.has(d)) {
        activeCategories.delete(d);
        referenceitem.style("stroke",color(d))
                .style("stroke-opacity","1.0")
                .style("fill-opacity","0.0");
    } else {
        activeCategories.add(d)
        console.log(activeCategories)
        referenceitem.style("fill",color(d))
                    .style("fill-opacity","1.0")
                    .style("stroke-opacity","0.0")
        };
    draw(currenttransform);
    }
    svg.append('g')
        .append('rect')
        .attr("x",-160)
        .attr("y",height/14)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("width","80")
        .attr("height","40")
        .attr("class", "interact")
        .style("pointer-events","auto")
        .on("click",toggleLoadings)
    
    svg.append("text")
        .attr("x", -120)
        .attr("y",height/14+26)
        .style('font-size', "18px")
        .style("pointer-events","none")
        .attr("class", "interacttext")
        .attr("text-anchor","middle")
        .text("Loadings")

    svg.append("text")
        .attr("x", -120)
        .attr("y", 0)
        .style('font-size', "24px")
        .attr("text-anchor","middle")
        .style("alignment-baseline", "hanging")
        .style('fill', "#000")
        .text("Toggle")

    svg.append("text")
        .attr("x", width+100)
        .attr("y", 0)
        .style('font-size', "24px")
        .attr("text-anchor","middle")
        .style("alignment-baseline", "hanging")
        .style('fill', "#000")
        .text("Color")

    function toggleLoadings() {
        drawLoadings = !drawLoadings;
        draw(currenttransform, "transform", currenttransform);
    }

    svg.append('g')
        .append('rect')
        .attr("x",-160)
        .attr("y",height/14+50)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("width","80")
        .attr("height","40")
        .attr("class", "interact")
        .style("pointer-events","auto")
        .on("click",toggleData)
    
    svg.append("text")
        .attr("x", -120)
        .attr("y",height/14+50+26)
        .style('font-size', "18px")
        .style("pointer-events","none")
        .attr("class", "interacttext")
        .attr("text-anchor","middle")
        .text("Data")

    function toggleData() {
        drawData = !drawData;
        draw(currenttransform, "transform", currenttransform)
    }
    
    svg.append('g')
        .append('rect')
        .attr("x",-160)
        .attr("y",height/14+100)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("width","80")
        .attr("height","40")
        .attr("class", "interact")
        .style("pointer-events","auto")
        .on("click",toggleLabels)
    
    svg.append("text")
        .attr("x", -120)
        .attr("y",height/14+100+26)
        .style('font-size', "18px")
        .style("pointer-events","none")
        .attr("class", "interacttext")
        .attr("text-anchor","middle")
        .text("Labels")

    function toggleLabels() {
        showLabels = !showLabels;
        draw(currenttransform, "transform", currenttransform)
    }

    svg.append("text")
        .attr("x", width+100)
        .attr("y",height/14 + (50 * (limitedCategories.length))+ 24)
        .style('font-size', "24px")
        .style("pointer-events","none")
        .style("fill","#000")
        .attr("class", "interacttext")
        .attr("text-anchor","middle")
        .style("alignment-baseline","middle")
        .text("Labels")

    var labelselect = svg.selectAll(".labelselect")
        .data(categoryTypes)
        .enter().append("g")
        .attr("transform", function(d, i) { var adjust = (i*50)+height/14 + (50 * (limitedCategories.length + 1));return "translate(0," + adjust + ")"; });
    
    var labelr = labelselect.append("rect")
        .attr("x", width + 60)
        .attr("width", 80)
        .attr("height", 40)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("class", "labelselect")
        .attr("id", function(d,i){return i})
        .style("pointer-events","auto")
        .on("click", function(d){setLabelValue(d);});
    
    labelselect.append("text")
        .attr("x", width+100)
        .attr("y", 26)
        .style("text-anchor","middle")
        .style('font-size',"18px")
        .style('text-transform', 'capitalize')
        .attr("class", "labeltext")
        .text(function(d) { return d; });

    function setLabelValue(input){
        activelabelnum = categoryTypes.indexOf(input)
        draw(currenttransform, "transform", currenttransform)
    }

    svg.append('g')
        .append('rect')
        .attr("x",-160)
        .attr("y",height/14 + 150)
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("width","80")
        .attr("height","40")
        .attr("class", "interact")
        .style("pointer-events","auto")
        .on("click",toggleGrid)
    
    svg.append("text")
        .attr("x", -120)
        .attr("y",height/14+150+26)
        .style('font-size', "18px")
        .style("pointer-events","none")
        .attr("class", "interacttext")
        .attr("text-anchor","middle")
        .text("0,0")

    function toggleGrid(){
        showGrid = !showGrid
        draw(currenttransform, "transform", currenttransform)
    }

    svg.append("text")
        .attr("x", width/2)
        .attr("y", -margin.top/2)
        .style("text-anchor","middle")
        .style("font-size","32px")
        .style("alignment-baseline", "middle")
        .text("Principal Component Analysis")

};