export function sig<T>(scramble: string, eventName: string, settings: T): {
    showNormalImage: () => void
    showLargeImage: () => void
}