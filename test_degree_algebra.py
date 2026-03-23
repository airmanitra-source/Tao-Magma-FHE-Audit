import numpy as np
import os

# ==========================================================
# 1. CHARGEMENT ET RÉPARATION DE LA S-BOX (IDENTIQUE AU TEST QUANTIQUE)
# ==========================================================
def load_sbox(filename="sbox.csv"):
    if not os.path.exists(filename):
        print(f"Erreur : '{filename}' introuvable.")
        return None
    with open(filename, 'r') as f:
        content = f.read().strip()
    sbox = [int(x) for x in content.split(',')][:256]
    
    # Mapping P=257 -> 256 pour l'unitarité informatique
    if any(x >= 256 for x in sbox):
        actual_vals = set(x for x in sbox if x < 256)
        missing_val = list(set(range(256)) - actual_vals)[0]
        sbox = [missing_val if x >= 256 else x for x in sbox]
    
    return np.array(sbox, dtype=np.uint8)

# ==========================================================
# 2. ANALYSE DE LA RÉSISTANCE AUX ATTAQUES
# ==========================================================
def perform_audit(sbox):
    n = 8
    size = 256
    print(f"--- Audit de Sécurité S-Box (Dimension {size}) ---")

    # A. Uniformité Différentielle (DDT)
    # Mesure la résistance à la cryptanalyse différentielle
    ddt = np.zeros((size, size), dtype=int)
    for delta_in in range(size):
        for x in range(size):
            delta_out = sbox[x] ^ sbox[x ^ delta_in]
            ddt[delta_in, delta_out] += 1
    
    # On cherche le maximum dans la DDT (en ignorant la ligne 0)
    max_ddt = np.max(ddt[1:, :])
    print(f"Uniformité Différentielle (Max DDT) : {max_ddt}")

    # B. Non-linéarité (LAT)
    # Mesure la distance à la fonction linéaire la plus proche
    # Une non-linéarité élevée bloque la cryptanalyse linéaire
    def get_bit(n, i):
        return (n >> i) & 1

    # Calcul simplifié de la non-linéarité via Walsh-Hadamard Transform
    # Pour 8 bits, le max théorique est ~120 (AES = 112)
    lat_max = 0
    for a in range(1, size): # masques d'entrée
        for b in range(1, size): # masques de sortie
            correlation = 0
            for x in range(size):
                # Produit scalaire binaire
                input_bit = bin(a & x).count('1') % 2
                output_bit = bin(b & sbox[x]).count('1') % 2
                if input_bit == output_bit:
                    correlation += 1
                else:
                    correlation -= 1
            lat_max = max(lat_max, abs(correlation))
    
    non_linearity = (size // 2) - (lat_max // 2)
    print(f"Non-linéarité : {non_linearity}")

    # ==========================================================
    # 3. INTERPRÉTATION POUR L'ARTICLE 2026
    # ==========================================================
    print("\n--- Verdict pour la publication ---")
    if max_ddt <= 8:
        print("[RÉSISTANCE DIFFÉRENTIELLE] Excellente (Score < 10)")
    elif max_ddt <= 16:
        print("[RÉSISTANCE DIFFÉRENTIELLE] Bonne")
    else:
        print("[ALERTE] Faiblesse différentielle détectée.")

    if non_linearity >= 100:
        print("[RÉSISTANCE LINÉAIRE] Optimale (Niveau AES)")
    elif non_linearity >= 90:
        print("[RÉSISTANCE LINÉAIRE] Très robuste")
    else:
        print("[ALERTE] Trop proche d'une fonction linéaire.")

# --- EXÉCUTION ---
sbox_data = load_sbox("sbox.csv")
if sbox_data is not None:
    perform_audit(sbox_data)
