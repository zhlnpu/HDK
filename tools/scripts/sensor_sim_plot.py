import sys
import math
import os.path
import argparse
import traceback

from numpy.core.numeric import * # imports empty
from matplotlib.pyplot import *  # imports figure
import matplotlib.pyplot as plt  # defines plt

#
# Sensor simulation dump format is:
#
#     yawAngle, pitchAngle, distanceFromBase, maximumIncidenceAngle,
#     num visible points, visible sensor extent in basestation x, y, z,
#     trials with a pose, trials with no pose, rotation err, translation err,
#     list of visible sensors
#

def ParseSensorSimLine( L ):
    p = L.split()
    d = {}
    d["yawAngle"] = 0.1 * round( 10.0 * math.degrees( float( p[0] ) ) )
    d["pitchAngle"] = 0.1 * round( 10.0 * math.degrees( float(p[1]) ) )
    d["distance"] = float(p[2])
    d["maxIncidence"] = float(p[3])
    d["numVisible"] = int(p[4])
    d["extentX"] = float(p[5])
    d["extentY"] = float(p[6])
    d["extentZ"] = float(p[7])
    d["gotPose"] = int(p[8])
    d["noPose"] = int(p[9])
    d["rotErr"] = math.degrees( float( p[10] ) )
    d["transErr"] = float(p[11])

    remainingSensors = len(p[12:])

    if d["numVisible"] == remainingSensors:
        d["unifiedErr"] = None
        d["visibleSensors"] = [ int(i) for i in p[12:] ]
    else:
        d["unifiedErr"] = float(p[12])
        d["visibleSensors"] = [ int(i) for i in p[13:] ]

    return d

def ReadSensorSimFile( filename ):
    simData = []
    for L in open( filename, "rb" ):
        simData.append( ParseSensorSimLine( L ) )
    return simData

def AnglesFromSimData( simData ):
    yawAngles = {}
    pitchAngles = {}
    for d in simData:
        yawAngles[ d[ "yawAngle" ] ] = 1
        pitchAngles[ d[ "pitchAngle" ] ] = 1
    return ( sorted( yawAngles.keys() ), sorted( pitchAngles.keys() ) )

def FindClosest( targetAngle, angleList ):
    aList = [ -9999.0 ] + angleList + [ 9999.0 ]
    for ( i, a ) in enumerate( aList ):
        if a > targetAngle:
            break
    diffLow = abs( aList[i-1] - targetAngle )
    diffHigh = abs( aList[i] - targetAngle )
    if diffLow < diffHigh:
        return i-2
    else:
        return i-1

def PrintPoseSummary( d ):

    if len( d[ "visibleSensors" ] ) != 0:
        print "    Saw %d sensors:" % ( d[ "numVisible" ], ),
        for s in d[ "visibleSensors" ]:
            print "  %d" % ( s, ),
        print
    else:
        print "    Saw %d sensors." % ( d[ "numVisible" ], )
    print "    Pose failure:  %.2f%%" % ( 100.0 * d["noPose"] / float ( d["gotPose"] + d["noPose"] ) )
    print "    RMS rotation error:  %.2f" % ( d["rotErr"] )
    print "    RMS translation error:  %.4f" % ( d["transErr"] )
    #print "X/Y/Z extent of visible sensors is ( %f %f %f ) millimeters" % ( d["extentX"]*1000, d["extentY"]*1000, d["extentZ"]*1000 )

class GraphClicker:
    def __init__( self, yawAngles, pitchAngles, simData ):
        self.yawAngles = yawAngles
        self.pitchAngles = pitchAngles
        self.simData = simData
    def __call__( self, event ):
        if event.xdata != None and event.ydata != None:
            yawIdx = FindClosest( event.xdata, self.yawAngles )
            pitchIdx = FindClosest( event.ydata, self.pitchAngles )
            print
            d = self.simData[ yawIdx * len(self.pitchAngles) + pitchIdx ]
            print "Clicked at %f, %f on yaw/pitch of ( %f , %f ):" % ( event.xdata, event.ydata, d["yawAngle"] - 180.0, d["pitchAngle"] )
            PrintPoseSummary( d )

def Axes( p, yawAngles, pitchAngles ):
    p.xlabel( "Yaw Angle" )
    p.xticks( arange( round(min(yawAngles)), round(max(yawAngles))+0.0001, 45.0 ) )
    p.ylabel( "Pitch Angle" )
    p.yticks( arange( round(min(pitchAngles)), round(max(pitchAngles))+0.0001, 30.0 ) )

def PlotSensorSim( simData, outputFilename, batch, bounds, diffData=None ):
    ( yawAngles, pitchAngles ) = AnglesFromSimData( simData )
    if not yawAngles or not pitchAngles:
        raise RuntimeError("No yaw Angles")

    simDataDict = {}
    for d in simData:
        simDataDict[ ( d["yawAngle"], d["pitchAngle"] ) ] = d

    yawAngles = [ a - 180.0 for a in yawAngles ]
    pitchAngles = [ a for a in pitchAngles ]

    nYaw = len( yawAngles )
    nPitch = len( pitchAngles )

    deltaAngle = yawAngles[1] - yawAngles[0]

    print "\tRead in data for %d x %d headset poses." % ( nYaw, nPitch )
    print "\tYaw range %.1f to %.1f, Pitch range %.1f to %.1f." % ( min(yawAngles), max(yawAngles), min(pitchAngles), max(pitchAngles) )
    print "\tSample angle resolution %.1f degrees." % ( deltaAngle, )

    graphExtent = [ min(yawAngles) - deltaAngle / 2.0, max(yawAngles) + deltaAngle / 2.0, min(pitchAngles) - deltaAngle / 2.0, max(pitchAngles) + deltaAngle / 2.0 ]

    poseChars = []
    errs = []

    for d in simData:
        poseSuccessFrac = 0.0
        poseAttempts = d["gotPose"] + d["noPose"]
        if poseAttempts != 0:
            poseSuccessFrac = float( d["gotPose"] ) / float( poseAttempts )
        minExtent = min( d["extentX"], min( d["extentY"], d["extentZ"] ) )
        poseFailurePercent = 100.0 * ( 1.0 - poseSuccessFrac )
        poseChars.append( ( d["numVisible"], minExtent, poseFailurePercent ) )
        if poseFailurePercent < 90.0:
            rotErr = min( d["rotErr"], bounds.rotErr[1] )
            transErr = min( d["transErr"], bounds.transErr[1] )
            errs.append( ( rotErr, transErr ) )
        else:
            errs.append( ( 9999.0, 9999.0 ) )

    diffErrs = []
    if diffData:
        for d,d2 in zip(simData, diffData):
            poseSuccessFrac = 0.0
            poseAttempts = d["gotPose"] + d["noPose"]
            if poseAttempts != 0:
                poseSuccessFrac = float( d["gotPose"] ) / float( poseAttempts )
            minExtent = min( d["extentX"], min( d["extentY"], d["extentZ"] ) )
            poseFailurePercent = 100.0 * ( 1.0 - poseSuccessFrac )
            poseChars.append( ( d["numVisible"], minExtent, poseFailurePercent ) )

            if "rotErr" in d and "rotErr" in d2:
                rotErr = d["rotErr"] - d2["rotErr"]
                transErr = d["transErr"] - d2["transErr"]
                diffErrs.append( ( rotErr, transErr ) )
            elif "rotErr" in d2 :
                diffErrs.append( ( -9999.0, -9999.0 ) )
            else:
                diffErrs.append( ( 9999.0, 9999.0 ) )
    
    numVisibleArray = empty( [ nPitch, nYaw ] )
    minExtentArray = empty( [ nPitch, nYaw ] )
    poseFailureArray = empty( [ nPitch, nYaw ] )
    rotErrorArray = empty( [ nPitch, nYaw ] )
    transErrorArray = empty( [ nPitch, nYaw ] )
    rotErrorDiffArray = empty( [ nPitch, nYaw ] )
    transErrorDiffArray = empty( [ nPitch, nYaw ] )

    for i in range( nYaw ):
        for j in range( nPitch ):
            numVisibleArray[j,i] = poseChars[ i * nPitch + j ][0]
            minExtentArray[j,i] = poseChars[ i * nPitch + j ][1]
            poseFailureArray[j,i] = poseChars[ i * nPitch + j ][2]
            rotErrorArray[j,i] = errs[ i * nPitch + j ][0]
            transErrorArray[j,i] = errs[ i * nPitch + j ][1]

            if diffData:
                rotErrorDiffArray[j,i] = diffErrs[ i * nPitch + j ][0]
                transErrorDiffArray[j,i] = diffErrs[ i * nPitch + j ][1]

    if diffData:
        fig = figure( figsize = ( 30, 10 ) )
    else:
        fig = figure( figsize = ( 20, 10 ) )

    plt.subplots_adjust( left = 0.05, right = 0.95, bottom = 0.05, top = 0.95 )

    if diffData:
        subplot( 2, 3, 1 )
    else:
        subplot( 2, 2, 1 )
    title( "Number of Visible Sensors" )
    plt.imshow( numVisibleArray, vmin = bounds.visibleSensors[0], vmax = bounds.visibleSensors[1], extent = graphExtent, 
        interpolation = "nearest", origin = "lower", cmap = matplotlib.cm.get_cmap('jet_r') )
    Axes( plt, yawAngles, pitchAngles )
    plt.colorbar()

    if diffData:
        subplot( 2, 3, 2 )
    else:
        subplot( 2, 2, 2 )
    title( "Pose Rotation Error" )
    plt.imshow( rotErrorArray, vmin = bounds.rotErr[0], vmax = bounds.rotErr[1], extent = graphExtent, 
        interpolation = "nearest", origin = "lower", cmap = matplotlib.cm.get_cmap('jet') )
    Axes( plt, yawAngles, pitchAngles )
    plt.colorbar()

    if diffData:
        subplot( 2, 3, 3 )
        title( "Rotation Error vs. Reference" )
        plt.imshow( rotErrorDiffArray, vmin = bounds.diffRotErr[0], vmax = bounds.diffRotErr[1], extent = graphExtent, 
            interpolation = "nearest", origin = "lower", cmap = matplotlib.cm.get_cmap('seismic') )
        Axes( plt, yawAngles, pitchAngles )
        plt.colorbar()

    if diffData:
        subplot( 2, 3, 4 )
    else:
        subplot( 2, 2, 3 )
    title( "Initial Pose Possible?" )
    plt.imshow( poseFailureArray, vmin = bounds.failurePercentage[0], vmax = bounds.failurePercentage[1], extent = graphExtent, 
        interpolation = "nearest", origin = "lower", cmap = matplotlib.cm.get_cmap('jet') )
    Axes( plt, yawAngles, pitchAngles )
    plt.colorbar()

    if diffData:
        subplot( 2, 3, 5 )
    else:
        subplot( 2, 2, 4 )
    title( "Pose Translation Error")
    plt.imshow( transErrorArray, vmin = bounds.transErr[0], vmax = bounds.transErr[1], extent = graphExtent, 
        interpolation = "nearest", origin = "lower", cmap = matplotlib.cm.get_cmap('jet') )
    Axes( plt, yawAngles, pitchAngles )
    plt.colorbar()

    if diffData:
        subplot( 2, 3, 6 )
        title( "Translation Error vs. Reference" )
        plt.imshow( transErrorDiffArray, vmin = bounds.diffTransErr[0], vmax = bounds.diffTransErr[1], extent = graphExtent, 
            interpolation = "nearest", origin = "lower", cmap = matplotlib.cm.get_cmap('seismic') )
        Axes( plt, yawAngles, pitchAngles )
        plt.colorbar()

    if outputFilename:
        savefig( outputFilename, transparent = False, facecolor = (0.7,0.7,0.7) )

    if not batch:
        gclicker = GraphClicker( yawAngles, pitchAngles, simData )
        cid = fig.canvas.mpl_connect( 'button_press_event', gclicker )
        show()

def main():
    parser = argparse.ArgumentParser( prefix_chars = '-/' )
    parser.add_argument( "filename_or_directory", help = "sensor placement simulation data filename. Point at a directory to batch process all matching files." )
    parser.add_argument( "/tightbounds", action = "store_true", help = "plot with tighter error bounds for more detail" )
    parser.add_argument( "/classicbounds", action = "store_true", help = "plot with classic error bounds (for less detail), original default" )
    parser.add_argument( "/batch", action = "store_true", help = "batch mode. Point at a filename (or a directory)" )
    parser.add_argument( "/diff", nargs=1, action = "store", help = "diff against a reference result.txt" )
    args = parser.parse_args()

    if args.tightbounds and args.classicbounds:
        print "Cannot specify both /tightbounds and /classicbounds" 
        return

    if args.tightbounds:
        print "/tightbounds argument deprecated. (matches default)"

    tightBounds = (not args.classicbounds)
    computeDiff = (args.diff and args.diff[0])

    class Bounds(object): pass

    bounds = Bounds()

    bounds.visibleSensors = (0, 6)
    if tightBounds:
        bounds.failurePercentage = (0.0, 5.0)
        bounds.rotErr = (0.0, 1.5)
        bounds.transErr = (0.0, 0.010)
        bounds.diffRotErr = (-0.75, 0.75)
        bounds.diffTransErr = (-0.005, 0.005)
    else:
        bounds.failurePercentage = (0.0, 100.0)
        bounds.rotErr = (0.0, 5.0)
        bounds.transErr = (0.0, 0.030)
        bounds.diffRotErr = (-2.5, 2.5)
        bounds.diffTransErr = (-0.015, 0.015)

    def GetDiffReference(diffSimData = {}):
        if not computeDiff:
            return None
        if args.diff[0] in diffSimData:
            return diffSimData[args.diff[0]]
        print "Loading reference result",args.diff[0]
        diffSimData[args.diff[0]] = ReadSensorSimFile( args.diff[0] )
        return diffSimData[args.diff[0]]

    if os.path.isdir(args.filename_or_directory):
        print 'Processing directory',args.filename_or_directory
        for rootname, dirname, files in os.walk(args.filename_or_directory):
            for filename in files:
                fullpath = os.path.join( rootname, filename)
                if os.path.getsize(fullpath) == 0:
                    print 'skipping',fullpath,'(empty file)'
                    continue
                basename, extension = os.path.splitext( fullpath )
                outputFilename =  basename + '.png'

                if os.path.exists(outputFilename):
                    continue

                try:
                    simData = ReadSensorSimFile( fullpath )
                except KeyboardInterrupt:
                    return
                except:
                    #traceback.print_exc()
                    continue

                if not simData:
                    print 'skipping',fullpath,': no parsed sim data'
                    continue
                else:
                    print 'Loaded',fullpath

                try:
                    PlotSensorSim( simData, outputFilename, True, bounds, GetDiffReference() )
                except Exception,e:
                    print "Exception plotting:",e
                    traceback.print_exc()
                if not os.path.exists(outputFilename):
                    print 'failed on',outputFilename
                else:
                    print '+',outputFilename,'...'

    else:
        simData = ReadSensorSimFile( args.filename_or_directory )
        basename, extension = os.path.splitext( args.filename_or_directory )
        outputFilename =  basename + '.png'
        print 'Output will be saved to %s' % ( outputFilename, )
        PlotSensorSim( simData, outputFilename, args.batch, bounds, GetDiffReference() )

if __name__ == "__main__":
    main()
