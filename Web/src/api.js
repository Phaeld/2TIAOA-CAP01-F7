export const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
export async function api(path, {token, body, method='GET', signal} = {}) {
  const form = body instanceof FormData;
  const response = await fetch(`${BASE}${path}`, {
    method, signal, headers: { ...(token ? {Authorization:`Bearer ${token}`} : {}), ...(!form && body ? {'Content-Type':'application/json'} : {}) },
    body: body ? (form ? body : JSON.stringify(body)) : undefined,
  });
  const data = await response.json().catch(() => {
    throw new Error('A API não respondeu corretamente. Confira a configuração e tente novamente.');
  });
  if (!response.ok) {
    const error = new Error(typeof data.detail === 'string' ? data.detail : response.status===422 ? 'Confira os valores informados.' : 'Não foi possível concluir. Verifique a conexão com a API.');
    error.status=response.status; throw error;
  }
  return data;
}
