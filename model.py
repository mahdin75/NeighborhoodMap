import numpy as np
from osgeo import gdal_array
from PIL import Image
import os

class Model:
    "main model"
    
    def __init__(self,image,land_uses,out_dir,*args,**kwargs):
        self.image_path = image
        self.land_uses = land_uses
        self.pixel_size = kwargs['pixel_size']
        self.max_effect_size = kwargs['max_effect_size']
        self.out_dir = out_dir
        self.laod_image()
        
    land_uses = None
    image_path = None
    image = None
    image_arr = None
    pixel_size = 200
    max_effect_size = 800
    out_dir = ''
    
    def plot_enrichment_factor(self,land_use1,land_use2):
        land_use2.image = self.image_arr
        land_use2.num_of_rings = int(self.max_effect_size/self.pixel_size)
        
        land_use1.image = self.image_arr
        
        target_landuse_index = np.asarray(np.where(self.image_arr==land_use2.value)).T
        
        local_density = {}
        for index in target_landuse_index:
            rings = land_use2.get_rings()
            rk = [k for k in rings.keys()]
            rk.reverse()
            for ring_key in rk:
                num_of_landuse1 = 0
                num_of_valid_cells = 0
                ring = rings[ring_key]
                for cell_index in ring:
                    if land_use2.validate_extent(index[0]+cell_index[0],index[1]+cell_index[1]):
                        if land_use2.image[index[0]+cell_index[0]][index[1]+cell_index[1]] == land_use1.value:
                            num_of_landuse1 += 1
                        num_of_valid_cells += 1
                if ring_key in local_density.keys():
                    local_density[ring_key].append(num_of_landuse1/num_of_valid_cells)
                else:
                    local_density[ring_key] = [num_of_landuse1/num_of_valid_cells]
        
        global_density = np.count_nonzero((land_use1.image==1)*1)/np.count_nonzero(land_use1.image)
        
        efs = [np.mean(local_density[ldk])/global_density for ldk in local_density.keys()]
        efs = [f if f!=0 else 0.0001 for f in efs]
        
        land_use2.append_efs(efs)
    
        dist = np.linspace(self.pixel_size, self.max_effect_size , num=land_use2.num_of_rings)
        
        print(dist,np.log(efs))
    
    def plot_neighborhood_map(self,target_land_use):
        N = np.zeros(self.image_arr.shape)
        for i in range(self.image_arr.shape[0]):
            for j in range(self.image_arr.shape[1]):
                su = 0
                rings = target_land_use.get_rings()
                rk = [k for k in rings.keys()]
                rk.reverse()
                for ring_key in rk:
                    for cell_index in rings[ring_key]:
                        if target_land_use.validate_extent(i+cell_index[0],j+cell_index[1]):
                            if(self.image_arr[i+cell_index[0]][j+cell_index[1]] in [l.value for l in self.land_uses]):
                                lui = [l.value for l in self.land_uses].index(self.image_arr[i+cell_index[0]][j+cell_index[1]])-1
                                ringi = ring_key-1
                                su += target_land_use.efs[lui][ringi]
                N[i,j] = su
        NN = N/np.linalg.norm(N)
        print(NN)
        im = Image.fromarray(NN)
        im.save(os.path.join(self.out_dir,target_land_use.name+'.tif'))
    
    def laod_image(self):
        self.image = gdal_array.LoadFile(self.image_path)
        self.image_arr = np.array(self.image)
