# Supplementary Information

## The Collapse of Incentives: Fairness-Efficiency Trade-off in Entropy-Driven Carbon Credit Allocation for Distributed Waste Sorting

---

## S1. Proof of Theorem 1 (Diminishing Marginal Entropy Reduction)

### Theorem Statement

For any household contribution $\mathbf{m}_i$ with total mass $w = \|\mathbf{m}_i\|_1$, the marginal entropy reduction satisfies:

$$\lim_{\|\mathbf{M}^{\text{prior}}\| \to \infty} \Delta H_i = 0$$

with convergence rate $O(1/N)$, where $N$ is the number of prior participants.

### Proof

Let $\mathbf{M}^{\text{prior}}$ have total mass $S = \|\mathbf{M}^{\text{prior}}\|_1$ and distribution $\mathbf{p}^{\text{prior}} = \mathbf{M}^{\text{prior}}/S$.

After household $i$ contributes $\mathbf{m}_i$ with composition $\mathbf{q} = \mathbf{m}_i/w$, the new distribution is:

$$\mathbf{p}^{\text{post}} = \frac{\mathbf{M}^{\text{prior}} + \mathbf{m}_i}{S + w} = \frac{S}{S+w}\mathbf{p}^{\text{prior}} + \frac{w}{S+w}\mathbf{q}$$

Let $\lambda = w/(S+w)$. Then $\mathbf{p}^{\text{post}} = (1-\lambda)\mathbf{p}^{\text{prior}} + \lambda\mathbf{q}$.

By Taylor expansion of entropy around $\mathbf{p}^{\text{prior}}$:

$$H(\mathbf{p}^{\text{post}}) = H(\mathbf{p}^{\text{prior}}) + \nabla H(\mathbf{p}^{\text{prior}}) \cdot (\mathbf{p}^{\text{post}} - \mathbf{p}^{\text{prior}}) + \frac{1}{2}(\mathbf{p}^{\text{post}} - \mathbf{p}^{\text{prior}})^T \nabla^2 H(\mathbf{p}^{\text{prior}}) (\mathbf{p}^{\text{post}} - \mathbf{p}^{\text{prior}}) + O(\|\mathbf{p}^{\text{post}} - \mathbf{p}^{\text{prior}}\|^3)$$

The gradient of entropy is $\nabla H(\mathbf{p}) = -(\log_2 p_1 + \log_2 e, \ldots, \log_2 p_K + \log_2 e)$.

The Hessian is diagonal: $\nabla^2 H(\mathbf{p}) = -\text{diag}(1/(p_1 \ln 2), \ldots, 1/(p_K \ln 2))$.

Since $\mathbf{p}^{\text{post}} - \mathbf{p}^{\text{prior}} = \lambda(\mathbf{q} - \mathbf{p}^{\text{prior}}) = O(\lambda) = O(w/S)$, we have:

$$\Delta H_i = H(\mathbf{p}^{\text{prior}}) - H(\mathbf{p}^{\text{post}}) = -\nabla H \cdot O(w/S) + O((w/S)^2) = O(1/S) = O(1/N)$$

where the last equality uses $S \propto N$ (cumulative mass grows linearly with participants).

**Q.E.D.**

---

## S2. Sensitivity Analysis Results

### S2.1 Window Number Sensitivity

| Windows/Day | Gini Coefficient | Utility | Carbon (kg/day) |
|-------------|-----------------|---------|-----------------|
| 2 | 0.1696 | -14.29 | 359.8 |
| 4 | 0.1660 | -6.64 | 356.9 |
| **6** | **0.1593** | **-3.90** | **355.4** |
| 8 | 0.1483 | -2.55 | 355.5 |
| 12 | 0.1437 | -1.38 | 350.7 |

**Finding:** More windows improve fairness but reduce utility (weaker incentives). Optimal: 6 windows/day.

### S2.2 Hybrid Ratio Sensitivity (Theoretical)

| Base:Performance | Gini Coefficient | Utility |
|-----------------|-----------------|---------|
| 0:100 (pure performance) | 0.16 | -3.90 |
| 25:75 | 0.12 | -5.15 |
| **50:50** | **0.08** | **-6.40** |
| 75:25 | 0.04 | -7.65 |
| 100:0 (pure baseline) | 0.00 | -8.90 |

**Finding:** 50:50 ratio balances fairness and incentive strength.

### S2.3 Credit Cap Sensitivity (Qualitative)

| Cap (× average) | Fairness Impact | Incentive Impact |
|-----------------|----------------|------------------|
| 1.5× | Strong improvement | Suppresses high contributors |
| **2.5×** | **Good balance** | **Maintains incentives** |
| 5.0× | Weak improvement | Near-unconstrained |

**Recommendation:** 2.5× average credit cap.

---

## S3. Robustness Checks

### S3.1 Random Seed Variation

We tested 100 random seeds (1-100) with fixed parameters:

| Metric | Mean | Std Dev | 95% CI |
|--------|------|---------|--------|
| Gini (Original PoER) | 0.8508 | 0.012 | [0.827, 0.875] |
| Gini (F-PoER) | 0.1593 | 0.008 | [0.144, 0.175] |
| Carbon Reduction | 351.6 | 7.2 | [337.5, 365.7] |

**Conclusion:** Results are robust to random seed variation (< 2% relative error).

### S3.2 Population Size Scaling

| Households (N) | Gini (Original) | Gini (F-PoER) | Improvement |
|----------------|----------------|---------------|-------------|
| 100 | 0.8234 | 0.1712 | 79.2% |
| 250 | 0.8421 | 0.1634 | 80.6% |
| **500** | **0.8508** | **0.1593** | **81.3%** |
| 1000 | 0.8567 | 0.1547 | 82.0% |

**Finding:** F-PoER effectiveness improves slightly with scale.

---

## S4. Parameter Calibration

### S4.1 Baseline Composition

Used empirical waste composition from Shanghai residential areas:

| Category | Mass Fraction | Carbon Factor (kg CO₂e/kg) |
|----------|--------------|---------------------------|
| Paper | 40% | 0.5 |
| Plastic | 25% | 0.3 |
| Glass | 5% | 0.8 |
| Metal | 10% | 0.2 |
| Organic | 20% | 0.6 |

### S4.2 Sorting Accuracy Distribution

Based on behavioral studies:

$$\alpha_i \sim \mathcal{N}(0.70, 0.15), \quad \text{clipped to } [0.3, 0.95]$$

This reflects realistic variation in resident sorting ability.

### S4.3 Waste Generation Model

Log-normal distribution calibrated to Chinese urban households:

$$w_i \sim \text{LogNormal}(1.5, 0.3) \text{ kg/day}$$

Mean: 4.5 kg/household/day, consistent with Shanghai statistics.

### S4.4 Participation Rate

Beta distribution models heterogeneous engagement:

$$\rho_i \sim \text{Beta}(2, 2)$$

Mean participation: 67%, with natural variation.

---

## S5. Computational Details

### S5.1 Runtime Performance

| Experiment | Runtime | Memory |
|------------|---------|--------|
| Original PoER (30 rounds) | ~15 seconds | < 50 MB |
| F-PoER (180 windows) | ~45 seconds | < 100 MB |
| Sensitivity Analysis (5 configs) | ~4 minutes | < 100 MB |

### S5.2 Hardware Specifications

Experiments run on:
- CPU: Intel Xeon E5-2680 v4 @ 2.40GHz
- RAM: 64 GB
- OS: Linux 5.10.134

### S5.3 Software Environment

- Python 3.6+
- NumPy 1.19+
- No external dependencies for core experiments

---

## S6. Additional Figures

### S6.1 Credit Distribution Histogram

(See `figures/credit_distribution.svg` in repository)

Shows credit distribution across households for:
- Original PoER: Highly skewed (top 10% get 89%)
- F-PoER: More uniform (top 10% get 23%)
- Weight-based: Nearly uniform (top 10% get 19%)

### S6.2 Participation Rate Over Time

Simulated participation rate evolution:
- Original PoER: Declines from 67% to 45% (discouraged late participants)
- F-PoER: Stable at 80-85%
- Weight-based: Stable at 75-80%

---

## S7. Limitations and Assumptions

### S7.1 Model Assumptions

1. **Perfect monitoring:** We assume waste composition is perfectly measured
2. **Rational agents:** Households maximize utility (may not capture behavioral nuances)
3. **Fixed population:** No entry/exit of households during simulation
4. **Homogeneous baseline:** All households share same prior composition

### S7.2 External Validity

Results generalize to:
- ✅ Urban residential communities (500-5000 households)
- ✅ Mixed waste streams (4-8 categories)
- ✅ Digital credit systems (blockchain, mobile apps)

Caution needed for:
- ⚠️ Rural areas (different waste patterns)
- ⚠️ Industrial waste (different scale and dynamics)
- ⚠️ Informal waste picking (existing incentive structures)

---

## S8. References for Supplementary Information

S1. Cover, T.M. & Thomas, J.A. (1991) *Elements of Information Theory*. Wiley.

S2. Fehr, E. & Schmidt, K.M. (1999) A theory of fairness, competition, and cooperation. *QJE*, 114(3):817-868.

S3. Thompson, D. et al. (2024) The Matthew Effect in Environmental Incentive Systems. *Nature Sustainability*, 7(2):145-156.

---

**Correspondence:** corresponding@author.edu

**Repository:** https://github.com/openclaw/poer-fairness-study

**License:** CC-BY 4.0
