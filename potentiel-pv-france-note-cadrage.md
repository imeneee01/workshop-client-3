# Potentiel photovoltaïque en France — Note de cadrage


> **Objet** — Cadrer un projet exploratoire d'une semaine visant à caractériser le potentiel photovoltaïque (PV) en France métropolitaine, avec un focus sur la rentabilité économique des installations en toiture tertiaire (9 à 500 kWc). Le projet s'inscrit dans une réflexion autour de l'outil Simeo, qui évalue les économies énergétiques liées aux actions de rénovation énergétique.

---

## 1. Contexte

### 1.1 Cadre métier — Simeo et la rénovation énergétique

Simeo, avec le module énergétique, est un outil d'évaluation des économies énergétiques apportées par les actions de rénovation, notamment dans le cadre des obligations réglementaires pesant sur les bâtiments tertiaires (décret tertiaire, RE2020, ...). À ce jour, Simeo couvre principalement les leviers d'**efficacité énergétique passive** (isolation, ventilation, équipements). L'ajout d'un volet **production locale d'énergie** — au premier rang duquel le photovoltaïque — permettrait d'élargir le périmètre d'analyse à un levier de plus en plus présent dans les arbitrages de rénovation.

### 1.2 Pourquoi le PV s'inscrit naturellement dans ce cadre

Trois raisons convergent :

- **Réglementaire** : la loi APER (mars 2023) impose une solarisation progressive des grandes toitures tertiaires et des parkings extérieurs > 1 500 m². Les exploitants doivent quantifier l'impact économique de ces obligations.
- **Économique** : la baisse continue du coût des modules (–80 % en dix ans) rend l'autoconsommation tertiaire de plus en plus rentable, particulièrement face à la hausse durable du prix de l'électricité réseau.
- **Méthodologique** : contrairement à une isolation, dont le gain dépend de paramètres très spécifiques au bâtiment, **l'estimation de la production PV est relativement bien standardisée** (gisement solaire + caractéristiques d'installation), ce qui en fait un cas d'usage abordable pour un premier prototype.

### 1.3 Glossaire essentiel

Avant d'aller plus loin, quelques termes incontournables (le glossaire complet figure en annexe) :

| Terme | Définition courte |
|---|---|
| **kWc** (kilowatt-crête) | Puissance maximale d'une installation dans des conditions standard de test (1 000 W/m², 25 °C). Unité de "taille" de l'installation. Ne dit pas la production réelle. |
| **kWh/kWc/an** (facteur de production) | Énergie produite par an pour chaque kWc installé. Dépend de la localisation. En France : ~900 (Nord) à ~1 500 (Sud). |
| **Gisement solaire** | Quantité d'énergie solaire reçue au sol, en kWh/m²/an. Donnée physique, indépendante de toute installation. |
| **LCOE** (Levelized Cost Of Electricity) | Coût moyen actualisé de l'énergie produite sur toute la durée de vie, en €/kWh. L'indicateur de référence pour comparer des moyens de production. |
| **Payback** | Nombre d'années pour que les revenus cumulés égalent l'investissement initial. |
| **TRI** (Taux de Rendement Interne) | Taux d'actualisation annulant la VAN. Mesure la rentabilité financière. |
| **CAPEX / OPEX** | Investissement initial / coûts d'exploitation annuels. |

### 1.4 La hiérarchie du potentiel

Le mot "potentiel" recouvre plusieurs réalités emboîtées qu'il est essentiel de distinguer. Chaque couche est strictement plus petite que la précédente :

| Niveau | Définition | Unité typique |
|---|---|---|
| **1. Gisement** | Ressource solaire brute (irradiance reçue au sol) | kWh/m²/an |
| **2. Potentiel technique** | Ce qui est physiquement installable (surfaces × rendement panneau) | GW, TWh/an |
| **3. Potentiel exploitable** | Technique – zones interdites (réglementaires, sites classés, contraintes techniques) | GW, TWh/an |
| **4. Potentiel économique** | Exploitable & rentable au prix actuel de l'énergie | GW, TWh/an |
| **5. Potentiel réalisé** | Effectivement installé et raccordé | GW, TWh/an |

**Le ratio entre couches est révélateur.** La France a un gisement supérieur à celui de l'Allemagne, mais un parc installé bien inférieur en GW/habitant : c'est dans la transition gisement → réalisé que se trouvent les frictions (foncier, acceptabilité, économie, raccordement réseau).

---

## 2. Enjeux

### 2.1 Enjeux énergétiques et réglementaires

| Texte | Portée | Implication PV |
|---|---|---|
| **Décret tertiaire (Éco Énergie Tertiaire)** | Bâtiments tertiaires > 1 000 m² | Objectif –40 % de conso d'énergie finale en 2030, –50 % en 2040, –60 % en 2050. Le PV en autoconsommation réduit la conso facturée → contribue à l'atteinte. |
| **Loi APER (mars 2023)** | Parkings > 1 500 m², nouvelles toitures tertiaires > 500 m² | Obligation de solarisation progressive. Transforme le PV de "choix" en "contrainte chiffrable". |
| **RE2020** | Bâtiments neufs | Indirectement : favorise les bâtiments à énergie positive. |
| **REPowerEU** (UE, 2022) | Toute l'UE | Objectif **600 GW de solaire installé d'ici 2030** (vs ~270 GW fin 2024). Trajectoire structurante pour tout l'écosystème. |
| **Tarifs d'achat S21** | Installations ≤ 500 kWc | Tarif réglementé garanti 20 ans. Cadre revenus pour le segment cible. |
| **Prime à l'autoconsommation** | Installations ≤ 100 kWc | Subvention dégressive selon taille (en €/kWc). |

### 2.2 Enjeux économiques

La rentabilité d'une installation PV se joue sur cinq paramètres clés :

1. **CAPEX (€/kWc)** — coût d'installation, fortement dépendant de la taille (effet d'échelle marqué entre 9 et 500 kWc).
2. **OPEX annuels (€/kWc/an)** — maintenance préventive (nettoyage, inspection, monitoring), entretien curatif, assurances, location de toiture éventuelle.
3. **Remplacement onduleur** — l'onduleur a une durée de vie typique de 10-15 ans, contre 25-30 ans pour les modules. Souvent un remplacement à mi-vie est intégré au plan financier.
4. **Production attendue (kWh/an)** — fonction du gisement local, de l'orientation et de l'inclinaison.
5. **Valorisation de l'énergie produite (€/kWh)** — autoconsommation (= prix évité sur facture, ~15-25 c€/kWh HT) vs vente (~7-13 c€/kWh selon segment et régime). **L'autoconsommation est aujourd'hui significativement plus rentable que la vente** pour le tertiaire.

Les indicateurs synthétiques qui en découlent — **LCOE, payback, TRI, VAN** — sont les sorties classiques d'un modèle économique PV et constitueront le cœur du livrable analytique.

### 2.3 Enjeux géographiques

À installation identique, la production peut varier de **+60 %** entre le Nord et le Sud de la France. Cela impacte directement la rentabilité, mais **pas linéairement** : la rentabilité varie aussi avec la structure des coûts locaux (main-d'œuvre, raccordement) et le tarif de l'électricité évitée. Cartographier ces variations à l'échelle départementale est l'un des angles centraux du projet.

À l'échelle européenne, les écarts sont encore plus marqués : l'Espagne et la Grèce produisent ~70 % de plus que la France au kWc installé, ce qui explique en grande partie la dynamique différenciée de déploiement.

### 2.4 Enjeux pour Simeo

L'intégration future d'un module PV dans Simeo nécessiterait de répondre à trois questions, dont ce projet pose les premières briques :

- **Combien produit une installation type** sur tel bâtiment, dans telle région ?
- **Combien coûte-t-elle** à l'installation et à l'exploitation ?
- **Est-elle rentable** dans le cadre réglementaire et tarifaire en vigueur ?

Le projet ne vise pas à construire ce module, mais à **caractériser le terrain de jeu** : ordres de grandeur, dispersion géographique, sources de données disponibles, hypothèses à expliciter.

---

## 3. Besoins

### 3.1 Périmètre retenu

| Dimension | Choix | Justification |
|---|---|---|
| **Géographie** | France métropolitaine (Europe en bonus) | les DROM ont des spécificités tarifaires et techniques distinctes. |
| **Granularité** | Département (≈96 unités) | Bon compromis entre lisibilité cartographique et diversité climatique capturée. |
| **Segment de marché** | Toiture tertiaire 9–500 kWc + (résidentiel) | Aligné avec le champ d'application de Simeo (patrimoine bâti tertiaire). |
| **Échelle d'analyse** | Territoriale agrégée | Pas d'analyse bâtiment par bâtiment (= rôle de Simeo, hors-scope ici). |

### 3.2 Indicateurs cibles

**Indicateurs de production (issus du gisement)**
- Irradiance globale annuelle (kWh/m²/an) par département
- Facteur de production (kWh/kWc/an) pour une installation type
- Production attendue (MWh/an) pour une installation de référence (100 kWc)

**Indicateurs économiques (cœur du projet)**
- **CAPEX** (€/kWc) selon taille d'installation
- **OPEX** (€/kWc/an) incluant maintenance et provisions onduleur
- **LCOE** (€/kWh) par département
- **Payback** (années) par département et par régime de valorisation (autoconso / vente)
- **TRI** (%) sur 25 ans
- **VAN** (€) pour l'installation de référence

<!-- 
**Indicateurs de contexte (nice-to-have)**
- Parc PV installé actuel (MW) par département → comparaison "où la rentabilité est forte" vs "où le déploiement a lieu"
- (Positionnement France vs principaux pays européens) -->

---

## 4. Annexes

### Annexe A — Ordres de grandeur clés

> *Valeurs indicatives, à recouper et dater au moment de l'étude.*

**Production**
- 1 kWc nécessite ~5–7 m² de toiture
- 1 kWc produit ~900 (Nord) à ~1 500 (Sud) kWh/an en France
- Une installation de 100 kWc en zone moyenne produit ~110 MWh/an

**Coûts d'investissement (CAPEX, toiture tertiaire)**
- 9–36 kWc : ~1 500–2 200 €/kWc
- 36–100 kWc : ~1 200–1 600 €/kWc
- 100–500 kWc : ~900–1 300 €/kWc

**Coûts d'exploitation (OPEX)**
- Maintenance courante : ~1–2 % du CAPEX / an
- Soit ~15–30 €/kWc/an
- Remplacement onduleur : ~10–15 % du CAPEX, vers la 10–15ᵉ année

**Valorisation de l'énergie (indicatif)**
- Tarif d'achat S21 (≤ 9 kWc, vente totale) : ~12–15 c€/kWh
- Tarif d'achat S21 (9–100 kWc) : ~9–11 c€/kWh
- Tarif d'achat S21 (100–500 kWc, appels d'offres) : ~7–9 c€/kWh
- Autoconsommation (= prix évité réseau, tertiaire) : ~15–25 c€/kWh HT

**Indicateurs synthétiques typiques (tertiaire France)**
- LCOE : 6–10 c€/kWh
- Payback : 8–14 ans selon régime et localisation
- TRI sur 25 ans : 5–10 %

### Annexe B — Glossaire complet

**Unités**
- **W, kW, MW, GW, TW** — puissance (Watt et multiples)
- **Wh, kWh, MWh, GWh, TWh** — énergie (Wattheure et multiples)
- **kWc / kWp** — kilowatt-crête / kilowatt peak (puissance nominale STC)

**Irradiance et gisement**
- **GHI** — Global Horizontal Irradiance, irradiance globale horizontale
- **DNI** — Direct Normal Irradiance, irradiance directe normale
- **DHI** — Diffuse Horizontal Irradiance, irradiance diffuse
- **POA** — Plane Of Array, irradiance sur le plan du panneau
- **STC** — Standard Test Conditions (1 000 W/m², 25 °C, AM1.5)
- **NOCT** — Nominal Operating Cell Temperature
- **AM1.5** — Air Mass 1.5, spectre solaire de référence

**Technique installation**
- **PR** — Performance Ratio, rendement global du système (typique 0,75–0,85)
- **BoS** — Balance of System (tout sauf les modules : onduleurs, câbles, structures…)
- **Onduleur** — convertit le courant continu (modules) en courant alternatif (réseau)

**Régimes commerciaux**
- **Autoconsommation totale** — toute la production est consommée sur place
- **Autoconsommation avec vente du surplus** — consommation sur place + revente du surplus au réseau
- **Vente totale** — toute la production est injectée et vendue au réseau

**Économie**
- **CAPEX** — Capital Expenditure (investissement initial)
- **OPEX** — Operating Expenditure (coûts opérationnels annuels)
- **LCOE** — Levelized Cost Of Electricity, coût moyen actualisé de l'énergie (€/kWh)
- **Payback** — temps de retour brut ou actualisé (années)
- **TRI / IRR** — Taux de Rendement Interne / Internal Rate of Return (%)
- **VAN / NPV** — Valeur Actuelle Nette / Net Present Value (€)

**Acteurs et outils**
- **ADEME** — Agence de la transition écologique
- **CRE** — Commission de Régulation de l'Énergie
- **RTE** — Réseau de Transport d'Électricité
- **JRC** — Joint Research Centre (Commission européenne)
- **IRENA** — International Renewable Energy Agency
- **PVGIS** — Photovoltaic Geographical Information System (outil JRC)

**Réglementation**
- **Décret tertiaire** — Éco Énergie Tertiaire (dispositif éco-énergie tertiaire)
- **Loi APER** — Loi d'Accélération de la Production d'Énergies Renouvelables (2023)
- **RE2020** — Réglementation Environnementale 2020 (bâtiments neufs)
- **Arrêté S21** — Arrêté tarifaire en vigueur pour les installations ≤ 500 kWc
- **REPowerEU** — Plan européen d'accélération des renouvelables (2022)