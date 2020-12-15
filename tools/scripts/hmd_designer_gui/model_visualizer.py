__author__ = 'douglasbr'
import json
import math
import numpy
import os

class model_visualizer():

    def visualizeModel(self, modelFile = "", objectFiles = [], outputFile = ""):
        #import the jason file
        with open(modelFile) as model_file:
            model = json.load(model_file)

        #must print double back slashes in .scad file, so all the backslashes need to be doubled
        stlFiles = []
        for object in objectFiles:
            stlScadFileName = '"' + os.path.basename(str(object)) + '"'
            stlScale = 1000
            with open(object) as stl_file:
                for line in stl_file:
                    line = line.strip(' \t')
                    elements = line.split(' ')
                    if elements[0] != 'vertex':
                        continue
                    else:
                        for element in elements:
                            try:
                                if abs(float(element)) >= 1:
                                    stlScale = 1
                            except ValueError:
                                continue
                        #print elements
            stlFiles.append([stlScadFileName, stlScale])
            #print object

        #for stl in stlFiles:
        #   print stl

        map = []
        normals = []
        positions = []
        if 'lighthouse_config' in model:
            normals = model['lighthouse_config']['modelNormals']
            positions = model['lighthouse_config']['modelPoints']
            map = model['lighthouse_config']['channelMap']
        else:
            normals = model['modelNormals']
            positions = model['modelPoints']
            if 'channelMap' in model:
                map = model['channelMap']
            else:
                map = [""] * len(normals)

        position_angle_axis = []
        if len(normals) != 0:
            #create x,y unit vectors
            i = 0
            for normal in normals:
                #normalize the x,y vector to a unit vector
                hyp = math.sqrt(math.pow(normal[0],2) + math.pow(normal[1],2))
                xy_unit = [1,0,0]
                if hyp != 0:
                    xy_unit = [normal[0]/hyp,normal[1]/hyp,0]

                #create the ortogonal vector to the x,y vector (the axis of rotation)
                axis = [xy_unit[1], -1*xy_unit[0],0]

                #compute the angle of rotation
                rotation = -1 * 360* (math.acos(normal[2])/(2*math.pi))
                position_angle_axis.append([positions[i], rotation, axis, str(map[i])])
                #print (normal)
                #print ([rotation, axis])
                i = i + 1

        # Override file for testing
        # model['imu'] = {
        # 	"plus_z" : [-1,0,0],
        # 	"plus_x" : [0,0,1],
        # 	"position" : [0,0,0]
        #     }

        imu_rotation = []
        if 'imu' in model:
            plus_z = model['imu']['plus_z']
            plus_x = model['imu']['plus_x']
            x_axis = [1,0,0]
            z_axis = [0,0,1]

            #find the axis of rotation unit vector
            hyp = math.sqrt(math.pow(plus_z[0],2) + math.pow(plus_z[1],2))
            xy_unit = [0,1,0]
            if hyp != 0:
                xy_unit = [plus_z[0]/hyp,plus_z[1]/hyp,0]

            ##create the ortogonal vector to the x,y vector (the axis of rotation)
            axis_rotation = [xy_unit[1], -1 * xy_unit[0],0]

            #find the angle between x-axis and axis of rotation
            alpha = 360* (math.acos(numpy.dot(axis_rotation, x_axis))/(2*math.pi))
            #print ('alpha = ' + str(alpha))
            #find the sign of the angle by verifying the cross product is the z axis
            cross = numpy.cross(axis_rotation, x_axis)
            #print ('cross_alpha = ' + str(cross))
            sign_alpha = numpy.dot(cross, z_axis)
            if sign_alpha >= 0:
                sign_alpha = 1
            else:
                sign_alpha = -1

            #print ('sign_alpha = ' + str(sign_alpha))

            #compute the rotaion about the axis of rotation
            theta = -1 * 360* (math.acos(plus_z[2])/(2*math.pi))
            #print ('theta = ' + str(theta))

            #find angle between axis of rotation and plus_x
            beta = 360* (math.acos(numpy.dot(axis_rotation, plus_x))/(2*math.pi))
            #print ('beta = ' + str(beta))
            #find the sign of the angle by verifying that the cross product is the plus_z vector
            cross = numpy.cross(axis_rotation, plus_x)
            #print ('cross_beta = ' + str(cross))
            sign_beta = numpy.dot(cross, plus_z)
            if sign_beta >= 0:
                sign_beta = 1
            else:
                sign_beta = -1
            #print ('sign_beta = ' + str(sign_beta))

            #encode the two rotations for openscad
            ##rotate around z by alpha
            imu_rotation.append([-1 * sign_alpha * alpha, z_axis])
            ##rotate around axis of rotation by theta
            imu_rotation.append([theta, axis_rotation])
            ##rotate around new z by beta
            imu_rotation.append([sign_beta * beta, plus_z])

        #dump the new scad file
        output_scad = open(outputFile, 'w')

        output_scad.write('include <shapes.scad>;\n')
        output_scad.write('\n')

        output_scad.write('objects = [\n')
        for stl in stlFiles:
            output_scad.write('\t[')
            output_scad.write(str(stl[0]))
            output_scad.write(',')
            output_scad.write(str(stl[1]))
            output_scad.write('],\n')
        output_scad.write('];\n')
        output_scad.write('\n')

        if 'imu' in model:
            output_scad.write('imu_rotations = [\n')
            for i in range(len(imu_rotation)):
                output_scad.write('\t' + str(imu_rotation[i]))
                if i < (len(imu_rotation) - 1):
                    output_scad.write(',')
                output_scad.write('\n')
            output_scad.write('];\n')
            output_scad.write('\n')

            output_scad.write('imu_translation = ')
            output_scad.write(str(model['imu']['position']))
            output_scad.write(';\n')
            output_scad.write('\n')

        output_scad.write('sensors = [\n')
        for i in range(len(position_angle_axis)):
            outputText = '[' + str(position_angle_axis[i][0]) + ',' + str(position_angle_axis[i][1]) + ',' + str(position_angle_axis[i][2]) + ',\"' + position_angle_axis[i][3] + '\"]'
            #output_scad.write('\t' + str(position_angle_axis[i]))
            output_scad.write('\t' + outputText)
            if i < (len(position_angle_axis) - 1):
                output_scad.write(',')
            output_scad.write('\n')
        output_scad.write('];\n')
        output_scad.write('\n')

        output_scad.write('model_objects();\n')
        output_scad.write('model_sensors();\n')
        if 'imu' in model:
            output_scad.write('model_imu();\n')

        output_scad.close()

