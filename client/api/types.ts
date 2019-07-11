export type HeaderInfo = {
    title: string
    records: {
        wca: {
            url: string
            name: string
        }[]
        nonWca: {
            url: string
            name: string
        }[]
        sum: {
            url: string
            name: string
        }[]
    }
}