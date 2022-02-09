import bpy
import bpy_extras 
import copy
import json 

zUpToYUp = bpy_extras.io_utils.axis_conversion(to_forward="-Z", to_up="Y").to_4x4()

def selectObject(obj):
  bpy.ops.object.select_all(action='DESELECT')
  obj.select = True
  bpy.context.scene.objects.active = obj
  
def neat(num):
	return round(num, 5)

def matToJson(mat):
  return [neat(mat[0][0]), neat(mat[0][1]), neat(mat[0][2]), neat(mat[0][3]), neat(mat[1][0]), neat(mat[1][1]), neat(mat[1][2]), neat(mat[1][3]), neat(mat[2][0]), neat(mat[2][1]), neat(mat[2][2]), neat(mat[2][3]), neat(mat[3][0]), neat(mat[3][1]), neat(mat[3][2]), neat(mat[3][3])]

def toYUp(mat):
  return zUpToYUp * mat * zUpToYUp.inverted()

def getBindTransform(b):
  return toYUp(b.matrix_local)

def getInvertedPose(b):
  mat = getBindTransform(b)
  mat = mat.inverted()

  return mat

def getWorldMatrix(obj):
  mat = copy.deepcopy(obj.matrix_world)
  selectObject(obj)
  bpy.ops.object.location_clear()
  bpy.ops.object.rotation_clear()
  bpy.ops.object.scale_clear()
  wm = copy.deepcopy(obj.matrix_world)
  wm = toYUp(wm)
  modelMat = toYUp(mat)
  obj.matrix_world = mat

  return matToJson(modelMat * wm)

armatures = {}
armature = bpy.data.objects['Armature']
boneMap = {}

for b in armature.pose.bones:
  datab = armature.data.bones[b.name]

  bt = getBindTransform(datab)
  ip = getInvertedPose(datab)

  btJson = matToJson(bt)
  ipJson = matToJson(ip)

  if not (b.parent):
    boneMap[b.name] = { "name" : b.name,
                        "matrix_local_inverted" : ipJson,
                        "matrix_local" : btJson }
  else:
    boneMap[b.name] = { "name" : b.name,
                        "matrix_local_inverted" : ipJson,
                        "matrix_local" : btJson ,
                        "parentName" : b.parent.name}

armatures[armature.name] = {  "name" : armature.name,
                              "bones" : boneMap,
                              "matrix_world" : getWorldMatrix(armature) };
                              
with open('/tmp/armatureData.json', 'w') as outfile:
    json.dump(armatures, outfile)