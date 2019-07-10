import * as types from './types'

function fetchResources<T>(url: string): Promise<T> {
    return fetch(url)
        .then(res => res.json())
        .then(json => json as T)
}

export function getHeaderInfo(): Promise<types.HeaderInfo> {
    return fetchResources("/api/header-info")
}