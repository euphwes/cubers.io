import * as React from 'react'

type ManualEntryProps = {
    disabled: boolean
    submit: (value: number) => void
}
type ManualEntryState = {
    value: string
}

export class ManualEntry extends React.Component<ManualEntryProps, ManualEntryState>{
    constructor(props: ManualEntryProps) {
        super(props)

        this.state = {
            value: ""
        }
    }

    processChange(value: string) {
        let numberValue = Number(this.cleanInput(value))
        if (Number.isNaN(numberValue)) return
        if (numberValue === 0) return this.setState({ value: "" })

        let cleanValue = `${numberValue}`

        let newValue = cleanValue.length < 4 ? ("0000" + cleanValue).slice(-4) : cleanValue
        if (cleanValue.length > 4) {
            newValue = newValue.slice(0, -4) + ':' + newValue.slice(-4)
        }
        newValue = newValue.slice(0, -2) + '.' + newValue.slice(-2)
        this.setState({ value: newValue })
    }

    cleanInput(value: string) {
        return value.replace(".", "").replace(",", "").replace(":", "")
    }

    convertToMilliseconds(value: string) {
        if (value.length <= 5) return Number(value) * 100

        let seconds = Number(value.includes(':') ? value.split(':')[0] : 0) * 60
        let milliSeconds = Math.round((Number(value.includes(':') ? value.split(':')[1] : value) + seconds) * 1000)

        return milliSeconds
    }

    render() {
        return <div className="timer-manual-entry">
            <form className="timer-manual-form" onSubmit={e => {
                e.preventDefault()
                if (this.state.value === "") return
                this.props.submit(this.convertToMilliseconds(this.state.value))
            }}>
                <input
                    className="timer-manual-input"
                    type="text"
                    value={this.state.value}
                    onChange={e => this.processChange(e.target.value)}
                    placeholder="00:00.00"
                    disabled={this.props.disabled}
                />
                <button className="timer-manual-submit" type="submit" disabled={this.props.disabled}>
                    <i className="fas fa-arrow-right" />
                </button>
            </form>
        </div>
    }
}