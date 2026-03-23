# Tao-Magma FHE Audit — S-Box Analysis Scripts

This repository contains Python scripts for cryptographic analysis of an 8-bit S-Box, as part of a Fully Homomorphic Encryption (FHE) audit. The analyses include Strict Avalanche Criterion (SAC), Bit Independence Criterion (BIC), algebraic degree / differential/linear resistance, and quantum spectral analysis via Quantum Fourier Transform (QFT).

---

## Requirements

### Python version

Python **3.8** or higher is recommended.

### Dependencies

| Package | Version | Used by |
|---|---|---|
| `numpy` | ≥ 1.21 | All scripts |
| `matplotlib` | ≥ 3.4 | `test_bit_criterion.py`, `test_sac_criterion.py`, `test_quantic_fourier_transform.py` |
| `qiskit` | ≥ 1.0 | `test_quantic_fourier_transform.py` |
| `qiskit-aer` | ≥ 0.13 | `test_quantic_fourier_transform.py` |

### Installation

Install all dependencies at once:

```bash
pip install numpy matplotlib qiskit qiskit-aer
```

Or install only what you need:

```bash
# For SAC and BIC tests only
pip install numpy matplotlib

# For algebraic degree / security audit only
pip install numpy

# For quantum Fourier transform analysis
pip install numpy matplotlib qiskit qiskit-aer
```

---

## Input File

All scripts expect a file named **`sbox.csv`** in the working directory. This file must contain at least 256 comma-separated integer values representing the S-Box permutation over GF(2⁸).

A sample `sbox.csv` is already provided in this repository.

---

## Scripts

### 1. `test_sac_criterion.py` — Strict Avalanche Criterion (SAC)

Verifies that flipping a single input bit changes each output bit with probability ≈ 0.5, indicating strong avalanche behaviour.

**Run:**
```bash
python test_sac_criterion.py
```

**Output:**
- Console report: mean, standard deviation, and maximum deviation of the SAC matrix.
- `sac_heatmap.pdf` — publication-quality heatmap of the 8×8 SAC matrix.

---

### 2. `test_bit_criterion.py` — Bit Independence Criterion (BIC)

Checks that any pair of output bits changes independently when a single input bit is flipped, measuring inter-bit correlation.

**Run:**
```bash
python test_bit_criterion.py
```

**Output:**
- Console report: BIC-SAC mean score and maximum deviation from 0.5.
- `bic_heatmap.pdf` — publication-quality heatmap of the 8×8 BIC matrix.

---

### 3. `test_degree_algebra.py` — Algebraic Security Audit

Computes two classical cryptographic metrics:
- **Differential Uniformity** (via the Difference Distribution Table, DDT) — measures resistance to differential cryptanalysis.
- **Non-linearity** (via the Linear Approximation Table, LAT / Walsh-Hadamard Transform) — measures distance from the nearest affine function.

**Run:**
```bash
python test_degree_algebra.py
```

> ⚠️ This script performs an exhaustive Walsh-Hadamard Transform over all 255 × 255 mask pairs. For a full 8-bit S-Box, this may take several minutes.

**Output:**
- Console report: maximum DDT value, non-linearity score, and a security verdict.

---

### 4. `test_quantic_fourier_transform.py` — Quantum Spectral Analysis (QFT)

Constructs a quantum circuit that applies the S-Box as a unitary operator followed by a Quantum Fourier Transform, then simulates the measurement distribution to detect spectral biases.

**Run:**
```bash
python test_quantic_fourier_transform.py
```

**Output:**
- Console report: loaded S-Box validation and top-15 measurement counts.
- `qft_analysis.pdf` — publication-quality bar chart of the QFT measurement distribution.

---

## File Overview

```
.
├── sbox.csv                          # Input: 256-entry S-Box permutation
├── test_sac_criterion.py             # SAC analysis + heatmap export
├── test_bit_criterion.py             # BIC analysis + heatmap export
├── test_degree_algebra.py            # Differential uniformity & non-linearity
├── test_quantic_fourier_transform.py # Quantum Fourier Transform simulation
├── sac_heatmap.pdf                   # Output (generated)
├── bic_heatmap.pdf                   # Output (generated)
└── qft_analysis.pdf                  # Output (generated)
```

---

## License

See [LICENSE](LICENSE) for details.
