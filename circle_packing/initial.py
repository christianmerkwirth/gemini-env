# EVOLVE-BLOCK-START
import numpy as np
from scipy.optimize import minimize, linprog
import time

def get_optimal_radii(centers):
    n = len(centers)
    c = -np.ones(n)
    
    A_ub = []
    b_ub = []
    
    for i in range(n):
        for j in range(i+1, n):
            row = np.zeros(n)
            row[i] = 1.0
            row[j] = 1.0
            A_ub.append(row)
            dist = np.sqrt(np.sum((centers[i] - centers[j])**2))
            b_ub.append(max(0, dist - 1e-9))
            
    bounds = []
    for i in range(n):
        x, y = centers[i]
        max_r = max(0, min(x, 1-x, y, 1-y) - 1e-9)
        bounds.append((0, max_r))
        
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method='highs')
    if res.success:
        return res.x
    else:
        return np.zeros(n)

def construct_packing():
    n = 26
    best_x = None
    best_sum = -1.0
    
    start_time = time.time()
    bounds = [(0.0, 1.0)] * (2 * n) + [(0.0, 0.5)] * n
    
    def constraints_fun(x):
        cx = x[:n]
        cy = x[n:2*n]
        cr = x[2*n:]
        c_wall = np.concatenate([cx - cr, 1.0 - cx - cr, cy - cr, 1.0 - cy - cr])
        idx_i, idx_j = np.triu_indices(n, 1)
        dx = cx[idx_i] - cx[idx_j]
        dy = cy[idx_i] - cy[idx_j]
        sr = cr[idx_i] + cr[idx_j]
        c_overlap = dx*dx + dy*dy - sr*sr
        return np.concatenate([c_wall, c_overlap])
        
    def constraints_jac(x):
        cx = x[:n]
        cy = x[n:2*n]
        cr = x[2*n:]
        n_wall = 4 * n
        n_overlap = n * (n - 1) // 2
        J = np.zeros((n_wall + n_overlap, 3 * n))
        for i in range(n): J[i, i] = 1; J[i, 2*n+i] = -1
        for i in range(n): J[n+i, i] = -1; J[n+i, 2*n+i] = -1
        for i in range(n): J[2*n+i, n+i] = 1; J[2*n+i, 2*n+i] = -1
        for i in range(n): J[3*n+i, n+i] = -1; J[3*n+i, 2*n+i] = -1
        idx_i, idx_j = np.triu_indices(n, 1)
        dx = cx[idx_i] - cx[idx_j]
        dy = cy[idx_i] - cy[idx_j]
        sr = cr[idx_i] + cr[idx_j]
        for k, (i, j) in enumerate(zip(idx_i, idx_j)):
            row = n_wall + k
            J[row, i] = 2 * dx[k]
            J[row, j] = -2 * dx[k]
            J[row, n+i] = 2 * dy[k]
            J[row, n+j] = -2 * dy[k]
            J[row, 2*n+i] = -2 * sr[k]
            J[row, 2*n+j] = -2 * sr[k]
        return J

    con = {'type': 'ineq', 'fun': constraints_fun, 'jac': constraints_jac}
    
    def objective(x): return -np.sum(x[2*n:])
    def obj_jac(x):
        j = np.zeros(3 * n)
        j[2*n:] = -1.0
        return j

    def gen_rings(counts):
        pts = []
        if len(counts) == 3:
            pts.append((0.5, 0.5))
            counts = counts[1:]
            radii = [0.2, 0.4]
        else:
            radii = [0.15, 0.35, 0.45]
            
        for r, count in zip(radii, counts):
            for i in range(count):
                angle = 2 * np.pi * i / count
                pts.append((0.5 + r * np.cos(angle), 0.5 + r * np.sin(angle)))
        return pts[:n]

    initializers = [
        lambda: np.random.uniform(0.1, 0.9, (n, 2)),
        lambda: gen_rings([1, 8, 17]),
        lambda: gen_rings([1, 9, 16]),
        lambda: gen_rings([4, 9, 13]),
        lambda: gen_rings([3, 10, 13]),
    ]
    
    rows, cols = 6, 6
    pts_hex = []
    for r in range(rows):
        for c in range(cols):
            x = (c + 0.5 * (r % 2)) / cols
            y = r / rows
            pts_hex.append((x, y))
    pts_hex = sorted(pts_hex, key=lambda p: (p[0]-0.5)**2 + (p[1]-0.5)**2)[:n]
    initializers.append(lambda: np.array([(0.05 + 0.9*p[0], 0.05 + 0.9*p[1]) for p in pts_hex]))

    for attempt in range(500):
        if time.time() - start_time > 45:
            break
            
        x0 = np.zeros(3 * n)
        
        if attempt < len(initializers):
            pts = np.array(initializers[attempt]())
            if len(pts) < n: 
                pts = np.random.uniform(0.1, 0.9, (n, 2))
            x0[:n] = pts[:, 0]
            x0[n:2*n] = pts[:, 1]
            x0[2*n:] = 0.001
            
        elif attempt % 3 == 0 and best_x is not None:
            x0 = best_x.copy()
            noise = np.random.uniform(0.001, 0.02)
            x0[:2*n] += np.random.normal(0, noise, 2*n)
            x0[:2*n] = np.clip(x0[:2*n], 0.01, 0.99)
            
            cr = np.ones(n) * 0.5
            cx = x0[:n]
            cy = x0[n:2*n]
            for i in range(n):
                cr[i] = min(cr[i], cx[i], 1-cx[i], cy[i], 1-cy[i])
            for i in range(n):
                for j in range(i+1, n):
                    dist = np.sqrt((cx[i]-cx[j])**2 + (cy[i]-cy[j])**2)
                    if cr[i] + cr[j] > dist:
                        scale = (dist * 0.99) / (cr[i] + cr[j] + 1e-9)
                        cr[i] *= scale
                        cr[j] *= scale
            x0[2*n:] = cr
            
        elif attempt % 3 == 1 and best_x is not None:
            x0 = best_x.copy()
            noise = np.random.uniform(0.03, 0.1)
            x0[:2*n] += np.random.normal(0, noise, 2*n)
            x0[:2*n] = np.clip(x0[:2*n], 0.01, 0.99)
            x0[2*n:] = 0.001
            
        else:
            x0[:n] = np.random.uniform(0.1, 0.9, n)
            x0[n:2*n] = np.random.uniform(0.1, 0.9, n)
            x0[2*n:] = 0.001

        res = minimize(objective, x0, method='SLSQP', bounds=bounds, 
                       constraints=con, jac=obj_jac, 
                       options={'maxiter': 600, 'ftol': 1e-6})
                       
        if res.success or res.status == 8:
            if -res.fun > best_sum:
                best_sum = -res.fun
                best_x = res.x.copy()

    if best_x is None:
        best_centers = np.zeros((n, 2))
        best_radii = np.zeros(n)
        return best_centers, best_radii
        
    best_centers = np.column_stack((best_x[:n], best_x[n:2*n]))
    best_radii = get_optimal_radii(best_centers)
    return best_centers, best_radii

# EVOLVE-BLOCK-END

def run_packing():
    centers, radii = construct_packing()
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
