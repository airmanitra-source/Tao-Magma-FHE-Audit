import numpy as np
import os
import matplotlib.pyplot as plt

def load_sbox(filename="sbox.csv"):
    if not os.path.exists(filename):
        print(f"Erreur: {filename} introuvable.")
        return None
    with open(filename, 'r') as f:
        content = f.read().strip()
    
    # On charge les 256 premières valeurs
    raw_sbox = [int(x) for x in content.split(',')][:256]
    
    # RÉPARATION UNITAIRE (P=257 -> 256)
    sbox = []
    actual_vals = set(x for x in raw_sbox if x < 256)
    all_possible = set(range(256))
    # On prend le premier élément de l'ensemble des valeurs manquantes
    missing_val = list(all_possible - actual_vals)[0] if (all_possible - actual_vals) else 0

    for x in raw_sbox:
        if x >= 256:
            sbox.append(missing_val)
        else:
            sbox.append(x)
            
    return np.array(sbox, dtype=np.uint8)

def test_bic(sbox):
    n = 8
    size = 256
    bic_matrix = np.zeros((n, n))

    print("=== ANALYSE BIC (Bit Independence Criterion) ===")

    for i in range(n): # Bit d'entrée inversé
        # Calcul du vecteur de changement pour le bit d'entrée i
        # On calcule sbox(x) XOR sbox(x with bit i flipped)
        x = np.arange(size, dtype=np.uint16)
        x_prime = x ^ (1 << i)
        diff_vectors = sbox[x] ^ sbox[x_prime]

        for j in range(n):
            for k in range(n):
                if j != k:
                    # On vérifie l'indépendance entre le bit de sortie j et k
                    bit_j = (diff_vectors >> j) & 1
                    bit_k = (diff_vectors >> k) & 1
                    
                    # Score de corrélation (doit tendre vers 0.5)
                    correlation = np.mean(bit_j ^ bit_k)
                    bic_matrix[j, k] += correlation

    # Moyenne sur les 8 configurations d'entrée
    bic_matrix /= n

    # Calcul des métriques pour l'article
    mask = ~np.eye(n, dtype=bool) # On ignore la diagonale
    valid_scores = bic_matrix[mask]
    avg_bic = np.mean(valid_scores)
    max_dev = np.max(np.abs(valid_scores - 0.5))

    print(f"Moyenne BIC-SAC : {avg_bic:.4f} (Idéal : 0.5000)")
    print(f"Déviation maximale BIC : {max_dev:.4f}")
    
    return bic_matrix

import matplotlib.pyplot as plt
import numpy as np

def save_bic_heatmap(matrix, filename="bic_heatmap.pdf"):
    # Style pro
    plt.rcParams.update({"font.family": "serif", "font.size": 10})
    fig, ax = plt.subplots(figsize=(7, 6))

    # Matrice BIC (on utilise 'plasma' pour varier du SAC)
    im = ax.imshow(matrix, cmap='plasma', vmin=0.45, vmax=0.55, interpolation='nearest')

    # Colorbar
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Independence Score", rotation=-90, va="bottom")

    # Annotations numériques (3 décimales)
    for i in range(8):
        for j in range(8):
            if i != j: # On n'annote pas la diagonale (toujours 0 ou 1)
                val = matrix[i, j]
                ax.text(j, i, f"{val:.3f}", ha="center", va="center", color="white" if val < 0.49 else "black")

    # Labels des bits B0 à B7
    ax.set_xticks(np.arange(8))
    ax.set_yticks(np.arange(8))
    ax.set_xticklabels([f"B{i}" for i in range(8)])
    ax.set_yticklabels([f"B{i}" for i in range(8)])

    # TITRES EN ANGLAIS (Standard ePrint/arXiv)
    ax.set_title("Bit Independence Criterion (BIC) Matrix", fontweight='bold', pad=15)
    ax.set_xlabel("Output Bit Index ($j$)")
    ax.set_ylabel("Output Bit Index ($k$)")

    plt.tight_layout()
    # EXPORT VECTORIEL PDF (Pas de flou dans LaTeX)
    plt.savefig(filename, bbox_inches='tight', format='pdf', dpi=300)
    print(f"✅ BIC Heatmap sauvegardée : {filename}")
    plt.show()

# save_bic_heatmap(matrix_bic)

    
# --- EXÉCUTION ---
sbox = load_sbox("sbox.csv")
if sbox is not None:
    matrix = test_bic(sbox)
    save_bic_heatmap(matrix)
