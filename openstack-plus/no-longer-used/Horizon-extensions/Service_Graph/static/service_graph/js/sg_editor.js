/*	 sg_editor.js
 *	 main javascript script that implements the Service Graph GUI
 *
 *	 Reference to external js libraries used in this script:
 *
 *   JQuery UI 							-> http://api.jqueryui.com/
 *	 SVG js 							-> http://documentup.com/wout/svg.js
 *	 SVG js path plugin 				-> https://github.com/otm/svg.path.js (manual path/link drawing)
 *	 JQuery UI ContextMenu plugin		-> https://github.com/mar10/jquery-ui-contextmenu
 *	 JQuery Collision Detection plugin 	-> http://sourceforge.net/projects/jquerycollision/
 */

/* GUI Layout description:
 * 
 * html #content div 
 *		- svg design window
 *			- foreign object inside svg (as large as the design window to contain all the html elements dragged into design window)
 *				- html div's
 *					- svg document inside each html div
 *						- svg elements, such as rect, polygon, text, etc. inside each svg document
 */
 
 /*  Data structures for each GUI element:
 
  *  VNF -> { id : string 
			  vnfDesc : object
		      ports : object
		      drawedPorts : array
		      links: array
			}
			
  *  Splitter -> { id : string
				   num_inout : integer (current number of ports in the splitter)
				   rules: array
			       links: array
			       drawedPorts : array
				}
				
  *  Endpoint -> {  id : string 
					type: string ("user", "internet")
					links: array
				 }
				 
  *  LAN ->		{
					id : string 
					links: array
				}
				
  *  Link ->    { 
					id : string
					path: object (SVG path)
					elem1: object -> { 
									   id: string
									   type: string
									   port: string
									   offset: integer
									 }
					elem2: object -> { 
									   id: string
									   type: string
									   port: string
									   offset: integer
									 }
				}	
  */

 
var MAX_PORTS = 16;		// Max number of ports in a VNF
var MAX_TS_INOUTS = 8;	// Max number of ports in a Splitter


// Closure (self-invoking function) that executes only once to create the Design Window SVG canvas
// When it's called again it returns the reference to the Design Window SVG document obgect
var getDesignWindowSvg = (function () {
	// Create a SVG canvas for the design window
	var designWindowSvg = SVG('content').size('100%', '100%').attr({ id: "design_window_svg" });
	designWindowSvg.fixSubPixelOffset();

	// Create a foreign object, as large as its html div container, in order to put html divs inside the svg design window
	var fobject = designWindowSvg.foreignObject('100%', '100%').attr({ id : "fobject", x: 0, y: 0 });
	fobject.attr({style : "position: relative;"});
        
	return function () {return designWindowSvg;}
})();

// The following closures initialize the element lists
// Each following call to any of these functions returns the corresponding element list
var getVnfList = (function () {

	var vnfList = {};
	
	return function (vnfId, vnfElem) {
		if (vnfId == undefined || vnfId == null || vnfElem == undefined || vnfElem == null)
			return vnfList;
		else vnfList[vnfId] = vnfElem;	
	}	
})();

var getSplitterList = (function () {

	var splittermergerList = {};
	
	return function (smId, smElem) {
		if (smId == undefined || smId == null || smElem == undefined || smElem == null)
			return splittermergerList;
		else splittermergerList[smId] = smElem;	
	}
	
})();

var getEndPointList = (function () {

	var endpointList = {};
	
	return function (epId, epElem) {
		if (epId == undefined || epId == null || epElem == undefined || epElem == null)
			return endpointList;
		else endpointList[epId] = epElem;	
	}
	
})();

var getLANList = (function () {

	var lanList = {};
	
	return function (lanId, lanElem) {
		if (lanId == undefined || lanId == null || lanElem == undefined || lanElem == null)
			return lanList;
		else lanList[lanId] = lanElem;	
	}
	
})();

var getLinkList = (function () {

	var linkList = {};
	
	return function (linkId, linkElem) {
		if (linkId == undefined || linkId == null || linkElem == undefined || linkElem == null)
			return linkList;
		else linkList[linkId] = linkElem;	
	}	
})();


// get a 'generic' element from the lists, given its global ID
function getSgElement(elemId, elemType) {
	switch (elemType) {
		case "vnf":
			return getVnfList()[elemId];
			break;
		case "endpoint":
			return getEndPointList()[elemId];
			break;
		case "lan":
			return getLANList()[elemId];
			break;
		case "splittermerger":
			return getSplitterList()[elemId];
			break;
		default:
			return null;
	}
}

// These functions are used to increment the counter for the corresponding element list
// They also return the updated counter
var getCurrentVnfId = (function () {
	
	var VnfIdCounter = 0;

        return function () { VnfIdCounter += 1; return VnfIdCounter;}
})();

var getCurrentSplitterMergerId = (function () {
	
	var SplitterMergerIdCounter = 0;

        return function () { SplitterMergerIdCounter += 1; return SplitterMergerIdCounter;}
})();

var getCurrentLanId = (function () {
	
	var LanIdCounter = 0;

        return function () { LanIdCounter += 1; return LanIdCounter;}
})();

var getCurrentEndpointId = (function () {
	
	var endpointIdCounter = 0;

        return function () { endpointIdCounter += 1; return endpointIdCounter;}
})();

var getCurrentLinkId = (function () {
	
	var linkIdCounter = 0;

        return function () { linkIdCounter += 1; return linkIdCounter;}
})();


// disable (if the boolean parameter is true) or enable (otherwise) all the draggable elements
// (those in the toolbar and those which are in the #content div)
function disableDraggables(disable) {	
	var elem_array = $("#menu").find("svg").get();
	var div_array = $("#content").find("div").get();
	elem_array = elem_array.concat(div_array);
	for (var i = 0; i < elem_array.length; i++) {
		if (elem_array[i].attributes["id"] != undefined) {
			var selector = "#"+elem_array[i].attributes["id"].value;
			if ($( selector ).draggable( "instance" ) != undefined) {
				if (disable == true)
					$( selector ).draggable( "disable" );
				else
					$( selector ).draggable( "enable" );
			}
		}
	}
}

// add a Link to the current graph, starting from the current element 
function addLink(elem_id, elemSvg, elemType, elemOffset) {

	var svg = getDesignWindowSvg();
	var svgOffsetLeft = svg.node.parentElement.offsetLeft;
	var svgOffsetTop = svg.node.parentElement.offsetTop;
	
	var elem_left;
	var elem_top;
	var vnfPort_id;
	var splitterPort_id;
	
	switch (elemType) {
		case "endpoint":
			elem_left = elemSvg.parent.offsetLeft + elemOffset.x;
			elem_top = elemSvg.parent.offsetTop + elemOffset.y;
			break;
		case "lan":
			elem_left = elemOffset.x - svgOffsetLeft;
			elem_top = elemSvg.parent.offsetTop + 11;
			break;
		case "vnf":
			vnfPort_id = elem_id;
			elem_id = elem_id.substring(0, elem_id.indexOf("-"));
			elem_left = elemSvg.parentNode.offsetLeft + elemOffset.x;
			elem_top = elemSvg.parentNode.offsetTop + elemOffset.y;
			break;
		case "splittermerger":
			splitterPort_id = elem_id;
			elem_id = elem_id.substring(0, elem_id.indexOf("-"));
			elem_left = elemSvg.parentNode.offsetLeft + elemOffset.x;
			elem_top = elemSvg.parentNode.offsetTop + elemOffset.y;
			break;
		default:
	}
		
	disableDraggables(true);
	
	var newLink = svg.path().M({x: elem_left, y: elem_top}).L({x: elem_left, y: elem_top});
	
	$("#design_window_svg").mousedown(function(event) {
		if (event.which > 1) { 	// right (or central) mouse button
			$("#design_window_svg").off("mousemove");
			newLink.clear();
			$("#design_window_svg").css("cursor", "default");
			
			disableDraggables(false);	// re-enable draggables
			event.stopImmediatePropagation();
			event.preventDefault();
			$("#design_window_svg").off("mousedown");
			return false;
			
		} else { 				// left mouse button
											
			var currentElem = event.target;
			var isTargetLinkable = false;
			for (var i = 0; i < currentElem.classList.length; i++) {
				if (currentElem.classList[i] == "linkable")
					isTargetLinkable = true;
			}
			
			if (isTargetLinkable == false) { 	// target is not linkable
				return;
			}
			
			// target is linkable
			while (currentElem.nodeName != "svg") {
				currentElem = currentElem.parentNode;
			}
			destSvg = currentElem;
			if (currentElem.parentNode.nodeName == "DIV") {
				currentElem = currentElem.parentNode;
				if (currentElem.id == elem_id)
					// Source and Destination are the same
					return;
			}
		
			destElemType = currentElem.id.substr(0, currentElem.id.indexOf("_"));
			destElemId = currentElem.id;
			
			var destX;
			var destY;
			
			switch (destElemType) {
				case "endpoint":
							destX = destSvg.parentElement.offsetLeft + 20;
							destY = destSvg.parentElement.offsetTop + 20;
							break;
				case "lan":
							destX = newLink.getSegment(1).coords[0];
							destY = destSvg.parentElement.offsetTop + 11;
							break;
				case "vnf":
							var portRect = $("#"+event.target.id).get()[0];
							destX = destSvg.parentElement.offsetLeft + portRect.x.baseVal.value + 3;
							destY = destSvg.parentElement.offsetTop + portRect.y.baseVal.value + 3;
							break;
				case "splittermerger":
							var portRect = $("#"+event.target.id).get()[0];
							destX = destSvg.parentElement.offsetLeft + portRect.x.baseVal.value + 3;
							destY = destSvg.parentElement.offsetTop + portRect.y.baseVal.value + 3;
							break;
				default:
			}
			
			// update the link end position
			newLink.L({x: destX, y: destY}).drawAnimated({ delay: 0, duration: 1, easing: "-" });
			newLink.replaceSegment(1, newLink.getSegment(2));
			newLink.removeSegment(2);
			
			$("#design_window_svg").off("mousemove");	// unbind mousemove event handler from the design window svg
			$("#design_window_svg").css("cursor", "default");
			
			
			// TO-DO: check that there is not yet a link between these two elements
			// how_to: -> scan getEndPointList()[destElemId].links array (or elem_id)
			// 		   -> check for each of its elements (links) that the linked element is different from elem_id
			 
			
			// add a new link into the SG data structures
			var link_id = "link_"+getCurrentLinkId();
			newLink.attr({id: link_id});
			
			// create a new Link object and add it to the corresponding list
			getLinkList()[link_id] = {  id : link_id, 
										path: newLink,
										elem1: { id: elem_id, type: elemType,
												 port: (elemType == "vnf") ? 
													vnfPort_id : (elemType == "splittermerger") ? splitterPort_id : undefined,
												 offset: (elemType == "lan") ? elemOffset.x - svgOffsetLeft - elemSvg.parent.offsetLeft: undefined },
										elem2: { id: destElemId, type: destElemType,
												 port: (destElemType == "vnf" || destElemType == "splittermerger") ? 
													event.target.id : undefined,
												 offset: (destElemType == "lan") ? destX - destSvg.parentElement.offsetLeft : undefined },
			};
			
			getSgElement(destElemId, destElemType).links.push(link_id);
			getSgElement(elem_id, elemType).links.push(link_id);
			
			// add context menu to the new link
			$("#"+link_id).contextmenu({
				delegate: null,
				menu: [
						{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
				],
				select: function(event, ui) { 	// the user selected the option to delete this link
					// remove reference to this link from the two element objects
					var lnk = getLinkList()[link_id];
					var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
					elem1Links.splice(elem1Links.indexOf(link_id), 1);
					var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
					elem2Links.splice(elem2Links.indexOf(link_id), 1);
					
					delete getLinkList()[link_id];
					this.remove();
				}
			});
			
			disableDraggables(false);	// re-enable draggable elements
			event.stopImmediatePropagation();
			event.preventDefault();
			$("#design_window_svg").off("mousedown");	// unbind mousedown event handler
			return false;
		}
	});
	
	$("#design_window_svg").mousemove(function(event) {
		$("#design_window_svg").css("cursor", "crosshair");

		var xCoord;
		var yCoord;
		if (event.target.id == "design_window_svg" || event.target.nodeName == "path") {
			xCoord = event.offsetX;
			yCoord = event.offsetY;
		} else {
			var currentElem = event.target;
			while (currentElem.nodeName != "DIV") { 
				currentElem = currentElem.parentNode;
			}
			xCoord = currentElem.offsetLeft + event.offsetX;
			yCoord = currentElem.offsetTop + event.offsetY;
		}
		
		newLink.L({ x: xCoord, y: yCoord })
			   .drawAnimated({ delay: 0, duration: 1, easing: "-" });
		newLink.replaceSegment(1, newLink.getSegment(2));
		newLink.removeSegment(2);
	});
}
	
// Draw VNF Port layout with fixed position (max # ports = 16, currently)
// the max number of ports could be increased by adding new fixed positions
// to the portPositions array (this may require enlarging the size of the
// VNF graphical element)
function vnfRefreshPorts(vnf, vnf_id, check) {
	var vnf_port_labels;
	if (vnf.ports) {
		vnf_port_labels = vnf.ports;
	} else {
		vnf_port_labels = [];
	}
	var vnf_svg = document.getElementById(vnf_id).firstChild;
	var vnf_oldPorts = vnf.drawedPorts;
	
	var svg_width = vnf_svg.offsetWidth;
	var svg_height = vnf_svg.offsetHeight;
	var rect_x = vnf_svg.childNodes[0].attributes.x.nodeValue / 1;
	var rect_y = vnf_svg.childNodes[0].attributes.y.nodeValue / 1;
	
	
	var portPositions = [
		{ x: (svg_width - rect_x) / 2 - 1, y: 0 + rect_y / 2 - 1 },					// 0
		{ x: (svg_width - rect_x) / 2 - 1, y: svg_height - (rect_y * 2 - 1) },		// 1
		{ x: 0 + rect_x / 2 - 1, y: svg_height / 2 - rect_y / 2 - 1 },				// 2
		{ x: svg_width - (rect_x * 2 - 1), y: svg_height / 2 - rect_y / 2 - 1 },	// 3
		{ x: (svg_width - rect_x) / 1.5 - 1, y: 0 + (rect_y / 2 - 1) },				// 4
		{ x: (svg_width - rect_x) / 3 - 1, y: svg_height - (rect_y * 2 - 1) },		// 5
		{ x: (svg_width - rect_x) / 1.5 - 1, y: svg_height - (rect_y * 2 - 1) },	// 6
		{ x: (svg_width - rect_x) / 3 - 1, y: 0 + rect_y / 2 - 1 },					// 7
		
		{ x: (svg_width - rect_x) / 6 - 1, y: svg_height - (rect_y * 2 - 1) },		// 8
		{ x: (svg_width - rect_x) / 1.2 - 1, y: svg_height - (rect_y * 2 - 1) },	// 9
		{ x: (svg_width - rect_x) / 6 - 1, y: 0 + rect_y / 2 - 1 },					// 10
		{ x: (svg_width - rect_x) / 1.2 - 1, y: 0 + rect_y / 2 - 1 },				// 11
		
		{ x: 0 + rect_x / 2 - 1, y: svg_height / 4 - rect_y / 4 - 1 },					// 12
		{ x: svg_width - (rect_x * 2 - 1), y: svg_height / 1.33 - rect_y / 1.33 - 1 },	// 13
		{ x: svg_width - (rect_x * 2 - 1), y: svg_height / 4 - rect_y / 4 - 1 },		// 14
		{ x: 0 + rect_x / 2 - 1, y: svg_height / 1.33 - rect_y / 1.33 - 1 },			// 15
	];
	
	// remove graphical elements corresponding to the 'old' ports
	for (var i = 0; i < vnf_oldPorts.length; i++) {
		vnf_oldPorts[i].remove();
	}
	
	// draw the graphical elements for the 'new' ports
	var vnfPorts = [];
	var portCounter = 0;
	for (var i = 0; i < vnf_port_labels.length; i++) {
		var borderColour = vnf_port_labels[i].colour;
		var fillColour = vnf_port_labels[i].type == "active" ? borderColour : "#FFFFFF";
		for (var j = 0; j < vnf_port_labels[i].cnt; j++) {
			var vnf_port_id = vnf_id + "-port_" + portCounter + "-" + vnf_port_labels[i].label + "_" + j;
			vnfPorts[portCounter] = vnf_svg.instance.rect(6, 6);
			vnfPorts[portCounter].attr({ fill: fillColour,
										 class: "linkable",
										 x: portPositions[portCounter].x,
										 y: portPositions[portCounter].y });
			vnfPorts[portCounter].radius(3);
			vnfPorts[portCounter].stroke({ color: borderColour, opacity: 1.0, width: 2 });
			vnfPorts[portCounter].attr({ "id" : vnf_port_id ,
										 "title" : vnf_port_labels[i].label + "#" + j });
			$("#"+vnf_port_id).tooltip({});
					
			var lnkStart;
			$("#"+vnf_port_id).contextmenu({
				delegate: null,
				menu: [
					{title: "Add link", cmd: "add_link", uiIcon: "ui-icon-arrow-2-e-w"},
				],
				//hide: {effect: "fadeOut", duration: "fast"},
				beforeOpen: function(event, ui) {
					lnkStart = { x: event.pageX, y: event.pageY };
					$("#"+this.id).tooltip("option", "hide", { effect: "fadeOut", duration: 1, delay: 0 });
					$("#"+this.id).tooltip("close");
					$("#"+this.id).tooltip("disable");
				},
				select: function(event, ui) {				
					if (ui.cmd == "add_link") {
						addLink(this.id, document.getElementById(this.id.substring(0, this.id.indexOf("-"))).firstChild, "vnf", 
							{ x: this.x.baseVal.value + 3, 
							  y: this.y.baseVal.value + 3 });
					}
				},
				close: function(event) {
					$("#"+this.id).tooltip("enable");
				},
			});
			
			portCounter++;
			if (portCounter == MAX_PORTS) {
				getVnfList()[vnf_id].drawedPorts = vnfPorts;
				return;
			}
		}
	}
	
	if (check) {
		// save the 'new' ports in the vnf data structure
		getVnfList()[vnf_id].drawedPorts = vnfPorts;
		return;
	}
	
	// remove links from / to ports that have been removed
	var vnf = getVnfList()[vnf_id];
	var vnf_links_length = vnf.links.length;
	for (var i = 0; i < vnf_links_length; i++) {
		var link_id = vnf.links[i];
		var lnk = getLinkList()[link_id];
		var portStr;
		var portLabel;
		var portLabelNumber;
		var portLabelCounter;
		
		if (lnk.elem1.id == vnf_id) {
			portStr = lnk.elem1.port.substring(lnk.elem1.port.lastIndexOf("-") + 1, lnk.elem1.port.length);
			portLabel = portStr.substr(0, portStr.indexOf("_"));
			portLabelNumber = parseInt(portStr.substr(portStr.indexOf("_") + 1));
		} else if (lnk.elem2.id == vnf_id) {
			portStr = lnk.elem2.port.substring(lnk.elem2.port.lastIndexOf("-") + 1, lnk.elem2.port.length);
			portLabel = portStr.substr(0, portStr.indexOf("_"));
			portLabelNumber = parseInt(portStr.substr(portStr.indexOf("_") + 1));
		}
		
		for (var k = 0; k < vnf_port_labels.length; k++) {
			if (vnf_port_labels[k].label == portLabel) {
				portLabelCounter = vnf_port_labels[k].cnt;
			}
		}
		
		if (portLabelNumber < portLabelCounter)
			continue;
		
		if (lnk.elem1.id != vnf_id) {
			var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
			elem1Links.splice(elem1Links.indexOf(link_id), 1);
			delete vnf.links[i];
		} else if (lnk.elem2.id != vnf_id) {
			var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
			elem2Links.splice(elem2Links.indexOf(link_id), 1);
			delete vnf.links[i];
		}
		
		delete getLinkList()[link_id];
		$("#"+link_id).remove();
	}
		
	var old_links_array = vnf.links;
	var new_links_array = [];
	for (var i = 0; i < old_links_array.length; i++) {
		if (old_links_array[i]) {
			new_links_array.push(old_links_array[i]);
		}
	}
	vnf.links = new_links_array;
	
	// save the 'new' ports in the vnf data structure
	getVnfList()[vnf_id].drawedPorts = vnfPorts;
}

// Draw Splitter Port layout
function splitterRefreshPorts(splitter, splitter_id) {
	var splitter_inouts = splitter.num_inout;
	var splitter_svg = document.getElementById(splitter_id).firstChild;
	var splitter_oldPorts = splitter.drawedPorts;
	
	//var svg_width = splitter_svg.node.offsetWidth;
	//var svg_height = splitter_svg.node.offsetHeight;
	
	var portPositions = [
		{ x: 2, y: 30 },		// 0
		{ x: 58, y: 30 },		// 1
		{ x: 30, y: 2 },		// 2
		{ x: 30, y: 58 },		// 3
		{ x: 45, y: 16 },		// 4
		{ x: 45, y: 44 },		// 5
		{ x: 15, y: 16 },		// 6
		{ x: 16, y: 45 },		// 7
	];
	
	// remove graphical elements corresponding to the 'old' ports
	var oldPortCounter = splitter_oldPorts.length;
	for (var i = 0; i < oldPortCounter; i++) {
		splitter_oldPorts[i].remove();
	}
	
	// draw the graphical elements for the 'new' ports
	var splitterPorts = [];
	var portCounter = 0;
	var borderColour = "#000000";
	var fillColour = "#FFFFFF";
	
	for (var i = 0; i < splitter_inouts; i++) {
	
		var splitter_port_id = splitter_id+"-port_"+portCounter;
		splitterPorts[portCounter] = splitter_svg.instance.rect(6, 6);
		splitterPorts[portCounter].attr({ fill: fillColour,
										  class: "linkable",
										  x: portPositions[portCounter].x,
										  y: portPositions[portCounter].y
										});
										
		splitterPorts[portCounter].radius(3);
		splitterPorts[portCounter].stroke({ color: borderColour, opacity: 1.0, width: 1 });
		splitterPorts[portCounter].attr({ "id" : splitter_port_id,
										  "title" : "port#" + (portCounter + 1)
										});
										
		$("#"+splitter_port_id).tooltip({});
				
		var lnkStart;
		$("#"+splitter_port_id).contextmenu({
			delegate: null,
			menu: [
				{title: "Add link", cmd: "add_link", uiIcon: "ui-icon-arrow-2-e-w"},
			],
			
			beforeOpen: function(event, ui) {
				lnkStart = { x: event.pageX, y: event.pageY };
				$("#"+this.id).tooltip("option", "hide", { effect: "fadeOut", duration: 1, delay: 0 });
				$("#"+this.id).tooltip("close");
				$("#"+this.id).tooltip("disable");
			},
			select: function(event, ui) {				
				if (ui.cmd == "add_link") {
					addLink(this.id, document.getElementById(this.id.substring(0, this.id.indexOf("-"))).firstChild, "splittermerger", 
						{ x: this.x.baseVal.value + 3, 
						  y: this.y.baseVal.value + 3 });
				}
			},
			close: function(event) {
				$("#"+this.id).tooltip("enable");
			},
		});
			
		portCounter++;
		if (portCounter == MAX_TS_INOUTS) {
			getSplitterList()[splitter_id].drawedPorts = splitterPorts;
			return;
		}
	}
	
	// remove rules regarding ports that have been removed
	var splitter_rules_length = splitter.rules.length;
	for (var i = 0; i < splitter_rules_length; i++) {
		if (splitter.rules[i].in > portCounter || splitter.rules[i].out > portCounter) {
			delete splitter.rules[i];
		}
	}
	var old_rules_array = splitter.rules;
	var new_rules_array = [];
	for (var i = 0; i < old_rules_array.length; i++) {
		if (old_rules_array[i]) {
			new_rules_array.push(old_rules_array[i]);
		}
	}
	splitter.rules = new_rules_array;
	
	// remove links from / to ports that have been removed
	var splitter_links_length = splitter.links.length;
	for (var i = 0; i < splitter_links_length; i++) {
		var link_id = splitter.links[i];
		var lnk = getLinkList()[link_id];
		var portStr;
		var portNumber;
		
		if (lnk.elem1.id == splitter_id) {
			portStr = lnk.elem1.port.substring(lnk.elem1.port.indexOf("-") + 1, lnk.elem1.port.length);
			portNumber = parseInt(portStr.substr(portStr.indexOf("_") + 1));
		} else if (lnk.elem2.id == splitter_id) {
			portStr = lnk.elem2.port.substring(lnk.elem2.port.indexOf("-") + 1, lnk.elem2.port.length);
			portNumber = parseInt(portStr.substr(portStr.indexOf("_") + 1));
		}
		
		if (portNumber < portCounter)
			continue;
		
		if (lnk.elem1.id != splitter_id) {
			var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
			elem1Links.splice(elem1Links.indexOf(link_id), 1);
			delete splitter.links[i];
		} else if (lnk.elem2.id != splitter_id) {
			var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
			elem2Links.splice(elem2Links.indexOf(link_id), 1);
			delete splitter.links[i];
		}
		
		delete getLinkList()[link_id];
		$("#"+link_id).remove();
	}
	var old_links_array = splitter.links;
	var new_links_array = [];
	for (var i = 0; i < old_links_array.length; i++) {
		if (old_links_array[i]) {
			new_links_array.push(old_links_array[i]);
		}
	}
	splitter.links = new_links_array;
	
	// save the 'new' ports in the vnf data structure
	getSplitterList()[splitter_id].drawedPorts = splitterPorts;
}

// AJAX request to get the JSON string that describes
// the template for the selected VNF type
function ajaxGetVnfData (vnf_id) {
	
	var vnfName = document.getElementById('vnf_select').value;
	var idx = vnfName.indexOf("(");
	vnfName = vnfName.substring(0, idx - 1);
	var vnf_desc;
	
	$.ajax({
		type: "POST",
		url: "ajax_vnf",  // or just url: "/my-url/path/"
		data: {
		    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		    vnf_name: vnfName,
		},
		success: function(data) {
		    
		    // parses the JSON string that describes this VNF
			vnf_desc = JSON.parse(data);
			getVnfList()[vnf_id].vnfDesc = vnf_desc;
			labelPortInfo = [];
			var ports = vnf_desc.ports;
			for (i = 0; i < ports.length; i++) { 
				if (ports[i].label == "control")
					continue;
				
				var portType = "transparent";
				if (ports[i]["ipv4-config"] != "none" || ports[i]["ipv6-config"] != "none")
					portType = "active";
				
				var portPos1 = ports[i].position[0];
				var portPos2 = ports[i].position[2];
				var portMax;
				if (portPos2 == "N")
					portMax = MAX_PORTS;
				else
					portMax = portPos2 - portPos1 + 1;
				
				if (portMax < ports[i].min)
					alert("Error: The maximum number of ports is less than the minimum number of ports !");
				
				labelPortInfo.push({label:ports[i].label, min:ports[i].min, cnt:ports[i].min, max:portMax,
									ipv4c:ports[i]["ipv4-config"], ipv6c:vnf_desc.ports[i]["ipv6-config"], type:portType,
									colour:"#000000"
								   });
			}
			
			getVnfList()[vnf_id].ports = labelPortInfo;		// saves the information related to the labels and their ports
			var svg = document.getElementById(vnf_id).getElementsByTagName("svg")[0].instance;
			
			// change the text (abc -> Abc) and color in the vnf title
			svg.children()[1].text(vnf_desc.name.charAt(0).toUpperCase().concat(vnf_desc.name.slice(1))).style('fill', "#000CCC");
			
			// remove the dbclick event handler associated with the rectangle
			$( "#".concat(svg.children()[0])).off( "dblclick" );
			$( "#".concat(vnf_id)).off( "dblclick" );
			
			$( "#".concat(vnf_id)).on( "dblclick", function() {
				
				var portcounters = openSettingsDialog(vnf_id);
				$("#vnfSettingsPanel").dialog("option", "buttons",
					{Ok: function(event) {
						$('#vnfSettingForm .submit').click();
						if (document.getElementById('vnfSettingForm').checkValidity() == false)
							return false;
						var counter_array = $("#vnfSettingsPanel").find("input[name=input_number]").get();
						var vnf = getVnfList()[vnf_id];
						for (i = 0; i < counter_array.length; i++) {
							vnf.ports[i].cnt = counter_array[i].valueAsNumber;
						}
						
						counter_array = $("#vnfSettingsPanel").find("input[name=label_colour]").get();
						for (i = 0; i < counter_array.length; i++) {
							vnf.ports[i].colour = counter_array[i].value;
						}
						
						vnfRefreshPorts(getVnfList()[vnf_id], vnf_id);
						dialog_settings.dialog( "close" );
					},
					Cancel: function() {
						dialog_settings.dialog( "close" );
					}
				});
				
				$("#vnfSettingsPanel").dialog( "open" );
				
			});
			
			$( "#".concat(svg.node.childNodes[1].id) ).attr("title", vnf_desc["vnf-type"]);
			$( "#".concat(svg.node.childNodes[1].id) ).tooltip({
				position: { my: "left+20 center-30", at: "center center" },
				show: {
					effect: "slideDown",
					delay: 250,
					duration: 150,
				}
			});
			
			$("#".concat(vnf_id)).contextmenu("enableEntry", "edit", true);
			
			// reset drawn ports
			vnf = getVnfList()[vnf_id];
			var vnf_oldPorts = vnf.drawedPorts;
			// remove graphical elements corresponding to the 'old' ports
			for (var i = 0; i < vnf_oldPorts.length; i++) {
				vnf_oldPorts[i].remove();
			}
			getVnfList()[vnf_id].drawedPorts = [];
			
			// remove links from/to old ports
			var vnf = getVnfList()[vnf_id];
			var vnf_links_length = vnf.links.length;
			for (var i = 0; i < vnf_links_length; i++) {
				var link_id = vnf.links[i];
				var lnk = getLinkList()[link_id];
				if (lnk.elem1.id != vnf_id) {
					var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
					elem1Links.splice(elem1Links.indexOf(link_id), 1);
				} else if (lnk.elem2.id != vnf_id) {
					var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
					elem2Links.splice(elem2Links.indexOf(link_id), 1);
				}
				
				delete getLinkList()[link_id];
				$("#"+link_id).remove();
			}
			vnf.links = [];
		},
		error: function(xhr, textStatus, errorThrown) {
		    alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
        }
    });
}

/*------------------------ ENDPOINT GET DATA -------------------------*/
function setEndpointData(endpoint_id){
	var endpointType = document.getElementById('endpoint').value;
	getEndPointList()[endpoint_id].type = endpointType;
	var svg = document.getElementById(endpoint_id).getElementsByTagName("svg")[0].instance;
	var img = svg.children()[1];
	if(img == undefined){
		svg.image(STATIC_URL + "/service_graph/images/"+endpointType+".png", 16, 16).attr({'x': 35, 'y': 35});
	}
	else{
		img.remove();
		svg.image(STATIC_URL + "/service_graph/images/"+endpointType+".png", 16, 16).attr({'x': 35, 'y': 35});
	}
	
	$( "#".concat(svg.children()[1]) ).attr("title", endpointType);
		$( "#".concat(svg.children()[1]) ).tooltip({
		  show: {
			effect: "slideDown",
			delay: 150,
			duration: 100,
		  }
	});
}


/*----------------------------- VNF DIALOG SETTINGS ---------------------*/

// Initializes the content of the VNF settings dialog form
function openSettingsDialog(vnf_id) {
	var vnf_desc = getVnfList()[vnf_id].vnfDesc;
	var vnfPorts = getVnfList()[vnf_id].ports;
	$("#vnfSettingsPanel").find("p").html(vnf_desc.name.toUpperCase() + 
								" - " + vnf_desc.uri + "<br />" + " (" + vnf_desc["vnf-type"] + ")");
	var tbody = $("#vnfSettingsPanel").find("tbody").get()[0];
	var new_tr;
	
	for (i = 0; i < vnfPorts.length; i++) {
		new_tr = document.createElement("tr");
		
		new_tr.appendChild(document.createElement("td")).innerHTML = vnfPorts[i].label;
		var input_td = document.createElement("td");
		var input = document.createElement("input");
		input.type = "number";
		input.name = "input_number";
		input.id = "labelports_" + i;
		input.min = vnfPorts[i].min;
		input.max = vnfPorts[i].max;
		input.step = "1";
		input.value = vnfPorts[i].cnt;
		input_td.appendChild(input);
		new_tr.appendChild(input_td);
		new_tr.appendChild(document.createElement("td")).innerHTML = vnfPorts[i].min;
		new_tr.appendChild(document.createElement("td")).innerHTML = vnfPorts[i].max;
		new_tr.appendChild(document.createElement("td")).innerHTML = vnfPorts[i].type;
		new_tr.appendChild(document.createElement("td")).innerHTML = vnfPorts[i].ipv4c;
		new_tr.appendChild(document.createElement("td")).innerHTML = vnfPorts[i].ipv6c;
		
		var color_input = document.createElement("input");
		color_input.type = "color";
		color_input.name = "label_colour";
		color_input.id = "labelportcolor_" + i;
		color_input.value = vnfPorts[i].colour;
		
		new_tr.appendChild(document.createElement("td")).appendChild(color_input);		
		
		tbody.appendChild(new_tr);
	}	
}

/*-----------------------------SPLITTER DIALOG SETTINGS --------------------------------------------------------------------------*/

// Function to create the settings strings, using the settings object
function toStr(s){

	var str = "";
	var sep = "<br />";
	if(s.macsrc != "")
		str = str.concat("mac src: ").concat(s.macsrc).concat(sep);
	if(s.macdst != "")
		str = str.concat("mac dst: ").concat(s.macdst).concat(sep);
	if(s.ipsrc != "")
		str = str.concat("ip src: ").concat(s.ipsrc).concat(sep);
	if(s.ipdst != "")
		str = str.concat("ip dst: ").concat(s.ipdst).concat(sep);
	if(s.vlanid != "")
		str = str.concat("vlan id: ").concat(s.vlanid).concat(sep);
	if(s.portsrc != "")
		str = str.concat("port src: ").concat(s.portsrc).concat(sep);
	if(s.portdst != "")
		str = str.concat("port dst: ").concat(s.portdst).concat(sep);
	if(s.protocol != "")
		str = str.concat("protocol: ").concat(s.protocol).concat(sep);
	
	return str;
}

// Function to save the field values of the addrule dialog
function addRuleFunction(splitter_id){
	var s = getSplitterList()[splitter_id];
	var l = s.rules.length;
	
	var radios = document.getElementsByName('protocol');
	var protocol = "";
	for (var i = 0, length = radios.length; i < length; i++) {
		if (radios[i].checked) {
			protocol = radios[i].value;
			break;
		}
	}
	
	if(l==undefined) l = 0;
	var p = document.getElementById("priority").value;
	if (p == "") p = 0;
	s.rules[l] = {'in' : document.getElementById("addRuleIn").valueAsNumber, 
					'out' : document.getElementById("addRuleOut").valueAsNumber, 
					'priority': p, 
					'settings' : {
								  'macsrc' : document.getElementById("macsrc").value,
								  'macdst' : document.getElementById("macdst").value,
								  'ipsrc' : document.getElementById("ipsrc").value,
								  'ipdst' : document.getElementById("ipdst").value,
								  'vlanid' : document.getElementById("vlanid").value,
								  'portsrc' : document.getElementById("portsrc").value,
								  'portdst' : document.getElementById("portdst").value,
								  'protocol' : protocol,
								}
				   };
}

function modifyRuleFunction(splitter_id, l){
	var s = getSplitterList()[splitter_id];
	
	var p = document.getElementById("priority").value;
	var radios = document.getElementsByName('protocol');
	var protocol="";
	for (var i = 0, length = radios.length; i < length; i++) {
		if (radios[i].checked) {
			protocol = radios[i].value;
			break;
		}
	}
	
	if (p == "") p = 0;
	s.rules[l] = {'in' : document.getElementById("addRuleIn").value, 
					'out' : document.getElementById("addRuleOut").value, 
					'priority': p, 
					'settings' : {'macsrc' : document.getElementById("macsrc").value,
								  'macdst' : document.getElementById("macdst").value,
								  'ipsrc' : document.getElementById("ipsrc").value,
								  'ipdst' : document.getElementById("ipdst").value,
								  'vlanid' : document.getElementById("vlanid").value,
								  'portsrc' : document.getElementById("portsrc").value,
								  'portdst' : document.getElementById("portdst").value,
								  'protocol' : protocol,
								  
								}
				   };
}


// Initialization of the splitter settings dialog
function initSplitterSettings(splitter_id) {
	
	var tbody = $("#splittermergerPanel").find("tbody").get()[0];
	var i = 0;
	
	// clear the previous existing records
	var new_tbody = document.createElement('tbody');
	tbody.parentNode.replaceChild(new_tbody,tbody)
	
	var s = getSplitterList()[splitter_id];
	var nports = s.num_inout;
	document.getElementById("splitterInput").value = nports; 
					
	var tbody = $("#splittermergerPanel").find("tbody").get()[0];
	
	for(i=0; i<s.rules.length; i++){	
		new_tr = document.createElement("tr");
		new_tr.id = "tr"+i;

		new_tr.appendChild(document.createElement("td")).innerHTML = s.rules[i].in;
		new_tr.appendChild(document.createElement("td")).innerHTML = s.rules[i].out;

		var settings = document.createElement("td");
		toString(splitter_id, i);

		var str_td = document.createElement("td");
		str_td.innerHTML = toStr(s.rules[i].settings);
		new_tr.appendChild(str_td);

		new_tr.appendChild(document.createElement("td")).innerHTML = s.rules[i].priority;

		var input1 = document.createElement("img");
		input1.src = STATIC_URL + "/service_graph/images/configure.png";
		input1.id = "configureButton"+i;
		input1.value = i;
		var edit =  document.createElement("td");
		edit.appendChild(input1);
		new_tr.appendChild(edit);
		var image = document.createElement("img");
		image.id = "deleteButton"+i;
		image.value = i;
		image.src = STATIC_URL + "/service_graph/images/delete.png";
		var del =  document.createElement("td");
		del.appendChild(image);
		new_tr.appendChild(del);
		tbody.appendChild(new_tr);
		$( "#configureButton"+i).on( "click", function() {
				var s = getSplitterList()[splitter_id];
				nports = document.getElementById("splitterInput").valueAsNumber;
				var t = this.value;
				
				document.getElementById("addRuleIn").max = nports;
				document.getElementById("addRuleOut").max = nports;
				document.getElementById("addRuleIn").value =  s.rules[this.value].in;
				document.getElementById("addRuleOut").value =  s.rules[this.value].out;
				document.getElementById("addRuleIn").max = nports;
				document.getElementById("addRuleOut").max = nports;
				document.getElementById("addRuleIn").value =  s.rules[this.value].in;
				document.getElementById("addRuleOut").value =  s.rules[this.value].out;
				document.getElementById("macsrc").value = s.rules[this.value].settings.macsrc;
				document.getElementById("macdst").value = s.rules[this.value].settings.macdst;
				document.getElementById("ipsrc").value = s.rules[this.value].settings.ipsrc;
				document.getElementById("ipdst").value = s.rules[this.value].settings.ipdst;
				document.getElementById("vlanid").value = s.rules[this.value].settings.vlanid;
				document.getElementById("portsrc").value = s.rules[this.value].settings.portsrc;
				document.getElementById("portdst").value = s.rules[this.value].settings.portdst;
				document.getElementById("priority").value = s.rules[this.value].priority;
				if(s.rules[this.value].settings.protocol != ""){
					var radios = document.getElementsByName('protocol');
					for (var i = 0, length = radios.length; i < length; i++) {
						if(radios[i].value == s.rules[this.value].settings.protocol) 
							radios[i].checked="true;"
					}
							
		
					
				}
			else{
				var radios = document.getElementsByName('protocol');
				for (var i = 0, length = radios.length; i < length; i++) {
						if(radios[i].value == s.rules[this.value].settings.protocol) 
							radios[i].checked="true;"
						else
							radios[i].checked = "false;"
					}
			}
				$("#addrulePanel").dialog("option", "buttons", {Ok: function(event) {
					
					modifyRuleFunction(splitter_id,t);
					var tr = $("#splittermergerPanel").find("tr").get()[t+1];
					tr.cells[0].innerHTML = s.rules[t].in;
					tr.cells[1].innerHTML = s.rules[t].out;
					tr.cells[2].innerHTML = toStr(s.rules[t].settings);
					tr.cells[3].innerHTML = s.rules[t].priority;
					
					//$("#tr"+t).replaceWith(tr);
					
					addrule_dialog.dialog( "close" );
				},
				Cancel: function() {addrule_dialog.dialog( "close" ); }});
				addrule_dialog.dialog( "open" );
			});
		$( "#deleteButton"+i).on( "click", function() {
			var k = this.value;
			var j = k;
			while(j<s.rules.length-1){
				document.getElementById("deleteButton"+(j+1)).value =  j;
				document.getElementById("configureButton"+(j+1)).value =  j;
				s.rules[j] = s.rules[j+1];
				j += 1;
			}
			s.rules.splice(j,1);
			//remove the corresponding table row
			var tr = $("#splittermergerPanel").find("tr").get()[k+1]; //i+1 because the first one is the header
			var tbody = $("#splittermergerPanel").find("tbody").get()[0];
			tbody.removeChild(tr);
		});
	}
	
	// By clicking on the "addrule" button, the add rule dialog is initialized and opened
	$("#addrulebutton").on("click", function() {
	
		nports = document.getElementById("splitterInput").valueAsNumber;
		
		document.getElementById("addRuleIn").max = nports;
		document.getElementById("addRuleOut").max = nports;
		document.getElementById("addRuleIn").value = "1";
		document.getElementById("addRuleOut").value = "1";
		/*document.getElementById("macsrc").value = "33:33:33:00:00:00";
		document.getElementById("macdst").value = "33:33:33:00:00:00";
		document.getElementById("ipsrc").value = "192.168.0.1/24";
		document.getElementById("ipdst").value = "192.168.0.1/24";*/
		document.getElementById("macsrc").value = "";
		document.getElementById("macdst").value = "";
		document.getElementById("ipsrc").value = "";
		document.getElementById("ipdst").value = "";
		document.getElementById("vlanid").value = "";
		document.getElementById("portsrc").value = "";
		document.getElementById("portdst").value = "";
		document.getElementById("priority").value = "";
		var radios = document.getElementsByName('protocol');
		for (var i = 0, length = radios.length; i < length; i++) {
			radios[i].checked = "false;"
		}
		
		$("#addrulePanel").dialog("option", "buttons", {Ok: function(event) {

			var tbody = $("#splittermergerPanel").find("tbody").get()[0];
	

			addRuleFunction(splitter_id);
			
			new_tr = document.createElement("tr");
			i = s.rules.length - 1;
			new_tr.id = i;

			new_tr.appendChild(document.createElement("td")).innerHTML = s.rules[i].in;
			new_tr.appendChild(document.createElement("td")).innerHTML = s.rules[i].out;

			var settings = document.createElement("td");
			toString(splitter_id, i);
			
			new_tr.appendChild(document.createElement("td")).innerHTML = toStr(s.rules[i].settings);

			
			new_tr.appendChild(document.createElement("td")).innerHTML = s.rules[i].priority;
			
			var input1 = document.createElement("img");
			input1.src = STATIC_URL + "/service_graph/images/configure.png";
			input1.id = "configureButton"+i;
			input1.value = i;
			var edit =  document.createElement("td");
			edit.appendChild(input1);
			new_tr.appendChild(edit);
			var image = document.createElement("img");
			image.id = "deleteButton"+i;
			image.value = i;
			image.src = STATIC_URL + "/service_graph/images/delete.png";
			var del =  document.createElement("td");
			del.appendChild(image);
			new_tr.appendChild(del);
			tbody.appendChild(new_tr);
			addrule_dialog.dialog( "close" );
			
			$( "#configureButton"+i).on( "click", function() {
				var s = getSplitterList()[splitter_id];
				nports = document.getElementById("splitterInput").valueAsNumber;
				
				i = this.value;
				document.getElementById("addRuleIn").max = nports;
				document.getElementById("addRuleOut").max = nports;
				document.getElementById("addRuleIn").value =  s.rules[this.value].in;
				document.getElementById("addRuleOut").value =  s.rules[this.value].out;
				document.getElementById("macsrc").value = s.rules[this.value].settings.macsrc;
				document.getElementById("macdst").value = s.rules[this.value].settings.macdst;
				document.getElementById("ipsrc").value = s.rules[this.value].settings.ipsrc;
				document.getElementById("ipdst").value = s.rules[this.value].settings.ipdst;
				document.getElementById("vlanid").value = s.rules[this.value].settings.vlanid;
				document.getElementById("portsrc").value = s.rules[this.value].settings.portsrc;
				document.getElementById("portdst").value = s.rules[this.value].settings.portdst;
				document.getElementById("priority").value = s.rules[this.value].priority;
				
				if(s.rules[this.value].settings.protocol!=""){
					var radios = document.getElementsByName('protocol');
						for (var i = 0, length = radios.length; i < length; i++) {
							if(radios[i].value == s.rules[this.value].settings.protocol) 
								radios[i].checked="true;"
							else
							radios[i].checked = "false;"
						}
			}
				$("#addrulePanel").dialog("option", "buttons", {Ok: function(event) {
					
					modifyRuleFunction(splitter_id,i);
					var tr = $("#splittermergerPanel").find("tr").get()[i+1]; //i+1 because the first one is the header
					tr.cells[0].innerHTML = s.rules[i].in;
					tr.cells[1].innerHTML = s.rules[i].out;
					tr.cells[2].innerHTML = toStr(s.rules[i].settings);
					tr.cells[3].innerHTML = s.rules[i].priority;
					addrule_dialog.dialog( "close" );
				},
				Cancel: function() {addrule_dialog.dialog( "close" ); }});
				addrule_dialog.dialog( "open" );
			});
			$( "#deleteButton"+i).on( "click", function() {
				// shifting the index into the rules vector
				var s = getSplitterList()[splitter_id];
				i = this.value;
				
				var j = i;
				while(j<s.rules.length-1){
					document.getElementById("deleteButton"+(j+1)).value =  j;
					document.getElementById("configureButton"+(j+1)).value =  j;
					s.rules[j] = s.rules[j+1];
					j += 1;
				}
				s.rules.splice(j,1);
				// remove the corresponding table row
				var tr = $("#splittermergerPanel").find("tr").get()[i+1]; //i+1 because the first one is the header
				var tbody = $("#splittermergerPanel").find("tbody").get()[0];
				tbody.removeChild(tr);
				
			});

			},
			Cancel: function() {
				addrule_dialog.dialog( "close" );
			}
		});
		addrule_dialog.dialog( "open" );
	});
	
	// Enable double click event handler on the splitter element
	$( "#".concat(splitter_id)).on( "dblclick", function() {
		$("#splittermergerPanel").dialog( "open" );
	});
	
	
}

/* --------- save SG button dialog --------------------------------------*/

savesg_dialog = $( "#savePanel" ).dialog({
						autoOpen: false,
						height: 250,
						width: 350,
						modal: true,
						show: {
							effect: "blind",
							duration: 300
						},
						buttons: {
							Ok: function() {
								saveSG();
							},
							Cancel: function() {
								savesg_dialog.dialog( "close" );
							},
						
						},
						close: function() {

						}
				});
				
/*-------------------------Load SG dialog ----------------------------------*/
	
loadsg_dialog = $( "#loadPanel" ).dialog({
					autoOpen: false,
					height: 250,
					width: 350,
					modal: true,
					show: {
						effect: "blind",
						duration: 300
						},
						buttons: {
							Ok: function() {
								loadSGAjax();
							},
							Cancel: function() {
								loadsg_dialog.dialog( "close" );
							},
						
						},
						close: function() {

						}
	});
	
/*----------------------------------------------*/
// ------------- Initializes the toolbar and its graphical elements ----------------
function toolbarInit()
{
	/*-------------VNF DIALOG----------------------*/
	dialog = $( "#vnfPanel" ).dialog({
		autoOpen: false,
		height: 250,
		width: 700,
		modal: true,
		show: {
			effect: "blind",
			duration: 200
		},
		close: function() {

		}
	});
	
	/*-------- VNF Settings Panel -------*/
	dialog_settings = $( "#vnfSettingsPanel" ).dialog({
		autoOpen: false,
		height: 500,
		width: 720,
		modal: true,		
		show: {
			effect: "blind",
			duration: 200
		},
		close: function() {
			tbody = $("#vnfSettingsPanel").find("tbody");
			tbody.empty();
		}
	});
	
	/*-------------ENDPOINT DIALOG----------------------*/
	endpoint_dialog = $( "#endpointPanel" ).dialog({
		autoOpen: false,
		height: 250,
		width: 300,
		modal: true,
		show: {
			effect: "blind",
			duration: 300
			},
			close: function() {

			}
		});
	

	/*-------------SPLITTERMERGER DIALOG----------------------*/
	splitter_dialog = $( "#splittermergerPanel" ).dialog({
		autoOpen: false,
		height: 450,
		width: 700,
		modal: true,
		show: {
			effect: "blind",
			duration: 300
			},
			close: function() {

			}
		});
	/*-------------------------Add rule dialog ----------------------------------*/
	
	addrule_dialog = $( "#addrulePanel" ).dialog({
		autoOpen: false,
		height: 700,
		width: 700,
		modal: true,
		show: {
			effect: "blind",
			duration: 300
			},
			close: function() {

			}
		});
	
	/*----------------------------------------------*/
	if (SVG.supported) {
		// Creates a canvas for the VNF graphical element
		var vnfToolSvg = SVG('vnf_tool').size(102, 48).attr({id: "vnf_tool_element"});
		vnfToolSvg.fixSubPixelOffset();
		vnfToolSvg.addClass('todrop');

		// Creates the VNF element
		var vnfToolElement = vnfToolSvg.rect(100, 46).attr({fill: '#9BC2E3', x: 1, y: 1});
		vnfToolElement.radius(15);
		vnfToolElement.stroke({ color: '#151e12', opacity: 1.0, width: 2 });

		// Creates a canvas for the Traffic Splitter graphical element
		var splitterToolSvg = SVG('splitter_tool').size(60, 60).attr({id: "splitter_tool_element"});
		splitterToolSvg.fixSubPixelOffset();
		splitterToolSvg.addClass('todrop');

		// Creates the VNF element
		var splitterToolElement = splitterToolSvg.polygon("30,1 59,30 30,59 1,30").attr({ fill: '#9BC2E3', x: 10, y: 10 });
		splitterToolElement.stroke({ color: '#151e12', opacity: 1.0, width: 2 });
		
		// Creates a canvas for the EndPoint graphical element
		var endpointToolSvg = SVG('endpoint_tool').size(52, 52).attr({id: "endpoint_tool_element"});
		endpointToolSvg.addClass('todrop');
		endpointToolSvg.fixSubPixelOffset();

		// Creates the EndPoint element
		var endpointToolElement = endpointToolSvg.rect(50, 50).attr({ fill: '#9BC2E3', x: 1, y: 1 });
		endpointToolElement.radius(25);
		endpointToolElement.stroke({ color: '#151e12', opacity: 1.0, width: 2 });
		
		// Creates a canvas for the LAN graphical element
		var lanToolSvg = SVG('lan_tool').size(102, 20).attr({ id: "lan_tool_element" });
		lanToolSvg.fixSubPixelOffset();
		lanToolSvg.addClass('todrop');

		// Creates the LAN graphical element
		var lanElementBar = lanToolSvg.rect(84, 4).attr({ fill: '#000000', x: 9, y: 10 });
		var lanElementLeft = lanToolSvg.rect(8, 8).attr({ fill: '#000000', x: 1, y: 8 }).radius(4);
		var lanElementRight = lanToolSvg.rect(8, 8).attr({ fill: '#000000', x: 93, y: 8 }).radius(4);
			
		var lanToolElement = lanToolSvg.group();
		lanToolElement.add(lanElementLeft);
		lanToolElement.add(lanElementBar);
		lanToolElement.add(lanElementRight);

	} else {
		alert('SVG not supported');
	}
};

$(function () {
	$("#saveButton").button();
	$("#loadButton").button();
	
	$("#content").on("contextmenu", function (event) {
		event.stopPropagation();
		event.preventDefault();
		return false;
	});
	
	// Initialize the toolbar
	toolbarInit();

	// test user name and user id
	//document.getElementById("footer_user_info").innerHTML = "username : " + USER_NAME + "<br />user_id : " + USER_ID;

	// Make the toolbar elements draggable
	
	$("#vnf_tool_element").draggable({
		revert: "invalid",
		revertDuration: 250,
		scroll: false,
		helper: "clone",
		containment: "#content",
		appendTo: "parent",
		cursor: "move",
		cursorAt: { left: 51, top: 24 },
		opacity: 0.6,
		drag: function(event, ui) {
			//document.getElementById("design_window_text").innerHTML = "Element at (" + ui.position.left + "," + ui.position.top + ")";
		},
	});
	$("#splitter_tool_element").draggable({
		revert: "invalid",
		revertDuration: 250,
		scroll: false,
		helper: "clone",
		containment: "#content",
		appendTo: "parent",
		cursor: "move",
		cursorAt: { left: 30, top: 30 },
		opacity: 0.6,
		drag: function(event, ui) {
			//document.getElementById("design_window_text").innerHTML = "Element at (" + ui.position.left + "," + ui.position.top + ")";
		},
	});
	$("#endpoint_tool_element").draggable({
		revert: "invalid",
		revertDuration: 250,
		scroll: false,
		helper: "clone",
		containment: "#content",
		cursor: "move",
		cursorAt: { left: 26, top: 26 },
		opacity: 0.6,
		drag: function(event, ui) {
			//document.getElementById("design_window_text").innerHTML = "Element at (" + ui.position.left + "," + ui.position.top + ")";
		},
	});
	$("#lan_tool_element").draggable({
		revert: "invalid",
		revertDuration: 250,
		scroll: false,
		helper: "clone",
		containment: "#content",
		cursor: "move",
		cursorAt: { left: 51, top: 10 },
		opacity: 0.6,
		drag: function(event, ui) {
			//document.getElementById("design_window_text").innerHTML = "Element at (" + ui.position.left + "," + ui.position.top + ")";
		},
	});
	
	$("#content").droppable({
		activeClass: "ui-state-active",
		hoverClass: "ui-state-hover",
		accept: ".todrop",
	    drop: function( event, ui ) {	// callback function that executes anytime a draggable element is dropped in the #content div
			var tool_id = ui.draggable[0].id;

			// TO-DO: we may want to use JQuery high-level offset functions 
			// in order to ensure cross-browser compatibility (i.e. fix issues with Firefox)
			var offset = $("#content").offset();
			var w = $("#content").width();
			var h = $("#content").height();

			var designWindowSvg = getDesignWindowSvg();

			switch (tool_id) {
			   case "vnf_tool_element":
				// Create a new VNF element and draw it in the design window
				
				// Get the foreign object created inside the svg design window in order to insert the new html div
				var fobj = designWindowSvg._children[0].node.instance;
				var vnfId = getCurrentVnfId();
				var vnf_id = "vnf_".concat(vnfId);
				var newDiv = document.createElement("div");
				newDiv.id = vnf_id;
				newDiv.style.position = "absolute";
				newDiv.style.width = "108px"; // 102px
				newDiv.style.height = "54px"; // 48px

				fobj.appendChild(newDiv);
				
				// Places the center of new element on the coordinates of the mouse event
				$("#"+vnf_id).position({ at: "center center", of: event, collision:"fit", within: "#content" });
		
				// Create an SVG canvas for the VNF graphical element --> inside the html div "vnf_1"	
				var vnfToolSvg = SVG(vnf_id).size('100%', '100%');	
				vnfToolSvg.attr({ id: "vnf_svg_".concat(vnfId), class: "obstacle" });
				vnfToolSvg.fixSubPixelOffset();
				
				// Insert the new VNF element in the vnf list
				getVnfList()[vnf_id] = { id : vnf_id, 
									     vnfDesc : null,
									     ports : null,
									     drawedPorts : [],
									     links: [],
									   };
				
				var vnfElement = vnfToolSvg.rect(100, 46);
				vnfElement.attr({ id: "vnf_rect_".concat(vnfId), fill: '#9BC2E3', x: 4, y: 4 });
				vnfElement.radius(15);
				vnfElement.stroke({color: '#151e12', opacity: 1.0, width: 2});

				var vnfText = vnfToolSvg.text('< vnf >').font({ family:   'Helvetica',
																size:     14,
																weight:   'bold',
																//anchor:   'right',
																leading:  '1.1em'
															}).attr({ x: 10, y: 16 });


				var vnf_svg = document.getElementById("vnf_".concat(vnfId)).getElementsByTagName("svg")[0].instance;
				
				$("#"+vnf_id).contextmenu({

					delegate: "#vnf_rect_"+vnfId,
					menu: [
					        {title: "Configure VNF", cmd: "edit", uiIcon: "ui-icon-pencil", disabled: true},
							{title: "Set VNF type", cmd: "set", uiIcon: "ui-icon-pencil"},
							{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
					],
					hide: {effect: "fadeOut", duration: 360, delay: 50},
					select: function(event, ui) {
						var menuId = ui.cmd;
						if (menuId == "set") {
							dialog.dialog( "option", "buttons", {Ok: function() {
										ajaxGetVnfData(vnf_id);
										dialog.dialog( "close" );
									},
									Cancel: function() {
										dialog.dialog( "close" );
									}
							});
							dialog.dialog( "open" );
						} else if (menuId == "delete") {
							var vnf = getVnfList()[vnf_id];
							var vnf_links_length = vnf.links.length;
							for (var i = 0; i < vnf_links_length; i++) {
								var link_id = vnf.links[i];
								var lnk = getLinkList()[link_id];
								if (lnk.elem1.id != vnf_id) {
									var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
									elem1Links.splice(elem1Links.indexOf(link_id), 1);
								} else if (lnk.elem2.id != vnf_id) {
									var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
									elem2Links.splice(elem2Links.indexOf(link_id), 1);
								}
								
								delete getLinkList()[link_id];
								$("#"+link_id).remove();
							}
							
							delete getVnfList()[vnf_id];
							$("#"+vnf_id).empty();
						}
						else if (menuId == "edit") {
							var portcounters = openSettingsDialog(vnf_id);
							$("#vnfSettingsPanel").dialog("option", "buttons", { 
									Ok: function(event) {
										$('#vnfSettingForm .submit').click();
										if (document.getElementById('vnfSettingForm').checkValidity() == false)
											return false;
										var counter_array = $("#vnfSettingsPanel").find("input[name=input_number]").get();
										var vnf = getVnfList()[vnf_id];
										for (i = 0; i < counter_array.length; i++) {
											vnf.ports[i].cnt = counter_array[i].valueAsNumber;
										}
										
										counter_array = $("#vnfSettingsPanel").find("input[name=label_colour]").get();
										for (i = 0; i < counter_array.length; i++) {
											vnf.ports[i].colour = counter_array[i].value;
										}
										
										vnfRefreshPorts(getVnfList()[vnf_id], vnf_id);
										dialog_settings.dialog( "close" );
									},
									Cancel: function() {
										dialog_settings.dialog( "close" );
									}
								}
							);
							
							$("#vnfSettingsPanel").dialog( "open" );
						}
					}
				});
					
				$("#vnf_rect_".concat(vnfId)).on("dblclick", function() {
				
					$( "#vnfPanel" ).dialog( "option", "buttons", {Ok: function() {
							ajaxGetVnfData(vnf_id);
							dialog.dialog( "close" );
						},
						Cancel: function() {
							dialog.dialog( "close" );
						}});
					$('#vnfPanel').dialog( "open" );
					
				});
				

				$("#vnf").selectmenu({ width: 150 });

				var dragInitialPos;
				var paths = [];
				var destX = [];
				var destY = [];
				$("#vnf_".concat(vnfId)).draggable({
						scroll: false,
						containment: "#content",
						cursor: "move",
						cursorAt: { left: 51, top: 24 },				
						opacity: 0.6,
						snap: true,
						snapMode: "outer",

						start: function(event,ui) {
							var div = document.getElementById(vnf_id);
							dragInitialPos = { x: div.style.left, y: div.style.top };
							
							var elem_array = $( "#".concat(vnf_id) ).find("*").get();
							for (var i = 0; i < elem_array.length; i++) {
								var selector = "#"+elem_array[i].attributes["id"].nodeValue;
								if ($(selector).tooltip( "instance" ) != undefined) {
									$( selector ).tooltip("disable");
								}
							}

							var vnf_elem = getSgElement(this.id, "vnf");
							var paths_array = [];
							
							for (var i = 0; i < vnf_elem.links.length; i++) {
								var link = getLinkList()[vnf_elem.links[i]];
								if (link.elem1.id == this.id) { // this element is the 1st in the link structure				
									// redraw path
									var x1 = link.path.getSegment(0).coords[0];
									var y1 = link.path.getSegment(0).coords[1];
									var x2 = link.path.getSegment(1).coords[0];
									var y2 = link.path.getSegment(1).coords[1];
									link.path.clear();
									link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
									
									// swap elem1 and elem2
									var el1 = link.elem1;
									link.elem1 = link.elem2;
									link.elem2 = el1;
									
									paths_array[paths_array.length] = link.path;
								} else if (link.elem2.id == this.id) { // this element is the 2nd in the link
									paths_array[paths_array.length] = link.path;
								}
							}
							paths = paths_array;
							for (var i = 0; i < paths.length; i++) {
								var portRect = $("#"+getLinkList()[vnf_elem.links[i]].elem2.port).get()[0];
								destX[i] = portRect.x.baseVal.value + 3;
								destY[i] = portRect.y.baseVal.value + 3;
							}
						},
						drag: function(ui, event) {
							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + destX[i],
											 y: this.offsetTop + destY[i] })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},						
						stop: function(event,ui) {
							var elem_array = $( "#".concat(vnf_id) ).find("*").get();
							for (var i = 0; i < elem_array.length; i++) {
								var selector = "#"+elem_array[i].attributes["id"].nodeValue;
								if ($(selector).tooltip( "instance" ) != undefined) {
									$( selector ).tooltip("enable");
								}
							}

							var list = $("#"+vnf_id).collision(".obstacle");
							if (list.length > 0) {
								for (var j = 0; j < list.length; j++) {
									if (list[j].parentNode.id != vnf_id) {
										var yy = document.getElementById(vnf_id).style;
										yy.left = dragInitialPos.x;
										yy.top = dragInitialPos.y;
										break;
									}
								}
							}

							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + destX[i],
											 y: this.offsetTop + destY[i] })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},
				});				
				break;
			   
			   	case "splitter_tool_element":
				var fobj = designWindowSvg._children[0].node.instance;
				var splitterMergerId = getCurrentSplitterMergerId();

				var splittermerger_id = "splittermerger_".concat(splitterMergerId);
				

				var newDiv = document.createElement("div");
				newDiv.id = "splittermerger_".concat(splitterMergerId);
				newDiv.style.position = "absolute";
				newDiv.style.width = "66px";
				newDiv.style.height = "66px";
				
				fobj.appendChild(newDiv);
				$("#"+splittermerger_id).position({ at: "center", of: event, collision:"fit", within: "#content", });

				var splitterToolSvg = SVG('splittermerger_'.concat(splitterMergerId)).size(66, 66);
				splitterToolSvg.attr({id: "splittermerger_svg_".concat(splitterMergerId), class: "obstacle" });
				splitterToolSvg.fixSubPixelOffset();		

				getSplitterList()[splittermerger_id] = { id : splittermerger_id,
														 num_inout : 3,
														 rules: [],
														 links: [],
													     drawedPorts : [],
													   };

				// Creates the Traffic Splitter element on the design window
				var startx = 4;
				var starty = 4;
				var splitterElement = splitterToolSvg.polygon("29,0 58,29 29,58 0,29");
				splitterElement.plot([[29 + startx,0 + starty],[58 + startx,29 + starty],
									  [29 + startx,58 + starty],[0 + startx,29 + starty]]);
				splitterElement.attr({ id: "splittermerger_polygon_"+splitterMergerId, fill: '#9BC2E3', 
									   x: ui.position.left - offset.left + 1, y: ui.position.top - offset.top + 1 });
				splitterElement.stroke({ color: '#151e12', opacity: 1.0, width: 2 });
				
				var splittermerger_svg = document.getElementById(splittermerger_id).getElementsByTagName("svg")[0].instance;
				
				splitterRefreshPorts(getSplitterList()[splittermerger_id], splittermerger_id);
				
				/* Splitter right click menu creation */
				$("#"+splittermerger_id).contextmenu({
					delegate: "#splittermerger_polygon_"+splitterMergerId,
					menu: [
							{title: "Configure Splitter", cmd: "edit", uiIcon: "ui-icon-pencil"},
							{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
					],
					
					select: function(event, ui) {
						var menuId = ui.cmd;
						if (menuId == "edit") {
							initSplitterSettings(splittermerger_id);
							$( "#splittermergerPanel" ).dialog( "option", "buttons", {
								Ok: function() {
									$('#splitterSettingForm .submit').click();
									if (document.getElementById('splitterSettingForm').checkValidity() == false)
										return false;
									getSplitterList()[splittermerger_id].num_inout = document
																							 .getElementById("splitterInput")
																							 .valueAsNumber;
								
									splitterRefreshPorts(getSplitterList()[splittermerger_id], splittermerger_id);
									splitter_dialog.dialog( "close" );
								},
								Cancel: function() {
									splitter_dialog.dialog( "close" );
								}
							});
					
							$('#splittermergerPanel').dialog( "open" );
						} else if (menuId == "delete") {
							var splitter = getSplitterList()[splittermerger_id];
							var splitter_links_length = splitter.links.length;
							for (var i = 0; i < splitter_links_length; i++) {
								var link_id = splitter.links[i];
								var lnk = getLinkList()[link_id];
								if (lnk.elem1.id != splittermerger_id) {
									var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
									elem1Links.splice(elem1Links.indexOf(link_id), 1);
								} else if (lnk.elem2.id != splittermerger_id) {
									var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
									elem2Links.splice(elem2Links.indexOf(link_id), 1);
								}
								
								delete getLinkList()[link_id];
								$("#"+link_id).remove();
							}
							
							delete getSplitterList()[splittermerger_id];
							$("#"+splittermerger_id).empty();
						}
					}
				});
				
				
				$( "#"+splittermerger_id).on( "dblclick", function() {
					initSplitterSettings(splittermerger_id);
					$( "#splittermergerPanel" ).dialog( "option", "buttons", {Ok: function() {
							$('#splitterSettingForm .submit').click();
							if (document.getElementById('splitterSettingForm').checkValidity() == false)
								return false;
							getSplitterList()[splittermerger_id].num_inout = document.getElementById("splitterInput").valueAsNumber;
							
							splitterRefreshPorts(getSplitterList()[splittermerger_id], splittermerger_id);
							splitter_dialog.dialog( "close" );
						},
						Cancel: function() {
							splitter_dialog.dialog( "close" );
						}});
					
					$('#splittermergerPanel').dialog( "open" );
				
				});
					
				$("#splittermerger").selectmenu({ width: 150 });
				
				var dragInitialPos;
				var paths = [];
				var destX = [];
				var destY = [];
				$("#splittermerger_".concat(splitterMergerId)).draggable({
						scroll: false,
						containment: "#content",
						cursor: "move",
						cursorAt: { left: 30, top: 30 },
						opacity: 0.6,
						snap: true,
						snapMode: "outer",
						
						start: function(event, ui) {
							var div = document.getElementById(splittermerger_id);
							dragInitialPos = { x: div.style.left, y: div.style.top };
							
							var elem_array = $( "#".concat(splittermerger_id) ).find("*").get();
							for (var i = 0; i < elem_array.length; i++) {
								var selector = "#"+elem_array[i].attributes["id"].value;
								if ($(selector).tooltip("instance") != undefined) {
									$(selector).tooltip("disable");
								}
							}

							var splitter_elem = getSgElement(this.id, "splittermerger");
							var paths_array = [];
							
							for (var i = 0; i < splitter_elem.links.length; i++) {
								var link = getLinkList()[splitter_elem.links[i]];
								if (link.elem1.id == this.id) { 	// this element is the 1st in the link					
									// redraw path
									var x1 = link.path.getSegment(0).coords[0];
									var y1 = link.path.getSegment(0).coords[1];
									var x2 = link.path.getSegment(1).coords[0];
									var y2 = link.path.getSegment(1).coords[1];
									link.path.clear();
									link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
									
									// swap elem1 and elem2
									var el1 = link.elem1;
									link.elem1 = link.elem2;
									link.elem2 = el1;
									
									paths_array[paths_array.length] = link.path;
								} else if (link.elem2.id == this.id) { 	// this element is the 2nd in the link
									paths_array[paths_array.length] = link.path;
								}
							}
							paths = paths_array;
							for (var i = 0; i < paths.length; i++) {
								var portRect = $("#"+getLinkList()[splitter_elem.links[i]].elem2.port).get()[0];
								destX[i] = portRect.x.baseVal.value + 3;
								destY[i] = portRect.y.baseVal.value + 3;
							}
						},
						drag: function(ui, event) {				
							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + destX[i],
											 y: this.offsetTop + destY[i] })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},						
						stop: function(event, ui) {
							var elem_array = $( "#".concat(splittermerger_id) ).find("*").get();
							for (var i = 0; i < elem_array.length; i++) {
								var selector = "#"+elem_array[i].attributes["id"].value;
								if ($(selector).tooltip("instance") != undefined) {
									$(selector).tooltip("enable");
								}
							}

							var list = $("#"+splittermerger_id).collision(".obstacle");
							if (list.length > 0) {
								for (var j = 0; j < list.length; j++) {
									if (list[j].parentNode.id != splittermerger_id) {
										var yy = document.getElementById(splittermerger_id).style;
										yy.left = dragInitialPos.x;
										yy.top = dragInitialPos.y;
										break;
									}
								}
							}

							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + destX[i],
											 y: this.offsetTop + destY[i] })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},
					});

				break;

			   case "endpoint_tool_element":
				var fobj = designWindowSvg._children[0].node.instance;
				var endpointId = getCurrentEndpointId();
				var endpoint_id = "endpoint_".concat(endpointId);
				var newDiv = document.createElement("div");
				newDiv.id = "endpoint_".concat(endpointId);
				newDiv.style.position = "absolute";
				newDiv.style.width = "52px";
				newDiv.style.height = "52px";

				getEndPointList()[endpoint_id] = { id : endpoint_id, 
										 		   type: null,
										 		   links: [],
												 };
		
				fobj.appendChild(newDiv);
				$("#"+endpoint_id).position({at: "center center", of: event, collision:"fit", within: "#content" });

				var endpointToolSvg = SVG('endpoint_'.concat(endpointId)).size(52, 52);	
				endpointToolSvg.attr({id: "endpoint_svg_".concat(endpointId), class: "obstacle" });
				endpointToolSvg.fixSubPixelOffset();				

				// Creates the Endpoint element on the design window
				var endpointElement = endpointToolSvg.rect(40, 40);
				endpointElement.attr({ id: "endpoint_rect_"+endpointId, fill: '#9BC2E3', x: 1, y: 1, class: 'linkable'});
				endpointElement.radius(20);
				endpointElement.stroke({color: '#151e12', opacity: 1.0, width: 2});
				
				var endpoint_svg = document.getElementById(endpoint_id).getElementsByTagName("svg")[0].instance;
				
				$("#"+endpoint_id).contextmenu({
					delegate: "#endpoint_rect_"+endpointId,
					menu: [
					        {title: "Add link", cmd: "add_link", uiIcon: "ui-icon-arrow-2-e-w"},
							{title: "Change type", cmd: "edit", uiIcon: "ui-icon-pencil"},
							{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
					],
					select: function(event, ui) {
						var menuId = ui.cmd;
						if (menuId == "add_link") {
							addLink(endpoint_id, endpointToolSvg, "endpoint", { x: 20, y: 20 });
						} else if (menuId == "edit") {
							endpoint_dialog.dialog( "option", "buttons", {Ok: function() {
								setEndpointData(endpoint_id);
								endpoint_dialog.dialog( "close" );
							},
							Cancel: function() {
								endpoint_dialog.dialog( "close" );
							}});
							endpoint_dialog.dialog( "open" );
						} else if (menuId == "delete") {
							var ep = getEndPointList()[endpoint_id];
							var ep_links_length = ep.links.length;
							for (var i = 0; i < ep_links_length; i++) {
								var link_id = ep.links[i];
								var lnk = getLinkList()[link_id];
								if (lnk.elem1.id != endpoint_id) {
									var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
									elem1Links.splice(elem1Links.indexOf(link_id), 1);
								} else if (lnk.elem2.id != endpoint_id) {
									var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
									elem2Links.splice(elem2Links.indexOf(link_id), 1);
								}
								
								delete getLinkList()[link_id];
								$("#"+link_id).remove();
							}
												
							delete getEndPointList()[endpoint_id];
							$("#"+endpoint_id).empty();
						}
					}
				});
				
				$( "#".concat(endpoint_svg)).on( "dblclick", function() {
					
					$( "#endpointPanel" ).dialog( "option", "buttons", {Ok: function() {
							setEndpointData(endpoint_id); 
							endpoint_dialog.dialog( "close" );
						},
						Cancel: function() {
							endpoint_dialog.dialog( "close" );
						}});
					$('#endpointPanel').dialog( "open" );
					
				});
					
				$("#endpoint").selectmenu({ width: 150 });

				var dragInitialPos;
				var paths = [];
				$("#endpoint_"+endpointId).draggable({
						scroll: false,
						containment: "#content",
						cursor: "move",
						cursorAt: { left: 26, top: 26 },
						opacity: 0.6,
						snap: true,
						snapMode: "outer",
						
						start: function(ui, event) {
							var div = document.getElementById(endpoint_id);
							dragInitialPos = { x: div.style.left, y: div.style.top };
							
							var ep = getSgElement("endpoint_"+endpointId, "endpoint");
							var paths_array = [];
							
							for (var i = 0; i < ep.links.length; i++) {
								var link = getLinkList()[ep.links[i]];
								if (link.elem1.id == "endpoint_"+endpointId) { // this element is the 1st in the link					
									// redraw path
									var x1 = link.path.getSegment(0).coords[0];
									var y1 = link.path.getSegment(0).coords[1];
									var x2 = link.path.getSegment(1).coords[0];
									var y2 = link.path.getSegment(1).coords[1];
									link.path.clear();
									link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
									
									// swap elem1 and elem2
									var el1 = link.elem1;
									link.elem1 = link.elem2;
									link.elem2 = el1;
									
									paths_array[paths_array.length] = link.path;
								} else if (link.elem2.id == "endpoint_"+endpointId) { // this element is the 2nd in the link
									paths_array[paths_array.length] = link.path;
								}
							}
							paths = paths_array;
						},
						drag: function(ui, event) {							
							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + 20,
											 y: this.offsetTop + 20 })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},
						stop: function(ui, event) {
							var list = $("#"+endpoint_id).collision(".obstacle");
							if (list.length > 0) {
								for (var j = 0; j < list.length; j++) {
									if (list[j].parentNode.id != endpoint_id) {
										var yy = document.getElementById(endpoint_id).style;
										yy.left = dragInitialPos.x;
										yy.top = dragInitialPos.y;
										break;
									}
								}
							}
							
							var destX = this.offsetLeft + 20;
							var destY = this.offsetTop + 20;
							
							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: destX, y: destY })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},
					});

				break;

			   case "lan_tool_element":
				var fobj = designWindowSvg._children[0].node.instance;
				var lanId = getCurrentLanId();
				var lan_id = "lan_".concat(lanId);
				var newDiv = document.createElement("div");
				newDiv.id = lan_id;
				newDiv.style.position = "absolute";
				newDiv.style.width = "182px";
				newDiv.style.height = "20px";

				getLANList()[lan_id] = { id : lan_id, 
				                         links: [],
				                       };

				fobj.appendChild(newDiv);
				$("#"+lan_id).position({at: "center center", of: event, collision:"fit", within: "#content" });

				// Creates a canvas for the LAN graphical element --> inside the html div "vnf_1"				
				var lanToolSvg = SVG('lan_'.concat(lanId)).size("100%", "100%");
				lanToolSvg.attr({id: "lan_svg_".concat(lanId), class: "obstacle", x: 0, y: 0 });
				lanToolSvg.fixSubPixelOffset();
				
				// Creates the LAN Network element on the design window
				var lanElementBar = lanToolSvg.rect(164, 4);
				lanElementBar.attr({ fill: '#000000', x: 9, y: 10, class: 'linkable'});
				var lanElementLeft = lanToolSvg.rect(8, 8).radius(4);
				lanElementLeft.attr({ fill: '#000000', x: 1, y: 8});
				var lanElementRight = lanToolSvg.rect(8, 8).radius(4);
				lanElementRight.attr({ fill: '#000000', x: 173, y: 8});
			
				var lanElement = lanToolSvg.group();	
				lanElement.add(lanElementLeft);
				lanElement.add(lanElementBar);
				lanElement.add(lanElementRight);
				lanElement.size("100%", "100%");	
				
				var lnkStart = {};
				$("#"+lan_id).contextmenu({
					delegate: null,
					menu: [
							{title: "Add link", cmd: "add_link", uiIcon: "ui-icon-arrow-2-e-w"},
							{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
					],
					//hide: {effect: "fadeOut", duration: "fast"},
					beforeOpen: function(event, ui) {
						//lnkStart = {x: event.offsetX, y: event.pageY };
						currentElem = event.target;
						while (currentElem.nodeName != "DIV") { 
							currentElem = currentElem.parentNode;
						}
						lnkStart.x = currentElem.offsetLeft + event.offsetX + 17;
						lnkStart.y = currentElem.offsetTop + event.offsetY;
					}, 
					select: function(event, ui) {
						var menuId = ui.cmd;
						if (menuId == "add_link") {
							addLink(lan_id, lanToolSvg, "lan", 
								{ x: lnkStart.x, 
								  y: lnkStart.y });
						} else if (menuId == "delete") {
							var lan = getLANList()[lan_id];
							var lan_links_length = lan.links.length;
							for (var i = 0; i < lan_links_length; i++) {
								var link_id = lan.links[i];
								var lnk = getLinkList()[link_id];
								if (lnk.elem1.id != lan_id) {
									var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
									elem1Links.splice(elem1Links.indexOf(link_id), 1);
								} else if (lnk.elem2.id != lan_id) {
									var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
									elem2Links.splice(elem2Links.indexOf(link_id), 1);
								}
								
								delete getLinkList()[link_id];
								$("#"+link_id).remove();
							}
							
							delete getLANList()[lan_id];
							$("#"+lan_id).empty();
						}
					}
				});
				
				var dragInitialPos;
				var destX = [];
				var destY = this.offsetTop + 11;
				$("#lan_".concat(lanId)).draggable({
						scroll: false,
						containment: "#content",
						cursor: "move",
						cursorAt: { left: 91, top: 10 },
						opacity: 0.6,
						snap: true,
						snapMode: "outer",
						start: function(ui, event) {
							var div = document.getElementById(lan_id);
							dragInitialPos = { x: div.style.left, y: div.style.top };
							
							var lan = getSgElement("lan_"+lanId, "lan");
							var paths_array = [];
							
							for (var i = 0; i < lan.links.length; i++) {
								var link = getLinkList()[lan.links[i]];
								if (link.elem1.id == "lan_"+lanId) { 	// this element is the 1st in the link					
									
									// redraw path
									var x1 = link.path.getSegment(0).coords[0];
									var y1 = link.path.getSegment(0).coords[1];
									var x2 = link.path.getSegment(1).coords[0];
									var y2 = link.path.getSegment(1).coords[1];
									link.path.clear();
									link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
									
									// swap elem1 and elem2
									var el1 = link.elem1;
									link.elem1 = link.elem2;
									link.elem2 = el1;
									
									paths_array[paths_array.length] = link.path;
								} else if (link.elem2.id == "lan_"+lanId) { 	// this element is the 2nd in the link
									paths_array[paths_array.length] = link.path;
								}
							}
							paths = paths_array;
							for (var i = 0; i < paths.length; i++) {
								destX[i] = paths[i].getSegment(1).coords[0] - lanToolSvg.node.parentElement.offsetLeft;
							}
						},
						drag: function(ui, event) {
							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + destX[i], 
											 y: this.offsetTop + 11 })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},
						stop: function(ui, event) {
							var list = $("#"+lan_id).collision(".obstacle");
							if (list.length > 0) {
								for (var j = 0; j < list.length; j++) {
									if (list[j].parentNode.id != lan_id) {
										var yy = document.getElementById(lan_id).style;
										yy.left = dragInitialPos.x;
										yy.top = dragInitialPos.y;
										break;
									}
								}
							}
							
							for (var i = 0; i < paths.length; i++) {
								paths[i].L({ x: this.offsetLeft + destX[i],
											 y: this.offsetTop + 11 })
										.drawAnimated({ delay: 0, duration: 1, easing: "-" });
								paths[i].replaceSegment(1, paths[i].getSegment(2));
								paths[i].removeSegment(2);
							}
						},
					});
					/*.resizable({containment: "#content",
								  minWidth: 115,
								  maxWidth: 400,
								  minHeight: 20,
								  maxHeight: 20,
								  resize: function(event, ui) {
									lanElementBar.size(ui.size.width - 9, 4);
									lanElementRight.attr({ x: ui.size.width - 8, y: 8});
								  }
					});*/

			   default: 
			}
		},

	});
});


/* Save / Load and redraw elements */

/*
 *  draws a VNF element given a VNF object and a (x,y) position in the design window
 */
function drawVnf(vnfObj, vnfPos) {

	// Get the foreign object created inside the svg design window in order to insert the new html div
	var fobj = getDesignWindowSvg().node.firstChild.instance;
	var vnf_id = vnfObj.id;
	var vnfId = parseInt(vnf_id.substring(vnf_id.indexOf("_") + 1));
	var newDiv = document.createElement("div");
	newDiv.id = vnf_id;
	newDiv.style.position = "absolute";
	newDiv.style.width = "108px";
	newDiv.style.height = "54px";
	newDiv.style.left = vnfPos.left;
	newDiv.style.top = vnfPos.top;

	fobj.appendChild(newDiv);

	// Creates a SVG canvas for the VNF graphical element --> inside the html div "vnf_1"	
	var vnfToolSvg = SVG(vnf_id).size('100%', '100%');	
	vnfToolSvg.attr({ id: "vnf_svg_".concat(vnfId), class: "obstacle" });
	vnfToolSvg.fixSubPixelOffset();
	
	var vnfElement = vnfToolSvg.rect(100, 46);
	vnfElement.attr({ id: "vnf_rect_".concat(vnfId), fill: '#9BC2E3', x: 4, y: 4 });
	vnfElement.radius(15);
	vnfElement.stroke({color: '#151e12', opacity: 1.0, width: 2});

	var vnfTitle = "< vnf >";
	if (vnfObj.vnfDesc) {
		vnfTitle = vnfObj.vnfDesc.name;
		vnfTitle = vnfTitle.charAt(0).toUpperCase().concat(vnfTitle.slice(1));
	}
	
	var vnfText = vnfToolSvg.text(vnfTitle).font({ family:   'Helvetica',
													size:     14,
													weight:   'bold',
													leading:  '1.1em'
												}).attr({ x: 10, y: 16 });
	if (vnfObj.vnfDesc) {
		vnfText = vnfText.style('fill', "#000CCC");
	}

	var vnf_svg = document.getElementById("vnf_".concat(vnfId)).getElementsByTagName("svg")[0].instance;
	
	// redraw VNF ports
	vnfRefreshPorts(vnfObj, vnf_id, true);
	
	$("#"+vnf_id).contextmenu({

		delegate: "#vnf_rect_"+vnfId,
		menu: [
				{ title: "Configure VNF", cmd: "edit", uiIcon: "ui-icon-pencil", disabled: !vnfObj.vnfDesc },
				{ title: "Set VNF type", cmd: "set", uiIcon: "ui-icon-pencil" },
				{ title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close" },
		],
		hide: {effect: "fadeOut", duration: 360, delay: 50},
		select: function(event, ui) {
			var menuId = ui.cmd;
			if (menuId == "set") {
				dialog.dialog( "option", "buttons", {Ok: function() {
							ajaxGetVnfData(vnf_id);
							dialog.dialog( "close" );
						},
						Cancel: function() {
							dialog.dialog( "close" );
						}
				});
				dialog.dialog( "open" );
			} else if (menuId == "delete") {
				var vnf = getVnfList()[vnf_id];
				var vnf_links_length = vnf.links.length;
				for (var i = 0; i < vnf_links_length; i++) {
					var link_id = vnf.links[i];
					var lnk = getLinkList()[link_id];
					if (lnk.elem1.id != vnf_id) {
						var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
						elem1Links.splice(elem1Links.indexOf(link_id), 1);
					} else if (lnk.elem2.id != vnf_id) {
						var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
						elem2Links.splice(elem2Links.indexOf(link_id), 1);
					}
					
					delete getLinkList()[link_id];
					$("#"+link_id).remove();
				}
				
				delete getVnfList()[vnf_id];
				$("#"+vnf_id).empty();
			}
			else if (menuId == "edit") {
				var portcounters = openSettingsDialog(vnf_id);
				$("#vnfSettingsPanel").dialog("option", "buttons", { 
						Ok: function(event) {
							$('#vnfSettingForm .submit').click();
							if (document.getElementById('vnfSettingForm').checkValidity() == false)
								return false;
							var counter_array = $("#vnfSettingsPanel").find("input[name=input_number]").get();
							var vnf = getVnfList()[vnf_id];
							for (i = 0; i < counter_array.length; i++) {
								vnf.ports[i].cnt = counter_array[i].valueAsNumber;
							}
							
							counter_array = $("#vnfSettingsPanel").find("input[name=label_colour]").get();
							for (i = 0; i < counter_array.length; i++) {
								vnf.ports[i].colour = counter_array[i].value;
							}
							
							vnfRefreshPorts(getVnfList()[vnf_id], vnf_id);
							dialog_settings.dialog( "close" );
						},
						Cancel: function() {
							dialog_settings.dialog( "close" );
						}
					}
				);
				
				$("#vnfSettingsPanel").dialog( "open" );
			}
		}
	});
		
		
	if (vnfObj.vnfDesc) {
		$( "#".concat(vnf_id)).on( "dblclick", function() {
				
			var portcounters = openSettingsDialog(vnf_id);
			$("#vnfSettingsPanel").dialog("option", "buttons",
				{Ok: function(event) {
					$('#vnfSettingForm .submit').click();
					if (document.getElementById('vnfSettingForm').checkValidity() == false)
						return false;
					var counter_array = $("#vnfSettingsPanel").find("input[name=input_number]").get();
					var vnf = getVnfList()[vnf_id];
					for (i = 0; i < counter_array.length; i++) {
						vnf.ports[i].cnt = counter_array[i].valueAsNumber;
					}
					
					counter_array = $("#vnfSettingsPanel").find("input[name=label_colour]").get();
					for (i = 0; i < counter_array.length; i++) {
						vnf.ports[i].colour = counter_array[i].value;
					}
					
					vnfRefreshPorts(getVnfList()[vnf_id], vnf_id);
					dialog_settings.dialog( "close" );
				},
				Cancel: function() {
					dialog_settings.dialog( "close" );
				}
			});
			
			$("#vnfSettingsPanel").dialog( "open" );
			
		});
	} else {
		$("#vnf_rect_".concat(vnfId)).on("dblclick", function() {
		
			$( "#vnfPanel" ).dialog( "option", "buttons", {
				Ok: function() {
					ajaxGetVnfData(vnf_id);
					dialog.dialog( "close" );
				},
				Cancel: function() {
					dialog.dialog( "close" );
				}
			});
			$('#vnfPanel').dialog( "open" );
			
		});
	}

	$("#vnf").selectmenu({ width: 150 });

	var dragInitialPos;
	var paths = [];
	var destX = [];
	var destY = [];
	$("#vnf_".concat(vnfId)).draggable({
			scroll: false,
			containment: "#content",
			cursor: "move",
			cursorAt: { left: 51, top: 24 },				
			opacity: 0.6,
			snap: true,
			snapMode: "outer",

			start: function(event,ui) {
				var div = document.getElementById(vnf_id);
				dragInitialPos = { x: div.style.left, y: div.style.top };
				
				var elem_array = $( "#".concat(vnf_id) ).find("*").get();
				for (var i = 0; i < elem_array.length; i++) {
					var selector = "#"+elem_array[i].attributes["id"].nodeValue;
					if ($(selector).tooltip( "instance" ) != undefined) {
						$( selector ).tooltip("disable");
					}
				}

				var vnf_elem = getSgElement(this.id, "vnf");
				var paths_array = [];
				
				for (var i = 0; i < vnf_elem.links.length; i++) {
					var link = getLinkList()[vnf_elem.links[i]];
					if (link.elem1.id == this.id) { // this element is the 1st in the link					
						// redraw path
						var x1 = link.path.getSegment(0).coords[0];
						var y1 = link.path.getSegment(0).coords[1];
						var x2 = link.path.getSegment(1).coords[0];
						var y2 = link.path.getSegment(1).coords[1];
						link.path.clear();
						link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
						
						// swap elem1 and elem2
						var el1 = link.elem1;
						link.elem1 = link.elem2;
						link.elem2 = el1;
						
						paths_array[paths_array.length] = link.path;
					} else if (link.elem2.id == this.id) { // this element is the 2nd in the link
						paths_array[paths_array.length] = link.path;
					}
				}
				paths = paths_array;
				for (var i = 0; i < paths.length; i++) {
					var portRect = $("#"+getLinkList()[vnf_elem.links[i]].elem2.port).get()[0];
					destX[i] = portRect.x.baseVal.value + 3;
					destY[i] = portRect.y.baseVal.value + 3;
				}
			},
			drag: function(ui, event) {
				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + destX[i],
								 y: this.offsetTop + destY[i] })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},						
			stop: function(event,ui) {
				var elem_array = $( "#".concat(vnf_id) ).find("*").get();
				for (var i = 0; i < elem_array.length; i++) {
					var selector = "#"+elem_array[i].attributes["id"].nodeValue;
					if ($(selector).tooltip( "instance" ) != undefined) {
						$( selector ).tooltip("enable");
					}
				}

				var list = $("#"+vnf_id).collision(".obstacle");
				if (list.length > 0) {
					for (var j = 0; j < list.length; j++) {
						if (list[j].parentNode.id != vnf_id) {
							var yy = document.getElementById(vnf_id).style;
							yy.left = dragInitialPos.x;
							yy.top = dragInitialPos.y;
							break;
						}
					}
				}

				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + destX[i],
								 y: this.offsetTop + destY[i] })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},
	});
}

/*
 *  Draws a Splitter element given a splitter object and a (x,y) position in the design window
 */
function drawSplitter(splitterObj, splitterPos) {
	// Get the foreign object created inside the svg design window in order to insert the new html div
	var fobj = getDesignWindowSvg().node.firstChild.instance;
	var splittermerger_id = splitterObj.id;
	var splitterMergerId = parseInt(splittermerger_id.substring(splittermerger_id.indexOf("_") + 1));
	
	var newDiv = document.createElement("div");
	newDiv.id = splittermerger_id;
	newDiv.style.position = "absolute";
	newDiv.style.width = "66px";
	newDiv.style.height = "66px";
	newDiv.style.left = splitterPos.left;
	newDiv.style.top = splitterPos.top;
	
	fobj.appendChild(newDiv);

	var splitterToolSvg = SVG('splittermerger_'.concat(splitterMergerId)).size(66, 66);
	splitterToolSvg.attr({ id: "splittermerger_svg_".concat(splitterMergerId), class: "obstacle" });
	splitterToolSvg.fixSubPixelOffset();		

	// Creates the Traffic Splitter element on the design window
	var startx = 4;
	var starty = 4;
	var offset = $("#content").offset();
	var splitterElement = splitterToolSvg.polygon("29,0 58,29 29,58 0,29");
	splitterElement.plot([[29 + startx,0 + starty],[58 + startx,29 + starty],
						  [29 + startx,58 + starty],[0 + startx,29 + starty]]);
	splitterElement.attr({ id: "splittermerger_polygon_"+splitterMergerId, fill: '#9BC2E3', 
						   x: splitterPos.left - offset.left + 1, y: splitterPos.top - offset.top + 1 });
	splitterElement.stroke({ color: '#151e12', opacity: 1.0, width: 2 });
	
	var splittermerger_svg = document.getElementById(splittermerger_id).getElementsByTagName("svg")[0].instance;

	splitterRefreshPorts(splitterObj, splittermerger_id);

	$( "#"+splittermerger_id).on( "dblclick", function() {
					initSplitterSettings(splittermerger_id);
					$( "#splittermergerPanel" ).dialog( "option", "buttons", {Ok: function() {
							$('#splitterSettingForm .submit').click();
							if (document.getElementById('splitterSettingForm').checkValidity() == false)
								return false;
							getSplitterList()[splittermerger_id].num_inout = document.getElementById("splitterInput").valueAsNumber;
							
							splitterRefreshPorts(getSplitterList()[splittermerger_id], splittermerger_id);
							splitter_dialog.dialog( "close" );
						},
						Cancel: function() {
							splitter_dialog.dialog( "close" );
						}});
					
					$('#splittermergerPanel').dialog( "open" );
				
				});
					
	
	$("#"+splittermerger_id).contextmenu({
		delegate: "#splittermerger_polygon_"+splitterMergerId,
		menu: [
				{title: "Configure Splitter", cmd: "edit", uiIcon: "ui-icon-pencil"},
				{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
		],
		
		select: function(event, ui) {
			var menuId = ui.cmd;
			if (menuId == "edit") {
				initSplitterSettings(splittermerger_id);
				$( "#splittermergerPanel" ).dialog( "option", "buttons", {
					Ok: function() {
						$('#splitterSettingForm .submit').click();
						if (document.getElementById('splitterSettingForm').checkValidity() == false)
							return false;
						getSplitterList()[splittermerger_id].num_inout = document
																				 .getElementById("splitterInput")
																				 .valueAsNumber;
					
						splitterRefreshPorts(getSplitterList()[splittermerger_id], splittermerger_id);
						splitter_dialog.dialog( "close" );
					},
					Cancel: function() {
						splitter_dialog.dialog( "close" );
					}
				});
		
				$('#splittermergerPanel').dialog( "open" );
			} else if (menuId == "delete") {
				var splitter = getSplitterList()[splittermerger_id];
				var splitter_links_length = splitter.links.length;
				for (var i = 0; i < splitter_links_length; i++) {
					var link_id = splitter.links[i];
					var lnk = getLinkList()[link_id];
					if (lnk.elem1.id != splittermerger_id) {
						var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
						elem1Links.splice(elem1Links.indexOf(link_id), 1);
					} else if (lnk.elem2.id != splittermerger_id) {
						var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
						elem2Links.splice(elem2Links.indexOf(link_id), 1);
					}
					
					delete getLinkList()[link_id];
					$("#"+link_id).remove();
				}
				
				delete getSplitterList()[splittermerger_id];
				$("#"+splittermerger_id).empty();
			}
		}
	});
	
	$( "#"+splittermerger_id).on( "dblclick", function() {
		initSplitterSettings(splittermerger_id);
		$( "#splittermergerPanel" ).dialog( "option", "buttons", {Ok: function() {
				$('#splitterSettingForm .submit').click();
				if (document.getElementById('splitterSettingForm').checkValidity() == false)
					return false;
				getSplitterList()[splittermerger_id].num_inout = document.getElementById("splitterInput").valueAsNumber;
				
				splitterRefreshPorts(getSplitterList()[splittermerger_id], splittermerger_id);
				splitter_dialog.dialog( "close" );
			},
			Cancel: function() {
				splitter_dialog.dialog( "close" );
			}});
		
		$('#splittermergerPanel').dialog( "open" );
	
	});
		
	$("#splittermerger").selectmenu({ width: 150 });
	
	var dragInitialPos;
	var paths = [];
	var destX = [];
	var destY = [];
	$("#splittermerger_".concat(splitterMergerId)).draggable({
			scroll: false,
			containment: "#content",
			cursor: "move",
			cursorAt: { left: 30, top: 30 },
			opacity: 0.6,
			snap: true,
			snapMode: "outer",
			
			start: function(event, ui) {
				var div = document.getElementById(splittermerger_id);
				dragInitialPos = { x: div.style.left, y: div.style.top };
				
				var elem_array = $( "#".concat(splittermerger_id) ).find("*").get();
				for (var i = 0; i < elem_array.length; i++) {
					var selector = "#"+elem_array[i].attributes["id"].value;
					if ($(selector).tooltip("instance") != undefined) {
						$(selector).tooltip("disable");
					}
				}

				var splitter_elem = getSgElement(this.id, "splittermerger");
				var paths_array = [];
				
				for (var i = 0; i < splitter_elem.links.length; i++) {
					var link = getLinkList()[splitter_elem.links[i]];
					if (link.elem1.id == this.id) { 	// this element is the 1st in the link					
						// redraw path
						var x1 = link.path.getSegment(0).coords[0];
						var y1 = link.path.getSegment(0).coords[1];
						var x2 = link.path.getSegment(1).coords[0];
						var y2 = link.path.getSegment(1).coords[1];
						link.path.clear();
						link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
						
						// swap elem1 and elem2
						var el1 = link.elem1;
						link.elem1 = link.elem2;
						link.elem2 = el1;
						
						paths_array[paths_array.length] = link.path;
					} else if (link.elem2.id == this.id) { 	// this element is the 2nd in the link
						paths_array[paths_array.length] = link.path;
					}
				}
				paths = paths_array;
				for (var i = 0; i < paths.length; i++) {
					var portRect = $("#"+getLinkList()[splitter_elem.links[i]].elem2.port).get()[0];
					destX[i] = portRect.x.baseVal.value + 3;
					destY[i] = portRect.y.baseVal.value + 3;
				}
			},
			drag: function(ui, event) {				
				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + destX[i],
								 y: this.offsetTop + destY[i] })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},						
			stop: function(event, ui) {
				var elem_array = $( "#".concat(splittermerger_id) ).find("*").get();
				for (var i = 0; i < elem_array.length; i++) {
					var selector = "#"+elem_array[i].attributes["id"].value;
					if ($(selector).tooltip("instance") != undefined) {
						$(selector).tooltip("enable");
					}
				}

				var list = $("#"+splittermerger_id).collision(".obstacle");
				if (list.length > 0) {
					for (var j = 0; j < list.length; j++) {
						if (list[j].parentNode.id != splittermerger_id) {
							var yy = document.getElementById(splittermerger_id).style;
							yy.left = dragInitialPos.x;
							yy.top = dragInitialPos.y;
							break;
						}
					}
				}

				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + destX[i],
								 y: this.offsetTop + destY[i] })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},
		});
}

/*
 *  Draws an Endpoint element given an Endpoint object and a (x,y) position in the design window
 */
function drawEndPoint(epObj, epPos) {
	// Get the foreign object created inside the svg design window in order to insert the new html div
	var fobj = getDesignWindowSvg().node.firstChild.instance;
	var endpoint_id = epObj.id;
	var endpointId = parseInt(endpoint_id.substring(endpoint_id.indexOf("_") + 1));

	var newDiv = document.createElement("div");
	newDiv.id = "endpoint_".concat(endpointId);
	newDiv.style.position = "absolute";
	newDiv.style.width = "52px";
	newDiv.style.height = "52px";
	newDiv.style.left = epPos.left;
	newDiv.style.top = epPos.top;

	fobj.appendChild(newDiv);
	$("#"+endpoint_id).position({ at: "center center", of: event, collision:"fit", within: "#content" });

	var endpointToolSvg = SVG('endpoint_'.concat(endpointId)).size(52, 52);	
	endpointToolSvg.attr({id: "endpoint_svg_".concat(endpointId), class: "obstacle" });
	endpointToolSvg.fixSubPixelOffset();				

	// Creates the Endpoint element and show it in the design window
	var endpointElement = endpointToolSvg.rect(40, 40);
	endpointElement.attr({ id: "endpoint_rect_"+endpointId, fill: '#9BC2E3', x: 1, y: 1, class: 'linkable'});
	endpointElement.radius(20);
	endpointElement.stroke({color: '#151e12', opacity: 1.0, width: 2});

	var endpoint_svg = document.getElementById(endpoint_id).getElementsByTagName("svg")[0].instance;
	if (epObj.type != null) {
		var img = endpoint_svg.children()[1];
		endpoint_svg.image(STATIC_URL + "/service_graph/images/"+epObj.type+".png", 16, 16).attr({'x': 35, 'y': 35});
	}

	$("#"+endpoint_id).contextmenu({
		delegate: "#endpoint_rect_"+endpointId,
		menu: [
				{title: "Add link", cmd: "add_link", uiIcon: "ui-icon-arrow-2-e-w"},
				{title: "Change type", cmd: "edit", uiIcon: "ui-icon-pencil"},
				{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
		],
		select: function(event, ui) {
			var menuId = ui.cmd;
			if (menuId == "add_link") {
				addLink(endpoint_id, endpointToolSvg, "endpoint", { x: 20, y: 20 });
			} else if (menuId == "edit") {
				endpoint_dialog.dialog( "option", "buttons", {Ok: function() {
					setEndpointData(endpoint_id);
					endpoint_dialog.dialog( "close" );
				},
				Cancel: function() {
					endpoint_dialog.dialog( "close" );
				}});
				endpoint_dialog.dialog( "open" );
			} else if (menuId == "delete") {
				var ep = getEndPointList()[endpoint_id];
				var ep_links_length = ep.links.length;
				for (var i = 0; i < ep_links_length; i++) {
					var link_id = ep.links[i];
					var lnk = getLinkList()[link_id];
					if (lnk.elem1.id != endpoint_id) {
						var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
						elem1Links.splice(elem1Links.indexOf(link_id), 1);
					} else if (lnk.elem2.id != endpoint_id) {
						var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
						elem2Links.splice(elem2Links.indexOf(link_id), 1);
					}
					
					delete getLinkList()[link_id];
					$("#"+link_id).remove();
				}
									
				delete getEndPointList()[endpoint_id];
				$("#"+endpoint_id).empty();
			}
		}
	});

	$( "#".concat(endpoint_svg)).on( "dblclick", function() {
		
		$( "#endpointPanel" ).dialog( "option", "buttons", {Ok: function() {
				setEndpointData(endpoint_id); 
				endpoint_dialog.dialog( "close" );
			},
			Cancel: function() {
				endpoint_dialog.dialog( "close" );
			}});
		$('#endpointPanel').dialog( "open" );
		
	});
		
	$("#endpoint").selectmenu({ width: 150 });

	var dragInitialPos;
	var paths = [];
	$("#endpoint_"+endpointId).draggable({
			scroll: false,
			containment: "#content",
			cursor: "move",
			cursorAt: { left: 26, top: 26 },
			opacity: 0.6,
			snap: true,
			snapMode: "outer",
			
			start: function(ui, event) {
				var div = document.getElementById(endpoint_id);
				dragInitialPos = { x: div.style.left, y: div.style.top };
				
				var ep = getSgElement("endpoint_"+endpointId, "endpoint");
				var paths_array = [];
				
				for (var i = 0; i < ep.links.length; i++) {
					var link = getLinkList()[ep.links[i]];
					if (link.elem1.id == "endpoint_"+endpointId) { // this element is the 1st in the link					
						// redraw path
						var x1 = link.path.getSegment(0).coords[0];
						var y1 = link.path.getSegment(0).coords[1];
						var x2 = link.path.getSegment(1).coords[0];
						var y2 = link.path.getSegment(1).coords[1];
						link.path.clear();
						link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
						
						// swap elem1 and elem2
						var el1 = link.elem1;
						link.elem1 = link.elem2;
						link.elem2 = el1;
						
						paths_array[paths_array.length] = link.path;
					} else if (link.elem2.id == "endpoint_"+endpointId) { // this element is the 2nd in the link
						paths_array[paths_array.length] = link.path;
					}
				}
				paths = paths_array;
			},
			drag: function(ui, event) {							
				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + 20,
								 y: this.offsetTop + 20 })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},
			stop: function(ui, event) {
				var list = $("#"+endpoint_id).collision(".obstacle");
				if (list.length > 0) {
					for (var j = 0; j < list.length; j++) {
						if (list[j].parentNode.id != endpoint_id) {
							var yy = document.getElementById(endpoint_id).style;
							yy.left = dragInitialPos.x;
							yy.top = dragInitialPos.y;
							break;
						}
					}
				}
				
				var destX = this.offsetLeft + 20;
				var destY = this.offsetTop + 20;
				
				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: destX, y: destY })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},
		});
}

/*
 *  Draws a LAN element given a LAN object and a (x,y) position in the design window
 */
function drawLan(lanObj, lanPos) {
	// Get the foreign object created inside the svg design window in order to insert the new html div
	var fobj = getDesignWindowSvg().node.firstChild.instance;
	var lan_id = lanObj.id;
	var lanId = parseInt(lan_id.substring(lan_id.indexOf("_") + 1));
	
	var newDiv = document.createElement("div");
	newDiv.id = lan_id;
	newDiv.style.position = "absolute";
	newDiv.style.width = "182px";
	newDiv.style.height = "20px";
	newDiv.style.left = lanPos.left;
	newDiv.style.top = lanPos.top;

	fobj.appendChild(newDiv);

	// Creates a canvas for the LAN graphical element --> inside the html div "vnf_1"				
	var lanToolSvg = SVG('lan_'.concat(lanId)).size("100%", "100%");
	lanToolSvg.attr({id: "lan_svg_".concat(lanId), class: "obstacle", x: 0, y: 0 });
	lanToolSvg.fixSubPixelOffset();
	
	// Creates the LAN Network element on the design window
	var lanElementBar = lanToolSvg.rect(164, 4);
	lanElementBar.attr({ fill: '#000000', x: 9, y: 10, class: 'linkable'});
	var lanElementLeft = lanToolSvg.rect(8, 8).radius(4);
	lanElementLeft.attr({ fill: '#000000', x: 1, y: 8});
	var lanElementRight = lanToolSvg.rect(8, 8).radius(4);
	lanElementRight.attr({ fill: '#000000', x: 173, y: 8});

	var lanElement = lanToolSvg.group();	
	lanElement.add(lanElementLeft);
	lanElement.add(lanElementBar);
	lanElement.add(lanElementRight);
	lanElement.size("100%", "100%");	
	
	var lnkStart = {};
	$("#"+lan_id).contextmenu({
		delegate: null,
		menu: [
				{title: "Add link", cmd: "add_link", uiIcon: "ui-icon-arrow-2-e-w"},
				{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
		],
		beforeOpen: function(event, ui) {
			currentElem = event.target;
			while (currentElem.nodeName != "DIV") { 
				currentElem = currentElem.parentNode;
			}
			lnkStart.x = currentElem.offsetLeft + event.offsetX + 17;
			lnkStart.y = currentElem.offsetTop + event.offsetY;
		}, 
		select: function(event, ui) {
			var menuId = ui.cmd;
			if (menuId == "add_link") {
				addLink(lan_id, lanToolSvg, "lan", 
					{ x: lnkStart.x, 
					  y: lnkStart.y });
			} else if (menuId == "delete") {
				var lan = getLANList()[lan_id];
				var lan_links_length = lan.links.length;
				for (var i = 0; i < lan_links_length; i++) {
					var link_id = lan.links[i];
					var lnk = getLinkList()[link_id];
					if (lnk.elem1.id != lan_id) {
						var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
						elem1Links.splice(elem1Links.indexOf(link_id), 1);
					} else if (lnk.elem2.id != lan_id) {
						var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
						elem2Links.splice(elem2Links.indexOf(link_id), 1);
					}
					
					delete getLinkList()[link_id];
					$("#"+link_id).remove();
				}
				
				delete getLANList()[lan_id];
				$("#"+lan_id).empty();
			}
		}
	});
	
	var dragInitialPos;
	var destX = [];
	var destY = this.offsetTop + 11;
	$("#lan_".concat(lanId)).draggable({
			scroll: false,
			containment: "#content",
			cursor: "move",
			cursorAt: { left: 91, top: 10 },
			opacity: 0.6,
			snap: true,
			snapMode: "outer",
			start: function(ui, event) {
				var div = document.getElementById(lan_id);
				dragInitialPos = { x: div.style.left, y: div.style.top };
				
				var lan = getSgElement("lan_"+lanId, "lan");
				var paths_array = [];
				
				for (var i = 0; i < lan.links.length; i++) {
					var link = getLinkList()[lan.links[i]];
					if (link.elem1.id == "lan_"+lanId) { 	// this element is the 1st in the link					
						
						// redraw path
						var x1 = link.path.getSegment(0).coords[0];
						var y1 = link.path.getSegment(0).coords[1];
						var x2 = link.path.getSegment(1).coords[0];
						var y2 = link.path.getSegment(1).coords[1];
						link.path.clear();
						link.path.M({x: x2, y: y2}).L({x: x1, y: y1});
						
						// swap elem1 and elem2
						var el1 = link.elem1;
						link.elem1 = link.elem2;
						link.elem2 = el1;
						
						paths_array[paths_array.length] = link.path;
					} else if (link.elem2.id == "lan_"+lanId) { 	// this element is the 2nd in the link
						paths_array[paths_array.length] = link.path;
					}
				}
				paths = paths_array;
				for (var i = 0; i < paths.length; i++) {
					destX[i] = paths[i].getSegment(1).coords[0] - lanToolSvg.node.parentElement.offsetLeft;
				}
			},
			drag: function(ui, event) {
				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + destX[i], 
								 y: this.offsetTop + 11 })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},
			stop: function(ui, event) {
				var list = $("#"+lan_id).collision(".obstacle");
				if (list.length > 0) {
					for (var j = 0; j < list.length; j++) {
						if (list[j].parentNode.id != lan_id) {
							var yy = document.getElementById(lan_id).style;
							yy.left = dragInitialPos.x;
							yy.top = dragInitialPos.y;
							break;
						}
					}
				}
				
				for (var i = 0; i < paths.length; i++) {
					paths[i].L({ x: this.offsetLeft + destX[i],
								 y: this.offsetTop + 11 })
							.drawAnimated({ delay: 0, duration: 1, easing: "-" });
					paths[i].replaceSegment(1, paths[i].getSegment(2));
					paths[i].removeSegment(2);
				}
			},
		});
}

/*
 *  Draws a Link between two elements given a Link object as a parameter
 */
function drawLink(linkObj) {
	var elem_id = linkObj.elem1.id;
	var elemType = linkObj.elem1.type;
	var elemSvg = document.getElementById(linkObj.elem1.id).firstChild;

	var svg = getDesignWindowSvg();
	var svgOffsetLeft = svg.node.parentElement.offsetLeft;
	var svgOffsetTop = svg.node.parentElement.offsetTop;
	
	var elem_left;
	var elem_top;
	var vnfPort_id;
	var splitterPort_id;
	
	switch (elemType) {
		case "endpoint":
			elem_left = elemSvg.parentNode.offsetLeft + 20;
			elem_top = elemSvg.parentNode.offsetTop + 20;
			break;
		case "lan":
			elem_left = elemSvg.parentNode.offsetLeft + linkObj.elem1.offset;
			elem_top = elemSvg.parentNode.offsetTop + 11;
			break;
		case "vnf":
			vnfPort_id = linkObj.elem1.port;
			vnfPort = document.getElementById(vnfPort_id);
			elem_left = elemSvg.parentNode.offsetLeft + vnfPort.x.baseVal.value + 3;
			elem_top = elemSvg.parentNode.offsetTop + vnfPort.y.baseVal.value + 3;
			break;
		case "splittermerger":
			splitterPort_id = linkObj.elem1.port;
			splitterPort = document.getElementById(splitterPort_id);
			elem_left = elemSvg.parentNode.offsetLeft + splitterPort.x.baseVal.value + 3;
			elem_top = elemSvg.parentNode.offsetTop + splitterPort.y.baseVal.value + 3;
			break;
		default:
	}
	
	var newLink = svg.path().M({ x: elem_left, y: elem_top });
	
	var destElemType = linkObj.elem2.type;
	var destElemId = linkObj.elem2.id;
	var destSvg = document.getElementById(destElemId).firstChild;
	var destX;
	var destY;
	
	switch (destElemType) {
		case "endpoint":
					destX = destSvg.parentElement.offsetLeft + 20;
					destY = destSvg.parentElement.offsetTop + 20;
					break;
		case "lan":
					destX = destSvg.parentElement.offsetLeft + linkObj.elem2.offset;
					destY = destSvg.parentElement.offsetTop + 11;
					break;
		case "vnf":
					var portRect = $("#"+linkObj.elem2.port).get()[0];
					destX = destSvg.parentElement.offsetLeft + portRect.x.baseVal.value + 3;
					destY = destSvg.parentElement.offsetTop + portRect.y.baseVal.value + 3;
					break;
		case "splittermerger":
					var portRect = $("#"+linkObj.elem2.port).get()[0];
					destX = destSvg.parentElement.offsetLeft + portRect.x.baseVal.value + 3;
					destY = destSvg.parentElement.offsetTop + portRect.y.baseVal.value + 3;
					break;
		default:
	}
	
	newLink.L({x: destX, y: destY}).drawAnimated({ delay: 0, duration: 1, easing: "-" });
	
	// add the new path in the sg link data structure
	newLink.attr({ id: linkObj.id });
	getLinkList()[linkObj.id].path = newLink;
	
	// add context menu to the new link
	$("#"+linkObj.id).contextmenu({
		delegate: null,
		menu: [
				{title: "Delete", cmd: "delete", uiIcon: "ui-icon-circle-close"},
		],
		select: function(event, ui) {
			// remove reference to this link from the two element objects
			var lnk = getLinkList()[linkObj.id];
			var elem1Links = getSgElement(lnk.elem1.id, lnk.elem1.type).links;
			elem1Links.splice(elem1Links.indexOf(linkObj.id), 1);
			var elem2Links = getSgElement(lnk.elem2.id, lnk.elem2.type).links;
			elem2Links.splice(elem2Links.indexOf(linkObj.id), 1);
			
			delete getLinkList()[linkObj.id];
			this.remove();
		}
	});
}


/*
 *  Save the SG data structure into a JSON string and start an AJAX request
 *  to write it in a file on the Server side
 */
function saveSG() {
	
	// perform a deep copy of VnfList, SplitterList and LinkList
	var tempVnfList = jQuery.extend(true, {}, getVnfList());
	var tempSplitterList = jQuery.extend(true, {}, getSplitterList());
	var tempLinkList = jQuery.extend(true, {}, getLinkList());


	for (var vnfId in tempVnfList) {
		if (tempVnfList.hasOwnProperty(vnfId)) {
			if (tempVnfList[vnfId].drawedPorts) {
				tempVnfList[vnfId].drawedPorts = [];
			}
		}
	}
	
	for (var splitterId in tempSplitterList) {
		if (tempSplitterList.hasOwnProperty(splitterId)) {
			if (tempSplitterList[splitterId].drawedPorts) {
				if (tempSplitterList[splitterId].drawedPorts) {
					tempSplitterList[splitterId].drawedPorts = [];
				}
			}
		}
	}
	
	for (var linkId in tempLinkList) {
		if (tempLinkList.hasOwnProperty(linkId)) {
			if (tempLinkList[linkId].path) {
				delete tempLinkList[linkId].path;
			}
		}
	}
	
	var positions = {};
	for (var vnfId in tempVnfList) {
		var os = document.getElementById(vnfId).style;
		positions[vnfId] = { left: os.left, top: os.top };
	}
	for (var splitterId in tempSplitterList) {
		var os = document.getElementById(splitterId).style;
		positions[splitterId] = { left: os.left, top: os.top };
	}
	for (var epId in getEndPointList()) {
		var os = document.getElementById(epId).style;
		positions[epId] = { left: os.left, top: os.top };
	}
	for (var lanId in getLANList()) {
		var os = document.getElementById(lanId).style;
		positions[lanId] = { left: os.left, top: os.top };
	}
	
	var SG = { user_id : USER_ID,
			   vnf_list: tempVnfList,
			   splitter_list: tempSplitterList,
			   endpoint_list : getEndPointList(),
			   lan_list : getLANList(),
			   link_list: tempLinkList,
			   position_list: positions,
	};
	var SG_json = JSON.stringify(SG, null, "\t");
	
	/* for example, if we want to save some information in a different JSON file on the server side */
	//var SG__json = JSON.stringify(tempPortList, null, "\t");
	//var SG_links_json = JSON.stringify({ user_id : USER_ID, link_list: tempLinkList });
	
	$.ajax({
		type: "POST",
		url: "ajax_save",  // or just url: "/my-url/path/"
		data: {
		    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		    user_id: USER_ID,
		    servicegraph: SG_json,
		    //sg_links: SG_links_json,
		    //sg_ports: SG_ports_json,
		},
		success: function() {
			alert("Service graph successfully saved");
		},
		error: function() {
		    alert("Please report this error");
		}
    });
    
    $('#savePanel').dialog( "close" );
}

/*
 *  loadSG() clears the previous state of the SG GUI and 
 *  sets it to a new status according to the given data
 *  structure as a parameter.
 */
function loadSG(SG) {
	// remove all graphical elements from the content div
	var paths = $("#content").find("path").get();
	for (var i = 0; i < paths.length; i++) {
		paths[i].remove();
	}
	var divs = $("#content").find("div").get();
	for (var i = 0; i < divs.length; i++) {
		divs[i].remove();
	}
	
	// clear element lists
	for (vnf in getVnfList()) {
		delete getVnfList()[vnf];
	}
	for (splitter in getSplitterList()) {
		delete getSplitterList()[splitter];
	}
	for (ep in getEndPointList()) {
		delete getEndPointList()[ep];
	}
	for (lan in getLANList()) {
		delete getLANList()[lan];
	}
	for (link in getLinkList()) {
		delete getLinkList()[link];
	}
	
	// fill element lists with loaded data and update current IDs
	var newVnfList = jQuery.extend(true, {}, SG.vnf_list);
	var vnfIdCounter = 0;
	for (var vnf in newVnfList) {
		var cnt = parseInt(newVnfList[vnf].id.substring(newVnfList[vnf].id.indexOf("_") + 1));
		if (cnt > vnfIdCounter) {
			vnfIdCounter = cnt;
		}
		getVnfList()[vnf] = newVnfList[vnf];
	}
	while (getCurrentVnfId() < vnfIdCounter) ;
	
	
	var newSplitterList = jQuery.extend(true, {}, SG.splitter_list);
	var splitterIdCounter = 0;
	for (var splitter in newSplitterList) {
		var cnt = parseInt(newSplitterList[splitter].id.substring(newSplitterList[splitter].id.indexOf("_") + 1));
		if (cnt > splitterIdCounter) {
			splitterIdCounter = cnt;
		}
		getSplitterList()[splitter] = newSplitterList[splitter];
	}
	while (getCurrentSplitterMergerId() < splitterIdCounter) ;
	
	
	var newEPList = jQuery.extend(true, {}, SG.endpoint_list);
	var endPointIdCounter = 0;
	for (var ep in newEPList) {
		var cnt = parseInt(newEPList[ep].id.substring(newEPList[ep].id.indexOf("_") + 1));
		if (cnt > endPointIdCounter) {
			endPointIdCounter = cnt;
		}
		getEndPointList()[ep] = newEPList[ep];
	}
	while (getCurrentEndpointId() < endPointIdCounter) ;
	
	
	var newLanList = jQuery.extend(true, {}, SG.lan_list);
	var lanIdCounter = 0;
	for (var lan in newLanList) {
		var cnt = parseInt(newLanList[lan].id.substring(newLanList[lan].id.indexOf("_") + 1));
		if (cnt > lanIdCounter) {
			lanIdCounter = cnt;
		}
		getLANList()[lan] = newLanList[lan];
	}
	while (getCurrentLanId() < lanIdCounter) ;
	
	
	var newLinkList = jQuery.extend(true, {}, SG.link_list);
	var linkIdCounter = 0;
	for (var link in newLinkList) {
		var cnt = parseInt(newLinkList[link].id.substring(newLinkList[link].id.indexOf("_") + 1));
		if (cnt > linkIdCounter) {
			linkIdCounter = cnt;
		}
		getLinkList()[link] = newLinkList[link];
	}
	while (getCurrentLinkId() < linkIdCounter) ;
	
	
	// draw elements
	for (var v in getVnfList()) {
		drawVnf(getVnfList()[v], SG.position_list[v]);
	}
	for (var s in getSplitterList()) {
		drawSplitter(getSplitterList()[s], SG.position_list[s]);
	}
	for (var ep in getEndPointList()) {
		drawEndPoint(getEndPointList()[ep], SG.position_list[ep]);
	}
	for (var lan in getLANList()) {
		drawLan(getLANList()[lan], SG.position_list[lan]);
	}
	for (var link in getLinkList()) {
		drawLink(getLinkList()[link]);
	}
	
	// close the load dialog
	$('#loadPanel').dialog( "close" );
}

/*
 *  Starts an AJAX request to read the JSON string
 *  which is read from a file on the Server side,
 *  then parses it into a js object and calls the 
 *  loadSG() function.
 */
function loadSGAjax() {
	$.ajax({
		type: "POST",
		url: "ajax_load",  // or just url: "/my-url/path/"
		data: {
		    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		    user_id: USER_ID,
		},
		success: function(data) {
		    
		    // parses the JSON string that describes this SG
			var sg = JSON.parse(data);
			loadSG(sg);
		},
		error: function() {
		    alert("No previosly saved SG data files found");
		}
    });
}
