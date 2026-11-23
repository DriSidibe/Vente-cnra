const API_BASE_URL = "/api";

interface Options { 
    body: unknown,
     headers: Map<string, string>,
      } 

type ApiOptions = Omit<RequestInit, "body"> & {
	body?: unknown;
};

function getCookie(name: string): string | undefined {
	const prefix = `${name}=`;
	const cookie = document.cookie
		.split(";")
		.map((item) => item.trim())
		.find((item) => item.startsWith(prefix));

	return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : undefined;
}

export async function apiRequest<T>(
	path: string,
	options: Options = {body: "", headers: new Map<string, string>()},
): Promise<T> {
	const { body, headers: requestHeaders, ...requestOptions } = options;
	const headers = new Headers(requestHeaders);
	const isFormData = typeof FormData !== "undefined" && body instanceof FormData;

	if (body !== undefined && !isFormData && !headers.has("Content-Type")) {
		headers.set("Content-Type", "application/json");
	}

	const method = (requestOptions.method ?? "GET").toUpperCase();
	if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
		const csrfToken = getCookie("csrftoken");
		if (csrfToken) headers.set("X-CSRFToken", csrfToken);
	}

	const response = await fetch(
		`${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`,
		{
			...requestOptions,
			method,
			headers,
			credentials: requestOptions.credentials ?? "same-origin",
			body:
				body === undefined
					? undefined
					: isFormData || typeof body === "string"
						? (body as BodyInit)
						: JSON.stringify(body),
		},
	);

	if (!response.ok) {
		const message = await response.text();
		throw new Error(message || `Erreur API (${response.status})`);
	}

	if (response.status === 204) return undefined as T;
	if (response.headers.get("content-type")?.includes("application/json")) {
		return (await response.json()) as T;
	}
	return (await response.text()) as T;
}

export const api = {
	get: <T>(path: string, options?: ApiOptions) =>
		apiRequest<T>(path, { ...options, method: "GET" }),
	post: <T>(path: string, body?: unknown, options?: ApiOptions) =>
		apiRequest<T>(path, { ...options, method: "POST", body }),
	put: <T>(path: string, body?: unknown, options?: ApiOptions) =>
		apiRequest<T>(path, { ...options, method: "PUT", body }),
	patch: <T>(path: string, body?: unknown, options?: ApiOptions) =>
		apiRequest<T>(path, { ...options, method: "PATCH", body }),
	delete: <T>(path: string, options?: ApiOptions) =>
		apiRequest<T>(path, { ...options, method: "DELETE" }),
};
