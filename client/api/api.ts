import * as types from './types'

let getHeaders = (): Headers => {
    let token = document.getElementsByName('Anti-Forgery-Token')[0].getAttribute('value')
    let headers = new Headers()
    headers.append('Content-Type', 'application/json')
    headers.append('X_CSRF_TOKEN', token)

    return headers
}

function fetchResources<T>(url: string): Promise<T> {
    return fetch(url)
        .then(res => res.json())
        .then(json => json as T)
}

function sendResources<T>(url: string, data: any, method: "POST" | "PUT" | "DELETE") {
    let request: RequestInit = {
        method: method,
        headers: getHeaders(),
    }

    if (!!data) request.body = JSON.stringify(data)

    return fetch(url, request)
        .then(res => res.json())
        .then(json => json as T)
}

function postResources<T>(url: string, data: any): Promise<T> {
    return sendResources(url, data, "POST")
}

function putResources<T>(url: string, data: any): Promise<T> {
    return sendResources(url, data, "PUT")
}

function deleteResources<T>(url: string, data: any): Promise<T> {
    return sendResources(url, data, "DELETE")
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

export function postSolve(time: {
    is_dnf: boolean
    is_plus_two: boolean
    scramble_id: number
    comp_event_id: number
    elapsed_centiseconds: number
}): Promise<types.Event> {
    return postResources('/api/submit-solve', time)
}

export function putDnf(compEventId: number): Promise<types.Event> {
    return putResources('/api/toggle-dnf', {
        comp_event_id: compEventId
    })
}

export function putPlusTwo(compEventId: number): Promise<types.Event> {
    return putResources('/api/toggle-plus-two', {
        comp_event_id: compEventId
    })
}

export function deleteSolve(compEventId: number): Promise<types.Event> {
    return deleteResources('/api/delete-solve', {
        comp_event_id: compEventId
    })
}

export function submitComment(compEventId: number, comment: string): Promise<types.Event> {
    return putResources('/api/submit-comment', {
        comp_event_id: compEventId,
        comment: comment
    })
}