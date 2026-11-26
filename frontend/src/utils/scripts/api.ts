
const API_URL = "/vente";
const COOKIE_CLE = "api_key";

export interface Utilisateur {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    is_active: boolean;
    is_superuser: boolean;
}

export interface Session {
    user: Utilisateur;
    api_key: string;
    api_key_expiration_datetime: string;
}

export class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.status = status;
    }
}

export function lireCle(): string {
    for (const cookie of document.cookie.split("; ")) {
        const [nom, ...valeurs] = cookie.split("=");

        if (nom === COOKIE_CLE && valeurs.length) {
            return decodeURIComponent(valeurs.join("="));
        }
    }

    return "";
}

export function enregistrerCle(cle: string, expiration: string) {
    const expires = new Date(expiration).toUTCString();

    document.cookie =
        `${COOKIE_CLE}=${encodeURIComponent(cle)};expires=${expires};path=/;SameSite=Lax`;
}

export function supprimerCle() {
    document.cookie =
        `${COOKIE_CLE}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;SameSite=Lax`;
}

let surSessionExpiree = () => {};

export function definirSurSessionExpiree(action: () => void) {
    surSessionExpiree = action;
}

async function requete<T>(
    chemin: string,
    options: RequestInit = {}
): Promise<T> {
    const cle = lireCle();

    const headers = new Headers(options.headers);

    if (!(options.body instanceof FormData) && options.body !== undefined) {
        headers.set("Content-Type", "application/json");
    }

    if (cle) {
        headers.set("X-API-Key", cle);
    }

    let reponse: Response;

    try {
        reponse = await fetch(API_URL + chemin, {
            ...options,
            headers,
        });
    } catch {
        throw new ApiError("Le serveur est injoignable.", 0);
    }

    if (!reponse.ok) {
        const erreur = await reponse.json().catch(() => ({}));

        if (reponse.status === 401 && cle) {
            surSessionExpiree();
        }

        throw new ApiError(
            erreur.error || erreur.detail || "Erreur API : " + reponse.status,
            reponse.status
        );
    }

    if (reponse.status === 204) {
        return undefined as T;
    }

    return reponse.json();
}

export function apiGet<T>(chemin: string) {
    return requete<T>(chemin);
}

export function apiPost<T>(chemin: string, donnees: object = {}) {
    return requete<T>(chemin, {
        method: "POST",
        body: JSON.stringify(donnees),
    });
}

export function apiPostForm<T>(chemin: string, donnees: FormData) {
    return requete<T>(chemin, {
        method: "POST",
        body: donnees,
    });
}

export function apiPatch<T>(
    chemin: string,
    donnees: object | FormData
) {
    return requete<T>(chemin, {
        method: "PATCH",
        body: donnees instanceof FormData
            ? donnees
            : JSON.stringify(donnees),
    });
}

export function apiDelete<T>(chemin: string) {
    return requete<T>(chemin, {
        method: "DELETE",
    });
}
