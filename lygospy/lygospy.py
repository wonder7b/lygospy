"""
Client Python pour l'API Lygos v1.

Ce module fournit une classe `Lygos` pour interagir avec l'API Lygos,
gérant l'authentification, la création de requêtes et la gestion des erreurs.
"""

import requests
import uuid
from requests.exceptions import HTTPError, RequestException
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

# Import custom exceptions from the local module
from .error_handler import (
    LygosAPIError,
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    ServerError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError
)

# Constant for the default API URL
DEFAULT_API_URL = "https://api.lygosapp.com/v1/"

# Type alias for JSON responses
JsonDict = Dict[str, Any]


class Lygos:
    """
    Client Python pour l'API Lygos.

    Ce client gère l'authentification, la construction des requêtes et la
    gestion des erreurs pour toutes les interactions avec l'API Lygos.

    Il supporte également des méthodes dynamiques pour récupérer des champs
    spécifiques d'une passerelle (gateway). Par exemple, appeler
    `lygos.get_link("gw_id")` renverra `{'link': 'https://...'}`.

    Champs supportés pour les méthodes `get_*` dynamiques:
    - link, amount, shop_name, message, user_country, creation_date,
    - order_id, success_url, failure_url

    Exemple:
        >>> from lygos_client import Lygos
        >>> lygos = Lygos(api_key="votre_cle_api")
        >>> new_gateway = lygos.create_gateway(amount=1000, shop_name="Mon Shop")
        >>> print(new_gateway['link'])
        >>> status = lygos.get_payin_status(new_gateway['order_id'])

    Attributes:
        api_key (str): Votre clé API Lygos.
        base_url (str): L'URL de base de l'API Lygos.
        session (requests.Session): Session pour la persistance des connexions.
    """

    # Use a set for O(1) existence checks
    _SUPPORTED_GET_FIELDS = {
        "link", "amount", "shop_name", "message", "user_country",
        "creation_date", "order_id", "success_url", "failure_url"
    }

    # Map HTTP status codes to exception classes
    _ERROR_MAP = {
        400: BadRequestError,
        401: AuthenticationError,
        403: PermissionDeniedError,
        404: NotFoundError,
        409: ConflictError,
        422: UnprocessableEntityError,
        500: ServerError,
        502: BadGatewayError,
        503: ServiceUnavailableError,
        504: GatewayTimeoutError,
    }

    def __init__(self, api_key: str, api_url: str = DEFAULT_API_URL):
        """
        Initialise le client Lygos.

        Args:
            api_key (str): Votre clé API Lygos. Ne doit pas être vide.
            api_url (str, optional): L'URL de base de l'API.
                                    Par défaut à `DEFAULT_API_URL`.
        
        Raises:
            ValueError: Si l'api_key est vide.
        """
        if not api_key:
            raise ValueError("Une 'api_key' est requise pour initialiser le client.")
            
        self.api_key = api_key
        self.base_url = api_url
        
        # Initialize a session for performance (connection pooling)
        self.session = requests.Session()
        self.session.headers.update({
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Lygos-Python-Client-v1"
        })

    def __repr__(self) -> str:
        """Représentation officielle de l'objet pour le débogage."""
        return f"<{type(self).__name__}(api_url='{self.base_url}')>"

    def __getattr__(self, name: str) -> Any:
        """
        Gère dynamiquement les appels de méthode `get_<field>(gateway_id)`.

        Ceci permet des appels comme `lygos.get_link(gw_id)` sans avoir à
        définir explicitement chaque méthode.

        Args:
            name (str): Le nom de l'attribut (méthode) demandé.

        Returns:
            function: Une fonction getter si le champ est supporté.

        Raises:
            AttributeError: Si le nom ne correspond pas à un attribut
                              existant ou à un getter dynamique supporté.
        """
        if name.startswith("get_") and name[4:] in self._SUPPORTED_GET_FIELDS:
            field = name[4:]

            def getter(gateway_id: str) -> JsonDict:
                """
                Getter généré dynamiquement pour un champ spécifique de la passerelle.

                Args:
                    gateway_id (str): L'ID de la passerelle à interroger.

                Returns:
                    JsonDict: Un dictionnaire contenant {field: value}.
                """
                gateway_data = self.get_gateway(gateway_id=gateway_id)
                return {field: gateway_data.get(field)}
            
            # Assign a more descriptive name to the dynamic function
            # for better debugging.
            getter.__name__ = name
            return getter

        # Raise the standard error if the attribute is not found
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Optional[Union[JsonDict, List[JsonDict]]]:
        """
        Méthode centrale pour effectuer des requêtes HTTP à l'API.

        Args:
            method (str): Méthode HTTP (GET, POST, PUT, DELETE).
            endpoint (str): Le point de terminaison de l'API (ex: 'gateway').
            **kwargs: Arguments supplémentaires à passer à `requests.request`
                      (ex: json, params).

        Returns:
            Optional[Union[JsonDict, List[JsonDict]]]:
                La réponse JSON de l'API, ou None si 204 No Content.

        Raises:
            LygosAPIError: Pour les erreurs génériques de l'API ou du client.
            (Specific Errors): Erreurs spécifiques (ex: NotFoundError)
                                 basées sur le code de statut HTTP.
        """
        # Build the URL robustly
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            # Raise an exception for HTTP error codes (4xx, 5xx)
            response.raise_for_status()

            # Handle the "204 No Content" case
            if response.status_code == 204:
                return None
            
            # Return the JSON if it exists
            return response.json()

        except HTTPError as err:
            status_code = err.response.status_code
            try:
                # Try to extract the error message from the JSON body
                error_data = err.response.json()
                error_message = error_data.get("message", err.response.reason)
                details = error_data.get("details")
                if details:
                    error_message = f"{error_message}: {details}"
            except requests.JSONDecodeError:
                # If the body is not JSON, use the raw text or reason
                error_message = err.response.text or err.response.reason

            # Raise the appropriate custom exception
            exception_class = self._ERROR_MAP.get(status_code, LygosAPIError)
            raise exception_class(error_message, status_code) from err
        
        except RequestException as err:
            # For network issues, timeouts, DNS, etc.
            raise LygosAPIError(f"Erreur de connexion à l'API: {err}") from err

    # --- Gateway API Methods ---

    def list_gateways(self) -> List[JsonDict]:
        """
        Récupère une liste de toutes les passerelles de paiement.

        Returns:
            List[JsonDict]: Une liste de dictionnaires, chacun représentant
                            une passerelle.
        """
        return self._request("GET", "gateway")

    def create_gateway(self, amount: int, shop_name: str, order_id: Optional[str] = None,
                       message: Optional[str] = None, success_url: Optional[str] = None,
                       failure_url: Optional[str] = None) -> JsonDict:
        """
        Crée une seule passerelle de paiement.

        Args:
            amount (int): Le montant de la transaction.
            shop_name (str): Le nom du magasin.
            order_id (str, optional): ID de commande unique. Si None, un UUID4
                                      est généré.
            message (str, optional): Message à afficher au client.
            success_url (str, optional): URL de redirection en cas de succès.
            failure_url (str, optional): URL de redirection en cas d'échec.

        Returns:
            JsonDict: Les données de la passerelle créée.
        """
        data: JsonDict = {
            "amount": amount,
            "shop_name": shop_name,
            "order_id": order_id or str(uuid.uuid4())
        }
        # Add optional fields only if they are not None
        if message is not None:
            data["message"] = message
        if success_url is not None:
            data["success_url"] = success_url
        if failure_url is not None:
            data["failure_url"] = failure_url
        
        return self._request("POST", "gateway", json=data)

    def create_gateways_batch(self, gateways_data: List[JsonDict]) -> List[JsonDict]:
        """
        Crée plusieurs passerelles de paiement (via des appels POST successifs).

        Args:
            gateways_data (List[JsonDict]): Une liste de dictionnaires,
                chacun contenant les données d'une passerelle à créer.
                'order_id' sera auto-généré si non fourni.

        Returns:
            List[JsonDict]: Une liste des passerelles créées.
        """
        created_gateways = []
        for gateway_data in gateways_data:
            # Ensure an order_id for each, without overwriting an existing one
            gateway_data.setdefault("order_id", str(uuid.uuid4()))
            try:
                created = self._request("POST", "gateway", json=gateway_data)
                created_gateways.append(created)
            except LygosAPIError as e:
                # Handle or log the error for a single batch failure
                print(f"Échec de la création de la passerelle (order_id: {gateway_data.get('order_id')}): {e}")
                created_gateways.append({"error": str(e), "data": gateway_data})
                
        return created_gateways

    def get_gateway(self, gateway_id: str) -> JsonDict:
        """
        Récupère une passerelle de paiement spécifique par son ID.

        Args:
            gateway_id (str): L'ID de la passerelle (ex: "gw_...").

        Returns:
            JsonDict: Les données de la passerelle.
        """
        return self._request("GET", f"gateway/{gateway_id}")

    def get_gateways_batch(self, gateway_ids: List[str]) -> List[JsonDict]:
        """
        Récupère plusieurs passerelles par leurs IDs (via des appels GET successifs).

        Args:
            gateway_ids (List[str]): Liste des IDs de passerelles à récupérer.

        Returns:
            List[JsonDict]: Liste des données des passerelles.
        """
        return [self.get_gateway(gid) for gid in gateway_ids]

    def update_gateway(self, gateway_id: str, **kwargs: Any) -> JsonDict:
        """
        Met à jour une passerelle de paiement spécifique.

        Les champs à mettre à jour sont passés en arguments-clés (kwargs).

        Exemple:
            >>> lygos.update_gateway("gw_123", amount=1500, message="Nouveau message")

        Args:
            gateway_id (str): L'ID de la passerelle à mettre à jour.
            **kwargs: Les champs et nouvelles valeurs à mettre à jour.

        Returns:
            JsonDict: La passerelle mise à jour.
            
        Raises:
            ValueError: Si aucun argument-clé (kwargs) n'est fourni.
        """
        if not kwargs:
            raise ValueError("Aucune donnée de mise à jour fournie. "
                             "Utilisez des arguments-clés pour spécifier les champs.")
        return self._request("PUT", f"gateway/{gateway_id}", json=kwargs)

    def update_gateways_batch(self, gateways_data: Dict[str, JsonDict]) -> List[JsonDict]:
        """
        Met à jour plusieurs passerelles (via des appels PUT successifs).

        Args:
            gateways_data (Dict[str, JsonDict]): Un dictionnaire où les clés
                sont les gateway_ids et les valeurs sont les dictionnaires
                de données à mettre à jour.

                Ex: {"gw_123": {"amount": 1500}, "gw_456": {"message": "Test"}}

        Returns:
            List[JsonDict]: Liste des passerelles mises à jour.
        """
        return [
            self.update_gateway(gid, **data)
            for gid, data in gateways_data.items()
        ]

    def delete_gateway(self, gateway_id: str) -> None:
        """
        Supprime une passerelle de paiement spécifique.
        L'API renvoie 204 No Content en cas de succès.

        Args:
            gateway_id (str): L'ID de la passerelle à supprimer.
        
        Returns:
            None
        """
        self._request("DELETE", f"gateway/{gateway_id}")
        return None

    def delete_gateways_batch(self, gateway_ids: List[str]) -> List[None]:
        """
        Supprime plusieurs passerelles (via des appels DELETE successifs).

        Args:
            gateway_ids (List[str]): Liste des IDs de passerelles à supprimer.

        Returns:
            List[None]: L'API renvoie 204 No Content, donc la liste
                        sera [None, None, ...].
        """
        return [self.delete_gateway(gid) for gid in gateway_ids]

    # --- Payin API Methods ---

    def get_payin_status(self, order_id: str) -> JsonDict:
        """
        Récupère le statut d'une transaction payin spécifique par son order_id.

        Args:
            order_id (str): L'ID de commande de la transaction.

        Returns:
            JsonDict: Les données de statut du payin.
        """
        return self._request("GET", f"gateway/payin/{order_id}")

