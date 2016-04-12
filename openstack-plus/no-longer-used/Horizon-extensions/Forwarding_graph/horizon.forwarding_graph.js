var svgns="http://www.w3.org/2000/svg";
var forwarding_graph_container = "#forwarding_graph_topology";
var link;
var node;
var myjson;
var links;
var all_nodes;

var ingressName;
var egressName;
var controlIngressName;
var controlEgressName;
var ingressImg;
var egressImg;
var controlIngressImg;
var controlEgressImg;

var ingressPattern;
var egressPattern;
var controlIngressPattern;
var controlEgressPattern;

//width sizes of different nodes 
var vnfSize = 120;
var switchSize = 200;
var controlSwitchSize = 600;

//fill select box with sessions
function fillSessions(sessions){

	var res = sessions.split("'"); 
	var num_of_sessions = ((res.length-1)/6);

	var j = 1;
	for(var i = 0; i < num_of_sessions; i++){
		$('#forwarding_graph_selector').append("<option value='"+res[j+2]+"'>"+res[j]+"</option>");
		j = j+6;
	}
	
	$('#forwarding_graph_selector').change(ajaxGetData);
}

function drawForwardingGraph(json_data) {
		myjson = jQuery.parseJSON(json_data);

		$(forwarding_graph_container).empty();

		var img_left=$(window).width();
		img_left-=(img_left*0.3);

		links = [];
		all_nodes = [];

		for (var i = 0 ; i < myjson.profile.VNFs.length; i++) { //take all info of VNFs (id, name and splitting rules(if exist))
			item = {};			
			item["id"] = myjson.profile.VNFs[i].id;
			item["name"] = myjson.profile.VNFs[i].name;
			item["splitting"] = '';
			for (var j = 0 ; j < myjson.profile.VNFs[i].ports.length; j++) {
				if(myjson.profile.VNFs[i].ports[j].outgoing_label !== undefined){
					for (var k = 0 ; k < myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules.length; k++) {
						if(myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules.length > 1) {
							var destPort = 0;
							var destVNF = '';

							if(myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF !== undefined){
								destPort = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.port;
								destVNF = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.id;
							}else if(myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.endpoint !== undefined){
								destPort = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.port;
								destVNF = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.port;
							}

							var priority = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].flowspec.matches[0].priority;
							var etherType = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].flowspec.matches[0].etherType;
							var protocol = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].flowspec.matches[0].protocol;
							var destNoPort = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].flowspec.matches[0].destPort;
							var srcPort = myjson.profile.VNFs[i].ports[j].id;
							item["splitting"] += '\n'+srcPort+'\n'+priority+'\n'+etherType+'\n'+protocol+'\n'+destNoPort+'\n'+destPort+'\n'+destVNF+'\nPS';
						}else{
							item["splitting"] += '';
						}
					}
				}else if(myjson.profile.VNFs[i].ports[j].ingoing_label !== undefined){
					for (var k = 0 ; k < myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules.length; k++) {
						if(myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules.length > 1) {
							var destPort = 0;
							var destVNF = '';

							if(myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.VNF !== undefined){
								destPort = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.VNF.port;
								destVNF = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.VNF.id;
							}else if(myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.endpoint !== undefined){
								destPort = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.VNF.port;
								destVNF = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.VNF.port;
							}

							var priority = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.matches[0].priority;
							var etherType = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.matches[0].etherType;
							var protocol = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.matches[0].protocol;
							var destNoPort = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.matches[0].destPort;
							var srcPort = myjson.profile.VNFs[i].ports[j].id;
							item["splitting"] += '\n'+srcPort+'\n'+priority+'\n'+etherType+'\n'+protocol+'\n'+destNoPort+'\n'+destPort+'\n'+destVNF+'\nPS';
						}else{
							item["splitting"] += '';
						}
					}
				}
			}
			item["splitting"] += '\nSplitRule';
			all_nodes.push(item);					
		}

		for (var i = 0 ; i < myjson.profile.endpoints.length; i++) { //take all endpoints info (id, name and sourceMacs (is exist)
			item = {};			
			item["id"] = myjson.profile.endpoints[i].id;
			item["name"] = myjson.profile.endpoints[i].name;
			item["sourceMACflowspec"] = "";
			for (var y = 0 ; y < myjson.profile.VNFs.length; y++) {
				for (var j = 0 ; j < myjson.profile.VNFs[y].ports.length; j++) {
					if(myjson.profile.VNFs[y].ports[j].ingoing_label !== undefined){
						for (var k = 0 ; k < myjson.profile.VNFs[y].ports[j].ingoing_label.flowrules.length; k++) {
							if(myjson.profile.VNFs[y].ports[j].ingoing_label.flowrules[k].flowspec.ingress_endpoint == myjson.profile.endpoints[i].id){
								for(var h = 0; h < myjson.profile.VNFs[y].ports[j].ingoing_label.flowrules[k].flowspec.matches.length; h++){
									if(myjson.profile.VNFs[y].ports[j].ingoing_label.flowrules[k].flowspec.matches[h].sourceMAC !== undefined){
									item["sourceMACflowspec"] += myjson.profile.VNFs[y].ports[j].ingoing_label.flowrules[k].flowspec.matches[h].sourceMAC;
									item["sourceMACflowspec"] += ',';
									}
								}
							}
						}
					}
				}
			}
			all_nodes.push(item);					
		}

		var countSwitch = 1;
		var numOfSwitch = getNumOfSwitch(all_nodes);

		for (var i = 0 ; i < myjson.profile.VNFs.length; i++) { //take all links between nodes
			for (var j = 0 ; j < myjson.profile.VNFs[i].ports.length; j++) {
				if(myjson.profile.VNFs[i].ports[j].outgoing_label !== undefined){
					for (var k = 0 ; k < myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules.length; k++) {
						if(myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF !== undefined){
							item = {};
							item["source_id"] = myjson.profile.VNFs[i].id;
							item["target_id"] = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.id;
							item["source_name"] = getName(all_nodes, myjson.profile.VNFs[i].name);
							item["target_name"] = getName(all_nodes, myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.id);

							if(item["source_name"] == "Switch"){
								item["source_type"] = "VNF_switch";
								item["source_width"] = switchSize;
							}else if(item["source_name"] == "Control_Switch"){
								item["source_width"] = controlSwitchSize;
								item["source_type"] = "VNF_control_switch";
							}else{
								item["source_type"] = "VNF";
								item["source_width"] = vnfSize;
							}

							if(item["target_name"] == "Switch"){
								item["target_type"] = "VNF_switch";
								item["target_width"] = switchSize;
							}else if(item["target_name"] == "Control_Switch"){
								item["target_width"] = controlSwitchSize;
								item["target_type"] = "VNF_control_switch";
							}else{
								item["target_type"] = "VNF"; 
								item["target_width"] = vnfSize;
							}
		
							item["source_port_pos"] = ((j+1)/(myjson.profile.VNFs[i].ports.length+1));
							item["target_port_pos"] = getPortPositionInGraph(myjson, myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.id, myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.port);
							
							item["source_port_id"] = myjson.profile.VNFs[i].ports[j].id;
							item["target_port_id"] = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.VNF.port;

							if(getName(all_nodes, myjson.profile.VNFs[i].name) == "Switch"){
								item["switchPos"] = (countSwitch/(numOfSwitch+1));
							}else{
								item["switchPos"] = 0;
							}

							links.push(item);

						}else if(myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.endpoint !== undefined){
							item = {};
							item["source_id"] = myjson.profile.VNFs[i].id;
							item["target_id"] = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.endpoint.id;
							item["source_name"] = getName(all_nodes, myjson.profile.VNFs[i].name);
							item["target_name"] = getName(all_nodes, myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.endpoint.id);

							if(item["source_name"] == "Switch"){
								item["source_type"] = "VNF_switch";
								item["source_width"] = switchSize;
							}else if(item["source_name"] == "Control_Switch"){
								item["source_width"] = controlSwitchSize;
								item["source_type"] = "VNF_control_switch";
							}else{
								item["source_type"] = "VNF";
								item["source_width"] = vnfSize;
							}

							item["target_type"] = "endpoint";
							item["target_width"] = 20;

							if(ingressPattern.test(item["target_name"])) item["source_port_pos"] = 0;
							else item["source_port_pos"] = 1; 						
							item["target_port_pos"] = (1/2);

							item["source_port_id"] = myjson.profile.VNFs[i].ports[j].id;
							item["target_port_id"] = myjson.profile.VNFs[i].ports[j].outgoing_label.flowrules[k].action.endpoint.id;

							if(getName(all_nodes, myjson.profile.VNFs[i].name) == "Switch"){
								item["switchPos"] = (countSwitch/(numOfSwitch+1));
							}else{
								item["switchPos"] = 0;
							}
							
							links.push(item);
						}
					}
				}
				if(myjson.profile.VNFs[i].ports[j].ingoing_label !== undefined){
					for (var k = 0 ; k < myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules.length; k++) {
						item = {};
						item["source_id"] = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.ingress_endpoint;
						item["target_id"] = myjson.profile.VNFs[i].id;
						item["source_name"] = getName(all_nodes, myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.ingress_endpoint);
						item["target_name"] = getName(all_nodes, myjson.profile.VNFs[i].name);
						item["source_type"] = "endpoint";
						item["source_width"] = 20;

						if(item["target_name"] == "Switch"){
							item["target_type"] = "VNF_switch";
							item["target_width"] = switchSize;
						}else if(item["source_name"] == "Control_Switch"){
							item["source_width"] = controlSwitchSize;
							item["source_type"] = "VNF_control_switch";
						}else{
							item["target_type"] = "VNF";
							item["target_width"] = vnfSize; 
						}

						item["source_port_pos"] = (1/2);

						if(ingressPattern.test(item["source_name"])) item["target_port_pos"] = 0;
						else item["target_port_pos"] = 1;

						item["source_port_id"] = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].flowspec.ingress_endpoint;
						item["target_port_id"] = myjson.profile.VNFs[i].ports[j].ingoing_label.flowrules[k].action.VNF.port;
									
						if(getName(all_nodes, myjson.profile.VNFs[i].name) == "Switch"){
							item["switchPos"] = (countSwitch/(numOfSwitch+1));
						}else{
							item["switchPos"] = 0;
						}

						links.push(item);
					}
				}
			}
			if(getName(all_nodes, myjson.profile.VNFs[i].name) == "Switch") countSwitch++;
		}

		var nodes = {};

		// Compute the distinct nodes from the links.
		links.forEach(function(link) {
			link.source = nodes[link.source_id] || (nodes[link.source_id] = {name: link.source_name, type: link.source_type, id: link.source_id, width: link.source_width, dragable: "true", switch_pos: link.switchPos});

		  	link.target = nodes[link.target_id] || (nodes[link.target_id] = {name: link.target_name, type: link.target_type, id: link.target_id, width: link.target_width, dragable: "true", switch_pos: link.switchPos});

		   	link.source_pos = link.source_port_pos;
		   	link.target_pos = link.target_port_pos;
		   	link.source_port = link.source_port_id;
		   	link.target_port = link.target_port_id;
		});

		var width = $( window ).width()-$( window ).width()*0.2,
			height = 900;

		//usage of d3 layout passing "links" var with all (distinct) links between nodes
		var force = d3.layout.force()
			.nodes(d3.values(nodes))
			.links(links)
			.size([width, height])
			.linkDistance(200)
			.charge(-2500)
			.on("tick", tick)
			.start();

		var svg = d3.select("#forwarding_graph_topology").append("svg")
			.attr("id", "svg_element")
			.attr("width", width)
			.attr("height", height);

		svg.append("defs").selectAll("marker")
		.data(["suit", "licensing", "resolved"])
	  	.enter().append("marker")
		.attr("id", function(d) { return d; })
		.attr("refX", 5)
		.attr("refY", 5)
		.attr("markerWidth", 8)
		.attr("markerHeight", 8)
		.attr("orient", "auto")
	  	.append("circle")
		.attr("cx", 5)
		.attr("cy", 5)
		.attr("r", 3)
		.style("stroke", "none")
		.style("fill", "#000000");

		link = svg.selectAll(".link")
			.data(force.links())
		  	.enter().append("line")
			.attr("id", function(d){ return "link"+d.source.id+d.target.id; })
			.attr("class", "link")
			.style("stroke", "#000000")
			.style("stroke-width", "2px")
			.style("fill", "none")
			.on("mouseover", function(d) {

				$("#link"+d.source.id+d.target.id).css("stroke-width", "4px");
				$("#link"+d.source.id+d.target.id).css("stroke", "#FF0000");

				//Update the tooltip position and value
				d3.select("#tooltip")
				  .style("left", ((d.source.x+d.target.x)/2) + "px")
				  .style("top", ((d.source.y+d.target.y)/2) + "px")
				  .select("#value")
				  .html(d.source.name+"_port: "+d.source_port+"<br>"+d.target.name+"_port: "+d.target_port);

				d3.select("#tooltip")
				  .select("#title")
				  .html("Link: "+d.source.name+" <-> "+d.target.name);

				//Show the tooltip
				d3.select("#tooltip").classed("hidden", false);

			})
			.on("mouseout", function(d) {
				//Hide the tooltip
				d3.select("#tooltip").classed("hidden", true);

				//change all links status
				$(".link").css("stroke-width", "2px");
				$(".link").css("stroke", "#000000");

				//change selected link status
				//$("#link"+d.source.id+d.target.id).css("stroke-width", "2px");
				//$("#link"+d.source.id+d.target.id).css("stroke", "#000000");
			})
			.style("marker-end",  "url(#suit)")
			.style("marker-start",  "url(#suit)");

		node = svg.selectAll(".node")
			.data(force.nodes())
		  	.enter().append("g")
			.attr("class", "node")
			.attr("id", function(d){ return "node"+d.id;})
			.on("mouseover", function(d) {
				if(d.type == "endpoint"){ //search if exist sourceMACs
					var retVal = returnSourceMACs(all_nodes, d.id);
					var splittedRetVal = retVal.split(',');
					var tooltipValue = '';
					
					if(splittedRetVal.length > 1){
						for(var i = 0; i < splittedRetVal.length; i++){
							if(splittedRetVal[i] != "") tooltipValue += "-"+splittedRetVal[i]+"<br>";
						}

						//Update the tooltip position and value
						d3.select("#tooltip")
						  .style("left", ((d.x) + "px"))
						  .style("top", ((d.y) + "px"))
						  .select("#value")
						  .html(tooltipValue);
						  
						d3.select("#tooltip")
						  .select("#title")
						  .html("SourceMacs");

						//Show the tooltip
						d3.select("#tooltip").classed("hidden", false);
					}
				}else{ //for VNFs search if exist a splitting rules
					var tooltipValue = '';
					var returnVal = returnSplitting(all_nodes, d.id);
					if(returnVal === undefined) return;

					var splitRule = returnVal.split('PS');

					if(splitRule.length == 1) return;

					tooltipValue += "FROM: ";
					var k = 0;
					for(var i = 0; i < splitRule.length; i++){
						if(splitRule[i] == "SplitRule" && (i+1) < splitRule.length) {
							tooltipValue += "FROM: ";
							k = 0;					
							continue;
						}
						var values = splitRule[i].split('\n');

						if(values[7] === undefined) continue;

						if(k == 0) {
							tooltipValue += "<b>"+values[1]+"</b><br>";
							k++;
						}

						$("#link"+values[7]+d.id).css("stroke-width", "4px");
						$("#link"+values[7]+d.id).css("stroke", "#FF0000");

						tooltipValue += "- TO: <b>"+getName(all_nodes, values[7])+"</b> ON: <b>"+values[6]+"</b><br>";
						tooltipValue += "&nbsp Priority: "+values[2]+"<br>";
						if(values[3] == "undefined" && values[4] == "undefined" && values[5] == "undefined"){
							tooltipValue += "&nbsp All_Other_Traffic<br>";
						}else{
							tooltipValue += "&nbsp Ethertype: "+values[3]+"<br>";
							tooltipValue += "&nbsp Protocol: "+values[4]+"<br>";
							tooltipValue += "&nbsp DestPort: "+values[5]+"<br>";
						}
					}

					//Update the tooltip position and value
					d3.select("#tooltip")
					  .style("left", ((d.x) + "px"))
					  .style("top", ((d.y) + "px"))
					  .select("#value")
					  .html(tooltipValue);
					  
					d3.select("#tooltip")
					  .select("#title")
					  .html("Splitting Rules");

					//Show the tooltip
					d3.select("#tooltip").classed("hidden", false);
				}
			})
			.on("mouseout", function(d) {
				//Hide the tooltip
				d3.select("#tooltip").classed("hidden", true);
				
				$(".link").css("stroke-width", "2px");
				$(".link").css("stroke", "#000000");

				/*var returnVal = returnSplitting(all_nodes, d.id);
				if(returnVal === undefined) return;

				var splitRule = returnVal.split('PS');

				if(splitRule.length == 1) return;

				for(var i = 0; i < splitRule.length; i++){
					if(splitRule[i] == "SplitRule" && (i+1) < splitRule.length) {
						continue;
					}
					var values = splitRule[i].split('\n');

					if(values[7] === undefined) continue;

					$("#link"+values[7]+d.id).css("stroke-width", "2px");
					$("#link"+values[7]+d.id).css("stroke", "#000000");
				}*/
			})
			.on("dblclick", function(d) {
				if(d.dragable == "true") d.dragable = "false";
				else d.dragable = "true";
			})
			.call(force.drag);

		node.append("rect") //draw all nodes like a rect
			.attr("x", function(d){ return -(d.width/2);})
			.attr("y", function(d){ if(d.type == "endpoint") return -10;
									else return -20;})
			.attr("width", function(d){ return d.width;})
			.attr("height", function(d){ if(d.type == "endpoint") return 20;
										 else return 40;})
			.attr("rx", function(d){ if(d.type == "endpoint") return 50;
									 else return 5;})
			.attr("ry", function(d){ if(d.type == "endpoint") return 50;
									 else return 5;})
			.attr("style", function(d){ if(d.type == "endpoint") return "fill:#000000;stroke:black;stroke-width:2;opacity:1";
										else return "fill:#00B53C;stroke:black;stroke-width:2;opacity:0.9;";});

		node.append("text")
			.attr("y", function(d){ if(d.type == "endpoint") return -12;
									 else return 0;})
			.text(function(d) { return d.name; })
			.style("font-family", "Arial")
			.style("font-weight", "bold")
			.style("font-style", "normal")
			.style("font-size", "10")
			.attr("fill", function(d){ if(d.type == "endpoint") return "black";
									   else return "white";})
			.attr("text-anchor", "middle");

        node.append("svg:image")
			.attr("xlink:href", function(d){ 
									var imgPath = "";

									if(ingressPattern.test(d.name)) imgPath = "/static/dashboard/img/"+ingressImg;
									if(egressPattern.test(d.name)) imgPath = "/static/dashboard/img/"+egressImg;
									if(controlIngressPattern.test(d.name)) imgPath = "/static/dashboard/img/"+controlIngressImg;			
									if(controlEgressPattern.test(d.name)) imgPath = "/static/dashboard/img/"+controlEgressImg;
									return imgPath;
								})
			.attr("width", function(d){ 
									if(ingressPattern.test(d.name) || egressPattern.test(d.name)) return 80;
									else return 0;
								})
			.attr("height", function(d){ 
									if(ingressPattern.test(d.name) || egressPattern.test(d.name)) return 80;
									else return 0;
								})
			.attr("x", function(d){ 
							if(controlIngressPattern.test(d.name)) return -120;
							if(controlEgressPattern.test(d.name)) return +70;
					   		if(ingressPattern.test(d.name)) return -100;
							if(egressPattern.test(d.name)) return +50;
							return "";
						})
			.attr("y", -50);

}

function returnSplitting(all_nodes_info, id_node){
	for (var i = 0 ; i < all_nodes_info.length; i++) {
		if(all_nodes_info[i].id == id_node) return all_nodes_info[i].splitting;
	}
	return 'noSplittingRules';
}

function returnSourceMACs(all_nodes_info, id_node){
	for (var i = 0 ; i < all_nodes_info.length; i++) {
		if(all_nodes_info[i].id == id_node) return all_nodes_info[i].sourceMACflowspec;
	}
	return 'noSourceMacRules';
}

function getName(all_nodes_info, id_node){
	for (var i = 0 ; i < all_nodes_info.length; i++) {
		if(all_nodes_info[i].id == id_node) return all_nodes_info[i].name;
	}
	return id_node;
}

function getNumOfSwitch(all_nodes_info){
	var numSwitch = 0;
	for (var i = 0 ; i < all_nodes_info.length; i++) {
		if(all_nodes_info[i].name == "Switch") numSwitch++;
	}
	return numSwitch;
}

//function called every X time for graphic change
function tick() {
  	$('#svg_element').attr("width", $(window).width());
	$('#ISP_Egress').css("left", ($(window).width()-($(window).width()*0.3))+"px");

	node
      .attr("transform", function(d) { 
									   if(d.dragable == "false") d.fixed = true;
									   
									   if(ingressPattern.test(d.name)){ 
									   	    d.x = 100;
											if(d.dragable == "true") d.y = 400;
											d.fixed = true;	 
									   } 

									   if(egressPattern.test(d.name)){
									   	    d.x = $( window ).width()-$( window ).width()*0.35;
											if(d.dragable == "true")  d.y = 400;
											d.fixed = true;	 
									   } 

									   if(controlIngressPattern.test(d.name)){ 
									   	    d.x = 100;
											if(d.dragable == "true") d.y = 200;
											d.fixed = true;	 
									   }
 
									   if(controlEgressPattern.test(d.name)){
									   	    d.x = $( window ).width()-$( window ).width()*0.35;
											if(d.dragable == "true")  d.y = 200;
											d.fixed = true;	 
									   } 
									   
									   if(d.name == "Control_Switch"){
											if(d.dragable == "true") {
												d.x = $( window ).width()-$( window ).width()*0.65;
												d.y = 200;
											}
									   }

									   if(d.name == "Switch"){
											if(d.dragable == "true") {
												var pos = (1-((d.switch_pos)-0.15));
												d.x = ($(window).width()-$(window).width()*pos);
												d.y = 600;
											}		
											d.fixed = true;	
									   }
 										
									   return "translate(" + d.x + "," + d.y + ")"; });
  

	link
      .attr("x1", function(d) { return ((d.source.x-(d.source.width/2))+(d.source.width*d.source_pos)); }) 
      .attr("y1", function(d) { if(d.source_pos == 0 || d.source_pos == 1) return d.source.y;
								if(d.source.type == "endpoint") return d.source.y;
								else if((d.target.y+20) > (d.source.y+20)) return d.source.y+20;
								else return d.source.y-20; })
      .attr("x2", function(d) { return ((d.target.x-(d.target.width/2))+(d.target.width*d.target_pos)); })
      .attr("y2", function(d) { if(d.target_pos == 0 || d.target_pos == 1) return d.target.y;	
								if(d.target.type == "endpoint") return d.target.y;
								else if((d.target.y+20) > (d.source.y+20)) return d.target.y-20; 							
								else return d.target.y+20; });

}

function getPortPosition(myjson, node_id, port_id){
	for (var i = 0 ; i < myjson.profile.VNFs.length; i++) {
		if(myjson.profile.VNFs[i].id == node_id){
			for (var j = 0 ; j < myjson.profile.VNFs[i].ports.length; j++) {
				if(myjson.profile.VNFs[i].ports[j].id == port_id) {
					return j;
				}
			}
		} 
	}
	return 0;
}

function getNumPorts(myjson, node_id){
	for (var i = 0 ; i < myjson.profile.VNFs.length; i++) {
		if(myjson.profile.VNFs[i].id == node_id){
			return myjson.profile.VNFs[i].ports.length;
		} 
	}
	return 0;
}

function getPortPositionInGraph(myjson, node_id, port_id){
	return ((getPortPosition(myjson, node_id, port_id)+1)/(getNumPorts(myjson, node_id)+1));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function ajaxGetConfig(){
	var csrftoken = getCookie('csrftoken');
	
	$.ajax({
		type: "POST",
		url: "/horizon/admin/forwarding_graph/ajax_config_request",  // or just url: "/my-url/path/"
		data: {
		   csrfmiddlewaretoken: csrftoken,
		},
		success: function(data) {
			var splittedVal = data.split(",");
			ingressName = splittedVal[0];
			egressName = splittedVal[1];
			controlIngressName = splittedVal[2];
			controlEgressName = splittedVal[3];
			ingressImg = splittedVal[4];
			egressImg = splittedVal[5];
			controlIngressImg = splittedVal[6];
			controlEgressImg = splittedVal[7];
			ingressPattern = new RegExp(ingressName);
			egressPattern = new RegExp(egressName);
			controlIngressPattern = new RegExp(controlIngressName);
			controlEgressPattern = new RegExp(controlEgressName);
			ajaxGetSessions();
		},
		error: function(xhr, textStatus, errorThrown) {
		   	alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
		}
	});
}

function ajaxGetSessions(){
	var csrftoken = getCookie('csrftoken');
	
	$.ajax({
		type: "POST",
		url: "/horizon/admin/forwarding_graph/ajax_sessions_request",  // or just url: "/my-url/path/"
		data: {
		   csrfmiddlewaretoken: csrftoken,
		},
		success: function(data) {
			fillSessions(data);
		},
		error: function(xhr, textStatus, errorThrown) {
		   	alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
		}
	});
}

function ajaxGetData(){
	var p_id = $('#forwarding_graph_selector').val();
	var csrftoken = getCookie('csrftoken');

	$.ajax({
		type: "POST",
		url: "/horizon/admin/forwarding_graph/ajax_data_request",  // or just url: "/my-url/path/"
		data: {
		   csrfmiddlewaretoken: csrftoken,
		   profile_id: p_id,
		},
		success: function(data) {
			drawForwardingGraph(data);
			if(myjson != ""){
				$("#showSplittingRulesButton").show();
			}
		},
		error: function(xhr, textStatus, errorThrown) {
		   	alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
		}
	});
}

//called when click on "showAllSplittingRules" button
function showSplittingRules(){
	var tooltipValue = '';
	for(var j = 0; j < all_nodes.length; j++){
		if(all_nodes[j].splitting === undefined) continue;

		var splitRule = all_nodes[j].splitting.split('PS');

		if(splitRule.length == 1) continue;

		tooltipValue += "FROM: ";
		var k = 0;
		for(var i = 0; i < splitRule.length; i++){
			if(splitRule[i] == "SplitRule" && (i+1) < splitRule.length) {
				tooltipValue += "FROM: ";
				k = 0;					
				continue;
			}
			var values = splitRule[i].split('\n');

			if(values[7] === undefined) continue;

			if(k == 0) {
				tooltipValue += "<b>"+all_nodes[j].name+"</b> ON: <b>"+values[1]+"</b><br>";
				k++;
			}

			$("#link"+values[7]+all_nodes[j].id).css("stroke-width", "4px");
			$("#link"+values[7]+all_nodes[j].id).css("stroke", "#FF0000");

			tooltipValue += "- TO: <b>"+getName(all_nodes, values[7])+"</b> ON: <b>"+values[6]+"</b><br>";
			tooltipValue += "&nbsp Priority: "+values[2]+"<br>";
			if(values[3] == "undefined" && values[4] == "undefined" && values[5] == "undefined"){
				tooltipValue += "&nbsp All_Other_Traffic<br>";
			}else{
				tooltipValue += "&nbsp Ethertype: "+values[3]+"<br>";
				tooltipValue += "&nbsp Protocol: "+values[4]+"<br>";
				tooltipValue += "&nbsp DestPort: "+values[5]+"<br>";
			}
		}

	}
	//Update the tooltip position and value
	d3.select("#tooltip")
	  .style("left", ("0px"))
	  .style("top", ("200px"))
	  .select("#value")
	  .html(tooltipValue);
				  
	d3.select("#tooltip")
	  .select("#title")
	  .html("Splitting Rules");

	//Show the tooltip
	d3.select("#tooltip").classed("hidden", false);

}