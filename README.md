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

Pour installer LygosPy, utilisez simplement `pip` :

```bash
pip install lygospy
```

Assurez-vous d'avoir Python 3.10 ou une version ultérieure.

---

## Démarrage rapide

Voici un exemple rapide  d'utilisation de LygosPy.

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
        message="Achat d\'un T-shirt exclusif",
        success_url="https://maboutique.com/paiement/succes",
        failure_url="https://maboutique.com/paiement/echec"
    )
    gateway_id = new_gateway['id']
    print(f"Passerelle créée avec succès ! ID : {gateway_id}")

    # 3. Récupérez le lien de paiement de cette passerelle
    link_info = lygos.get_link(gateway_id)
    print(f"Lien de paiement : {link_info['link']}")

    # 4. Listez toutes vos passerelles
    print("\nListe de toutes les passerelles :")
    all_gateways = lygos.list_gateways()
    for gateway in all_gateways:
        print(f"- ID: {gateway['id']}, Montant: {gateway['amount']}")

except LygosAPIError as e:
    print(f"Une erreur est survenue avec l\'API Lygos : {e}")
    print(f"Code de statut HTTP : {e.status_code}")

```

---

## Guide d\'utilisation

### Initialisation du client

La première étape consiste à importer la classe `Lygos` et à créer une instance avec votre clé d\'API.

```python
from lygospy import Lygos

api_key = "lygos-xxxxxxxxxxxxxxxxxxxx"  # Remplacez par votre clé
lygos = Lygos(api_key=api_key)
```

Vous pouvez également spécifier une URL d\'API différente si nécessaire (si il y a une nouvelle version par exemple) :

```python
lygos_staging = Lygos(api_key=api_key, api_url="https://api.lygosapp.com/v2/")
```

### Lister les passerelles de paiement

Pour obtenir la liste de toutes les passerelles de paiement que vous avez créées.

```python
all_gateways = lygos.list_gateways()
print(all_gateways)
# Sortie : [{'id': 'gw_...', 'amount': 1500, ...}, {'id': 'gw_...', 'amount': 2000, ...}]
```

### Créer une ou plusieurs passerelles

#### Création simple

Pour créer une seule passerelle, utilisez la méthode `create_gateway` avec les paramètres requis.

- `amount` (int) : Le montant de la transaction en centimes.
- `shop_name` (str) : Le nom de votre boutique ou service.
- `order_id` (str, optionnel) : Un identifiant unique pour cette commande. **Si non fourni, un UUID sera généré automatiquement.**
- `message` (str, optionnel) : Un message ou une information à l'attention du client
- `success_url` (str, optionnel) : une url de redirection si le paiement est effectué
- `failure_url` (str, optionnel) : une url de redirection si le paiement echou

```python
gateway = lygos.create_gateway(
    amount=2500,
    shop_name="Le Café du Coin",
    message="Commande de 2 cafés et 1 croissant"
)
print(gateway)
# Sortie : {'id': 'gw_...', 'order_id': 'généré-automatiquement', ...}
```

#### Création multiple

Pour créer plusieurs passerelles en un seul appel, passez `multiple=True` et fournissez une liste de dictionnaires à `gateways_data`.

```python
gateways_to_create = [
    {'amount': 1000, 'shop_name': 'Service A', 'message': 'Abonnement Mensuel'},
    {'amount': 5000, 'shop_name': 'Service B', 'order_id': 'f4401bd2-xxxxxxxxx'},
    {'amount': 250, 'shop_name': 'Service C'},
]

created_gateways = lygos.create_gateway(multiple=True, gateways_data=gateways_to_create)
print(created_gateways)
# Sortie : [{'id': 'gw_...', ...}, {'id': 'gw_...', ...}, {'id': 'gw_...', ...}]
```

### Récupérer une ou plusieurs passerelles

#### Récupération simple

Pour obtenir les détails d\'une passerelle spécifique, utilisez `get_gateway` avec son ID.

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
details = lygos.get_gateway(gateway_id=gateway_id)
print(details)
```

#### Récupération multiple

Pour récupérer plusieurs passerelles, passez `multiple=True` et une liste d\'IDs à `gateway_ids`.

```python
ids_to_get = ["gw_id_1", "gw_id_2", "gw_id_3"]
gateways_details = lygos.get_gateway(multiple=True, gateway_ids=ids_to_get)
print(gateways_details)
# Sortie : [{'id': 'gw_id_1', ...}, {'id': 'gw_id_2', ...}, {'id': 'gw_id_3', ...}]
```

### Mettre à jour une ou plusieurs passerelles

#### Mise à jour simple

Pour modifier une passerelle existante, utilisez `update_gateway` avec son ID et les champs à modifier.

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
updated_gateway = lygos.update_gateway(gateway_id=gateway_id, amount=1200, message="Montant mis à jour")
print(updated_gateway)
```

#### Mise à jour multiple

Pour mettre à jour plusieurs passerelles, passez `multiple=True` et un dictionnaire à `gateways_data`. Les clés sont les IDs des passerelles à mettre à jour et les valeurs sont des dictionnaires contenant les champs et les valeurs à mettre à jour.

```python
updates = {
    "gw_id_1": {"amount": 999, "success_url": "https://site.com/new_success"},
    "gw_id_2": {"message": "Information de commande mise à jour."},
}

update_results = lygos.update_gateway(multiple=True, gateways_data=updates)
print(update_results)
```

### Supprimer une ou plusieur passerelle

#### suprime un passerelle

Pour supprimer une passerelle, utilisez `delete_gateway`.

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
response = lygos.delete_gateway(gateway_id=gateway_id)

```

#### suprimer plusieur passerelle

Pour suprimer plusieur passerelle, passez `multiple=True` et une list d'IDs à `getaway_ids`.

```python
gateway_ids = ['gw_id_1', 'gw_id_2', 'gw_id_3']
response = lygos.delete_gateway(multiple=True, gateway_ids=gateway_ids)

```


### Obtenir le statut d\'un paiement (Payin)

Pour vérifier le statut d\'une transaction, utilisez `get_payin_status` avec l\'`order_id` de la transaction.

```python
order_id = "order_xxxxxxxx"
status_info = lygos.get_payin_status(order_id=order_id)
print(status_info)
# Sortie : {'order_id': 'order_xxxxxxxx', 'status': 'paid'}
```

### Accesseurs de champ pratiques

Pour éviter d\'avoir à récupérer l\'objet passerelle complet juste pour un seul champ, utilisez des méthodes simple. Appelez simplement `get_<nom_du_champ>()` avec l\'ID de la passerelle.

**Champs supportés :**
`link`, `amount`, `shop_name`, `message`, `user_country`, `creation_date`, `order_id`, `success_url`, `failure_url`.

```python
gateway_id = "gw_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Au lieu de faire :
# gateway = lygos.get_gateway(gateway_id)
# link = gateway['link']

# Faites simplement :
link_info = lygos.get_link(gateway_id)
print(link_info)
# Sortie : {'link': 'https://pay.lygosapp.com/...'}

amount_info = lygos.get_amount(gateway_id)
print(amount_info)
# Sortie : {'amount': 1500}
```

---

## Gestion des erreurs

LygosPy transforme les codes d\'erreur HTTP de l\'API en exceptions Python claires, héritant toutes de `LygosAPIError`. Cela vous permet de gérer les problèmes de manière programmatique avec des blocs `try...except`.

Chaque exception contient une propriété `.status_code` pour vous permettre d\'identifier la nature de l\'erreur HTTP.

### Exemple de gestion d\'erreur

```python
from lygospy.error_handler import NotFoundError, AuthenticationError, LygosAPIError

try:
    # Tente de récupérer une passerelle qui n\'existe pas
    lygos.get_gateway(gateway_id="gw_id_inexistant")

except NotFoundError as e:
    print(f"Erreur : La ressource n\'a pas été trouvée. (Status: {e.status_code})")

except AuthenticationError as e:
    print(f"Erreur d\'authentification. Votre clé d\'API est-elle correcte ? (Status: {e.status_code})")

except LygosAPIError as e:
    # Attrape toutes les autres erreurs de l\'API Lygos
    print(f"Une erreur inattendue de l\'API est survenue : {e} (Status: {e.status_code})")
```

### Liste des exceptions

| Exception                  | Code HTTP | Description                                                              |
| -------------------------- | --------- | ------------------------------------------------------------------------ |
| `BadRequestError`          | 400       | La requête est mal formée (ex: JSON invalide).                           |
| `AuthenticationError`      | 401       | L\'authentification a échoué. La clé d\'API est probablement incorrecte.     |
| `PermissionDeniedError`    | 403       | Vous n\'avez pas les permissions pour accéder à cette ressource.          |
| `NotFoundError`            | 404       | La ressource demandée (ex: une passerelle) n\'a pas été trouvée.          |
| `ConflictError`            | 409       | La requête est en conflit avec l\'état actuel du serveur.                 |
| `UnprocessableEntityError` | 422       | La requête est valide, mais contient des données sémantiquement incorrectes. |
| `ServerError`              | 500       | Erreur générique du serveur Lygos.                                       |
| `BadGatewayError`          | 502       | Le serveur a reçu une réponse invalide d\'un autre serveur.               |
| `ServiceUnavailableError`  | 503       | Le service est temporairement indisponible (maintenance ou surcharge).   |
| `GatewayTimeoutError`      | 504       | Le serveur n\'a pas reçu de réponse à temps.                              |

---

## Contribuer

Les contributions sont les bienvenues ! Si vous souhaitez améliorer LygosPy, n\'hésitez pas à forker le dépôt, à créer une branche pour votre fonctionnalité et à soumettre une Pull Request.

Pour les bugs ou les suggestions, veuillez ouvrir une "Issue" sur le dépôt GitHub.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

made with ❤️ by [wonder7b](https://github.com/wonder7b)
