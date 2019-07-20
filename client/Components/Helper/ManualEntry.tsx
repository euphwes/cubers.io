import * as React from 'react'

type ManualEntryProps = {
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
        let cleanValue = this.cleanInput(value)
        let numberValue = Number(cleanValue)
        if (Number.isNaN(numberValue)) return

        if (numberValue === 0) return this.setState({ value: "" })

        let goodValue = `${numberValue}`

        let newValue = goodValue.length < 4 ? ("0000" + goodValue).slice(-4) : goodValue
        if (goodValue.length > 4) {
            newValue = newValue.slice(0, -4) + ':' + newValue.slice(-4)
        }
        newValue = newValue.slice(0, -2) + '.' + newValue.slice(-2)
        this.setState({ value: newValue })
    }

    cleanInput(value: string) {
        return value.replace(".", "").replace(",", "").replace(":", "")
    }

    convertToCentiseconds(value: string) {
        if (value.length <= 5) return Number(value) * 100

        let minutes = Number(value.includes(':') ? value.split(':')[0] : 0) * 60
        let centiseconds = Math.round((Number(value.includes(':') ? value.split(':')[1] : value) + minutes) * 100)

        return centiseconds
    }

    render() {
        return <form onSubmit={e => {
            e.preventDefault()
            if (this.state.value === "") return
            this.props.submit(this.convertToCentiseconds(this.state.value))
        }}>
            <input type="text" value={this.state.value} onChange={e => {
                this.processChange(e.target.value)
            }} />
            <button type="submit">
                <i className="fas fa-arrow-right" />
            </button>
        </form>
    }
}