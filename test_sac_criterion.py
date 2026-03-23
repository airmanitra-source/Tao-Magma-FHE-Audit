import numpy as np
import os

def load_sbox(filename="sbox.csv"):
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        content = f.read().strip()
    sbox = [int(x) for x in content.split(',')][:256]
    # Réparation unitaire si nécessaire
    if any(x >= 256 for x in sbox):
        actual = set(x for x in sbox if x < 256)
        missing = list(set(range(256)) - actual)[0]
        sbox = [missing if x >= 256 else x for x in sbox]
    return np.array(sbox, dtype=np.uint8)

def test_sac(sbox):
    n = 8  # 8 bits
    size = 256
    sac_matrix = np.zeros((n, n))

    for i in range(n): # Pour chaque bit d'entrée i
        for x in range(size):
            # On inverse le bit i de l'entrée x
            x_prime = x ^ (1 << i)
            
            # On calcule la différence entre les sorties (XOR)
            diff = sbox[x] ^ sbox[x_prime]
            
            # On regarde quels bits de sortie ont changé
            for j in range(n): # Pour chaque bit de sortie j
                if (diff >> j) & 1:
                    sac_matrix[i, j] += 1

    # Normalisation pour obtenir des probabilités (idéal = 0.5)
    sac_matrix /= size

    print("=== RAPPORT DE TEST SAC (Strict Avalanche Criterion) ===")
    print(f"Moyenne de la matrice SAC : {np.mean(sac_matrix):.4f} (Idéal : 0.5000)")
    print(f"Écart-type : {np.std(sac_matrix):.4f}")
    print(f"Déviation maximale par rapport à l'idéal : {np.max(np.abs(sac_matrix - 0.5)):.4f}")
    
    return sac_matrix
import matplotlib.pyplot as plt
import numpy as np

def save_sac_heatmap(matrix, filename="sac_heatmap.pdf"):
    # 1. Configuration du style scientifique
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
    })

    fig, ax = plt.subplots(figsize=(7, 6))

    # 2. Création de la heatmap
    # On utilise 'RdYlGn' (Rouge-Jaune-Vert) centré sur 0.5
    im = ax.imshow(matrix, cmap='RdYlGn', vmin=0.4, vmax=0.6, interpolation='nearest')

    # 3. Ajout de la barre de couleur
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Change Probability", rotation=-90, va="bottom")

    # 4. Ajout des valeurs numériques dans chaque case (Annotations)
    # C'est ce qui donne l'aspect "expert" à la figure
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            # On choisit la couleur du texte (noir ou blanc) selon la luminosité du fond
            color = "black" if 0.45 < val < 0.55 else "white"
            ax.text(j, i, f"{val:.3f}", ha="center", va="center", color=color, fontsize=8)

    # 5. Configuration des axes (Bits 0 à 7)
    ax.set_xticks(np.arange(8))
    ax.set_yticks(np.arange(8))
    ax.set_xticklabels([f"B{i}" for i in range(8)])
    ax.set_yticklabels([f"B{i}" for i in range(8)])

    # Titres en anglais pour ePrint/arXiv
    ax.set_title("Strict Avalanche Criterion (SAC) Matrix", fontweight='bold', pad=15)
    ax.set_xlabel("Output Bit Index")
    ax.set_ylabel("Inverted Input Bit Index")

    # 6. Exportation Haute Qualité
    plt.tight_layout()
    # bbox_inches='tight' est crucial pour ne pas avoir de flou ou de décalage dans LaTeX
    plt.savefig(filename, bbox_inches='tight', format='pdf', dpi=300)
    print(f"✅ Heatmap sauvegardée en haute définition : {filename}")
    plt.show()

# Exemple d'utilisation avec ta variable 'matrix'
# save_sac_heatmap(matrix)

# --- EXÉCUTION ---
sbox_data = load_sbox("sbox.csv")
if sbox_data is not None:
    matrix = test_sac(sbox_data)
    save_sac_heatmap(matrix)
