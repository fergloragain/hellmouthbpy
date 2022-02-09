import bpy
import bpy_extras
import json
import collections

zUpToYUp3 = bpy_extras.io_utils.axis_conversion(to_forward="-Z", to_up="Y").to_3x3()

def toYUp3(vec):
  return zUpToYUp3 * vec;

def neat(num):
	return round(num, 5)

vertex_data = {}

# get the currently selected object
obj = bpy.context.active_object

# get the mesh data belonging to that object (selected object should be a mesh)
mesh = obj.data

uvCoords = collections.defaultdict(list)
indices = []

# get the starting index count for new indices
newIndex = len(mesh.vertices)

# get the uv map, the exporter expects all textures to use the same uv map
uvMap = mesh.uv_layers[0].data


# loop over the individual polygons in the mesh
for poly in mesh.polygons:

  # loop over the vertices that make up this polygon
  for loopIndex in poly.loop_indices:

    # get the uv coordinates for the current uv vertex
    uvCoordinates = [neat(uvMap[loopIndex].uv.x), neat(uvMap[loopIndex].uv.y)]

    # get the vertex data for the current loop index
    v = mesh.loops[loopIndex]

    vertexIndex = v.vertex_index

    # vertex = mesh.vertices[vertex_loop_data.vertex_index]

    # vertex_list = uv_coords[vertex.index]

    # calculate the skin for this vertex
    skin = {}
    totalWeight = 0
    for group in mesh.vertices[vertexIndex].groups:
      skin[bpy.data.objects["Cube"].vertex_groups[group.group].name] = neat(group.weight)
      totalWeight = totalWeight + neat(group.weight)

    vertexList = uvCoords[vertexIndex]

    found=False

    if (len(vertexList) > 0):

      # iterate over the list of vertices
      for vertex in vertexList:

        # if the uv coordinates match, we don't need to create a new vertex
        if(neat(vertex["uvs"][0]) == neat(uvCoordinates[0]) and neat(vertex["uvs"][1]) == neat(uvCoordinates[1])):

          # append the vertex index to the list of indices
          indices.append(vertex["index"])

          # set the found flag so we don't create a new vertex
          found=True

          # stop processing the list of vertices
          break

      # if we didn't find a vertex with matching uv coordinates
      if (not found):

        # create a new vertex with the associated vertex data
        vertex = mesh.vertices[vertexIndex]

        vco = toYUp3(vertex.co)

        uvCoords[vertexIndex].append({
          "index" : newIndex,
          "xyz" : [neat(vco.x), neat(vco.y), neat(vco.z)],
          "uvs" : uvCoordinates,
          "totalWeight" : neat(totalWeight),
          "skin": skin})

        indices.append(newIndex)

        # increment the new index
        newIndex += 1

    else:

      # first time encountering this vertex
      vertex = mesh.vertices[vertexIndex]

      vco = toYUp3(vertex.co)

      uvCoords[vertexIndex].append({
        "index" : vertex.index,
        "xyz" : [neat(vco.x), neat(vco.y), neat(vco.z)],
        "uvs" : uvCoordinates,
        "totalWeight" : neat(totalWeight),
        "skin": skin})

      indices.append(vertexIndex)

coords = {}
for idx in uvCoords:
  vList = uvCoords[idx]
  for vertex in vList:
    coords[vertex["index"]] = vertex

crds = []
for idx in coords:
  crds.append(coords[idx])

crds.sort(key=lambda x: x["index"], reverse=False)

vertex_data[mesh.name] = {"coordinates": crds, "indices": indices }

with open('/tmp/vertexData.json', 'w') as outfile:
    json.dump(vertex_data, outfile)
