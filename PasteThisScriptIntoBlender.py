### DESCRIPTION  ###
#Convert an Image to an into an STL with local height analog to its colors/grayscale. Useful for Stamp making or PCB printing on Resin Printer.

#It is simple but relatively slow. (Runtime Linear to Pixelcount, 1 Face in STL per Pixel!)
#WARNING:Large images will take a long time to compute, blender will be "unresponsive" during the calculation.

#If you want to check the Progress of the calculation go to "Window=>Toggle System Console" in the main menue(top left)
#Works only on specific datatypes such as JPG and PNG.

### IMPORTS ###
import bpy
import numpy as np
from mathutils import Vector

### PARAMETERS ###
useColor="g" #Options: r=Red, g=green, b=blue, g=grayscale, a=Alpha(=Transparency)
invertImage=False # for convinience
exportMeshName="DepthObject" #Name of the exported object.
pixelsPerUnit=10 # Image resolution. In STLs Units are not defined, so chose one you and your slicing software like.
desiredHeight=1 #enter value in the same unit
Offset=0

#Load the image: Option 1:
image_path=r"C:\Users\YourUserNameHere\OneDrive\Desktop\Example.jpg"
image = bpy.data.images.load(image_path)

# Option 2:read the Image in the Blender GUI in the UV Editing Tab, 
# =>creating a blender image object before executing script and call it instead of image path,
# uncomment line below to use this approach. 
#image=bpy.data.objects["Beispielbild"] 


usemodifiers=False # Also select modifiers by uncommenting desired lines in "MODIFIERS" section.


### HELPER FUNCTIONS ###
def img2array(img,**kwargs):
    invertImg=kwargs.get("invert",False)
    w, h = img.size
    pixels = np.empty(w * h *4, dtype=np.float32)
    img.pixels.foreach_get(pixels)
    imgArr=pixels.reshape((h, w, 4))#w,h swapped, because row, column!=x,y
    if invertImg:
        imgArr=1-imgArr
    return imgArr

def extractGray(arr):
    rgb=arr[:,:,:3]
    gray=np.sum(rgb,axis=2)/3
    return gray

def extractColor(arr,color):
    colors={"r":0,"g":1,"b":2,"a":3}
    if colors.get(color):
        return arr[:,:,colors.get(color)]
    else:
        return extractGray(arr)  


def printProgress(idx,total):    
    percentage=round(idx/total*100)
    lastPercentage=round((idx-1)/total*100)
    if (not percentage%10) and lastPercentage!=percentage:
        print(f"{percentage} % done")
        
def makeSurf(imgarr,**kwargs): # main function
    res=kwargs.get("res",1)
    zscale=kwargs.get("zscale",1)
    offset=kwargs.get("offset",0)
    name=kwargs.get("name","Surface")
    print("Creating Vertecies (1/3)")
    verts=createVerts(imgarr,res,zscale,offset)
    print("Creating Faces (2/3)")        
    faces=createFaces(imgarr) 
    print("Adding Mesh Object (3/3")        
    makeObjFromMeshdata(name,verts,[],faces)
    
def createVerts(imgarr,res,zscale,offset):
    verts=[]
    w,h=imgarr.shape    
    for idx in range(w):
        for idy in range(h):    
            verts.append(Vector([idx*res,idy*res,zscale*imgarr[idx,idy]+offset]))
        printProgress(idx,w)
    return verts    

def createFaces(imgarr):
    faces=[]
    w,h=imgarr.shape   
    for idx in range(w-1):
        for idy in range(h-1):
            faces.append([(idx)*h+idy,(idx)*h+idy+1,(idx+1)*h+idy+1,(idx+1)*h+idy])
        printProgress(idx,w-1) 
    return faces    
        
def makeObjFromMeshdata(name,verts,edges,faces):       
    mesh = bpy.data.meshes.new(name)  # add the new mesh
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections.get("Collection")
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)

### MAIN PROGRAMM ###
if __name__=="__main__":
    a=img2array(image,invert=invertImage)
    colorarr=extractColor(a,useColor)
    makeSurf(colorarr,name=exportMeshName,zscale=desiredHeight,res=1/pixelsPerUnit,offset=Offset)


### MODIFIERS ###
    if usemodifiers:
        pass
        #print("Using Modifiers")
        #bpy.ops.object.modifier_add(type='DECIMATE')
        #bpy.context.object.modifiers["Decimate"].decimate_type = 'UNSUBDIV'
        #bpy.context.object.modifiers["Decimate"].iterations = 1
        #bpy.ops.object.modifier_apply(modifier="Decimate")

        #bpy.ops.object.modifier_add(type='CORRECTIVE_SMOOTH')
        #bpy.context.object.modifiers["CorrectiveSmooth"].use_only_smooth = True
        #bpy.context.object.modifiers["CorrectiveSmooth"].iterations = 12
        #bpy.context.object.modifiers["CorrectiveSmooth"].factor = 0.9
        #bpy.ops.object.modifier_apply(modifier="CorrectiveSmooth")

        #bpy.ops.object.modifier_add(type='TRIANGULATE')
        #bpy.ops.object.modifier_apply(modifier="Triangulate")

        #bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        #bpy.context.object.modifiers["Decimate"].angle_limit = 0.1



        #bpy.ops.object.modifier_add(type='SOLIDIFY')
        #bpy.context.object.modifiers["Solidify"].thickness = zscale*1.2
        #bpy.ops.object.modifier_apply(modifier="Solidify")

