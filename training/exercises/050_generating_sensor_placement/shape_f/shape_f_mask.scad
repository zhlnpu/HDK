// trackable shape
module obsHandle(width=30, length=100, facets=5)
{
	translate([0,0,-length])
		cylinder(r1=width, r2=width, h=length, $fn=facets);
}

handleLength=200;
handleWidth=30;
obsHandle(width=handleWidth, length=handleLength);
