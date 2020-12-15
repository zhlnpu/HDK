// trackable shape
module sensMace (width=100, midHeight=30, outerHeight=50, plateau=30, facets=5)
{
	//positive space
	translate([0,0,outerHeight])
		cylinder(r1=width, r2=width, h=midHeight,center=false, $fn=facets);
	translate ([0,0,midHeight+outerHeight])
		cylinder(r1=width, r2=plateau, h=outerHeight, center=false, $fn=facets);
	cylinder(r1=plateau, r2=width, h=outerHeight, center=false, $fn=facets);
	
	//negative space
	
	//subtract
}

module obsHandle(width=30, length=100, facets=5)
{
	translate([0,0,-length])
		cylinder(r1=width, r2=width, h=length, $fn=facets);
}

handleLength=200;
handleWidth=30;
sensMace(plateau=handleWidth);
