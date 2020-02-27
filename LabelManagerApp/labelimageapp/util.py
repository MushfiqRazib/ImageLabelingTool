# file: util.py
# author: name <email>
# date: 05-21-2019
# this util file will be used by labelimagecontroller package i.e. other modules will be using it's implemented methods.
'''
- string manipulation
- datetime conversion to string
- all kinds of utility function related to labeling.
'''

import sys, os
import datetime
import decimal
from settings import Configuration_Settings

from utility.loggingfile import Log

logger = Log().logging.getLogger(__name__)


class Utility(object):
    def __init__(self):
        self.configuration_obj = Configuration_Settings()

    # create image_web_url link
    def get_web_url(self, image_dir, subdir, image_uuid, image_ext):
        if self.configuration_obj.WEB_SERVER_HTTPS != False:
            #image_web_url = 'https://' + self.configuration_obj.WEB_SERVER_HOST + '/' + os.path.join(image_dir,subdir).replace("\\","/") + '/?image=' + image_uuid + '.' + image_ext
            image_web_url = 'https://' + self.configuration_obj.WEB_SERVER_HOST + os.path.join(image_dir,subdir).replace("\\","/") + '/?image=' + image_uuid + '.' + image_ext
        else:
            logger.warning('Using http instead of https! This might be a security risk!')
            #image_web_url = 'http://' + self.configuration_obj.WEB_SERVER_HOST + '/' + os.path.join(image_dir,subdir).replace("\\","/") + '/' + image_uuid + '.' + image_ext
            image_web_url = 'http://' + self.configuration_obj.WEB_SERVER_HOST + os.path.join(image_dir,subdir).replace("\\","/") + '/' + image_uuid + '.' + image_ext
        return image_web_url

    # create image dir path.
    def get_image_dir(self, image_path, subdir):
        image_dir = os.path.join(image_path,subdir,'')
        return image_dir
        
    #encode an image into an RLE format        
    def rle_encode (self,img):
        #The image input is a 2D numpy array consisting of 1's and 0's 
        #It's flatten, then encoded to rle based on the number of repeated 1's and 0's 
        
        rle=np.array([], dtype=np.int)
        flat_img = img.flatten()
        flat_img = np.where(flat_img > 0.5, 1, 0).astype(np.uint8)
            
        rle=np.array([], dtype=np.int)
        flat_img = img.flatten()
        flat_img = np.where(flat_img > 0.5, 1, 0).astype(np.uint8)

        starts = np.array((flat_img[:-1] == 0) & (flat_img[1:] == 1))
        ends = np.array((flat_img[:-1] == 1) & (flat_img[1:] == 0))
        starts_ix = np.where(starts)[0] + 2
        ends_ix = np.where(ends)[0] + 2
        lengths = ends_ix - starts_ix
        for i in range(len(lengths)):
            rle=np.append(rle,starts_ix[i]-np.sum(rle)-1)
            rle=np.append(rle,lengths[i])
            if (i==len(lengths)-1):
                rle=np.append(rle,len(img.flatten())-np.sum(rle))
                
        return (rle)

    #A linear array of RLE converts to an image based on 1's and 0's 
    #The input should be the RLE array and the image(to obtain its height and width)
    def rle_decode(self,rle,img):
        width, height = len(img[:,0]), len(img[0,:])
        pixels=np.array([],dtype=np.int)
    
        for i in range(len(rle)):

            if (i%2==0):
                pixels=np.append(pixels,(np.repeat(0,rle[i])))

            elif (i%2==1):
                pixels=np.append(pixels,(np.repeat(1,rle[i])))
                
        pixels=pixels.reshape(width, -height)

        return (pixels)
    





