export type HeaderInfo = {
    title: string
    recordsItems: {
        wca: HeaderItem
        nonWca: HeaderItem
        sum: HeaderItem
    }
    leaderboardItems: {
        current: DetailedUrl
        previous: DetailedUrl
        all: DetailedUrl
    }
}

export type HeaderItem = {
    title: string
    urls: DetailedUrl[]
}

export type DetailedUrl = {
    url: string
    name: string
}