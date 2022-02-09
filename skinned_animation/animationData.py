import bpy 
import bpy_extras
import json 
import collections

original_frame = bpy.context.scene.frame_current

zUpToYUp = bpy_extras.io_utils.axis_conversion(to_forward="-Z", to_up="Y").to_4x4()

def neat(num):
	return round(num, 5)

def toYUp(mat):
  return zUpToYUp * mat * zUpToYUp.inverted()

def matToJson(mat):
  return [neat(mat[0][0]), neat(mat[0][1]), neat(mat[0][2]), neat(mat[0][3]), neat(mat[1][0]), neat(mat[1][1]), neat(mat[1][2]), neat(mat[1][3]), neat(mat[2][0]), neat(mat[2][1]), neat(mat[2][2]), neat(mat[2][3]), neat(mat[3][0]), neat(mat[3][1]), neat(mat[3][2]), neat(mat[3][3])]

original_frame = bpy.context.scene.frame_current

meshName = "Cube"

armature = bpy.context.scene.objects["Armature"]
animation = bpy.data.actions['ArmatureAction']

keyframes = {}
boneKeyFrames = {}

visitedBones = set()

# loop over the animation fcurves; effectively the animated elements within this animation, which in this case, will be a bone
for curve in animation.fcurves:
  # curve.data_path looks like "pose.bones["Bone"].rotation_quaternion", and we want to get the "pose.bones["Bone"]", which we retrieve with rpartition on a period '.', and capturing the first element on the returned array
  pose_bone_path = curve.data_path.rpartition('.')[0]
  pose_bone = armature.path_resolve(pose_bone_path)
  boneName = pose_bone.name

  # if we've seen this bone before, skip to the next fcurve
  if boneName in visitedBones:
      continue
  else:
      visitedBones.add(boneName)

  # loop over the keyframes of the animation
  for keyframe in curve.keyframe_points:
    frame = round(keyframe.co.x)
    # update the scene's current frame to the keyframe from this iteration
    bpy.context.scene.frame_set(frame)
    # fetch the bone from the armature
    bone = armature.pose.bones[boneName]
    # convert the bone's basis matrix to a Y-up matrix
    boneMatrix = toYUp(bone.matrix_basis)
    # convert the matrix to JSON
    boneMatrixJSON = matToJson(boneMatrix)
    boneKeyFrames.setdefault(animation.name, {}).setdefault(boneName, {}).setdefault(frame, {})
    # update the dict of matrices for [animation][bone][frame]
    boneKeyFrames[animation.name][boneName][frame] = boneMatrixJSON

# set the bone keyframes on the keyframes dict for the current mesh name
keyframes[meshName] = boneKeyFrames

# restore the current frame within the scene back to the original frame
bpy.context.scene.frame_set(original_frame)

with open('/tmp/animationData.json', 'w') as outfile:
    json.dump(keyframes, outfile)