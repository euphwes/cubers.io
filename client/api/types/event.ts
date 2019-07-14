export type Event = {
    currentScramble: {
        id: number,
        index: number,
        text: string
    },
    event: {
        description: string,
        format: "Ao5" | "Mo3" | "Bo3" | "Bo1",
        id: number,
        name: string,
        solves: string[]
    }
}