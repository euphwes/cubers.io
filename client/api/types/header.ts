export type HeaderInfo = {
    title: string
    recordsItems: Record
    leaderboardItems: Leaderboard
    current_user: CurrentUser
}

export type Record = {
    wca: HeaderItem
    nonWca: HeaderItem
    sum: HeaderItem
}

export type Leaderboard = {
    current: DetailedUrl
    previous: DetailedUrl
    all: DetailedUrl
}

export type CurrentUser = {
    logout_url: string
    name: string
    profile_url: string
    settings_url: string
} | "none"

export type HeaderItem = {
    title: string
    urls: DetailedUrl[]
}

export type DetailedUrl = {
    url: string
    name: string
}