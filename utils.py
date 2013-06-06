import math
import numpy

'''
Code to illustrate my stackoverflow question
on Multilateration of GPS Coordinates.
See: http://stackoverflow.com/questions/8318113
'''

## Some locations:
loc_munich = (48.136944, 11.575278)
loc_ffm = (50.110556, 8.682222)
loc_aa = (50.776667, 6.083611)
loc_zh = (47.379022, 8.541001)
loc_bonn = (50.733992, 7.099814)
loc_plauen = (50.495, 12.138333)
loc_nuernberg = (49.452778, 11.077778)
loc_schweinfurt = (50.045556, 10.231667)
loc_madrid = (40.4125, -3.703889)


def lla_to_ecef(ll):
    ''' Converts the given coordinates in longitue/latitude/height (LLA)
    into ECEF. If only longitude and latitude are provided, a height of
    zero is assumed '''
    a = 6378137
    b = 6356752.31424518
    f = 1./298.257223563
    e = math.sqrt((a*a-b*b)/(a*a))
    ep = math.sqrt((a*a-b*b)/(b*b))
    lat = ll[0]
    lon = ll[1]
    if len(ll)==3:
        h = ll[2]
    else:
        h = 0
    sin_lat = math.sin( math.radians( lat ) )
    cos_lat = math.cos( math.radians( lat ) )
    sin_lon = math.sin( math.radians( lon ) )
    cos_lon = math.cos( math.radians( lon ) )
    N = a/math.sqrt(1-e*e*sin_lat*sin_lat)
    X = (N+h)*cos_lat*cos_lon
    Y = (N+h)*cos_lat*sin_lon
    Z = (((b*b)/(a*a))*N + h) * sin_lat
    return (X,Y,Z)


def ecef_to_lla(ecef):
    ''' Convert coordinates given in ECEF back into LLA'''
    a = 6378137
    b = 6356752.31424518
    f = 1./298.257223563
    e = math.sqrt((a*a-b*b)/(a*a))

    X = ecef[0]
    Y = ecef[1]
    Z = ecef[2]

    p = math.sqrt(X*X+Y*Y)

    lon = math.atan2(Y,X)
    latr = math.atan2(Z, p*(1.-f))
    latg = math.atan2(Z+ e*e*(1.-f)/(1.-e*e) * a * pow(math.sin(latr),3),
        p-e*e*a*pow(math.cos(latr),3))
    for i in range(40):
        latr = math.atan2((1.-f)*math.sin(latg), math.cos(latg))
        latg = math.atan2(Z+ e*e*(1.-f)/(1.-e*e) * a * pow(math.sin(latr),3),
            p-e*e*a*pow(math.cos(latr),3))


    sin_lat = math.sin( math.radians( latg ) )
    cos_lat = math.cos( math.radians( latg ) )
    N = a/math.sqrt(1-e*e*sin_lat*sin_lat)
    h = p*cos_lat+(Z+e*e*N*sin_lat)*sin_lat - N

    return (math.degrees(latg),math.degrees(lon),h)


def lla_distance(a,b):
    ''' Returns the distance between two locations provided
    in LLA in meters '''
    R = 6378137
    dlat = math.radians(a[0]-b[0])
    dlon = math.radians(a[1]-b[1])
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])

    q = pow(math.sin(dlat/2.),2.) + pow(math.sin(dlon/2.),2.)*math.cos(lat1)*math.cos(lat2)
    v = 2.*math.atan2(math.sqrt(q), math.sqrt(1.-q))
    return R*v


def find_zero_height(w):
    ''' Determines the normalization of a homogeneous
    vector in ECEF using primitive secant root finding.
    This is very sensible to a good choice of initial
    x0 and x1 and needs some improvements. '''
    x0 = 1
    x1 = 0.5

    def fx(x):
        ''' This function normalizes the vector with
        weighted with the provided x, converts the
        resulting vector in LLA and returns the altitude
        (which we eventually want to get to zero) '''
        w0 = w/(x*w[3])
        ecef = (float(w0[0]), float(w0[1]), float(w0[2]))
        lla = ecef_to_lla(ecef)
        return lla[2]

    for iter in range(23):
        xn = x1 - fx(x1) * (x1-x0)/(fx(x1)-fx(x0))
        if abs(xn-x1)<0.0000000000001:
            return xn
        x0 = x1
        x1 = xn
    return xn

def multilaterate(locs,dists):
    ''' The core function for multilateration. Given
    a list of locations and corresponding distances to
    an unknown location, which is to be determined. '''
    # 1. convert input to ECEF
    P = [lla_to_ecef(loc) for loc in locs]
    # 2. Build matrix A
    A = []
    for m in range(1,len(locs)):
        Am = 2.*P[m][0]/dists[m] - 2.*P[0][0]/dists[0]
        Bm = 2.*P[m][1]/dists[m] - 2.*P[0][1]/dists[0]
        Cm = 2.*P[m][2]/dists[m] - 2.*P[0][2]/dists[0]
        tm = pow(P[m][0],2) + pow(P[m][1],2) + pow(P[m][2],2)
        t0 = pow(P[0][0],2) + pow(P[0][1],2) + pow(P[0][2],2)
        Dm = dists[m] - dists[0] - tm/dists[m] + t0/dists[0]
        A += [[Am,Bm,Cm,Dm]]
    # 3. Solve using SVD
    A = numpy.array(A)
    (_,_,v) = numpy.linalg.svd(A)
    # Get the minimizer
    w = v[3,:]
    # (Debug) Print the residual error
    print 'Error:', math.sqrt(sum(pow(numpy.dot(A,w),2.)))

    # (Debug) Print the result w/o finding a normalization
    ww = w/w[3]
    q = (float(ww[0]), float(ww[1]), float(ww[2]))
    print 'Initial: ',ecef_to_lla(q)

    # 4. Determine a normalization which minimizes the
    # height.
    norm = find_zero_height(w)
    w /= w[3]*norm

    # Return output
    q = (float(w[0]), float(w[1]), float(w[2]))
    print 'End: ',ecef_to_lla(q)
    lla = ecef_to_lla(q)
    print 'http://maps.google.com/?q=%.8f,%.8f' % lla[:2]
    return lla

def trilaterate(locs, dists):
    ''' Perform trilateration. Nearly copy&paste
    from stackoverflow.com, but using my far more
    accurate LLA<-->ECEF conversions'''
    DistA = dists[0]
    DistB = dists[1]
    DistC = dists[2]

    (xA,yA,zA) = lla_to_ecef(locs[0])
    (xB,yB,zB) = lla_to_ecef(locs[1])
    (xC,yC,zC) = lla_to_ecef(locs[2])

    P1 = numpy.array([xA, yA, zA])
    P2 = numpy.array([xB, yB, zB])
    P3 = numpy.array([xC, yC, zC])

    #from wikipedia
    #transform to get circle 1 at origin
    #transform to get circle 2 on x axis
    ex = (P2 - P1)/(numpy.linalg.norm(P2 - P1))
    i = numpy.dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex)/(numpy.linalg.norm(P3 - P1 - i*ex))
    ez = numpy.cross(ex,ey)
    d = numpy.linalg.norm(P2 - P1)
    j = numpy.dot(ey, P3 - P1)

    #from wikipedia
    #plug and chug using above values
    x = (pow(DistA,2) - pow(DistB,2) + pow(d,2))/(2*d)
    y = ((pow(DistA,2) - pow(DistC,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i*x)/j)

    # make sure that circles are not contained within each other
    # (no solution in that case)
    ss = pow(DistA, 2) - pow(x, 2) - pow(y, 2)
    if ss < 0:
        raise ValueError('circles contained within each other')

    z = math.sqrt(ss)

    #triPt is an array with ECEF x,y,z of trilateration point
    triPt = P1 + x*ex + y*ey + z*ez

    (lat,lon,_) = ecef_to_lla((triPt[0],triPt[1],triPt[2]))
    return (lat,lon,0)


def test_case_1():
    print '------ Test case 1 -----'
    print 'Target ECEF:', lla_to_ecef(loc_zh)

    locs = (loc_aa, loc_schweinfurt, loc_ffm, loc_munich, loc_madrid)
    dists = list()
    for l in locs:
        dists.append( lla_distance(l, loc_zh) )
    ml = multilaterate(locs, dists)
    print 'Actual: ',loc_zh
    print '** Error in m: ',lla_distance(ml,loc_zh)


def test_case_2():
    print '------ Test case 2 -----'
    print 'Target ECEF:', lla_to_ecef(loc_zh)

    locs = (loc_aa, loc_schweinfurt, loc_ffm, loc_munich, loc_plauen, loc_bonn)
    dists = list()
    for l in locs:
        dists.append( lla_distance(l, loc_zh) )
    ml = multilaterate(locs, dists)
    print 'Actual: ',loc_zh
    print '** Error in m: ',lla_distance(ml,loc_zh)

def test_case_3():
    print '------ Test case 3 (reference, trilateration) -----'
    print 'Target ECEF:', lla_to_ecef(loc_zh)

    locs = (loc_aa, loc_schweinfurt, loc_ffm)
    dists = list()
    for l in locs:
        dists.append( lla_distance(l, loc_zh) )
    ml = trilaterate(locs, dists)
    print 'Actual: ',loc_zh
    print '** Error in m: ',lla_distance(ml,loc_zh)


if __name__ == '__main__':
    test_case_1()
    test_case_2()
    test_case_3()

