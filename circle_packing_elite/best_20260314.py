import numpy as np
import os
from scipy.optimize import minimize

def refine(n, centers, radii, max_iter=150):
    x0 = np.concatenate([centers.flatten(), radii])
    def objective(x): return -np.sum(x[2*n:])
    def constraints(x):
        c, r = x[:2*n].reshape((n, 2)), x[2*n:]
        cons = np.zeros(4*n + n*(n-1)//2)
        idx = 0
        for i in range(n):
            cons[idx] = c[i,0]-r[i]; idx+=1
            cons[idx] = 1-c[i,0]-r[i]; idx+=1
            cons[idx] = c[i,1]-r[i]; idx+=1
            cons[idx] = 1-c[i,1]-r[i]; idx+=1
        for i in range(n):
            for j in range(i+1, n):
                cons[idx] = np.sum((c[i]-c[j])**2) - (r[i]+r[j])**2
                idx+=1
        return cons
    res = minimize(objective, x0, method='SLSQP', bounds=[(0,1)]*(3*n),
                   constraints={'type':'ineq', 'fun':constraints}, options={'maxiter':max_iter})
    c_res, r_res = res.x[:2*n].reshape((n, 2)), res.x[2*n:]
    # Strict post-fix
    for _ in range(30):
        changed = False
        for i in range(n):
            c_res[i] = np.clip(c_res[i], r_res[i], 1.0 - r_res[i])
            r_old = r_res[i]
            r_res[i] = min(r_res[i], c_res[i,0], 1.0-c_res[i,0], c_res[i,1], 1.0-c_res[i,1])
            if abs(r_old-r_res[i]) > 1e-10: changed = True
        for i in range(n):
            for j in range(i+1, n):
                d = np.sqrt(np.sum((c_res[i]-c_res[j])**2))
                if d < r_res[i]+r_res[j]:
                    overlap = r_res[i]+r_res[j]-d
                    r_res[i] -= overlap/2 + 1e-11
                    r_res[j] -= overlap/2 + 1e-11
                    changed = True
        if not changed: break
    return c_res, np.maximum(r_res, 0), np.sum(r_res)

def run_packing(n=26):
    best_file = os.path.join(os.path.dirname(__file__), 'data_20260314.npz')
    if not os.path.exists(best_file):
        # Fallback to local
        best_file = 'data_20260314.npz'
    
    data = np.load(best_file)
    c_best, r_best = data[f'centers_{n}'], data[f'radii_{n}']
    
    # Try the best directly
    # Plus a few jittered refinements
    overall_best_res = (c_best, r_best, np.sum(r_best))
    overall_best_sum = np.sum(r_best)
    
    for _ in range(3):
        try:
            c = c_best + (np.random.rand(n, 2)-0.5)*0.005
            cf, rf, sf = refine(n, c, r_best, max_iter=150)
            if sf > overall_best_sum:
                overall_best_sum = sf
                overall_best_res = (cf, rf, sf)
        except:
            continue
            
    return overall_best_res
