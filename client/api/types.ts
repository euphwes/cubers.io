export type HeaderInfo = {
    title: string
    recordsItems: {
        wca: HeaderItem
        nonWca: HeaderItem
        sum: HeaderItem
    }
}

export type HeaderItem = {
    title: string
    urls: DetailedUrl[]
}

type DetailedUrl = {
    url: string
    name: string
}