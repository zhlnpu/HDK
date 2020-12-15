import rhinoscriptsyntax as rs
import json, os

"""
Version 0.1.1
11/20/17
"""

def equalWithAbsError(x1, x2, e = 1e-5):
    return bool( abs(x1 - x2) <= e )

def equalWithAbsErrorVec(x1, x2, e = 1e-5):
    return all((equalWithAbsError(c1, c2, e) for c1,c2 in zip(x1,x2)))

def GetSensorPosAndNormal( centerPoint, lineVerts):
    assert( len(lineVerts) == 2 )
    if equalWithAbsErrorVec(centerPoint, lineVerts[0]):
        return centerPoint,rs.VectorUnitize( lineVerts[1] - lineVerts[0] )
    elif equalWithAbsErrorVec(centerPoint, lineVerts[1]):
        return centerPoint,rs.VectorUnitize( lineVerts[0] - lineVerts[1] )
    else:
        return None,None

def ExportLighthouseSensorsToJSON(filename):
    print "Writing",filename
    
    #objectIds = rs.GetObjects("Select Sensors",rs.filter.curves,True,True)
    #if( objectIds==None ): return3
    
    # Find all circle and all lines in scene
    circles = []
    lines = []
    for obj in rs.AllObjects():
        # Skip hidden objects, and invisible layers
        # TODO: Recuse up layet hierarchy?
        if rs.IsObjectHidden(obj):
            continue
        layer = rs.ObjectLayer(obj)
        if layer and not rs.IsLayerVisible(layer):
            continue
        
        if rs.IsCurve(obj):
            if rs.IsCircle(obj):
                circles.append((obj, rs.CircleCenterPoint(obj)))
            elif rs.IsLine(obj):
                verts = rs.PolylineVertices(obj)
                if len(verts) == 2:
                    lines.append((obj, verts))
    
    print 'found',len(circles),'sensor candidates (circles) in scene'
    print 'found',len(lines),'sensor candidates (normals) in scene'
    
    modelJSON = {'modelNormals':[], 'modelPoints' : []}
    
    # TODO: Better sort order? Perhaps based on winding around origin?
    for circleObj, circleCenter in reversed(circles):
        for line, lineVerts in lines:
            pos, normal = GetSensorPosAndNormal( circleCenter, lineVerts )
            if pos is None:
                continue
            else:
                modelJSON['modelNormals'].append( [ float(x) for x in normal ] )
                modelJSON['modelPoints'].append( [ float(x) / 1000.0 for x in pos ] )
                break
    modelJSON['channelMap'] = range(len(modelJSON['modelNormals']))
    
    print "Extracted",len(modelJSON['channelMap']),"sensors"
    
    if len(modelJSON['modelNormals']) > 0:
        outputFile = file(filename, 'w')
        jsonText = json.dumps(modelJSON, indent=4, sort_keys=True)
        outputFile.write(jsonText)
        outputFile.close()
        
        print "Wrote",filename
    else:
        print "Error: No sensors found in scene"

def ExportDialog():
    filter = "(JSON Files)|*.json|All Files (*.*)|*.*||"
    filename = rs.SaveFileName("Save JSON Sensors...", filter)
    return filename


if( __name__ == "__main__" ):
    filename = ExportDialog()
    if filename:
        ExportLighthouseSensorsToJSON(filename)