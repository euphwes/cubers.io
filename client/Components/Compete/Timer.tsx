import * as React from 'react'

type TimerProps = {
    solve: { time: string } | "none"
    postTime: (time: number) => void
}
type TimerState = {}

export class Timer extends React.Component<TimerProps, TimerState>{
    constructor(props: TimerProps) {
        super(props)

        this.state = {}
    }

    onKeyDown = (event: KeyboardEvent) => {
        console.log(event.key)
    }

    componentDidMount() {
        window.addEventListener('keydown', this.onKeyDown)
    }

    componentWillUnmount() {
        window.removeEventListener('keydown', this.onKeyDown)
    }

    render() {
        return <div className="timer-wrapper">
            <div className="timer-time">
                {this.props.solve === "none" ? "0.00" : this.props.solve.time}
            </div>
            <div className="timer-buttons">
                <button className="timer-modifier-button"></button>
                <button className="timer-modifier-button"></button>
                <button className="timer-modifier-button"></button>
                <button className="timer-modifier-button"></button>
            </div>
        </div>
    }
}