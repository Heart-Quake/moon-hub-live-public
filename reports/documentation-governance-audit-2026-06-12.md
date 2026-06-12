# Audit gouvernance documentaire des outils live Automation SEO

Date : 2026-06-12

Périmètre audité :

- Similarweb Free API Cockpit, `Heart-Quake/Similarweb-free-API`
- Amazon Reviews Scraper, `Heart-Quake/amazon-scraper`
- Analyse Content Gap, `Heart-Quake/analyse-content-gap`
- SEO Audit Automator, `Heart-Quake/automation-seo-audit-tech`
- SILO, `Heart-Quake/silo`
- Générateur de Spin Content, `Heart-Quake/Content-Spinner`
- Keyword Categorization App, `Heart-Quake/automation-seo-keyword-categorization`

## Angle d'audit

Objectif : vérifier si la documentation permet à un dev vibe coding exigeant, ou à un agent de code, de développer vite sans casser la production.

La documentation optimale doit permettre de répondre sans deviner à ces questions :

- Quel est le rôle produit de l'outil et son périmètre exact ?
- Quelle est la source live, le fichier d'entrée Streamlit et la branche de déploiement ?
- Comment installer, lancer, tester et déployer ?
- Quelles données d'entrée sont attendues, avec quels formats et limites ?
- Quels modules portent la logique métier ?
- Quels secrets, fichiers runtime ou outputs sont interdits dans Git ?
- Quels tests protègent les règles métier ?
- Comment diagnostiquer les incidents fréquents ?
- Quelles conventions UI/design sont obligatoires ?
- Quel backlog documentaire ou technique est connu ?

## Score global

| Projet | Score | Niveau | Diagnostic court |
|---|---:|---|---|
| SILO | 7.5/10 | Bon mais dispersé | Documentation riche, tests présents, mais certains docs sont datés et le runbook Streamlit/GSC doit être consolidé. |
| Amazon Reviews Scraper | 7/10 | Solide mais à assainir | Bonne recette fonctionnelle et CI, mais README contient encore des placeholders et beaucoup de promesses Docker/CI à vérifier. |
| Générateur de Spin Content | 6.5/10 | Correct | README clair, tests utiles, mais documentation trop locale et pas assez orientée live Streamlit/gouvernance. |
| Similarweb Free API Cockpit | 5/10 | Moyen | README fonctionnel historique, mais ne documente pas assez la version live, les modules récents, le circuit breaker et les risques d'API non officielle. |
| Keyword Categorization App | 3/10 | Faible | README minimal, pas de tests, pas d'architecture ni de guide d'entrée/sortie. Risque élevé pour reprise agent/dev. |
| SEO Audit Automator | 2.5/10 | Faible | README trop court, pas de tests, aucune documentation des scénarios d'audit ni du format Screaming Frog attendu. |
| Analyse Content Gap | 2/10 | Critique | README quasi vide alors que l'app est complexe, riche en règles métier et déjà exposée à des incidents runtime. |

## Grille de maturité cible

Chaque repo devrait contenir au minimum :

```text
README.md
docs/
  ARCHITECTURE.md
  RUNBOOK.md
  DATA_CONTRACTS.md
  TESTING.md
  DEPLOYMENT.md
  CHANGELOG.md
  TROUBLESHOOTING.md
.env.example, si secrets ou env vars
tests/, dès qu'une régression métier serait coûteuse
```

Pour les outils Streamlit live, le README doit commencer par un bloc standard :

```text
Produit :
Live URL :
Repo GitHub :
Branche live :
Entrypoint Streamlit :
Commande locale :
Commande de test :
Dernier contrôle live :
Secrets / fichiers runtime :
Owner fonctionnel :
```

## Findings transverses

### P0, documentation source de vérité absente ou trop faible

Trois outils n'ont pas de documentation suffisante pour une reprise professionnelle :

- `analyse-content-gap`
- `automation-seo-audit-tech`
- `automation-seo-keyword-categorization`

Impact :

- Un agent risque de modifier la logique métier sans comprendre les formats d'entrée.
- Les incidents Streamlit sont plus longs à diagnostiquer.
- Les limites de fichiers, dépendances lourdes et cas d'erreur ne sont pas explicités.
- Les critères de non-régression ne sont pas visibles.

Action recommandée :

- Créer un README complet et `docs/DATA_CONTRACTS.md` pour chacun.
- Ajouter `docs/RUNBOOK.md` orienté Streamlit Cloud.
- Ajouter au moins des tests smoke ou fixtures pour les repos sans tests.

### P0, incohérence source live vs documentation

Certaines docs mentionnent encore des dépôts ou chemins qui ne sont pas la source live observée.

Exemples :

- `automation-seo-audit-tech` documente `YN-CodingClub/automation-seo-audit-tech`, alors que le hub live cible aussi `Heart-Quake/automation-seo-audit-tech`.
- `automation-seo-keyword-categorization` documente `streamlit_app.py`, alors que le manifest live audite `app/main.py` comme entrypoint métier et `streamlit_app.py` existe comme wrapper.
- `silo/DEPLOY_STREAMLIT.md` utilise `TON_USERNAME/silo`, pas le repo live réel.

Action recommandée :

- Standardiser une section "Source live vérifiée" dans chaque README.
- Reprendre les URLs et entrées depuis `moon-hub-live-public/tools_audit_manifest.json`.

### P1, design system non documenté dans les outils

Les 7 apps utilisent désormais `automation_seo_theme.py`, `logo-sidebar-cream.png`, `.tool-hero` et `data-app-build`, mais cette convention est surtout implicite.

Impact :

- Un dev peut réintroduire un titre legacy ou un composant non conforme.
- Les futurs outils peuvent diverger du hub.

Action recommandée :

- Ajouter `docs/DESIGN_SYSTEM.md` ou une section README identique dans chaque repo :
  - obligation de `apply_automation_seo_theme()`
  - logo sidebar
  - hero `.tool-hero`
  - build marker caché
  - patterns interdits : `#2BAF9C`, `DR SEO`, `base = "light"`

### P1, runbooks d'incident Streamlit insuffisants

L'incident `Bad message format / SessionInfo before it was initialized` sur `space-gap` a montré qu'un composant HTML custom pouvait fragiliser Streamlit Cloud.

Action recommandée :

- Documenter dans chaque runbook :
  - symptômes Running/Connecting
  - où lire le build marker live
  - quoi vérifier dans l'iframe Streamlit
  - composants à éviter ou à isoler
  - procédure rebuild/restart
  - commande de smoke test locale

### P1, tests et fixtures absents sur deux outils critiques

Repos sans tests détectés :

- `automation-seo-audit-tech`
- `automation-seo-keyword-categorization`

Impact :

- Les règles de scoring audit Screaming Frog et de catégorisation keyword ne sont pas protégées.
- La documentation ne peut pas pointer vers des scénarios vérifiables.

Action recommandée :

- Ajouter `tests/fixtures/` avec petits CSV anonymisés.
- Tester au minimum :
  - lecture des fichiers
  - détection des colonnes
  - sortie attendue sur 3 à 5 lignes
  - compile Streamlit

## Audit par projet

### Similarweb Free API Cockpit

Docs présentes :

- `README.md`
- tests existants : `tests/test_similar_stabilization.py`, `test.py`, `test_batch.py`

Points forts :

- README explique le endpoint, les fonctions Python, le batch, le cache et les limites API.
- Les risques de rate limit et d'API non officielle sont mentionnés.
- Tests de stabilisation présents.

Points faibles :

- README centré sur le projet historique, pas sur l'app live Yuri & Neil.
- Ne documente pas les modules récents : `core_async.py`, `rate_state.py`, `ui_*`, `cache.py`, `config.py`.
- Pas de runbook pour cooldown, circuit breaker, erreurs 403/429, cache SQLite.
- Pas de section déploiement Streamlit Cloud avec branche exacte `2026-01-23-sa97` observée sur le clone de déploiement.
- Pas de conventions design/build marker documentées.

Priorités :

1. Créer `docs/ARCHITECTURE.md` avec flux `streamlit_app -> core_async -> similar -> cache/rate_state -> ui_*`.
2. Créer `docs/RUNBOOK.md` pour cooldown, erreurs API, cache et rebuild Streamlit.
3. Ajouter un bloc source live dans le README.

### Amazon Reviews Scraper

Docs présentes :

- `README.md`
- `docs/recette-fonctionnelle.md`
- `docs/ROADMAP.md`
- `docs/compte-rendu-2025-10-03.md`
- CI GitHub, `pyproject.toml`, `pytest.ini`, `Makefile`, `env.example`

Points forts :

- Documentation fonctionnelle solide.
- Recette E2E utile.
- Variables d'environnement et conformité scraping documentées.
- Tests et CI présents.
- Roadmap structurée.

Points faibles :

- README contient des placeholders `your-username`, liens GitHub génériques et badges non adaptés.
- README très large, mélange CLI, Docker, conformité, architecture et usage, ce qui ralentit l'onboarding.
- Documentation Streamlit live moins nette que la documentation CLI.
- Le risque légal/compliance est mentionné, mais pas traduit en règles produit dans l'UI et le runbook.
- Pas de décision claire sur ce qui est supporté en live Community Cloud vs local.

Priorités :

1. Remplacer tous les placeholders par les repos réels.
2. Séparer `docs/CLI.md`, `docs/STREAMLIT_LIVE.md`, `docs/COMPLIANCE.md`.
3. Ajouter une matrice "supporté local / supporté Streamlit Cloud".

### Analyse Content Gap

Docs présentes :

- `README.md` quasi vide.
- Tests : `test_ahrefs_consolidation.py`, `test_export_formats.py`, `test_keyword_ngrams.py`, `test_keyword_normalization.py`.

Points forts :

- Le code dispose de tests métier utiles.
- L'app a une logique riche : Ahrefs, Semrush, normalisation, n-grams, templates URL, exports.
- Le live dispose maintenant d'un build marker vérifiable.

Points faibles critiques :

- README ne documente pas le produit réel.
- Aucun contrat de données Ahrefs/Semrush.
- Aucune architecture des fonctions clés dans `app.py`, qui est très volumineux.
- Aucun runbook pour les incidents Streamlit.
- Aucune doc sur l'incident récent `Bad message format` et l'interdiction des composants HTML custom non nécessaires.
- Aucune doc de limites : taille fichiers, encodage, séparateur, colonnes obligatoires.

Priorités :

1. Réécrire `README.md` intégralement.
2. Créer `docs/DATA_CONTRACTS.md` avec exemples Ahrefs/Semrush et colonnes obligatoires.
3. Créer `docs/ARCHITECTURE.md` pour cartographier les blocs d'un `app.py` monolithique.
4. Créer `docs/RUNBOOK.md` incluant l'incident `SessionInfo before initialized`.
5. Ajouter des fixtures anonymisées documentées.

### SEO Audit Automator

Docs présentes :

- `README.md` court.
- Pas de tests.

Points forts :

- README indique l'objectif, le déploiement Streamlit et le type d'entrée.
- Code séparé entre `streamlit_app.py` et `audit_engine.py`.

Points faibles critiques :

- Aucun contrat précis d'export Screaming Frog.
- Aucun inventaire des scénarios d'audit.
- Aucun test des règles déterministes.
- Aucun guide de modification d'une règle d'audit.
- Aucun runbook de déploiement/rebuild.
- Pas de sample CSV anonymisé.

Priorités :

1. Créer `docs/AUDIT_RULES.md` listant chaque issue, colonnes requises, scope, priorité, exemple.
2. Créer `docs/DATA_CONTRACTS.md` pour Screaming Frog.
3. Ajouter un CSV fixture et des tests unitaires sur `audit_engine.py`.
4. Étendre le README avec commande locale, tests, live URL, design system.

### SILO

Docs présentes :

- `README.md`
- `PRD.md`
- `TEST_SPEC.md`
- `TEST_RESULTS.md`
- `DEPLOY_STREAMLIT.md`
- `ADJUSTMENTS.md`
- `scripts/README.md`
- Tests nombreux.

Points forts :

- Très bon niveau de détail produit et technique.
- PRD et test strategy présents.
- Runbook partiel Streamlit.
- Formats GSC, ZIP HTML, crawl Screaming Frog et cache documentés.
- Tests couvrent parser, NLP, scoring, GSC, priorisation.

Points faibles :

- Documentation dispersée, certaines pages sont datées ou en statut draft.
- `TEST_RESULTS.md` mentionne des résultats historiques et un pipeline "en cours", potentiellement obsolète.
- `DEPLOY_STREAMLIT.md` n'utilise pas le repo live réel.
- Les secrets GSC (`client_secret.json`, token) sont documentés dans l'UI/code mais pas dans un runbook sécurité complet.
- Les tests modifient des outputs CSV suivis, signal de gouvernance à corriger.

Priorités :

1. Créer `docs/INDEX.md` ou simplifier le README pour pointer vers les bons docs.
2. Remplacer les infos génériques de déploiement par la source live réelle.
3. Ajouter `docs/SECRETS_AND_RUNTIME.md` pour GSC OAuth, `.runtime/`, `config/client_secret.json`.
4. Corriger les tests pour ne plus modifier les outputs suivis.
5. Archiver ou actualiser `TEST_RESULTS.md`.

### Générateur de Spin Content

Docs présentes :

- `README.md`
- Tests : `test_csv_service.py`, `test_template_engine.py`

Points forts :

- README clair et récent.
- Installation, usage, tests, limites et comportement fonctionnel bien décrits.
- Les règles de template et CSV sont compréhensibles.
- Mentionne la dette Git historique `venv/`.

Points faibles :

- README reste trop local-centric alors que l'app est live.
- Pas de documentation Streamlit Cloud, branche live, repo source `Heart-Quake/Content-Spinner`.
- Pas de `docs/DATA_CONTRACTS.md` séparé pour grammaire spin, variables CSV et formats exports.
- Pas de changelog du refactor récent.
- La dette `venv/` est mentionnée mais pas transformée en action gouvernée.

Priorités :

1. Ajouter un bloc source live et déploiement.
2. Extraire la grammaire dans `docs/TEMPLATE_LANGUAGE.md`.
3. Créer `docs/RELEASE_NOTES.md` pour le refactor moteur/template.
4. Nettoyer `venv/` du suivi Git dans une PR dédiée.

### Keyword Categorization App

Docs présentes :

- `README.md` court.
- Pas de tests.

Points forts :

- README signale les dépendances lourdes et Python 3.11.
- Wrapper Streamlit présent.
- Code organisé en modules `config`, `utils`, `clustering`, `scraping`.

Points faibles critiques :

- Aucun contrat de données d'entrée.
- Aucun détail sur les algorithmes : nettoyage, scraping menu, lemmatisation, clustering, e-commerce detection.
- Aucun test.
- Pas de guide de performance pour `sentence-transformers`, `umap-learn`, `hdbscan`.
- Pas de runbook pour builds Streamlit échoués.
- Pas de documentation des référentiels embarqués.

Priorités :

1. Créer `docs/ARCHITECTURE.md` avec flux `upload -> clean -> e-commerce entities -> clustering -> export`.
2. Créer `docs/DATA_CONTRACTS.md` pour CSV, CSV.gz, ZIP, colonnes keyword/volume.
3. Ajouter des fixtures et tests sur `utils.py` et `clustering.py`.
4. Créer `docs/PERFORMANCE.md` pour dépendances lourdes et limites Community Cloud.

## Backlog priorisé

### Sprint 1, stabilisation documentaire critique

1. Réécrire README `analyse-content-gap`.
2. Créer `docs/DATA_CONTRACTS.md` pour Content Gap, SEO Audit, Keyword Categorization.
3. Créer `docs/RUNBOOK.md` pour Content Gap avec l'incident `Bad message format`.
4. Ajouter source live standard dans les 7 README.
5. Corriger les placeholders Amazon et SILO.

### Sprint 2, gouvernance dev

1. Ajouter tests fixtures pour SEO Audit Automator.
2. Ajouter tests fixtures pour Keyword Categorization.
3. Créer `docs/DESIGN_SYSTEM.md` commun ou synchronisé.
4. Créer `docs/ARCHITECTURE.md` sur Content Gap, Keyword, SEO Audit, Similarweb.
5. Corriger les tests SILO qui modifient `data/output/*.csv`.

### Sprint 3, industrialisation

1. Ajouter un script d'audit documentaire dans le hub, proche de `scripts/audit_live_tools.py`.
2. Ajouter un badge ou un champ `docs_maturity` dans `tools_audit_manifest.json`.
3. Créer un template `docs/` commun réutilisable pour tout nouvel outil.
4. Ajouter une check-list PR : README mis à jour, data contract mis à jour, tests, build marker, design system.

## Template documentaire recommandé

À appliquer repo par repo :

````markdown
# Nom de l'outil

## Source live

- Live URL :
- Repository :
- Branch :
- Entrypoint :
- Build marker attendu :

## Rôle produit

- Problème résolu :
- Utilisateur cible :
- Inputs :
- Outputs :
- Hors périmètre :

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run <entrypoint>
python3 -m pytest
```

## Architecture

- Entrypoint :
- Modules métier :
- Modules UI :
- Fichiers runtime :

## Contrats de données

- Formats acceptés :
- Colonnes obligatoires :
- Encodages :
- Taille recommandée :
- Erreurs utilisateur fréquentes :

## Tests

- Commande :
- Fixtures :
- Ce qui est couvert :
- Ce qui n'est pas couvert :

## Déploiement Streamlit

- Paramètres :
- Secrets :
- Rebuild :
- Smoke test live :

## Troubleshooting

- Symptôme :
- Cause probable :
- Vérification :
- Correction :

## Design system

- `automation_seo_theme.py`
- `logo-sidebar-cream.png`
- `.tool-hero`
- `data-app-build`
- patterns interdits
````

## Conclusion

Le niveau documentaire actuel permet de maintenir certains outils, mais pas encore de développer "dans les meilleures conditions possibles" sur l'ensemble du portefeuille.

La priorité n'est pas d'ajouter beaucoup de documentation, mais de créer une documentation de gouvernance courte, stable et vérifiable :

- source live,
- contrats de données,
- runbook,
- architecture,
- tests,
- design system.

Le risque principal est concentré sur trois outils : Content Gap, SEO Audit Automator et Keyword Categorization. SILO et Amazon peuvent servir de base, mais doivent être nettoyés et alignés sur la réalité live.
