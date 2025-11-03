# Registre de Traitement des Données - Digital Social Score

**Organisme** : ESIGELEC  
**Date de création** : [À compléter]  
**Responsable du traitement** : [Nom de l'équipe]  
**DPO (si applicable)** : [N/A]

---

## 1. Identification du Traitement

### Nom du traitement
**API Digital Social Score - Détection de toxicité dans les textes**

### Finalité du traitement
Analyser et scorer automatiquement le niveau de toxicité dans des commentaires ou textes en ligne pour permettre une modération automatisée et la protection des utilisateurs contre les contenus haineux, insultants ou harcelants.

### Base légale (RGPD Art. 6)
- [ ] Consentement de la personne concernée
- [x] **Intérêt légitime** : Modération de contenu et protection des utilisateurs
- [ ] Exécution d'un contrat
- [ ] Obligation légale
- [ ] Sauvegarde des intérêts vitaux
- [ ] Mission d'intérêt public

**Justification** : L'analyse de toxicité répond à un intérêt légitime de maintenir un environnement en ligne sûr et respectueux.

---

## 2. Catégories de Données Traitées

### 2.1 Données Collectées

| Catégorie | Type de données | Exemple | Caractère sensible |
|-----------|----------------|---------|-------------------|
| **Données de contenu** | Textes soumis à analyse | "Ce commentaire..." | Non |
| **Données techniques** | Adresse IP (temporaire) | 192.168.1.1 | Non |
| **Métadonnées** | Timestamp, identifiant session | 2025-11-03T10:00:00 | Non |

### 2.2 Données Personnelles Identifiées dans les Textes

⚠️ **Potentiellement présentes** dans les textes soumis :
- Noms de personnes (ex: "Jean Dupont est méchant")
- Adresses email
- Numéros de téléphone
- Identifiants utilisateurs

**Traitement appliqué** : ✅ **Anonymisation systématique avant stockage**

---

## 3. Personnes Concernées

- Utilisateurs de plateformes utilisant l'API
- Auteurs de commentaires/textes analysés
- Modérateurs de contenu

**Nombre approximatif** : [Estimation basée sur le volume d'utilisation]

---

## 4. Destinataires des Données

| Destinataire | Finalité | Type d'accès |
|--------------|----------|--------------|
| **Système d'IA** | Analyse de toxicité | Automatique |
| **Logs système** | Monitoring et sécurité | Pseudonyme uniquement |
| **Administrateurs** | Maintenance technique | Données anonymisées |

**Aucun transfert vers des tiers commerciaux.**

---

## 5. Durée de Conservation

| Type de données | Durée | Justification |
|-----------------|-------|---------------|
| **Textes analysés** | ❌ Non stockés | Analyse en temps réel uniquement |
| **Scores calculés** | ❌ Non stockés | Retournés directement au client |
| **Logs techniques** | 90 jours | Conformité sécurité (ANSSI) |
| **Logs d'erreurs** | 30 jours | Débogage et maintenance |

**Suppression automatique** après expiration des durées.

---

## 6. Mesures de Sécurité

### 6.1 Mesures Techniques

- ✅ **Chiffrement en transit** : HTTPS/TLS 1.3
- ✅ **Chiffrement au repos** : AES-256 (logs)
- ✅ **Authentification** : JWT ou API Key
- ✅ **Anonymisation** : NER + Masquage automatique
- ✅ **Validation des entrées** : Protection injection
- ✅ **Rate limiting** : Protection contre abus

### 6.2 Mesures Organisationnelles

- [ ] Accès restreint par IAM
- [ ] Logs d'accès aux systèmes
- [ ] Formation RGPD de l'équipe
- [ ] Procédure d'incident de sécurité
- [ ] Revue annuelle de la conformité

---

## 7. Transferts Internationaux

**Localisation des données** : 
- [x] Union Européenne uniquement
- [ ] Clauses contractuelles types (CCT)
- [ ] Privacy Shield
- [ ] Autre : [À préciser]

**Hébergement Cloud** : [AWS / GCP / Scaleway - région EU]

---

## 8. Droits des Personnes

### Droits applicables (RGPD Chapitre 3)

| Droit | Applicable | Modalités |
|-------|-----------|-----------|
| **Droit d'accès** (Art. 15) | ⚠️ Limité | Aucune donnée stockée identifiable |
| **Droit de rectification** (Art. 16) | ❌ Non | Pas de stockage |
| **Droit à l'effacement** (Art. 17) | ✅ Oui | Suppression logs sur demande |
| **Droit à la portabilité** (Art. 20) | ❌ Non | Pas de données personnelles |
| **Droit d'opposition** (Art. 21) | ✅ Oui | Ne pas utiliser l'API |

**Contact pour exercice des droits** : [email@esigelec.fr]

---

## 9. Analyse d'Impact (AIPD)

### 9.1 Risques Identifiés

| Risque | Gravité | Probabilité | Mesure de mitigation |
|--------|---------|-------------|---------------------|
| Fuite de données personnelles | Élevée | Faible | Anonymisation systématique |
| Attaque par injection | Moyenne | Moyenne | Validation stricte des entrées |
| Déni de service (DoS) | Moyenne | Moyenne | Rate limiting + WAF |
| Biais du modèle IA | Moyenne | Moyenne | Tests d'équité réguliers |

### 9.2 Nécessité d'une AIPD Complète

- [ ] Oui - Traitement à grande échelle de données sensibles
- [x] **Non** - Risques limités grâce à l'anonymisation

---

## 10. Sous-traitants et Co-responsables

| Entité | Rôle | Localisation | Contrat RGPD |
|--------|------|--------------|--------------|
| AWS / GCP / Scaleway | Hébergement Cloud | EU | ✅ Oui - DPA signé |
| [Autre] | [Description] | [Pays] | ✅/❌ |

---

## 11. Violations de Données

### Procédure en cas d'incident

1. **Détection** : Monitoring automatique + alertes
2. **Évaluation** : Gravité et impact
3. **Notification CNIL** : Si risque élevé (< 72h)
4. **Information personnes concernées** : Si risque élevé pour leurs droits
5. **Mesures correctives** : Patch, rotation clés, etc.

**Registre des violations** : [À créer si incident]

---

## 12. Conformité et Audits

| Élément | Statut | Date dernière vérification |
|---------|--------|---------------------------|
| Registre de traitement | ✅ Complété | [Date] |
| Politique de confidentialité | ⏳ À rédiger | - |
| Analyse d'impact (si req.) | ⏳ À faire | - |
| Tests de sécurité | ⏳ À planifier | - |
| Formation RGPD équipe | ⏳ À planifier | - |

---

## 13. Documentation Complémentaire

### Documents associés
- [ ] Politique de confidentialité
- [ ] Conditions Générales d'Utilisation (CGU)
- [ ] Documentation technique de l'API
- [ ] Procédure de gestion des incidents
- [ ] Guide d'anonymisation

### Revue et mise à jour
- **Fréquence** : Annuelle ou lors de changements significatifs
- **Prochaine revue** : [Date + 1 an]
- **Responsable** : [Nom/Fonction]

---

**Dernière mise à jour** : [Date]  
**Version** : 1.0
