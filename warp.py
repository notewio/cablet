# warping / calibration stuff, ported from johnny lee's wiimote 4 point calibration system
# see here: http://johnnylee.net/projects/wii/

def squareToQuad(x0, y0,
                 x1, y1,
                 x2, y2,
                 x3, y3):

    dx1, dy1 = x1 - x2, y1 - y2
    dx2, dy2 = x3 - x2, y3 - y2
    sx = x0 - x1 + x2 - x3
    sy = y0 - y1 + y2 - y3
    g = (sx * dy2 - dx2 * sy) / (dx1 * dy2 - dx2 * dy1)
    h = (dx1 * sy - sx * dy1) / (dx1 * dy2 - dx2 * dy1)
    a = x1 - x0 + g * x1
    b = x3 - x0 + h * x3
    c = x0
    d = y1 - y0 + g * y1
    e = y3 - y0 + h * y3
    f = y0

    return [
            a, d, 0, g,
            b, e, 0, h,
            0, 0, 1, 0,
            c, f, 0, 1
        ]

def quadToSquare(x0, y0,
                 x1, y1,
                 x2, y2,
                 x3, y3):

    mat = squareToQuad(x0,y0,x1,y1,x2,y2,x3,y3)

    a, d,    g = mat[ 0], mat[ 1],          mat[ 3]
    b, e,    h = mat[ 4], mat[ 5],          mat[ 7]
    c, f       = mat[12], mat[13]

    A =     e - f * h
    B = c * h - b
    C = b * f - c * e
    D = f * g - d
    E =     a - c * g
    F = c * d - a * f
    G = d * h - e * g
    H = b * g - a * h
    I = a * e - b * d

    idet = 1.0 / (a * A           + b * D           + c * G);

    return [
            A*idet, D*idet, 0, G*idet,
            B*idet, E*idet, 0, H*idet,
            0,      0,      1, 0,
            C*idet, F*idet, 0, I*idet
        ]

def multMats(srcMat, dstMat):
    res = [0] * len(srcMat)
    for r in range(4):
        ri = r * 4;
        for c in range(4):
            res[ri + c] = (srcMat[ri    ] * dstMat[c     ] +
                           srcMat[ri + 1] * dstMat[c +  4] +
                           srcMat[ri + 2] * dstMat[c +  8] +
                           srcMat[ri + 3] * dstMat[c + 12])
    return res

def computeWarp(src, dst):
    srcMat = quadToSquare(*src)
    dstMat = squareToQuad(*dst)
    return multMats(srcMat, dstMat)

def warp(mat, x, y):
    result = [
        x*mat[0] + y*mat[4] + mat[12],
        x*mat[1] + y*mat[5] + mat[13],
        #x*mat[2] + y*mat[6] + mat[14],     # Not needed
        x*mat[3] + y*mat[7] + mat[15],
    ]
    return (result[0] / result[2], result[1] / result[2])
