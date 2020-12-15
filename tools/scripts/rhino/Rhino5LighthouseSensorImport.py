import rhinoscriptsyntax as rs
import json, os, random

"""
Version 0.1.1
11/20/17

"""

# Construct an arbitrary, orthogonal vector
def Orthogonal( vecIn ):
    vecIn = rs.VectorUnitize( vecIn )
    
    # Pick any vector which isn't aligned to the input
    otherVec = rs.coerce3dvector( (1.0, 0.0, 0.0) )
    if abs(rs.VectorDotProduct(vecIn, otherVec )) > 0.99:
        otherVec = rs.coerce3dvector( (0.0, 1.0, 0.0) )
    
    # Create a unit length orthogonal to both the other one, and the original one
    return rs.VectorUnitize( rs.VectorCrossProduct( vecIn, otherVec ) );

def RandomSaturatedColor():
    color = [ 255, 0, random.randint(0,255) ]
    random.shuffle(color)
    return color

def ImportLighthouseSensorsFromJSON(filename):
    print "Reading",filename
    contents = file(filename).read()
    if "{" not in contents:
        raise Exception("Malformed JSON")
    header = contents[0:contents.find('{')]
    print header
    
    try:
        layername = os.path.splitext(os.path.basename(filename))[0].lower()
    except:
        layername = "sensors"
    
    jsonstr = contents[contents.find('{'):]
    data = json.loads(jsonstr)
    
    originalLayer = rs.CurrentLayer()
    layername = rs.AddLayer(layername)
    rs.CurrentLayer(layername)
    rs.LayerColor(layername, RandomSaturatedColor())
    
    groupName = rs.AddGroup(layername)
    
    SENSOR_RADIUS_MM = 3.0
    SENSOR_NORMAL_LENGTH_MM = 8.0
    
    for point, normal in zip(data['modelPoints'], data['modelNormals']):
        position = rs.coerce3dvector( [x * 1000.0 for x in point] )
        normal = rs.VectorUnitize( normal )
        normalOrthoA = Orthogonal( normal )
        normalOrthoB = rs.VectorCrossProduct( normalOrthoA, normal )
        
        objID = rs.AddCircle3Pt(position + SENSOR_RADIUS_MM * normalOrthoA,
            position - SENSOR_RADIUS_MM * normalOrthoA,
            position + SENSOR_RADIUS_MM * normalOrthoB)
        rs.AddObjectToGroup(objID, groupName)
       
        objID = rs.AddLine( position, position + SENSOR_NORMAL_LENGTH_MM * normal )
        rs.AddObjectToGroup(objID, groupName)
    
    rs.CurrentLayer(originalLayer)

def ImportDialog():
    filter = "(JSON Files)|*.json|All Files (*.*)|*.*||"
    filename = rs.OpenFileName("Open JSON File", filter)
    return filename

if( __name__ == "__main__" ):
    filename = ImportDialog()
    if filename:
        ImportLighthouseSensorsFromJSON(filename)