# -*- coding: utf-8 -*-
import torch
from PIL import Image
from io import BytesIO
from facenet_pytorch import MTCNN
"""
Multi-task Cascaded Convolutional Networks (MTCNN) model for multi-view face
detection. This version is part of facenet-pytorch repository which lecense
permits it's free use.  
"""

class Facenet:
    def __init__(self, logfile):
        # determine if an nvidia GPU is available
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        #create a face detection pipeline using MTCNN
        self.mtcnn = MTCNN(device=device)
        self.threshold = 0.90        
        self.logs = logfile
    
    def detect_face(self, img, img_sizes):
        is_face = False                
        
        img = Image.open(BytesIO(img))
        
        if not self.logs is None:
            self.logs.write(f'PIL converted image to pixel data of size {img.size}. \n')
        
        x_aligned, prob = self.mtcnn(img, return_prob=True)
        if not x_aligned is None:
            if prob >= self.threshold:
                is_face = True
        if prob is None:
            prob = 0
        
        return is_face, prob
