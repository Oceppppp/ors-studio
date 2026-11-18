from __future__ import annotations
import math
from scipy.special import gammaln
from .common import require


def solve_mm1(arrival_rate: float, service_rate: float) -> dict:
    lam, mu = float(arrival_rate), float(service_rate)
    require(math.isfinite(lam) and math.isfinite(mu), "arrival and service rates must be finite")
    require(lam >= 0 and mu > 0, "arrival_rate must be >= 0 and service_rate must be > 0")
    require(lam < mu, "M/M/1 is unstable when arrival_rate >= service_rate")
    rho=lam/mu
    return {"model":"M/M/1","utilization":rho,"P0":1-rho,"L":rho/(1-rho),"Lq":rho*rho/(1-rho),"W":1/(mu-lam),"Wq":lam/(mu*(mu-lam)),"assumptions":["Poisson arrivals, exponential service times, one server, infinite calling population/queue, FCFS, steady state.","Rates must use the same time unit."]}


def solve_mmc(arrival_rate: float, service_rate: float, servers: int) -> dict:
    lam,mu,c=float(arrival_rate),float(service_rate),int(servers)
    require(math.isfinite(lam) and math.isfinite(mu), "arrival and service rates must be finite")
    require(lam>=0 and mu>0 and c>=1 and c==servers,"arrival_rate >= 0, service_rate > 0, servers must be a positive integer")
    a=lam/mu; rho=lam/(c*mu)
    require(rho<1,"M/M/c is unstable when arrival_rate >= servers * service_rate")
    terms=[a**n/math.factorial(n) for n in range(c)]
    tail=a**c/(math.factorial(c)*(1-rho))
    p0=1/(sum(terms)+tail)
    pw=tail*p0
    Lq=pw*rho/(1-rho)
    Wq=Lq/lam if lam else 0
    W=Wq+1/mu; L=lam*W
    return {"model":"M/M/c","servers":c,"utilization_per_server":rho,"P0":p0,"probability_wait":pw,"Lq":Lq,"L":L,"Wq":Wq,"W":W,"assumptions":["Poisson arrivals, exponential independent service times, c identical servers, FCFS, infinite queue and calling population, steady state.","Rates must use the same time unit."]}
