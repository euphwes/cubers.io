import * as types from './types'

function fetchResources<T>(url: string): Promise<T> {
    return fetch(url)
        .then(res => res.json())
        .then(json => json as T)
}

function postResources<T>(url: string, data: any) {
    let token = document.getElementsByName('Anti-Forgery-Token')[0].getAttribute('value')
    let headers = new Headers()
    headers.append('Content-Type', 'application/json')
    headers.append('X_CSRF_TOKEN', token)
    let request: RequestInit = {
        method: "POST",
        headers: headers,
        body: JSON.stringify(data),
    }

    return fetch(url, request)
        .then(res => res.json())
        .then(json => json as T)
}

export function getUserSettings(): Promise<types.UserSettings> {
    return fetchResources('/api/user-settings')
}

export function getHeaderInfo(): Promise<types.HeaderInfo> {
    return fetchResources("/api/header-info")
}

export function getCompetitionEvents(): Promise<types.CompetitionEvent[]> {
    return fetchResources("/api/competition-events")
}

export function getEventInfo(eventId: number): Promise<types.Event> {
    return fetchResources(`/api/get-event/${eventId}`)
}