module new_object() {
	translate ([0, 0, -1])
		color("orange") import("ventriloquist_handle_vr_graphic (REV-02).stl", convexity = 4);
	color("orange") import("ventriloquist_hmd_vr_graphic (REV-02).stl", convexity = 4);
}
new_object();

module thor() {
	union() {
		difference(){
		color("orange")
		translate([0, 0, -65/2])
			cube([250,170,65], center=true);
		color("blue")
		translate([0, 0, -20])
			cube([200, 120, 50], center=true);
			}
	handle();
	}
}
	
!thor();

module handle() {
	union() {
		translate([0,8,-50])
			scale([1,.65,1])
				cylinder(r=25, h=186, $fn=6);
		translate([0,20,12])
			cube([25,10,15], center=true);
		scale([1, 1.4,1])
		translate([8,0,23])
			rotate([0, 270, 0])
				cylinder(r=20, h=16, $fn=3);
	
	
	}
}
