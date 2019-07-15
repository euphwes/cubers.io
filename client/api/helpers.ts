export function toReadableTime(millisecondTimestamp: number) {
    let millis = millisecondTimestamp

    let hours = Math.floor(millis / (1000 * 3600))
    millis = millis - (hours * (3600 * 1000))

    let minutes = Math.floor(millis / (1000 * 60))
    millis = millis - (minutes * (60 * 1000))

    let seconds = Math.floor(millis / 1000)
    millis = millis - (seconds * 1000)

    millis = Math.floor(millis / 10)

    if (hours > 0) {
        return (
            `${hours}:` +
            `${("0" + minutes).slice(-2)}:` +
            `${("0" + seconds).slice(-2)}.` +
            `${("0" + millis).slice(-2)}`)
    }

    if (minutes > 0) {
        return (
            `${minutes}:` +
            `${("0" + seconds).slice(-2)}.` +
            `${("0" + millis).slice(-2)}`)
    }

    return `${seconds}.${("0" + millis).slice(-2)}`
}