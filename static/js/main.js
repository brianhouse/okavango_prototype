

/*
	set back map (display:none)
	rétablir color body
*/


var currentPage = "Map";
var cursorRange = [0.1,0.66];


// window.onload = function (){ 
// 	console.log('load');
// 	initLayout();
// }

window.onresize = function(){
	setVideoHeight();
	setHr();
}


var initLayout = function(){

	setHr();
	setColumns();
	setVideoHeight();
	initNav();
	initVideo();
	initTimeline();
	initGraphs();
	d3.select('#fullPanelWrapper')
		.style('display','none');
	d3.selectAll('div.page')
		.style('display','none');

	loadTweets();

}

var setVideoHeight = function(){

	// console.log('aga');
	// console.log(d3.select('#video').node().clientWidth*0.6);
	// console.log('aga');

	d3.select('#video')
		.style('height',d3.select('#video').node().clientWidth*0.6 + 'px');

	d3.select('#video img.poster')
		.attr('height',d3.select('#video').node().clientWidth*0.6);

	d3.select('#video svg.playButton')
		.attr('height',d3.select('#video svg.playButton').node().clientWidth)
	d3.select('#video')
		.on('mouseover',function(){
			console.log(d3.select(this).select('svg.playButton g#ABOUT'))
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
		.on('click',function(d,i){
			if(i == 0 || i==3) togglePanel(this,false,i);
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


var initTimeline = function(){

	var w = d3.select('svg.timeline').style('width');
	w = +w.substring(0,w.length-2)-4;
	var h = d3.select('svg.timeline').style('height');
	h = +h.substring(0,h.length-2)-4;

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
        		var min = i==0?0:(coords[0]+h*2+90);
        		var max = i==1?w:(coords[1]-h*2-90);

        		var x = d3.select(this).attr('transform');
        		x = +x.substring(10,x.length-3);
	        	x = Math.min(max,Math.max(min,x+d3.event.dx));
	        	d3.select(this)
	        		.attr('transform','translate('+x+',0)')

	        	d3.select(this)
	        		.datum(x/w);
	        	cursorRange[i] = x/w;

	        	updateSelection();

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

	// var selectionDrag = d3.behavior.drag()
 //    	.on('drag', function() {
 //    		console.log(d3.event.dx);
 //    		var x = 
 //    		return this;
 //    	})

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
		.text('12:45')
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
		// .style('cursor','pointer')
		// .on('mouseover',function(){
		// 	d3.select(this)
		// 		.transition()
		// 		.duration(150)
		// 		.attr('fill','rgba(255,182,55,0.66)')
		// })
		// .on('mouseout',function(){
		// 	d3.select(this)
		// 		.transition()
		// 		.duration(150)
		// 		.attr('fill','rgba(255,182,55,0.5)')
		// })
		// .call(selectionDrag)

	timeline.selectAll('rect.outside')
		.data(cursorRange)
        .enter()
		.append('rect')
		.classed('outside',true)
		.attr('height',h)
		.attr('fill','rgba(255,255,255,0.1)')

	updateSelection();

}

var initGraphs = function(){

	var w = d3.select('#scale svg.graph').style('width');
	w = +w.substring(0,w.length-2);
	var h = d3.select('#scale svg.graph').style('height');
	h = +h.substring(0,h.length-2);

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
		.append('line')
        .attr('x2',w)
        .attr('y1',h/2)
        .attr('y2',h/2)
        .attr('stroke','rgba(255,255,255,0.3')

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

		d3.select('#credits')
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

		d3.select('#credits')
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
			});

	    d3.select('#map_holder')
	    	.style('cursor','auto')
			.on('click',null);
		currentPage = 'Map';

		d3.select('#credits')
			.transition()
			.style('opacity',1)
	}
}

var loadTweets = function(){
	var daysRange = Math.ceil((new Date().getTime() - new Date('August 7, 2014').getTime())/(1000*3600*24));
	var url = 'http://intotheokavango.org/api/timeline?date=20140807&types=tweet&days=' + daysRange
	d3.json(url, function (json) {
		if(!json)return;    
    	var tweets = [];
    	json.features.reverse();
		for(var i =0; i<json.features.length; i++){
			var t = {
				username: json.features[i].properties.tweet.user.name,
				message: json.features[i].properties.tweet.text,
				date: new Date(Math.round(parseFloat(json.features[i].properties.t_utc))),
				coords: json.features[i].geometry.coordinates,
				profilePicUrl: json.features[i].properties.tweet.user.profile_image_url,
			};
			try{
				if(t.photoUrl = json.features[i].properties.tweet.extended_entities.media[0].type == 'photo'){
					t.photoUrl = json.features[i].properties.tweet.extended_entities.media[0].media_url;
				}
			} catch(e){}
			tweets.push(t);
		}

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

	        	var t = new Date(d.date.getTime() * 1000);
	        	t = ((t.getDay()+1) + ' ' + m_names[t.getMonth()] + ' - ' + ((t.getHours()+'').length==1?'0':'') + t.getHours() + ':'+ ((t.getMinutes()+'').length==1?'0':'') +t.getMinutes());

	        	d3.select(this).select('p.meta')
	        		.html(t + '<span></span>' + d.username);
	        	d3.select(this).select('p.message')
	        		.html(d.message);
	        	var _this = this;
	        	d3.select(this).selectAll('div.body, div.locationFinder')
	        		.on('click',function(d){findTweetLocation(d3.select(_this).datum().coords)});
	        })	

	    d3.select('#tweetsButton')
	    	.style('display','block')
	    	.style('opacity',0.6)
	    	.on('click',function(){toggleTwitterPanel();})
	    	.on('mouseover',function(){d3.select(this).style('opacity',1)})
	    	.on('mouseout',function(){d3.select(this).style('opacity',0.6)})

    })
	
}



