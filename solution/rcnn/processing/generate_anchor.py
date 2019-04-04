"""
Generate base anchors on index 0
"""
from __future__ import print_function
import sys
from builtins import range
import numpy as np
from ..cython.anchors import anchors_cython
from ..config import config


def anchors_plane(feat_h, feat_w, stride, base_anchor):
    return anchors_cython(feat_h, feat_w, stride, base_anchor)

def generate_anchors(base_size=16, ratios=[0.5, 1, 2],
                     scales=2 ** np.arange(3, 6)):
    """
    Generate anchor (reference) windows by enumerating aspect ratios X
    scales wrt a reference (0, 0, 15, 15) window.
    """

    base_anchor = np.array([1, 1, base_size, base_size]) - 1
    ratio_anchors = _ratio_enum(base_anchor, ratios)
    anchors = np.vstack([_scale_enum(ratio_anchors[i, :], scales)
                         for i in range(ratio_anchors.shape[0])])
    return anchors

#def generate_anchors_fpn(base_size=[64,32,16,8,4], ratios=[0.5, 1, 2], scales=8):
#    """
#    Generate anchor (reference) windows by enumerating aspect ratios X
#    scales wrt a reference (0, 0, 15, 15) window.
#    """
#    anchors = []
#    _ratios = ratios.reshape( (len(base_size), -1) )
#    _scales = scales.reshape( (len(base_size), -1) )
#    for i,bs in enumerate(base_size):
#      __ratios = _ratios[i]
#      __scales = _scales[i]
#      #print('anchors_fpn', bs, __ratios, __scales, file=sys.stderr)
#      r = generate_anchors(bs, __ratios, __scales)
#      #print('anchors_fpn', r.shape, file=sys.stderr)
#      anchors.append(r)
#    return anchors

def generate_anchors_fpn():
    #assert(False)
    """
    Generate anchor (reference) windows by enumerating aspect ratios X
    scales wrt a reference (0, 0, 15, 15) window.
    """
    anchors = []
    for k, v in config.RPN_ANCHOR_CFG.items():
    #for k, v in config.RPN_ANCHOR_CFG.iteritems():
      bs = v['BASE_SIZE']
      __ratios = np.array(v['RATIOS'])
      __scales = np.array(v['SCALES'])
      #print('anchors_fpn', bs, __ratios, __scales, file=sys.stderr)
      r = generate_anchors(bs, __ratios, __scales)
      #print('anchors_fpn', r.shape, file=sys.stderr)
      anchors.append(r)
      #print (r)
    anchors=[np.array([[-248., -248.,  263.,  263.],
       [-120., -120.,  135.,  135.]]), np.array([[-56., -56.,  71.,  71.],
       [-24., -24.,  39.,  39.]]), np.array([[-8., -8., 23., 23.],
       [ 0.,  0., 15., 15.]])]
    return anchors

def _whctrs(anchor):
    """
    Return width, height, x center, and y center for an anchor (window).
    """

    w = anchor[2] - anchor[0] + 1
    h = anchor[3] - anchor[1] + 1
    x_ctr = anchor[0] + 0.5 * (w - 1)
    y_ctr = anchor[1] + 0.5 * (h - 1)
    return w, h, x_ctr, y_ctr


def _mkanchors(ws, hs, x_ctr, y_ctr):
    """
    Given a vector of widths (ws) and heights (hs) around a center
    (x_ctr, y_ctr), output a set of anchors (windows).
    """

    ws = ws[:, np.newaxis]
    hs = hs[:, np.newaxis]
    anchors = np.hstack((x_ctr - 0.5 * (ws - 1),
                         y_ctr - 0.5 * (hs - 1),
                         x_ctr + 0.5 * (ws - 1),
                         y_ctr + 0.5 * (hs - 1)))
    return anchors


def _ratio_enum(anchor, ratios):
    """
    Enumerate a set of anchors for each aspect ratio wrt an anchor.
    """

    w, h, x_ctr, y_ctr = _whctrs(anchor)
    size = w * h
    size_ratios = size / ratios
    ws = np.round(np.sqrt(size_ratios))
    hs = np.round(ws * ratios)
    anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
    return anchors


def _scale_enum(anchor, scales):
    """
    Enumerate a set of anchors for each scale wrt an anchor.
    """

    w, h, x_ctr, y_ctr = _whctrs(anchor)
    ws = w * scales
    hs = h * scales
    anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
    return anchors