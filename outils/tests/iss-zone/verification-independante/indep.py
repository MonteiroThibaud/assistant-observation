# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Thibaud Monteiro
# Calcul INDÉPENDANT des transits de l'ISS (sgp4 de Vallado en Python, éphémérides intégrées d'astropy) pour contrôler l'application.
import numpy as np, math
from astropy.time import Time
from astropy.coordinates import get_body, solar_system_ephemeris, TEME
from astropy.utils import iers
import astropy.units as u
iers.conf.auto_download=False; iers.conf.iers_degraded_accuracy='ignore'; solar_system_ephemeris.set('builtin')
from sgp4.api import Satrec
TLE=[l for l in open('tle_reel_2026-11-09.txt').read().strip().split('\n')]
SAT=Satrec.twoline2rv(TLE[1],TLE[2])
A_E=6378.137; F=1/298.257223563; E2=F*(2-F)
def jd_of_ms(ms): return 2440587.5+np.asarray(ms,dtype=float)/86400000.0
def gmst(jd):                                    # même formule que sgp4 (IAU 1982), UT1 ≈ UTC comme dans l'application
    t=(jd-2451545.0)/36525.0
    s=-6.2e-6*t**3+0.093104*t**2+(876600*3600+8640184.812866)*t+67310.54841
    return np.mod(s*math.pi/180/240,2*math.pi)
def obs_ecef(lat,lon,alt_m):
    la,lo=math.radians(lat),math.radians(lon); N=A_E/math.sqrt(1-E2*math.sin(la)**2); h=alt_m/1000
    return np.array([(N+h)*math.cos(la)*math.cos(lo),(N+h)*math.cos(la)*math.sin(lo),(N*(1-E2)+h)*math.sin(la)])
def ecef_to_teme(v,th):                          # v : (3,) ou (N,3)
    c,s=np.cos(th),np.sin(th); x,y,z=v[...,0],v[...,1],v[...,2] if v.ndim>1 else (v[0],v[1],v[2])
    return np.stack([x*c-y*s,x*s+y*c,z*np.ones_like(c)],axis=-1)
def iss_teme(jd):
    jd=np.atleast_1d(jd); i=np.floor(jd); fr=jd-i
    e,r,v=SAT.sgp4_array(i,fr)
    return r
def body_teme(name,jd):
    t=Time(np.atleast_1d(jd),format='jd',scale='utc'); c=get_body(name,t).transform_to(TEME(obstime=t))
    return c.cartesian.xyz.to(u.km).value.T
def sep_deg(a,b):
    a=a/np.linalg.norm(a,axis=-1,keepdims=True); b=b/np.linalg.norm(b,axis=-1,keepdims=True)
    return np.degrees(np.arccos(np.clip(np.sum(a*b,axis=-1),-1,1)))
def azel(vteme,th,lat,lon):                      # direction topocentrique : azimut (depuis le nord vers l'est) et hauteur
    c,s=np.cos(th),np.sin(th); x,y,z=vteme[...,0],vteme[...,1],vteme[...,2]
    xe,ye,ze=x*c+y*s,-x*s+y*c,z                  # TEME -> ECEF
    la,lo=math.radians(lat),math.radians(lon)
    e=-math.sin(lo)*xe+math.cos(lo)*ye; n=-math.sin(la)*math.cos(lo)*xe-math.sin(la)*math.sin(lo)*ye+math.cos(la)*ze; up=math.cos(la)*math.cos(lo)*xe+math.cos(la)*math.sin(lo)*ye+math.sin(la)*ze
    return np.degrees(np.arctan2(e,n))%360, np.degrees(np.arctan2(up,np.hypot(e,n)))
def topo_pair(name,jd,lat,lon,alt_m):
    jd=np.atleast_1d(jd); th=gmst(jd); o=ecef_to_teme(obs_ecef(lat,lon,alt_m)[None,:].repeat(len(jd),0),th)
    i=iss_teme(jd)-o; b=body_teme(name,jd)-o
    return i,b,th
def radius_deg(name,b):
    d=np.linalg.norm(b,axis=-1); R=695700.0 if name=='sun' else 1737.4
    return np.degrees(np.arcsin(R/d))
