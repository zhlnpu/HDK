use <writescad/Write.scad>

$fn = 40;

module model_objects() {
	for (obj = objects)
		scale([obj[1], obj[1], obj[1]]) {
			%import(obj[0], convexity = 4);
	}
}

module model_sensors() {
	scale([1000, 1000, 1000])
		constellation();
}

module model_imu() {
	scale([1000, 1000, 1000])
	translate(imu_translation)
	rotate(imu_rotations[2][0], imu_rotations[2][1])
	rotate(imu_rotations[1][0], imu_rotations[1][1])
	rotate(imu_rotations[0][0], imu_rotations[0][1])
		imu();
}

module constellation() {
	for(s = sensors)
		translate(s[0])
			rotate(s[1], s[2])
				sensor(s[3]);
}

module sensor(text) {
	union(){
		color("black")
		translate([0,0,0.0005])
		write(text, t=.0001, h=.0025, center=true, font="letters.dxf");
		color("lime")
		cylinder(r = 0.0025, h = 0.0005, center=false);
		color("red")
		translate([0,0,-.0005])
		cylinder(r = 0.0025, h = 0.0005, center=false);
		color("black")
		translate([-.0007, -.0018, 0])
		cube([.0014, .0002, .00055], center=false);
	}
}

module imu() {
	union(){
		color("deepskyblue")
		translate([0,0,.00075])
		cube([.003, .003, 0.0005], center=true);
		color("red")
		translate([0,0,.00025])
		cube([.003, .003, 0.0005], center=true);
		color("black")
		translate([-.001, .001, .0001])
		cylinder(r = .00025, h = .001, center=false);
		color("black")
		translate([0,-.00005,.0001])
		cube([.0014,.0001,.001], center=false);
	}

}


