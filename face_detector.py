# -*- coding: utf-8 -*-
import torch
from facenet_pytorch import MTCNN
"""
Multi-task Cascaded Convolutional Networks (MTCNN) model for multi-view face
detection. This version is part of facenet-pytorch repository which lecense
permits it's free use.  
"""

class Facenet:
    def __init__(self):
        # determine if an nvidia GPU is available
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        #create a face detection pipeline using MTCNN
        self.mtcnn = MTCNN(device=device)
        self.threshold = 0.8
    
    def detect_face(self, img, img_sizes):
        is_face = False                
        # Get cropped and prewhitened image tensor
        x_aligned, prob = self.mtcnn.detect(img, return_prob=True)
        if not x_aligned is None:
            if prob >= self.threshold:
                is_face = True
        
        return is_face
