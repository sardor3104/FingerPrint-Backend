import cv2
import numpy as np
import base64
from typing import List, Tuple
from app.core.config import settings

class BiometricService:
    @staticmethod
    def decode_image(image_base64: str) -> np.ndarray:
        """Decode base64 image to OpenCV format."""
        encoded_data = image_base64.split(',')[-1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        return img

    @staticmethod
    def preprocess_fingerprint(image: np.ndarray) -> np.ndarray:
        """Enhance, binarize, and skeletonize the fingerprint image."""
        # 1. Normalize
        normalized = cv2.equalizeHist(image)
        
        # 2. Gaussian Blur to reduce noise
        blurred = cv2.GaussianBlur(normalized, (5, 5), 0)
        
        # 3. Binarize (Adaptive Thresholding)
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # 4. Skeletonize
        skeleton = np.zeros(binary.shape, np.uint8)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        temp_img = binary.copy()
        
        while True:
            eroded = cv2.erode(temp_img, element)
            temp = cv2.dilate(eroded, element)
            temp = cv2.subtract(temp_img, temp)
            skeleton = cv2.bitwise_or(skeleton, temp)
            temp_img = eroded.copy()
            if cv2.countNonZero(temp_img) == 0:
                break
                
        return skeleton

    @staticmethod
    def extract_minutiae(skeleton: np.ndarray) -> List[dict]:
        """Extract ridge endings and bifurcations from skeletonized image."""
        minutiae = []
        rows, cols = skeleton.shape
        
        # Minutiae extraction using Crossing Number (Cn)
        # Cn(P) = 0.5 * sum(|P_i - P_{i+1}|) for i=1..8
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if skeleton[i, j] == 255:
                    # 8-neighborhood
                    p = [
                        skeleton[i-1, j-1], skeleton[i-1, j], skeleton[i-1, j+1],
                        skeleton[i, j+1], skeleton[i+1, j+1], skeleton[i+1, j],
                        skeleton[i+1, j-1], skeleton[i, j-1], skeleton[i-1, j-1]
                    ]
                    # Convert to 0 or 1
                    p = [1 if val == 255 else 0 for val in p]
                    
                    cn = 0.5 * sum(abs(p[k] - p[k+1]) for k in range(8))
                    
                    if cn == 1:
                        # Ridge Ending
                        minutiae.append({"x": j, "y": i, "angle": 0.0, "type": "ending"})
                    elif cn == 3:
                        # Bifurcation
                        minutiae.append({"x": j, "y": i, "angle": 0.0, "type": "bifurcation"})
                        
        return minutiae

    @staticmethod
    def match_minutiae(minutiae1: List[dict], minutiae2: List[dict]) -> Tuple[bool, float]:
        """Match two sets of minutiae using FLANN and return score."""
        if not minutiae1 or not minutiae2:
            return False, 0.0
            
        # Convert minutiae to keypoints and descriptors for FLANN
        # Since we only have coordinates, we'll use them as fake descriptors
        # In a real-world scenario, we'd use SIFT/ORB around the minutiae
        # For this MVP, we match coordinates with tolerance
        
        pts1 = np.array([[m["x"], m["y"]] for m in minutiae1], dtype=np.float32)
        pts2 = np.array([[m["x"], m["y"]] for m in minutiae2], dtype=np.float32)
        
        # Use FLANN for matching
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        
        # We need at least 2 points to match
        if len(pts1) < 2 or len(pts2) < 2:
            return False, 0.0
            
        matches = flann.knnMatch(pts1, pts2, k=min(2, len(pts2)))
        
        # Ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)
        
        # Match score based on percentage of good matches
        score = (len(good_matches) / max(len(pts1), len(pts2))) * 100
        
        return score >= settings.BIOMETRIC_THRESHOLD, score
