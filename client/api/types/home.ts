export type CompetitionEvent = {
    compId: number
    competeLocation: string
    name: string
    status: "not_started" | "incomplete" | "complete"
    bonusEvent: boolean
    summary: string
}