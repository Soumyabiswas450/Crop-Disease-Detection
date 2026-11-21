"""Experimental pixel-level color segmentation for rice-leaf lesion area.

This is a classical OpenCV color heuristic, NOT a trained segmentation model.
It returns pixel counts from the generated masks and must be validated against
expert pixel annotations before being described as agronomically accurate.
"""
import cv2
import numpy as np


def _grabcut_estimate(image_bgr):
    """Return leaf/lesion masks, overlay, and pixel-area statistics.

    Best suited to a single, clearly visible rice leaf against a contrasting
    background. Brown/dark lesion colors are estimated; symptoms with similar
    colors to healthy tissue, shadows, blur, or complex backgrounds can cause
    false positives/negatives.
    """
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Invalid image supplied to segmentation")

    # Work at original resolution for pixel counting; cap very large images
    # only to keep processing responsive, while retaining a consistent mask.
    original_h, original_w = image_bgr.shape[:2]
    max_side = 1600
    scale = min(1.0, max_side / float(max(original_h, original_w)))
    if scale < 1.0:
        work = cv2.resize(image_bgr, (max(1, int(original_w * scale)), max(1, int(original_h * scale))), interpolation=cv2.INTER_AREA)
    else:
        work = image_bgr.copy()

    hsv = cv2.cvtColor(work, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Green/yellow-green pixels are used as leaf foreground seeds.
    green_seed = cv2.inRange(hsv, np.array([20, 28, 25], np.uint8), np.array([100, 255, 255], np.uint8))

    # Brown/tan and dark chromatic pixels are candidate lesions. This is a
    # visual heuristic, not a disease-specific learned segmentation model.
    brown_candidate = ((h <= 24) & (s >= 45) & (v >= 25) & (v <= 235)).astype(np.uint8) * 255
    dark_candidate = ((v <= 62) & (s >= 22)).astype(np.uint8) * 255
    lesion_candidate = cv2.bitwise_or(brown_candidate, dark_candidate)

    # Seed GrabCut from vegetation, not arbitrary dark soil or shadows.
    saturation_floor = int(np.clip(np.percentile(s, 40) * 0.65, 25, 90))
    seed = ((h >= 25) & (h <= 100) & (s >= saturation_floor) & (v >= 35)).astype(np.uint8) * 255
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    k = max(3, int(min(work.shape[:2]) * 0.025) | 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(seed)
    if n <= 1:
        raise ValueError("No clear vegetation seed found. Use one leaf on a contrasting background.")
    core = np.uint8(labels == (1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]))) * 255
    # Fill internal holes so brown lesions can belong to the leaf.
    contours, _ = cv2.findContours(core, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(core, contours, -1, 255, cv2.FILLED)
    near = cv2.dilate(core, kernel, iterations=3)
    sure = cv2.erode(core, kernel_open)
    image_pixels = core.size
    if cv2.countNonZero(core) < max(100, image_pixels * .005) or cv2.countNonZero(near) >= image_pixels * .995 or not cv2.countNonZero(sure):
        raise ValueError("Unreliable leaf/background separation. Retake the image with the entire leaf visible against a contrasting background.")
    gc = np.full(core.shape, cv2.GC_BGD, np.uint8)
    gc[near > 0] = cv2.GC_PR_BGD
    gc[core > 0] = cv2.GC_PR_FGD
    gc[(sure > 0) & (seed > 0)] = cv2.GC_FGD
    if not np.any(gc == cv2.GC_FGD):
        raise ValueError("No confident leaf foreground found.")
    cv2.grabCut(work, gc, None, np.zeros((1,65),np.float64), np.zeros((1,65),np.float64), 4, cv2.GC_INIT_WITH_MASK)
    foreground = np.uint8((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)) * 255
    n, labels, stats, _ = cv2.connectedComponentsWithStats(foreground)
    if n <= 1:
        raise ValueError("Leaf segmentation failed. Try a clearer image.")
    leaf_mask = np.uint8(labels == (1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]))) * 255
    contours, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(leaf_mask, contours, -1, 255, cv2.FILLED)
    leaf_pixels = int(cv2.countNonZero(leaf_mask))
    if not max(100, image_pixels * .005) <= leaf_pixels <= image_pixels * .97:
        raise ValueError("Leaf mask is nearly empty or full. Severity withheld; use a contrasting background.")

    # Restrict candidate lesions to the isolated leaf. Morphology removes tiny
    # isolated specks; connected-component filtering removes single-pixel noise.
    lesion_mask = cv2.bitwise_and(lesion_candidate, leaf_mask)
    lesion_mask = cv2.morphologyEx(lesion_mask, cv2.MORPH_OPEN, kernel_open, iterations=1)
    n, lesion_labels, lesion_stats, _ = cv2.connectedComponentsWithStats(lesion_mask, connectivity=8)
    cleaned = np.zeros_like(lesion_mask)
    min_component = max(4, int(leaf_pixels * 0.00002))
    for idx in range(1, n):
        if lesion_stats[idx, cv2.CC_STAT_AREA] >= min_component:
            cleaned[lesion_labels == idx] = 255
    lesion_mask = cleaned

    lesion_pixels = int(cv2.countNonZero(lesion_mask))
    # The lesion mask is a subset of the leaf mask by construction.
    severity_percent = (lesion_pixels / leaf_pixels) * 100.0 if leaf_pixels else 0.0

    overlay = work.copy()
    red_layer = np.zeros_like(work)
    red_layer[:] = (35, 45, 230)  # red in BGR
    lesion_bool = lesion_mask > 0
    overlay[lesion_bool] = cv2.addWeighted(work, 0.35, red_layer, 0.65, 0)[lesion_bool]

    overlay[leaf_mask == 0] = (24, 24, 24)

    # Resize result visuals to the original dimensions for display.
    if scale < 1.0:
        leaf_mask = cv2.resize(leaf_mask, (original_w, original_h), interpolation=cv2.INTER_NEAREST)
        lesion_mask = cv2.resize(lesion_mask, (original_w, original_h), interpolation=cv2.INTER_NEAREST)
        overlay = cv2.resize(overlay, (original_w, original_h), interpolation=cv2.INTER_LINEAR)

    leaf_pixels = int(cv2.countNonZero(leaf_mask))
    lesion_pixels = int(cv2.countNonZero(lesion_mask))
    severity_percent = 100.0 * lesion_pixels / leaf_pixels

    return {
        "leaf_mask": leaf_mask,
        "lesion_mask": lesion_mask,
        "overlay": overlay,
        "leaf_pixels": leaf_pixels,
        "lesion_pixels": lesion_pixels,
        "severity_percent": round(float(severity_percent), 2),
    }


def estimate_leaf_lesion_pixels(image_bgr):
    try:
        return _grabcut_estimate(image_bgr)
    except (ValueError, cv2.error):
        # Conservative alternative for a distinct vegetation region.
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (25, 35, 40), (95, 255, 255))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError('No usable leaf region')
        leaf = np.zeros_like(mask)
        cv2.drawContours(leaf, [max(contours, key=cv2.contourArea)], -1, 255, cv2.FILLED)
        count = cv2.countNonZero(leaf)
        if not max(100, leaf.size*.02) <= count <= leaf.size*.95:
            raise ValueError('Uncertain leaf boundary')
        h,s,v = cv2.split(hsv)
        lesion = np.uint8((((h<=24)&(s>=45)&(v>=25)&(v<=235))|((v<=62)&(s>=22))) & (leaf>0))*255
        lesion = cv2.morphologyEx(lesion, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        n = cv2.countNonZero(lesion)
        overlay = image_bgr.copy()
        overlay[leaf==0] = (24,24,24)
        overlay[lesion>0] = (35,45,230)
        return dict(leaf_mask=leaf, lesion_mask=lesion, overlay=overlay, leaf_pixels=count, lesion_pixels=n, severity_percent=round(100*n/count,2), method='HSV fallback (low confidence)')
