# EVOLVE-BLOCK-START
import numpy as np
from scipy.optimize import minimize
import math

def construct_packing(n=26):
    best_centers = None
    best_radii = None
    best_score = -np.inf
    
    num_overlaps = n * (n - 1) // 2
    overlap_pairs = np.zeros((num_overlaps, 2), dtype=int)
    idx = 0
    for i in range(n):
        for j in range(i+1, n):
            overlap_pairs[idx] = [i, j]
            idx += 1
            
    def objective(vars):
        return -np.sum(vars[2::3])
        
    def gradient(vars):
        grad = np.zeros_like(vars)
        grad[2::3] = -1.0
        return grad
        
    def constraint_box(vars):
        x = vars[0::3]
        y = vars[1::3]
        r = vars[2::3]
        return np.concatenate([x - r, 1.0 - x - r, y - r, 1.0 - y - r])
        
    def jacobian_box(vars):
        jac = np.zeros((4*n, 3*n))
        for i in range(n):
            jac[i, 3*i] = 1
            jac[i, 3*i+2] = -1
            jac[n+i, 3*i] = -1
            jac[n+i, 3*i+2] = -1
            jac[2*n+i, 3*i+1] = 1
            jac[2*n+i, 3*i+2] = -1
            jac[3*n+i, 3*i+1] = -1
            jac[3*n+i, 3*i+2] = -1
        return jac

    def constraint_overlap(vars):
        x = vars[0::3]
        y = vars[1::3]
        r = vars[2::3]
        i = overlap_pairs[:, 0]
        j = overlap_pairs[:, 1]
        dx = x[i] - x[j]
        dy = y[i] - y[j]
        return dx**2 + dy**2 - (r[i] + r[j])**2
        
    def jacobian_overlap(vars):
        jac = np.zeros((num_overlaps, 3*n))
        x = vars[0::3]
        y = vars[1::3]
        r = vars[2::3]
        i = overlap_pairs[:, 0]
        j = overlap_pairs[:, 1]
        
        dx = x[i] - x[j]
        dy = y[i] - y[j]
        sum_r = r[i] + r[j]
        
        jac[np.arange(num_overlaps), 3*i] = 2*dx
        jac[np.arange(num_overlaps), 3*j] = -2*dx
        jac[np.arange(num_overlaps), 3*i+1] = 2*dy
        jac[np.arange(num_overlaps), 3*j+1] = -2*dy
        jac[np.arange(num_overlaps), 3*i+2] = -2*sum_r
        jac[np.arange(num_overlaps), 3*j+2] = -2*sum_r
        
        return jac
        
    constraints = [
        {'type': 'ineq', 'fun': constraint_box, 'jac': jacobian_box},
        {'type': 'ineq', 'fun': constraint_overlap, 'jac': jacobian_overlap}
    ]
    
    bounds = [(0, 1), (0, 1), (0, 0.5)] * n
    options = {'maxiter': 1000, 'ftol': 1e-6, 'disp': False}
    
    # 50 Restarts with basin hopping
    num_attempts = 50
    for attempt in range(num_attempts):
        np.random.seed(42 + n * 6000 + attempt)
        
        x0 = np.random.rand(n, 2)
        r0 = np.random.uniform(0.01, 0.05, n)
        
        if attempt == 0:
            side = int(np.ceil(np.sqrt(n)))
            idx = 0
            for i in range(side):
                for j in range(side):
                    if idx < n:
                        x0[idx] = [(i + 0.5)/side, (j + 0.5)/side]
                        idx += 1
            r0 = np.ones(n) * (0.4 / side)
        elif attempt == 1:
            x0[0] = [0.5, 0.5]
            r0[0] = 0.1
            n_inner = min(6, n - 1)
            n_outer = n - 1 - n_inner
            for i in range(n_inner):
                angle = 2 * np.pi * i / n_inner
                x0[i + 1] = [0.5 + 0.2 * np.cos(angle), 0.5 + 0.2 * np.sin(angle)]
                r0[i + 1] = 0.05
            for i in range(n_outer):
                angle = 2 * np.pi * i / n_outer if n_outer > 0 else 0
                x0[i + 1 + n_inner] = [0.5 + 0.4 * np.cos(angle), 0.5 + 0.4 * np.sin(angle)]
                r0[i + 1 + n_inner] = 0.05
        elif attempt in [2, 3, 4] and n >= 4:
            r_corner = 0.15 + attempt * 0.02
            r0[:4] = r_corner
            x0[0] = [r_corner, r_corner]
            x0[1] = [1 - r_corner, r_corner]
            x0[2] = [r_corner, 1 - r_corner]
            x0[3] = [1 - r_corner, 1 - r_corner]
            for i in range(4, n):
                x0[i] = [np.random.uniform(0.2, 0.8), np.random.uniform(0.2, 0.8)]
                r0[i] = 0.02
        else:
            if attempt % 5 == 0:
                r0[0] = 0.25 # 1 big
            elif attempt % 5 == 1:
                r0[:min(4, n)] = 0.15 # 4 big
            elif attempt % 5 == 2:
                r0 = np.ones(n) * 0.05 # all same small
            elif attempt % 5 == 3:
                r0[:min(8, n)] = 0.1
            
            for _ in range(50):
                for i in range(n):
                    for j in range(i+1, n):
                        diff = x0[i] - x0[j]
                        dist = np.linalg.norm(diff)
                        if dist < 0.1:
                            force = (0.1 - dist) * (diff / (dist + 1e-6))
                            x0[i] += force * 0.5
                            x0[j] -= force * 0.5
                x0 = np.clip(x0, 0.05, 0.95)
            
        var0 = np.zeros(n * 3)
        var0[0::3] = x0[:, 0]
        var0[1::3] = x0[:, 1]
        var0[2::3] = r0
        
        try:
            res = minimize(objective, var0, method='SLSQP', jac=gradient, bounds=bounds, constraints=constraints, options=options)
            vars_opt = res.x
            
            # Basin hopping refinement: perturb and optimize again
            if res.success:
                for bh in range(2):
                    noise = np.random.normal(0, 0.02, n*3)
                    noise[2::3] = 0 # Don't perturb radii directly
                    vars_perturbed = np.clip(vars_opt + noise, 0, 1)
                    res_refine = minimize(objective, vars_perturbed, method='SLSQP', jac=gradient, bounds=bounds, constraints=constraints, options={'maxiter': 500, 'ftol': 1e-6, 'disp': False})
                    if res_refine.success and res_refine.fun < objective(vars_opt):
                        vars_opt = res_refine.x
        except:
            continue
        
        centers = np.column_stack((vars_opt[0::3], vars_opt[1::3]))
        radii = vars_opt[2::3]
        
        radii = np.maximum(0, radii - 2e-6)
        radii = np.minimum(radii, centers[:, 0])
        radii = np.minimum(radii, 1.0 - centers[:, 0])
        radii = np.minimum(radii, centers[:, 1])
        radii = np.minimum(radii, 1.0 - centers[:, 1])
        
        for _ in range(5):
            for i in range(n):
                for j in range(i + 1, n):
                    dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if radii[i] + radii[j] > dist:
                        safe_dist = max(0.0, dist - 1e-6)
                        scale = safe_dist / (radii[i] + radii[j] + 1e-12)
                        if scale < 1.0:
                            radii[i] *= scale
                            radii[j] *= scale
                            
        radii = np.maximum(0.0, radii)

        score = np.sum(radii)
        if score > best_score:
            valid = True
            for i in range(n):
                if radii[i] < 0:
                    valid = False
            for i in range(n):
                for j in range(i+1, n):
                    d = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                    if d < radii[i] + radii[j] - 1e-6:
                        valid = False
            if valid:
                best_score = score
                best_centers = centers
                best_radii = radii

    return best_centers, best_radii
# EVOLVE-BLOCK-END

def run_packing(n=26):
    centers, radii = construct_packing(n)
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
