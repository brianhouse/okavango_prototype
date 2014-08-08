

/*

*/


var currentPage = "Map";


window.onload = function (){ 
	init();
}

window.onresize = function(){
	setVideoHeight();
	setHr();
}

window.onkeypress = function(){
	// toggleTwitterPanel();
}


var init = function(){
	setVideoHeight();
	setHr();
	initNav();
	initVideo();
	d3.select('#fullPanelWrapper')
		.style('display','none');
	d3.selectAll('div.page')
		.style('display','none');

	loadTweets();

}

var setVideoHeight = function(){

	d3.select('#video')
		.style('height',d3.select('#video').node().clientWidth*0.6);
	d3.select('#video img.poster')
		.attr('height',d3.select('#video').node().clientWidth*0.6);

	d3.select('#video svg.playButton')
		.attr('height',d3.select('#video svg.playButton').node().clientWidth)
	d3.select('#video')
		.on('mouseover',function(){
			d3.select(this).select('svg.playButton g#about')
				.transition()
				.duration(100)
				.attr('fill','#FFB637')
		})
		.on('mouseout',function(){
			d3.select(this).select('svg.playButton g#about')
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
			d3.select(d3.select(this).node().parentNode).select('hr').style('width',w);
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

var togglePanel = function(node, mapClick, i){

	if(currentPage == 'Twitter'){
		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('display','block')
			.transition()
			.duration(400)
			.ease("cubic-out")
			.style('right',w*0.03+1)
			.style('opacity',1)

		d3.select('#map_holder')
			.style('cursor','pointer')
			.on('click',function(){
				togglePanel(this, true, 0);
			});
	}

	if(mapClick || (d3.select(node).text() == "Map" && currentPage != "Map")){

		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#credits')
			.transition()
			.style('opacity',1)

		d3.select('#fullPanelWrapper')
			.style('right',w*0.03+1)
			.transition()
			.duration(200)
			.ease("cubic-in")
			.style('opacity',0)
			.style('right',w*0.08)
			.each('end',function(){
				d3.select(this).style('display','none');
			});

	    d3.select('#map_holder')
	    	.style('cursor','auto')
			.on('click',null);

	} else if(d3.select(node).text() != "Map" && currentPage == "Map"){

		d3.select('#credits')
			.transition()
			.style('opacity',0)

		d3.select('#fullPanelWrapper')
			.style('display','block')

		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('display','block')
			.style('right',w*0.08)
			.transition()
			.duration(200)
			.ease("cubic-out")
			.style('right',w*0.03+1)
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
			.style('right',w*0.68)
			.transition()
			.duration(200)
			.ease("cubic-out")
			.style('right',w*0.645)
			.style('opacity',1)

		d3.select('#map_holder')
			.style('cursor','pointer')
			.on('click',function(){
				togglePanel(this, true, 0);
			});
		currentPage = 'Twitter';
	} else {
		var w = d3.select('#fullPanelWrapper').style('width');
		w = +w.substring(0,w.length-2);

		d3.select('#fullPanelWrapper')
			.style('right',w*0.645)
			.transition()
			.duration(200)
			.ease("cubic-in")
			.style('right',w*0.68)
			.style('opacity',0)
			.each('end',function(){
				d3.select(this).style('display','none');
			});

	    d3.select('#map_holder')
	    	.style('cursor','auto')
			.on('click',null);
		currentPage = 'Map';
	}
}

var loadTweets = function(){

	// var url = "http://storageName.blob.core.windows.net/containerName/file.json";
 //    d3.json("url", function (json) {
    	
 //     //code here
 //    })

}




