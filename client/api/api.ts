import * as types from './types'

function fetchResources<T>(url: string): Promise<T> {
    return fetch(url)
        .then(res => res.json())
        .then(json => json as T)
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