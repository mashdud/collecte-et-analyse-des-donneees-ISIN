# Récupération du prix d’un fonds commun de placement (ISIN : IE0002XZSHO1) depuis JustETF

# Fonctionnalités
Conçu pour calculer les principaux indicateurs financiers, notamment :

- la performance,
- la volatilité,
- les rendements attendus,
- et le drawdown maximal (perte maximale enregistrée).

# 
├── collector.py        
├── analyzer.py         
├── main.py                
├── requirements.txt  
├── venv/               
└── README.md           


1. Requirements

Python ≥ 3.7
Dependencies listed in requirements.txt:

```bash
pip install -r requirements.txt
```
2. Installation

Clonez ou téléchargez les fichiers du projet

Créez et activez un environnement virtuel (recommandé) :

```bash
python -m venv venv
source venv/bin/activate # Linux/Mac
.\venv\Scripts\activate # Windows
```
4. Exécution de l'application :

```bash
python main.py
```


# Comment ça fonctionne
1. Collecte de données (collector.py)
- Récupère les données depuis l'API de JustETF pour des périodes définies
- Gère le format de variation relative de JustETF (variation en pourcentage depuis la date de base)
- Convertit les pourcentages en série de prix absolus
- Implémente une logique de relance en cas d’échec pour assurer la fiabilité de l’API


2. Analyse financière (analyzer.py)
- Performance : Calcul du rendement total → (prix_fin / prix_début - 1) * 100
- Volatilité : Écart-type annualisé basé sur √252 jours de bourse
- Rendement attendu : Moyenne des rendements journaliers annualisée → (moyenne_journalière * 252)
Max Drawdown : Baisse maximale du pic au creux via un maximum glissant


# Détails Techniques
Format des données API
JustETF renvoie les données dans le format suivant :

json
{
  "series": [
    {"date": "2025-04-23", "value": {"raw": 0.0}},
    {"date": "2025-04-24", "value": {"raw": 1.4}},
    {"date": "2025-04-25", "value": {"raw": 2.2}}
  ],
  "price": {"raw": 5.38}
}

📌 Explication :

-le champseries contient les variations en pourcentage par rapport à la date de base.
-Le champ price est le prix de base correspondant à 0.0% (c’est-à-dire le point de départ).

Chaque valeur de pourcentage doit être convertie en prix absolu avec la formule suivante :


#  Exemple de sortie
Period  Performance (%)  Volatility (%)  Expected Return (%)  Max Drawdown (%)  Data Points Start Date   End Date
   YTD            -5.78           17.91                -8.96             20.23          143 2025-01-01 2025-05-23
    3M            -7.24           21.85               -19.64             18.32           87 2025-02-26 2025-05-23
    6M            -5.78           16.60                -7.15             20.23          177 2024-11-28 2025-05-23
    1Y             6.32           14.08                 5.27             20.23          362 2024-05-27 2025-05-23
    3Y             8.25           13.42                 5.72             20.23          416 2024-04-03 2025-05-23
================================================================================
Results exported to financial_metrics_20250527_123256.csv
Results exported to financial_metrics_20250527_123256.json

 SUMMARY:
• Periods analyzed: 5
• Best performance: 3Y (8.25%)
• Highest volatility: 3M (21.85%)
• Maximum drawdown: YTD (20.23%)









https://github.com/user-attachments/assets/02d60d35-6253-43e6-a248-8e371cfb3c93



