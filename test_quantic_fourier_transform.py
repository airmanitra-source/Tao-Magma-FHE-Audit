import numpy as np
import matplotlib.pyplot as plt
import os
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Operator
from qiskit.circuit.library import QFTGate
from qiskit.visualization import plot_histogram

# ==========================================================
# 1. CHARGEMENT DE LA S-BOX EXPORTÉE DEPUIS C#
# ==========================================================
def load_sbox(filename="sbox.csv"):
    if not os.path.exists(filename):
        raise Exception(f"Fichier '{filename}' introuvable.")

    with open(filename, 'r') as f:
        content = f.read().strip()
    
    # Charger les 256 premières valeurs
    sbox = [int(x) for x in content.split(',')][:256]

    # --- RÉPARATION UNITAIRE (P=257 -> 256) ---
    # Si la valeur 256 est présente, on la remplace par le chiffre manquant entre 0 et 255
    if any(x >= 256 for x in sbox):
        actual_values = set(x for x in sbox if x < 256)
        all_possible = set(range(256))
        missing_value = list(all_possible - actual_values)[0]
        
        # On remplace le 256 par la valeur manquante pour garder une permutation parfaite
        sbox = [missing_value if x >= 256 else x for x in sbox]
        print(f"🔧 Réparation effectuée : Valeur 256 remplacée par {missing_value}")

    if len(set(sbox)) != 256:
        print("❌ ERREUR : La S-Box n'est pas une permutation parfaite (collisions).")
        return None

    print(f"✅ S-Box 8-bits (256 entrées) chargée et validée.")
    return np.array(sbox)


# ==========================================================
# 2. CONSTRUCTION DU CIRCUIT D'ATTAQUE QUANTIQUE
# ==========================================================
def run_interference_test(sbox):
    dim = 256
    num_qubits = 8
    
    matrix = np.zeros((dim, dim))
    for x, res in enumerate(sbox):
        matrix[res, x] = 1
    gate = Operator(matrix)
    
    qc = QuantumCircuit(num_qubits)
    
    # ÉTAPE CLÉ : On ne fait pas un H partout (superposition totale)
    # On crée une superposition de DEUX états seulement (ex: 0 et 1)
    # C'est ce qui permet de voir si la S-Box "casse" la structure
    qc.h(0) 
    
   
    qc.append(gate, range(num_qubits))
    
    # Analyse QFT
    qc.append(QFTGate(num_qubits), range(num_qubits))
    
    qc.measure_all()
    return qc

# --- CONFIGURATION STYLE SCIENTIFIQUE ---
plt.style.use('seaborn-v0_8-paper') # Style propre
plt.rcParams.update({
    "text.usetex": False, # Mets True si tu as LaTeX installé sur ton PC
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": 14,
    "legend.fontsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 12
})

def plot_publication_qft(counts, shots=2048):
    # On trie et on prend les top résultats ou un échantillon représentatif
    # Ici on simule tes données de l'image
    labels = list(counts.keys())
    values = list(counts.values())

    fig, ax = plt.subplots(figsize=(10, 6))

    # Barres en bleu nuit (plus pro que le bleu standard)
    bars = ax.bar(labels, values, color='#1f4e79', edgecolor='black', linewidth=0.8)

    # Titres et labels en anglais (standard pour arXiv)
    ax.set_title("Quantum Spectral Analysis: QFT on Seeded Cubic S-Box", fontweight='bold', pad=20)
    ax.set_ylabel("Measurement Count", fontweight='bold')
    ax.set_xlabel("Basis State $|x\\rangle$", fontweight='bold')
    
    # Ligne horizontale de la moyenne théorique (bruit blanc idéal)
    # 2048 / 256 = 8
    ax.axhline(y=8, color='red', linestyle='--', alpha=0.6, label='Theoretical Ideal (White Noise)')
    
    # Grille légère
    ax.grid(axis='y', linestyle=':', alpha=0.7)
    
    # Rotation des labels X pour la lisibilité
    plt.xticks(rotation=45, ha='right')
    
    # Affichage des valeurs au-dessus des barres (facultatif mais utile)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    ax.legend()
    plt.tight_layout()

    # --- EXPORTATION CRUCIALE ---
    # Le format PDF est vectoriel : il reste net à n'importe quel zoom
    plt.savefig("qft_analysis.pdf", bbox_inches='tight', dpi=300)
    plt.show()

# Exemple d'appel avec tes données
# counts = {"11101111": 13, "11110000": 5, ...}
# plot_publication_qft(counts)


# ==========================================================
# 3. EXÉCUTION ET AFFICHAGE
# ==========================================================
try:
    my_sbox = load_sbox("sbox.csv")
    
    if my_sbox is not None:
        print("Lancement de la simulation quantique (shots=2048)...")
        qc = run_interference_test(my_sbox)
        
        simulator = Aer.get_backend('qasm_simulator')
        qc_compiled = transpile(qc, simulator)
        
        # Exécution
        job = simulator.run(qc_compiled, shots=2048)
        result = job.result()
        counts = result.get_counts()

        # Filtrage pour l'affichage (Top 15 résultats)
        top_counts = dict(sorted(counts.items(), key=lambda item: item, reverse=True)[:15])
        
        print("\n--- RÉSULTAT DE L'ANALYSE ---")
        plot_publication_qft(top_counts)

except Exception as e:
    print(f"Erreur : {e}")
