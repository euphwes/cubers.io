export type Event = {
    currentScramble: {
        id: number
        index: number
        text: string
    },
    previousSolve: PreviousSolve
    event: {
        description: string,
        format: "Ao5" | "Mo3" | "Bo3" | "Bo1",
        id: number,
        name: string,
        solves: string[],
        comment: string
    }
}

export type PreviousSolve = {
    is_dnf: boolean
    is_inspection_dnf: boolean
    is_plus_2: boolean
    time: string
}