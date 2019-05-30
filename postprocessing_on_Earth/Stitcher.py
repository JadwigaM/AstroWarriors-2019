#   AstroWarriors   Team (Jaslo, Poland)

#==========================================================================
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

class MyStitcher:
   def __init__(self):
      # determine if we are using OpenCV v3.X
      self.isv3 = imutils.is_cv3()
      print(self.isv3)
      self.homography = None

   def getHomography(self):
      return self.homography

   def stitch(self, images, ratio=0.75, reprojThresh=4.0,
      showMatches=False):
      # unpack the images, then detect keypoints and extract
      # local invariant descriptors from them
      
      (imageB, imageA) = images
      
      (kpsA, featuresA) = self.detectAndDescribe(imageA)
      (kpsB, featuresB) = self.detectAndDescribe(imageB)
      
      # match features between the two images
      M = self.matchKeypoints(kpsA, kpsB,
      featuresA, featuresB, ratio, reprojThresh)
      
      # if the match is None, then there aren't enough matched
      # keypoints to create a panorama
      if M is None:
         return None
      
      # otherwise, apply a perspective warp to stitch the images
      # together
      (matches, H, status) = M
      self.homography = H
      result = cv2.warpPerspective(imageA, H,
      (imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
      result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB
      
      # check to see if the keypoint matches should be visualized
      if showMatches:
         vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches,
         status)
         # return a tuple of the stitched image and the
         # visualization
         return (result, vis)
      
      # return the stitched image
      return result

   def detectAndDescribe(self, image):
      # convert the image to grayscale
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      # detect keypoints in the image
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      detector = cv2.AKAZE_create()
      (kps, descs) = detector.detectAndCompute(gray, None)
      features = descs
      return (kps, features)
   

   def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh):
                #compute the raw matches and initialize the list of actual matches
                #matches = flann.knnMatch(descs1,descs2,k=2)
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
                search_params = dict(checks = 50)
                bf = cv2.BFMatcher(cv2.NORM_HAMMING)
                matches = bf.knnMatch(featuresA,featuresB, k=2)    # typo fixed
                # store all the good matches as per Lowe's ratio test.
                good = []
                #usuniete 25 05 2019
                #matcher = cv2.DescriptorMatcher_create("BruteForce")
                #rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
                #loop over the raw matches
                for m,n in matches:
                        if m.distance < 0.7*n.distance:
                                good.append(m)
                                #for m in rawMatches:
                #if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                #matches.append((m[0].trainIdx, m[0].queryIdx))
                #computing a homography requires at least 4 matches
                if len(matches) > 4:
                        # construct the two sets of points
                        ptsA = np.float32([ kpsA[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                        ptsB = np.float32([ kpsB[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                        #ptsA = np.float32([kpsA[i] for (_, i) in matches])
                        #ptsB = np.float32([kpsB[i] for (i, _) in matches])
                        # compute the homography between the two sets of points
                        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)
                        
      # return the matches along with the homograpy matrix
      # and status of each matched point
                return (matches, H, status)

      # otherwise, no homograpy could be computed
                return None
   def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
      im3 = cv2.drawMatchesKnn(imageA, kpsA, imageB, kpsB, matches[1:20], None, flags=2)
      # initialize the output visualization image
      (hA, wA) = imageA.shape[:2]
      (hB, wB) = imageB.shape[:2]
      vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
      vis[0:hA, 0:wA] = imageA
      vis[0:hB, wA:] = imageB
      #im3 = cv2.drawMatchesKnn(imageA, kpsA, imageB, kpsB, good[1:20], None, flags=2)

      return vis
