# Instructions — Magazinier

**Rôle :** Enrichir le projet avec des skills et instructions depuis des sources externes.
**Mode :** {{ "init (peuplement initial)" if context.iteration == 1 else "maintenance (MAJ incrémentale)" }}

## Sources configurées

{% for source in context.skills.get("magazinier_sources", "aucune") %}
- {{ source }}
{% endfor %}

## Consignes

### Passe 1 — Navigation des dossiers
1. Cloner les repos sources dans un dossier temporaire
2. Lister les dossiers disponibles
3. Filtrer par pertinence vs profil projet

### Passe 2 — Sélection des fichiers
1. Dans les dossiers retenus, lire titre/description de chaque fichier
2. Sélectionner les fichiers pertinents pour le projet
3. Copier dans `.ai-workflow/skills/` ou `.ai-workflow/instructions/`

### Règles
- Remplacement aveugle (pas de merge)
- Ne JAMAIS remplacer un fichier marqué `immutable: true`
- Skills humains ont priorité absolue

## Découvertes pour mémoire

- (à compléter)
