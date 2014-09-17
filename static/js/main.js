

/*

TODO

- fix distance and speed 
- controls time map
- disable pan when autoplay
- twitter feed max scroll
- bad request ambit and sighting

*/



var currentPage = "Map";
var cursorRange = [0,1];
var tweets = [];
var metrics = {};
var dateRange;
var timelineRange = [];
var personalColors = ['#EB624C','#9263FF','#69D6AF','#FFC96B','#FF0000','#FF0000','#FF0000','#FF0000'];
var dataReady = false;
var loaderOffset = 0;
var ambitJson = [];
var sightingJson = [];
var closeFeedTimer;
var mapTimeline;



window.onresize = function(){
	setVideoHeight();
	setHr();
}


var initLayout = function(){

	dateRange = Math.ceil((new Date().getTime() - new Date('August 16, 2014').getTime())/(1000*3600*24))+1;

	setHr();
	setVideoHeight();
	initNav();
	initVideo();
	setColumns();
	initMetrics();
	initMapTimeline();
	if(!isGraphReady){
		initFeed();
	}
	d3.select('#fullPanelWrapper')
		.style('display','none');
	d3.selectAll('div.page')
		.style('display','none');


}

var setVideoHeight = function(){

	d3.select('#video')
		.style('height',d3.select('#video').node().clientWidth*0.6 + 'px');

	d3.select('#video img.poster')
		.attr('height',d3.select('#video').node().clientWidth*0.6);

	d3.select('#video svg.playButton')
		.attr('height',d3.select('#video svg.playButton').node().clientWidth)
	d3.select('#video')
		.on('mouseover',function(){
			d3.select(this).select('svg.playButton g#ABOUT')
				.transition()
				.duration(100)
				.attr('fill','#FFB637')
		})
		.on('mouseout',function(){
			d3.select(this).select('svg.playButton g#ABOUT')
				.transition()
				.duration(100)
				.attr('fill','#040019')
		});
}

var setHr = function(){
	d3.selectAll('h2')
		.each(function(){
			var m = d3.select(this).style('margin-left');
			m = m.substring(0,m.length-2);
			var w = d3.select(this).node().parentNode.clientWidth - d3.select(this).node().clientWidth - 6 - m;
			d3.select(d3.select(this).node().parentNode).select('hr').style('width',w + 'px');
		})
}

var setColumns = function(){
	var h = 0;
	d3.selectAll('#data div.column')
		.each(function(){
			if(d3.select(this).node().clientHeight-80 > h) h = d3.select(this).node().clientHeight-80;

		})
		.each(function(){
			d3.select(this).style('height',h+'px');
		})
}

var initNav = function(){

	d3.selectAll('#pagesNav li')
		.filter(function(d,i){return i<3})
		.on('click',function(d,i){
			if(i!=2) togglePanel(this,false,i);
		})
	d3.select('svg.closeButton')
		.on('click',function(){
			if(currentPage == 'Twitter') toggleTwitterPanel();
			else togglePanel(d3.select('#pagesNav li:first-child').node(),false, 0);
		})

	
}

var initVideo = function(){
	d3.select('#video')
	    .on("click", function(){
	        var elm = d3.select(this),
	            conts   = elm.html().split('\n'),
	            le      = conts.length,
	            ifr     = null;
	        for(var i = 0; i<le; i++){
	        	var m = conts[i].match(/<!--([^-]+)-->/);
	        	if(m) ifr = m[1];
	        }
	        elm.classed("player",true)
	        	.html(ifr+elm.html())
	        	.on('click',null);
	        d3.select('#video iframe')
	        	.attr('height',d3.select('#video').node().clientWidth*0.6);
	        d3.selectAll('#video img.poster , #video svg.playButton')
	        	.style('pointer-events','none')
	        	.transition()
	        	.style('opacity',0)
	    });
}

var initMetrics = function(){

	var updateLoader = function(){
		loaderOffset += 0.03;
		var arc1 = d3.svg.arc()
		    .innerRadius(2)
		    .outerRadius(6)
		    .startAngle(loaderOffset)
		    .endAngle(Math.PI+loaderOffset)
		var arc2 = d3.svg.arc()
		    .innerRadius(2)
		    .outerRadius(6)
		    .startAngle(Math.PI+loaderOffset)
		    .endAngle(Math.PI*2+loaderOffset)

		d3.select('svg#loader path:first-child')
			.attr('d', arc1)
			
		d3.select('svg#loader path:last-child')
			.attr('d', arc2)
		if(!dataReady) requestAnimationFrame(updateLoader);
	}

	d3.select('svg#loader')
		.append('path')
		.attr('transform','translate(6,6)')
		.attr('fill','rgba(255,255,255,0.6)')
	d3.select('svg#loader')
		.append('path')
		.attr('transform','translate(6,6)')
		.attr('fill','white')
	updateLoader();

	var d = new Date('August 17, 2014');
	queryAmbit(d);
	querySightings(d);

}

var queryAmbit = function(date){
	var dateString = ''+date.getFullYear() + (date.getMonth()>8?'':0) + (date.getMonth()+1) + (date.getDate()>9?'':0) + (date.getDate()+(date.getDate()<10?1:0));
	var url = 'http://intotheokavango.org/api/timeline?date='+dateString+'&types=ambit&days=1';
	if(!isGraphReady) url = 'http://intotheokavango.org/api/timeline?date=20140817&types=ambit&days=18';
	console.log('d3.json : ' + url);
	// d3.json(url, function (json) {

		// if(json.features.length == 0) return;
		// ambitJson.push(json);
		
		// if(ambitJson.length>0 && sightingJson.length>0 && !dataReady) enableDataPage(ambitJson,sightingJson);
		// else if(ambitJson.length>0 && sightingJson.length>0 && dataReady) updateAmbitData();
		// if(isGraphReady) queryAmbit(new Date(+date.getTime() + (24*60*60*1000)));
	// });
}

var querySightings = function(date){
	var dateString = ''+date.getFullYear() + (date.getMonth()>8?'':0) + (date.getMonth()+1) + (date.getDate()>9?'':0) + date.getDate();
	var url = 'http://intotheokavango.org/api/timeline?date='+dateString+'&types=sighting&days=1';
	if(!isGraphReady) url = 'http://intotheokavango.org/api/timeline?date=20140817&types=sighting&days=18';
	console.log('d3.json : ' + url);
	// d3.json(url, function (json) {
		
	// 	if(json.features.length == 0) return;
	// 	sightingJson.push(json);

	// 	if(ambitJson.length>0 && sightingJson.length>0 && !dataReady) enableDataPage(ambitJson,sightingJson);
	// 	else if(ambitJson.length>0 && sightingJson.length>0 && dataReady) initSighting(sightingJson);
	// 	if(isGraphReady) querySightings(new Date(+date.getTime() + (24*60*60*1000)));
	// });
}


var enableDataPage = function(ambitJson,sightingJson){

	console.log('ENABLE DATA PAGE');
	dataReady = true;

	d3.select('#fullPanelWrapper')
			.style('display','block')
			.style('opacity',0)

	d3.select('#fullPanelWrapper div.page:nth-child(3)')
		.style('display','block')
		.style('position','relative')
		.style('margin-left',0)
		.style('opacity',0)

	d3.selectAll('#pagesNav li')
		.filter(function(d,i){return i==3})
		.classed('inactive',false)
		.on('click',function(d,i){
			togglePanel(this,false,3);
		})
		.style('color','rgb(255, 182, 55)')
		.style('opacity','1')
		.each(function(){
			var _this = this;
			requestAnimationFrame(function(){
				d3.select(_this)
					.on('mouseover',function(){
						d3.select(_this).style('opacity',1)
					})
					.on('mouseout',function(){
						d3.select(_this).style('opacity',0.6)
					})
					.transition()
					.delay(500)
					.style('color','rgb(255, 255, 255)')
					.style('opacity','0.6')

				if(currentPage == 'Map') {
					d3.select('#fullPanelWrapper')
						.style('display','none')
				}

				d3.select('#fullPanelWrapper div.page:nth-child(3)')
					.style('display','none')
			})
		})

	d3.select('svg#loader')
		.transition()
		.delay(1000)
		.style('opacity',0)
		.each('end',function(){
			d3.select(this)
				.style('display','none')
		})

	initTimeline(ambitJson);
	initGraphs(ambitJson);
	initSighting(sightingJson);
}


var initSighting = function(data){

	if(currentPage != 'Data'){
		d3.select('#fullPanelWrapper')
			.style('display','block')
		d3.select('#fullPanelWrapper div.page:nth-child(3)')
			.style('display','block')

		requestAnimationFrame(function(){
			if(currentPage == 'Map'){
				d3.select('#fullPanelWrapper')
					.style('display','none')
			}
			d3.select('#fullPanelWrapper div.page:nth-child(3)')
				.style('display','none')
		});
	}

	var sightings = [];

	for(var h = 0; h<data.length; h++){
		var json = data[h].features;
		var len = json.length;
		for(var i = 0; i<len; i++){
			var flag = false;
			for(var j=0; j<sightings.length; j++){
				if(json[i].properties['Bird Name'] == sightings[j].id) {
					var c = json[i].properties['Count'];
					if(c){
						c = parseInt(c);
						sightings[j].count += c;
					} else sightings[j].count ++;
					flag = true;
					break;
				}
			}
			if(!flag) sightings.push({id:json[i].properties['Bird Name'],count:1});
		}
	}

	sightings.sort(function(a, b){ return d3.descending(a.count, b.count); })

	d3.select('#data #sightings p').html('')

	len = sightings.length;
	var flag = false;
	for(var i=0; i<len && !flag; i++){
		d3.select('#data #sightings p')
			.html(function(){return d3.select(this).html() + sightings[i].id + ' (<span>' + sightings[i].count +'</span>) • '})
			.each(function(){
				if(d3.select(this).node().clientHeight>105){
					flag = true;
					var last = sightings[i].id + ' (' + sightings[i].count +') • ';
					var s = d3.select(this).html();
					d3.select(this).html(s.substring(0,s.length-last.length-3)+'...');
				}
			})
	}

}


var initTimeline = function(json){

	var w = d3.select('body').node().clientWidth*0.89*0.97-4;
	var h = d3.select('#timeline').style('height');
	h = +h.substring(0,h.length-2)-4;

	var timeScale = d3.scale.linear()
 		.range([0, w])
 		.domain([new Date(json[0].features[0].properties.t_utc*1000).getTime(),new Date(json[json.length-1].features[json[json.length-1].features.length-1].properties.t_utc*1000+1).getTime()]);

	var timeline = d3.select('svg.timeline')
		.attr('width',w)
		.attr('height',h)
		.style('margin-top','2px')
		.style('margin-left','2px')

	var updateSelection = function(){
		timeline.select('rect.selection')
			.attr('x',function(d){return w*d[0]+h})
			.attr('width',function(d){return w*(d[1]-d[0])-h*2})

		timeline.selectAll('rect.outside')
			.data(cursorRange)
			.attr('x',function(d,i){return i==0?0:w*d})
			.attr('width',function(d,i){return i==0?w*d:w-w*d})

	}

	var sliderBehavior = function(){
        
        var _this = this;
		
		var drag = d3.behavior.drag()
        	.on('drag', function(d,i) {

        		var coords = [];
        		for(var j=1; j<=2; j++){
        			var x = d3.select('g.slider:nth-child('+j+')').attr('transform');
        			x = +x.substring(10,x.length-3);
        			coords.push(x);
        		}
        		var min = i==0?0:(coords[0]+h*2-h);
        		var max = i==1?w:(coords[1]-h*2+h);

        		var x = d3.select(this).attr('transform');
        		x = +x.substring(10,x.length-3);
	        	x = Math.min(max,Math.max(min,x+d3.event.dx));
	        	d3.select(this)
	        		.attr('transform','translate('+x+',0)')

	        	d3.select(this)
	        		.datum(x/w);
	        	cursorRange[i] = x/w;

	        	updateSelection();

	        	var d = new Date(timeScale.invert(x));
	        	d = [(d.getMonth()+1)+'',d.getDate()+'',d.getHours()+'',d.getMinutes()+''];
	        	d = (d[0].length==1?'0':'')+d[0]+'/'+(d[1].length==1?'0':'')+d[1]+' '+(d[2].length==1?'0':'')+d[2]+':'+(d[3].length==1?'0':'')+d[3];
	        	d3.select(this).select('text')
	        		.text(d);

	        	var otherSliderX = d3.selectAll('g.slider').filter(function(d,i1){return i!=i1}).attr('transform');
	        	otherSliderX = +otherSliderX.substring(10,otherSliderX.length-3);
	        	var dist = Math.abs(otherSliderX - x);

	        	if(dist > 210) d3.selectAll('g.slider text').transition().duration(50).style('opacity',1);
	        	else if(dist > 110) {
	        		d3.select('g.slider:first-child text').transition().duration(50).style('opacity',0);
	        		d3.select('g.slider:last-child text').transition().duration(50).style('opacity',1);
	        	} else d3.selectAll('g.slider text').transition().duration(50).style('opacity',0);

	        	timelineRange = [timeScale.invert(i==0?x:otherSliderX),timeScale.invert(i==1?x:otherSliderX)];
	        	
	        	updateGraphs();

        		return this;
        	})

		this
			.on('mouseover',function(){
				d3.select(this).select('rect')
					.transition()
					.duration(150)
					.attr('fill','rgb(255,255,255)')
			})
			.on('mouseout',function(){
				d3.select(this).select('rect')
					.transition()
					.duration(150)
					.attr('fill','rgb(255,182,55)')
			})
			.call(drag)
		return this;
	}

	timeline.selectAll('g.slider')
		.data(cursorRange)
        .enter()
		.append('g')
		.classed('slider',true)
		.attr('transform',function(d,i){return 'translate(' + (i==0?w*cursorRange[0]:w*cursorRange[1])+',0)'})
		.call(sliderBehavior);

	timeline.selectAll('g.slider')
		.append('rect')
		.attr('width',h)
		.attr('height',h)
		.attr('x',function(d,i){return i==0 ? 0:-h})
		.attr('fill','rgb(255,182,55)')
		.style('cursor','pointer')

	timeline.selectAll('g.slider')
		.append('text')
		.text(function(d,i){
			var d = new Date(timeScale.invert(i==0?w*cursorRange[0]:w*cursorRange[1]));
        	d = [(d.getMonth()+1)+'',d.getDate()+'',d.getHours()+'',d.getMinutes()+''];
        	d = (d[0].length==1?'0':'')+d[0]+'/'+(d[1].length==1?'0':'')+d[1]+' '+(d[2].length==1?'0':'')+d[2]+':'+(d[3].length==1?'0':'')+d[3];
        	return d;
		})
		.attr('x',function(d,i){return i==0 ? h+5:-5-h})
		.attr('y',h*0.66)
		.attr('text-anchor',function(d,i){return i==0 ? 'start':'end'})
		.attr('fill','rgb(255,255,255)')
		
	timeline
		.append('rect')
		.datum(cursorRange)
		.classed('selection',true)
		.attr('height',h)
		.attr('fill','rgba(255,182,55,0.5)')

	timeline.selectAll('rect.outside')
		.data(cursorRange)
        .enter()
		.append('rect')
		.classed('outside',true)
		.attr('height',h)
		.attr('fill','rgba(255,255,255,0.1)')

	updateSelection();

	timelineRange = [timeScale.invert(0),timeScale.invert(w)];

}

var initGraphs = function(data){

	var w = d3.select('#scale svg.graph').style('width');
	w = +w.substring(0,w.length-2);
	var h = d3.select('#scale svg.graph').style('height');
	h = +h.substring(0,h.length-2);

	// timescale
	d3.select('#scale svg.labels')
		.append('text')
		.text('time')
		.attr('text-anchor','end')
		.attr('y',h*0.58)
		.attr('fill','white')
		.attr('x',function(){
			var w = d3.select('#scale svg.labels').style('width');
			return +w.substring(0,w.length-2)-10;
		})

	d3.select('#scale svg.graph')
		.append('g')
		.classed('dates',true)
		.attr('transform','translate(0,'+(-33)+')')

	d3.select('#scale svg.graph')
		.append('line')
		.attr('stroke','rgba(255,255,255,0.2)')
		.attr('x1',0)
		.attr('y1',h/2+0.5)
		.attr('x2',w)
		.attr('y2',h/2+0.5)

	
	// data
	metrics = {
		minHeartRate:10000,
		maxHeartRate:0,
		maxEnergyConsumption:0,
		maxSpeed:3,
		persons:[]
	};

	for(var h=0; h<data.length; h++){
		var json = data[h].features;
		var len = json.length;
		for(var i=0; i<len; i++){
			var ambit = json[i].properties;
			if(!metrics[ambit.Person]){
				metrics[ambit.Person] = {
					heartrate:[],
					energyConsumption:[],
					speed:[]
				}
				metrics.persons.push(ambit.Person);
			}
			var d = ambit.t_utc*1000;
			if(ambit.HR) metrics[ambit.Person].heartrate.push([d,ambit.HR])
			if(ambit.EnergyConsumption) metrics[ambit.Person].energyConsumption.push([d,ambit.EnergyConsumption])
			if(ambit.Speed) metrics[ambit.Person].speed.push([d,ambit.Speed])

			if(ambit.HR > metrics.maxHeartRate) metrics.maxHeartRate = ambit.HR;
			if(ambit.HR < metrics.minHeartRate) metrics.minHeartRate = ambit.HR;
			if(ambit.EnergyConsumption > metrics.maxEnergyConsumption) metrics.maxEnergyConsumption = ambit.EnergyConsumption;
		}
	}

	d3.selectAll('div.graph svg.labels')
		.filter(function(d,i){return i>0})
		.append('g')
		.classed('axis',true)
		.attr('width',w)

	len = metrics.persons.length;
	for(var i=0; i<len; i++){
		var p = metrics.persons[i]
		d3.select('#heartrate svg.graph')
	        .append('path')
	        .classed(p,true)
	        .attr('stroke',personalColors[i])
	        .attr('fill','none');
	    d3.select('#energyConsumption svg.graph')
	        .append('path')
	        .classed(p,true)
	        .attr('stroke',personalColors[i])
	        .attr('fill','none');
	    d3.select('#speed svg.graph')
	        .append('path')
	        .classed(p,true)
	        .attr('stroke',personalColors[i])
	        .attr('fill','none');

	    d3.select('#persons')
	    	.append('span')
	    	.html('<span></span>'+metrics.persons[i])
	    	.select('span')
	    		.style('background-color',personalColors[i]);
	}

	updateGraphs();

	// var totalDistance = Math.round(parseInt(json[json.length-1].properties.Distance)/100)/10;
	// d3.select('#data p.counter span')
	// 	.html('320km ')
	// 	// .html(totalDistance + 'km ')

	// var averageSpeed = 0;
	// var len = json.length;
	// var offset = 0;
	// for(var i=0; i<len; i++){
	// 	if(json[i].properties.Speed) averageSpeed += parseFloat(json[i].properties.Speed);
	// 	else offset --;
	// }
	// averageSpeed /= (len+offset);
	// averageSpeed = Math.round(averageSpeed*10)/10;
	// d3.select('#data p.counter:last-child span:last-child')
	// 	.html(' ' + averageSpeed + 'km/h')

}

var updateGraphs = function(){

	var w = d3.select('#scale svg.graph').style('width');
	w = +w.substring(0,w.length-2);
	var h = d3.select('#scale svg.graph').style('height');
	h = +h.substring(0,h.length-2);
	var hGraph = d3.select('#heartrate svg.graph').style('height');
	hGraph = +hGraph.substring(0,hGraph.length-2);
	var wGraph = d3.select('#scale svg.labels').style('width');
	wGraph = +wGraph.substring(0,wGraph.length-2);

	var timeScale = d3.time.scale()
 		.range([0, w])
 		.domain([timelineRange[0],timelineRange[1]]);
    var timelineAxis = d3.svg.axis()
        .scale(timeScale)
        .orient("bottom")
        .tickSize(h)
	  	.ticks(Math.max(5,Math.ceil((timelineRange[1]-timelineRange[0])/(1000*3600*24))))

	d3.select('#scale svg.graph g.dates')
		.call(timelineAxis);
	

	var x = d3.scale.linear().range([0, w]).domain([timelineRange[0]/1000,timelineRange[1]/1000]);
	var yHeartrate = d3.scale.linear().range([hGraph, 0]).domain([metrics.minHeartRate,metrics.maxHeartRate]);
	var yEnergyConsumption = d3.scale.linear().range([hGraph, 0]).domain([0,metrics.maxEnergyConsumption]);
	var ySpeed = d3.scale.linear().range([hGraph, 0]).domain([0,metrics.maxSpeed]);
	var lines = {
		HeartRate : d3.svg.line().x(function(d) { return x(d[0]/1000); }).y(function(d) { return yHeartrate(d[1]); }),
		EnergyConsumption : d3.svg.line().x(function(d) { return x(d[0]/1000); }).y(function(d) { return yEnergyConsumption(d[1]); }),
		Speed : d3.svg.line().x(function(d) { return x(d[0]/1000); }).y(function(d) { return ySpeed(d[1]); })
	}

	len = metrics.persons.length;
	for(var i=0; i<len; i++){
		var p = metrics.persons[i]
		d3.select('#heartrate svg.graph path.'+p)
	        .datum(function(){
	        	var subsetRange = [];
	        	var len = metrics[p].heartrate.length;
	        	var d;
	        	for(var j=0; j<len; j++){
	        		if((metrics[p].heartrate[j][0])>=timelineRange[0]) break;
	        	}
	        	subsetRange[0] = j;
	        	for(var j=len-1; j>=0; j--){
	        		if((metrics[p].heartrate[j][0])<=timelineRange[1]) break;
	        	}
	        	subsetRange[1] = j;
	        	var datum = metrics[p].heartrate.slice(subsetRange[0],subsetRange[1]);
		        	// if(datum.length>0){
		        	// 	var temp;
		        	// 	len = datum.length;
		        	// 	for(var j=0; j<len; j++){
		        	// 		// if(j%(1/))
		        	// 	}
		        	// }
	        	return datum;
	        })
	        .attr('d',lines.HeartRate)
	    d3.select('#energyConsumption svg.graph path.'+p)
	        .datum(function(){
	        	var subsetRange = [];
	        	var len = metrics[p].energyConsumption.length;
	        	var d;
	        	for(var j=0; j<len; j++){
	        		if((metrics[p].energyConsumption[j][0])>=timelineRange[0]) break;
	        	}
	        	subsetRange[0] = j;
	        	for(var j=len-1; j>=0; j--){
	        		if((metrics[p].energyConsumption[j][0])<=timelineRange[1]) break;
	        	}
	        	subsetRange[1] = j;
	        	return metrics[p].energyConsumption.slice(subsetRange[0],subsetRange[1]);
	        })
	        .attr('d',lines.EnergyConsumption)
	    d3.select('#speed svg.graph path.'+p)
	        .datum(function(){
	        	var subsetRange = [];
	        	var len = metrics[p].speed.length;
	        	var d;
	        	for(var j=0; j<len; j++){
	        		if((metrics[p].speed[j][0])>=timelineRange[0]) break;
	        	}
	        	subsetRange[0] = j;
	        	for(var j=len-1; j>=0; j--){
	        		if((metrics[p].speed[j][0])<=timelineRange[1]) break;
	        	}
	        	subsetRange[1] = j;
	        	return metrics[p].speed.slice(subsetRange[0],subsetRange[1]);
	        })
	        .attr('d',lines.Speed)
	}

	d3.select('#heartrate svg.labels g.axis')
		.attr('transform','translate('+wGraph+',-5)')
		.attr('text-align','end')
		.call(d3.svg.axis().scale(yHeartrate).orient("left").ticks(5));

	d3.select('#energyConsumption svg.labels g.axis')
		.attr('transform','translate('+wGraph+',-5)')
		.attr('text-align','end')
		.call(d3.svg.axis().scale(yEnergyConsumption).orient("left").ticks(5));

	d3.select('#speed svg.labels g.axis')
		.attr('transform','translate('+wGraph+',-5)')
		.attr('text-align','end')
		.call(d3.svg.axis().scale(ySpeed).orient("left").ticks(5));

	d3.selectAll('svg.graph text, svg.labels text')
		.attr('fill','white');
	d3.selectAll('svg.graph path.domain,svg.labels path.domain')
		.remove()
    
}

var updateAmbitData = function(){

	d3.selectAll('svg.timeline *').remove();
	initTimeline(ambitJson);

	d3.selectAll('div.graph svg *').remove();
	d3.selectAll('#graphWrapper #persons').remove();
	initGraphs(ambitJson);

}


var togglePanel = function(node, mapClick, i){

	if(currentPage == 'Twitter'){
		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('display','block')
			.transition()
			.duration(400)
			.ease("cubic-out")
			.style('right',(d3.select(node).text() != "Map" ? (w*0.03+1) : (w*0.68)) + 'px')
			.style('opacity',d3.select(node).text() != "Map" ? 1:0)

		d3.select('#map_holder')
			.style('cursor','pointer')
			.on('click',function(){
				togglePanel(this, true, 0);
			});
	}

	if(mapClick || (d3.select(node).text() == "Map" && currentPage != "Map" && currentPage != "Twitter")){

		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('div.leaflet-top.leaflet-right')
			.transition()
			.style('opacity',1)
		d3.select('#credits')
			.transition()
			.style('opacity',1)
		d3.select('div.leaflet-control-attribution')
			.transition()
			.style('opacity',1)
		d3.select('#tweetsButton')
			.transition()
			.style('opacity',1)

		d3.select('#fullPanelWrapper')
			.style('right',(w*0.03+1) + 'px')
			.transition()
			.duration(200)
			.ease("cubic-in")
			.style('opacity',0)
			.style('right',(w*0.08)+'px')
			.each('end',function(){
				d3.select(this).style('display','none');
			});

	    d3.select('#map_holder')
	    	.style('cursor','auto')
			.on('click',null);

	} else if(d3.select(node).text() != "Map" && (currentPage == "Map" || currentPage =='Twitter')){

		d3.select('div.leaflet-top.leaflet-right')
			.transition()
			.style('opacity',0)
		d3.select('#credits')
			.transition()
			.style('opacity',0)
		d3.select('div.leaflet-control-attribution')
			.transition()
			.style('opacity',0)
		d3.select('#tweetsButton')
			.transition()
			.style('opacity',0)

		d3.select('#fullPanelWrapper')
			.style('display','block')

		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('display','block')
			.style('right',(w*0.08)+'px')
			.transition()
			.duration(200)
			.ease("cubic-out")
			.style('right',(w*0.03+1) + 'px')
			.style('opacity',1)

		d3.select('#map_holder')
			.style('cursor','pointer')
			.on('click',function(){
				togglePanel(this, true, 0);
			});

	}

	var div = document.getElementById("video");
    var iframe = div.getElementsByTagName("iframe")[0];
    if(iframe) {
    	iframe = iframe.contentWindow;
    	iframe.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
    }

	d3.selectAll('#fullPanelWrapper div.page')
		.style('position','absolute')
		.transition()
		.duration(180)
		.style('opacity',0)
		.each('end',function(){
			d3.select(this).style('display','none');
		})

	if(i>0){
		d3.select('#fullPanelWrapper div.page:nth-child('+i+')')
			.style('display','block')
			.style('margin-left',-50)
			.style('position','relative')
			.transition()
			.duration(180)
			.ease("cubic-out")
			.style('margin-left',0)
			.style('opacity',1)
	}

	currentPage = mapClick ? 'Map' : d3.select(node).text();
	d3.selectAll('#pagesNav li')
		.classed('focused',function(){return d3.select(this).text() == currentPage || (d3.select(this).text() == 'Map' && mapClick)});

	clearTimeout(toggleTwitterPanel);

}

var toggleTwitterPanel = function(){

	d3.selectAll('#fullPanelWrapper div.page')
		.style('position','absolute')
		.transition()
		.duration(180)
		.style('opacity',0)
		.each('end',function(){
			d3.select(this).style('display','none');
		})

	if(currentPage != 'Twitter'){
		d3.select('#credits')
			.transition()
			.style('opacity',0)

		d3.select('#fullPanelWrapper div.page:nth-child(4)')
			.style('display','block')
			.style('margin-left',-50)
			.style('position','relative')
			.transition()
			.duration(180)
			.ease("cubic-out")
			.style('margin-left',0)
			.style('opacity',1)

		d3.select('#fullPanelWrapper')
			.style('display','block')

		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('display','block')
			.style('right',(w*0.68) + 'px')
			.transition()
			.duration(200)
			.ease("cubic-out")
			.style('right',(w*0.645) + 'px')
			.style('opacity',1)

		d3.select('#headerWrapper').style('position','fixed');

		currentPage = 'Twitter';
	} else {
		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('right',(w*0.645) + 'px')
			.transition()
			.duration(200)
			.ease("cubic-in")
			.style('right',(w*0.68) + 'px')
			.style('opacity',0)
			.each('end',function(){
				d3.select(this).style('display','none');
				d3.select('#headerWrapper').style('position','absolute');
				d3.select('#map_holder')
			    	.style('cursor','auto')
					.on('click',null);
				currentPage = 'Map';
			});

		d3.select('#credits')
			.transition()
			.style('opacity',1)
	}

	clearTimeout(closeFeedTimer);
}

var initFeed = function(json){

	if(!json)return;    
	for(var i =0; i<json.features.length; i++){
		var t = {
			username: json.features[i].properties.tweet.user.name,
			message: json.features[i].properties.tweet.text,
			date: new Date(Math.round(parseFloat(json.features[i].properties.t_utc*1000))),
			coords: json.features[i].geometry.coordinates,
			profilePicUrl: json.features[i].properties.tweet.user.profile_image_url,
			id: json.features[i].id
		};
		try{
			if(t.photoUrl = json.features[i].properties.tweet.extended_entities.media[0].type == 'photo'){
				t.photoUrl = json.features[i].properties.tweet.extended_entities.media[0].media_url;
			}
		} catch(e){}
		if(t.message.substring(0,2).toLowerCase() != 'rt') tweets.push(t);
	}
	tweets.reverse();

	var m_names = new Array("Jan", "Feb", "Mar", 
	"Apr", "May", "Jun", "Jul", "Aug", "Sep", 
	"Oct", "Nov", "Dec");

	d3.select('#twitterWrapper').selectAll('div.tweet')
        .data(tweets)
        .enter()
        .append('div')
        .classed('tweet',true)
        .html(function(d,i){
        	return '<div class="controls"><div class="locationFinder"></div><a><div class="twitter"></div></a></div><p class="meta">        	</p><hr class="innerSeparator"/><div class="body"><img src = "'+d.profilePicUrl+'" width="10%" height="10%" class="profile"/><p class="message"></p>' + (d.photoUrl ? '<img src = "'+d.photoUrl+'" width="100%" class="pic"/>' : '') + '</div><hr class="outerSeparator"/>'
        })
        .each(function(d,i){
        	d3.select(this).select('a')
        		.attr('href','http://www.twitter.com')

        	var t = d.date;
        	t = ((parseInt(t.getDate())+1) + ' ' + m_names[t.getMonth()] + ' - ' + ((t.getHours()+'').length==1?'0':'') + t.getHours() + ':'+ ((t.getMinutes()+'').length==1?'0':'') +t.getMinutes());
        	d3.select(this).select('p.meta')
        		.html(t + '<span></span>' + d.username);
        	d3.select(this).select('p.message')
        		.html(function(){
        			var content = d.message;
        	// 		content.replace('http[^>]*','').
        	// // [^>]*
        	// // var content = 
        			return content;
        		});
        	var _this = this;
        	d3.select(this).selectAll('div.body, div.locationFinder')
        		.on('click',function(d){findTweetLocation(d3.select(_this).datum().coords)});
        })	

    d3.select('#tweetsButton')
    	.style('display','inline-block')
    	.on('click',function(){toggleTwitterPanel();})
    	.transition()
    	.style('opacity',1);

    d3.select('#twitterFeed')
    	.style('height',(d3.select('body').node().clientHeight-192)+'px')

    d3.select('#twitterWrapper')
    	.on('mousewheel',function(){
    		d3.select(this)
    			.style('margin-top',function(){
    				var h = d3.select(this).style('margin-top')
    				h = parseFloat(h.substring(0,h.length-2));
    				h = h + d3.event.wheelDeltaY/2.5;
    				h = Math.min(0,h);	// fix max scroll
    				return h + 'px';
    			})
    	})


}

var focusTweet = function(queue){

	var tweetFound = false;
    var id = queue.marker.feature.id;
    var h = d3.select('#twitterWrapper').style('margin-top');
    h = -parseFloat(h.substring(0,h.length-2));

    d3.select('#twitterWrapper').selectAll('div.tweet')
        .filter(function(d){return id == d.id})
        .each(function(){
        	h += this.offsetTop;
        	tweetFound = true;
        })

    if(tweetFound){
    	console.log('focusing tweet: ' + queue.marker.feature.properties.tweet.text);
    	clearTimeout(closeFeedTimer);
    	if(currentPage != 'Twitter') toggleTwitterPanel();
	    d3.select('#twitterWrapper')
	    	.transition()
	    	.duration(500)
	    	.ease("cubic-in-out")
	    	.style('margin-top',(20-h)+'px');
    	if(startTime - (tweetsQueue[tweetCounter].time/1000 - 300) > 20) closeFeedTimer = setTimeout(toggleTwitterPanel,10000);
    }

}


var initMapTimeline = function(){
	if(isGraphReady){
	var h = 27;

	var w = window.innerWidth - (d3.select('#tweetsButton').node().clientWidth + window.innerWidth*0.463 + 100);
	d3.select('#mapTimeline')
		.style('width',w+'px');

	w = d3.select('#mapTimeline').node().clientWidth - h - d3.select('#mapTimeline div.counter').node().clientWidth - 38;
	d3.select('#mapTimeline div.bar')
		.style('width',w+'px');
	d3.select('#mapTimeline div.bar')
		.append('svg')

		d3.select('#mapTimeline div.bar svg').selectAll('circle')
			.data(function(){
				var dates = [];
				var d = new Date('August 17, 2014');
				for(var i = 0; i<19; i++){
					dates.push(d);
					d = new Date(d.getTime() + (24*60*60*1000));
				}
				return dates;
			})
			.enter()
			.append('g')
			.attr('transform',function(d,i){ return 'translate(' + (5+(i/16)*(w-10)) + ',' + h/2 +')';})
			.each(function(d,i){
				d3.select(this)
					.append('rect')
					.attr('x',-w/16/2)
					.attr('y',-h/2)
					.attr('width',w/16)
					.attr('height',h)
					.attr('fill','rgba(0,0,0,0)')
				d3.select(this)
					.append('circle')
					.attr('r',2.5)
					.attr('fill','rgba(255,255,255,0.6)');
			})
			.style('cursor','pointer')
			.on('mouseover',function(){
				d3.select(this).select('circle')
					.transition()
					.duration(150)
					.attr('r',5)
			})
			.on('mouseout',function(){
				d3.select(this).select('circle')
					.transition()
					.duration(150)
					.attr('r',2.5)
			})
			.on('click',function(){alert("still broken, I'm working on it.")})

		d3.select('#mapTimeline div.bar svg')
			.append('line')
			.classed('covered',true)
			.attr('x1',5)
			.attr('y1',h/2)
			.attr('x2',5)
			.attr('y2',h/2)
			.attr('stroke','rgba(255,255,255,1)')

		d3.select('#mapTimeline div.bar svg')
			.append('line')
			.classed('uncovered',true)
			.attr('x1',5)
			.attr('y1',h/2)
			.attr('x2',w-5)
			.attr('y2',h/2)
			.attr('stroke','rgba(255,255,255,0.5)')
	}
			
}

var updateMapTimeline = function(d){
	if(isGraphReady){

		var h = 27;
		var w = window.innerWidth - (d3.select('#tweetsButton').node().clientWidth + window.innerWidth*0.463 + 100);

		function map(value, start1, stop1, start2, stop2) {
		    return parseFloat(start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1)));
		}

		var dd = new Date();
	    var offset = dd.getTimezoneOffset();
	    var sd = new Date((sightingsQueue[sightingCounter].time * 1000) + (offset * 60 * 1000) );
	    var dom = d.getDate();
	    var dispd = (d.getMonth() == 7 ? dom - 16:15 + dom)
		d3.select('#mapTimeline div.counter')
			.text("DAY " + dispd + " - " + (d.getHours()<10?'0':'') +d.getHours() + ':' + (d.getMinutes()<10?'0':'') +d.getMinutes());

		var d1 = new Date('August 17, 2014');
		var d2 = new Date('September 4, 2014');
		var r = map(d.getTime(),d1.getTime(),d2.getTime(),0,1);

		d3.select('#mapTimeline div.bar svg line.covered')
			.attr('x1',5)
			.attr('y1',h/2)
			.attr('x2',5+(w-10)*r)
			.attr('y2',h/2)

		d3.select('#mapTimeline div.bar svg line.uncovered')
			.attr('x1',5+(w-10)*r)
			.attr('y1',h/2)
			.attr('x2',w-5)
			.attr('y2',h/2)

		d3.select('#mapTimeline div.bar svg').selectAll('circle')
			.filter(function(d1){ return d1.getTime()<=d.getTime()})
			.attr('fill','rgba(255,255,255,1)');

		d3.select('#mapTimeline div.bar svg').selectAll('circle')
			.filter(function(d1){ return d1.getTime()>d.getTime()})
			.attr('fill','rgba(255,255,255,0.6)');

	}

}

