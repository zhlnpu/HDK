//Mug
union(){
	cylinder(d=100,h=120, center=true);
	translate([50,0,0]){
		rotate([90,0,0]){
			difference(){
				cylinder(d=70,h=10,center=true);
				cylinder(d=50,h=20,center=true);
			}
		}
	}
}