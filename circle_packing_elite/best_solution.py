import numpy as np
import torch
from scipy.optimize import minimize, linprog

def run_packing(n=26):
    """
    Super Hybrid: 15 seeds, 1500 steps Sim, 25 iterations Alt-Opt with micro-SLSQP.
    """
    device = torch.device('cpu')

    def soft_body_sim(nc, init_c, steps=1500):
        c = torch.tensor(init_c, dtype=torch.float32, requires_grad=True)
        r = torch.full((nc,), 0.05, dtype=torch.float32, requires_grad=True)
        opt = torch.optim.Adam([c, r], lr=0.02)
        for i in range(steps):
            opt.zero_grad()
            alpha = 1.0 - i/steps
            diff = c.unsqueeze(1) - c.unsqueeze(0); d = torch.sqrt((diff**2).sum(dim=-1) + 1e-9)
            overlap = torch.clamp(r.unsqueeze(1) + r.unsqueeze(0) - d, min=0)
            rv = r.view(-1, 1); b_pen = torch.clamp(rv-c, min=0).pow(2).sum() + torch.clamp(c+rv-1, min=0).pow(2).sum()
            loss = -torch.sum(torch.log(r+1e-5))*(1.0+alpha) + overlap.pow(2).sum()*80 + b_pen*80
            loss.backward(); opt.step()
            with torch.no_grad(): r.clamp_(0.001, 0.5); c.clamp_(0, 1)
        return c.detach().numpy(), r.detach().numpy()

    def lp_squeeze(nc, centers):
        c_lp = -np.ones(nc); A_ub, b_ub = [], []
        for i in range(nc):
            for j in range(i + 1, nc):
                row = np.zeros(nc); row[i] = 1.0; row[j] = 1.0
                A_ub.append(row); b_ub.append(np.linalg.norm(centers[i] - centers[j]))
        bounds_r = []
        for i in range(nc):
            max_r = min(centers[i, 0], 1.0 - centers[i, 0], centers[i, 1], 1.0 - centers[i, 1])
            bounds_r.append((0, max(0, max_r)))
        res = linprog(c_lp, A_ub=A_ub, b_ub=b_ub, bounds=bounds_r, method='highs')
        return res.x if res.success else np.full(nc, 0.001)

    def slsqp_refine(nc, c, r, miter=150):
        p = np.zeros(3*nc)
        for i in range(nc): p[3*i:3*i+2] = c[i]; p[3*i+2] = r[i]
        def obj(p): return -np.sum(p[2::3])
        def cons(p):
            p = p.reshape((nc, 3)); x, y, r = p[:, 0], p[:, 1], p[:, 2]; res = []
            res.extend(x-r); res.extend(1-x-r); res.extend(y-r); res.extend(1-y-r)
            for i in range(nc):
                for j in range(i+1, nc): res.append((x[i]-x[j])**2 + (y[i]-y[j])**2 - (r[i]+r[j])**2)
            return np.array(res)
        res = minimize(obj, p, method='SLSQP', constraints={'type': 'ineq', 'fun': cons},
                       bounds=[(0, 1), (0, 1), (0, 0.5)] * nc, options={'maxiter': miter})
        fp = res.x.reshape((nc, 3))
        return fp[:, :2], fp[:, 2]

    def cleanup(c, r):
        e = 1e-8; nc = len(r)
        for _ in range(50):
            for i in range(nc): r[i] = max(0, min(r[i], c[i,0], 1-c[i,0], c[i,1], 1-c[i,1]) - e)
            for i in range(nc):
                for j in range(i+1, nc):
                    d = np.linalg.norm(c[i]-c[j])
                    if d < r[i]+r[j]:
                        a = (r[i]+r[j]-d) + e; s = r[i]+r[j]; ra = r[i]/s if s > 0 else 0.5
                        r[i] -= a*ra; r[j] -= a*(1-ra)
        return r

    best_s = -1; bc, br = None, None
    seeds = []
    # Grid & Hex
    s = int(np.ceil(np.sqrt(n)))
    seeds.append(np.array([[(i % s + 0.5)/s, (i // s + 0.5)/s] for i in range(n)]))
    rows = int(np.ceil(np.sqrt(n * 1.15))); cols = int(np.ceil(n / rows)); dx, dy = 1.0/cols, 1.0/rows
    seeds.append(np.array([[(i%cols + 0.5 + (0.25 if (i//cols)%2 else 0))*dx, (i//cols + 0.5)*dy] for i in range(n)]))
    # Randomized Greedy Seeds
    for _ in range(8):
        gc, gr = [], []
        for _ in range(n):
            bp, bg = None, -1
            for _ in range(150):
                p = np.random.rand(2); g = min(p[0], 1-p[0], p[1], 1-p[1])
                for j in range(len(gc)): g = min(g, np.linalg.norm(p - gc[j]) - gr[j])
                if g > bg: bg = g; bp = p
            gc.append(bp if bp is not None else np.random.rand(2)); gr.append(max(0.01, bg))
        seeds.append(np.array(gc))

    for c_i in seeds:
        c, r = soft_body_sim(n, c_i)
        c, r = slsqp_refine(n, c, r, 200)
        r = lp_squeeze(n, c)
        
        for alt_it in range(25):
            # LNS
            nr = max(1, n // 5); ids = np.argsort(r); to_rem = ids[:nr]; to_keep = ids[nr:]
            cn, rn = list(c[to_keep]), list(r[to_keep])
            for _ in range(nr):
                bp, bg = None, -1; pts = np.random.rand(300, 2)
                for p in pts:
                    g = min(p[0], 1-p[0], p[1], 1-p[1])
                    for i in range(len(cn)): g = min(g, np.linalg.norm(p - cn[i]) - rn[i])
                    if g > bg: bg = g; bp = p
                cn.append(bp if bp is not None else np.random.rand(2)); rn.append(max(0.001, bg))
            cc, rc = slsqp_refine(n, np.array(cn), np.array(rn), 150)
            rc = lp_squeeze(n, cc)
            if np.sum(rc) > np.sum(r): c, r = cc, rc
            
            # Local coordinate descent
            for i in range(n):
                co = c[i].copy(); cur_sc = np.sum(r)
                for _ in range(5):
                    c[i] = co + np.random.normal(0, 0.005 * (1.0-alt_it/25.0), 2)
                    c[i] = np.clip(c[i], 0, 1)
                    rn = lp_squeeze(n, c)
                    if np.sum(rn) > cur_sc: r = rn; co = c[i].copy(); cur_sc = np.sum(r)
                    else: c[i] = co
        
        r = cleanup(c, r); sc = np.sum(r)
        if sc > best_s: best_s = sc; bc = c; br = r
        
    return bc, br, best_s
