

Node.prototype.removeChildren = function() {
	if ( this.hasChildNodes() ) {
	    while ( this.childNodes.length >= 1 ) {
	        this.removeChild( this.firstChild );       
	    } 
	}
}

Node.prototype.reverseChildren = function() {
	var kids = this.childNodes;
	var numkids = kids.length;
	for(var i = numkids-1; i >= 0; i--) {
		this.appendChild(this.removeChild(kids[i]));
	}
}
