# LygosPy

[![PyPI version](https://mintlify.s3.us-west-1.amazonaws.com/lygos/logo/light-with-name.svg)](https://badge.fury.io/py/lygospy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bienvenue sur LygosPy, le client Python officiel, complet et facile à utiliser pour l'API Lygos. Ce package est conçu pour simplifier l'intégration de la passerelle de paiement Lygos dans vos applications Python.

Ce wrapper gère l'authentification, la construction des requêtes et la gestion des réponses, vous permettant de vous concentrer sur la logique métier de votre application plutôt que sur les détails de bas niveau de l'API HTTP.

**Lien vers le dépôt GitHub :** [https://github.com/lygosapp/lygospy/](https://github.com/lygosapp/lygospy/)

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Guide d'utilisation détaillé](#guide-dutilisation-détaillé)
  - [Initialisation du client](#initialisation-du-client)
  - [Lister les passerelles de paiement](#lister-les-passerelles-de-paiement)
  - [Créer une ou plusieurs passerelles](#créer-une-ou-plusieurs-passerelles)
    - [Création simple](#création-simple)
    - [Création multiple](#création-multiple)
  - [Récupérer une ou plusieurs passerelles](#récupérer-une-ou-plusieurs-passerelles)
    - [Récupération simple](#récupération-simple)
    - [Récupération multiple](#récupération-multiple)
  - [Mettre à jour une ou plusieurs passerelles](#mettre-à-jour-une-ou-plusieurs-passerelles)
    - [Mise à jour simple](#mise-à-jour-simple)
    - [Mise à jour multiple](#mise-à-jour-multiple)
  - [Supprimer une passerelle](#supprimer-une-passerelle)
  - [Obtenir le statut d'un paiement (Payin)](#obtenir-le-statut-dun-paiement-payin)
  - [Accesseurs de champ pratiques](#accesseurs-de-champ-pratiques)

## Gestion des erreurs

  - [Exemple de gestion d'erreur](#exemple-de-gestion-derreur)
  - [Liste des exceptions](#liste-des-exceptions)

## Contribuer

## Licence

---

## Fonctionnalités

- **Couverture complète de l'API :** Toutes les fonctionnalités de l'API Lygos Gateway et Payin sont implémentées.
- **Opérations en masse :** Créez, récupérez et mettez à jour plusieurs passerelles en un seul appel de méthode.
- **Gestion d'erreurs explicite :** Un ensemble complet d'exceptions personnalisées pour gérer les erreurs de l'API de manière prévisible.
- **Accesseurs dynamiques :** Récupérez des champs spécifiques d'une passerelle avec des méthodes pratiques comme `get_link()` ou `get_amount()`.
- **Logique intelligente :** Génération automatique des `order_id` si non fournis lors de la création.
- **Interface Pythonique :** Une conception simple et intuitive qui s'intègre naturellement dans n'importe quel projet Python.

---

## Installation

Pour installer **LygosPy**, utilisez simplement pip :

```bash
pip install lygospy
````

Assurez-vous d'avoir **Python 3.10** ou une version ultérieure.

---

## Démarrage rapide

Voici un exemple rapide d'utilisation de **LygosPy** :

```python
import uuid
from lygospy import Lygos
from lygospy.error_handler import LygosAPIError

# 1. Initialisez le client avec votre clé d'API
# Remplacez "VOTRE_CLE_API" par votre véritable clé
lygos = Lygos(api_key="VOTRE_CLE_API")

try:
    # 2. Créez une passerelle de paiement
    print("Création d'une nouvelle passerelle...")
    new_gateway = lygos.create_gateway(
        amount=1500,  # Montant en centimes (par exemple, 15.00)
        shop_name="Ma Boutique Inc.",
        order_id=f"order_{uuid.uuid4()}",
        message="Achat d'un T-shirt exclusif",
        success_url="[https://maboutique.com/paiement/succes](https://maboutique.com/paiement/succes)",
        failure_url="[https://maboutique.com/paiement/echec](https://maboutique.com/paiement/echec)"
    )
    gateway_id = new_gateway.get('id', 'ID_NON_TROUVE')
    print(f"Passerelle créée avec succès ! ID : {gateway_id}")

    # 3. Récupérez le lien de paiement de cette passerelle
    if gateway_id != 'ID_NON_TROUVE':
        link_info = lygos.get_link(gateway_id)
        print(f"Lien de paiement : {link_info.get('link')}")

    # 4. Listez toutes vos passerelles
    print("\nListe de toutes les passerelles :")
    all_gateways = lygos.list_gateways()
    for gateway in all_gateways:
        print(f"- ID: {gateway.get('id')}, Montant: {gateway.get('amount')}")

except LygosAPIError as e:
    print(f"Une erreur est survenue avec l'API Lygos : {e}")
    print(f"Code de statut HTTP : {e.status_code}")
except Exception as ex:
    print(f"Une erreur inattendue est survenue : {ex}")
```

---

## Guide d'utilisation

### Initialisation du client

```python
from lygospy import Lygos

api_key = "lygos-xxxxxxxxxxxxxxxxxxxx"  # Remplacez par votre clé
lygos = Lygos(api_key=api_key)
```

Vous pouvez également spécifier une URL d'API différente :

```python
lygos_staging = Lygos(api_key=api_key, api_url="[https://api.lygosapp.com/v2/](https://api.lygosapp.com/v2/)")
```

---

### Lister les passerelles de paiement

```python
all_gateways = lygos.list_gateways()
print(all_gateways)
# Sortie : [{'id': 'gw_...', 'amount': 1500, ...}, {'id': 'gw_...', 'amount': 2000, ...}]
```

---

### Créer une passerelle

```python
gateway = lygos.create_gateway(
    amount=2500,
    shop_name="Le Café du Coin",
    message="Commande de 2 cafés et 1 croissant"
)
print(gateway)
# Sortie : {'id': 'gw_...', 'order_id': 'généré-automatiquement', ...}
```

---

### Créer plusieurs passerelles (Batch)

```python
gateways_to_create = [
    {'amount': 1000, 'shop_name': 'Service A', 'message': 'Abonnement Mensuel'},
    {'amount': 5000, 'shop_name': 'Service B', 'order_id': 'f4401bd2-xxxxxxxxx'},
    {'amount': 250, 'shop_name': 'Service C'},
]

created_gateways = lygos.create_gateways_batch(gateways_data=gateways_to_create)
print(created_gateways)
# Sortie : [{'id': 'gw_...', ...}, {'id': 'gw_...', ...}, {'id': 'gw_...', ...}]
```

---

### Récupérer une passerelle

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
details = lygos.get_gateway(gateway_id=gateway_id)
print(details)
```

---

### Récupérer plusieurs passerelles (Batch)

```python
ids_to_get = ["gw_id_1", "gw_id_2", "gw_id_3"]
gateways_details = lygos.get_gateways_batch(gateway_ids=ids_to_get)
print(gateways_details)
# Sortie : [{'id': 'gw_id_1', ...}, {'id': 'gw_id_2', ...}, {'id': 'gw_id_3', ...}]
```

---

### Mettre à jour une passerelle

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
updated_gateway = lygos.update_gateway(gateway_id=gateway_id, amount=1200, message="Montant mis à jour")
print(updated_gateway)
```

---

### Mettre à jour plusieurs passerelles (Batch)

```python
updates = {
    "gw_id_1": {"amount": 999, "success_url": "[https://site.com/new_success](https://site.com/new_success)"},
    "gw_id_2": {"message": "Information de commande mise à jour."},
}

update_results = lygos.update_gateways_batch(gateways_data=updates)
print(update_results)
```

---

### Supprimer une passerelle

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
response = lygos.delete_gateway(gateway_id=gateway_id)
# Renvoie None en cas de succès (Status 204)
```

---

### Supprimer plusieurs passerelles (Batch)

```python
gateway_ids = ['gw_id_1', 'gw_id_2', 'gw_id_3']
response = lygos.delete_gateways_batch(gateway_ids=gateway_ids)
# Renvoie [None, None, None] en cas de succès
```

---

### Obtenir le statut d'un paiement (Payin)

```python
order_id = "order_xxxxxxxx"
status_info = lygos.get_payin_status(order_id=order_id)
print(status_info)
# Sortie : {'order_id': 'order_xxxxxxxx', 'status': 'paid'}
```

---

### Accesseurs de champ pratiques

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

link_info = lygos.get_link(gateway_id)
print(link_info)
# Sortie : {'link': '[https://pay.lygosapp.com/](https://pay.lygosapp.com/)...'}

amount_info = lygos.get_amount(gateway_id)
print(amount_info)
# Sortie : {'amount': 1500}
```

---

## Gestion des erreurs

LygosPy transforme les codes d'erreur HTTP de l'API en exceptions Python claires, héritant toutes de `LygosAPIError`.

### Exemple

```python
from lygospy.error_handler import NotFoundError, AuthenticationError, LygosAPIError

try:
    lygos.get_gateway(gateway_id="gw_id_inexistant")

except NotFoundError as e:
    print(f"Erreur : La ressource n'a pas été trouvée. (Status: {e.status_code})")

except AuthenticationError as e:
    print(f"Erreur d'authentification. Votre clé d'API est-elle correcte ? (Status: {e.status_code})")

except LygosAPIError as e:
    print(f"Une erreur inattendue de l'API est survenue : {e} (Status: {e.status_code})")
```

---

## Liste des exceptions

| Exception                | Code HTTP | Description                                                                  |
| ------------------------ | --------- | ---------------------------------------------------------------------------- |
| BadRequestError          | 400       | La requête est mal formée (ex: JSON invalide).                               |
| AuthenticationError      | 401       | L'authentification a échoué. La clé d'API est probablement incorrecte.       |
| PermissionDeniedError    | 403       | Vous n'avez pas les permissions pour accéder à cette ressource.              |
| NotFoundError            | 404       | La ressource demandée n'a pas été trouvée.                                   |
| ConflictError            | 409       | La requête est en conflit avec l'état actuel du serveur.                     |
| UnprocessableEntityError | 422       | La requête est valide, mais contient des données sémantiquement incorrectes. |
| ServerError              | 500       | Erreur générique du serveur Lygos.                                           |
| BadGatewayError          | 502       | Le serveur a reçu une réponse invalide d'un autre serveur.                   |
| ServiceUnavailableError  | 503       | Le service est temporairement indisponible.                                  |
| GatewayTimeoutError      | 504       | Le serveur n'a pas reçu de réponse à temps.                                  |

---

## Contribuer

Les contributions sont les bienvenues !
Si vous souhaitez améliorer **LygosPy**, n'hésitez pas à forker le dépôt, à créer une branche pour votre fonctionnalité et à soumettre une **Pull Request**.

Pour les bugs ou les suggestions, veuillez ouvrir une "Issue" sur le dépôt GitHub.

---

## Licence

Ce projet est sous licence **MIT**.
Voir le fichier `LICENSE` pour plus de détails.

---


*made with ❤️ by [wonder7b](https://github.com/wonder7b/)*
