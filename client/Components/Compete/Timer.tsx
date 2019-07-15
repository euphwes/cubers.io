import * as React from 'react'

import * as Api from '../../api/api'
import * as Types from '../../api/types'
import * as Helpers from '../../api/helpers'

type TimerProps = {
    solve: { time: string } | "none"
    postTime: (time: number) => void
}

type TimerState = {
    timerState: TimeState
    timerStart: number | "none"
    timerEnd: number | "none"
    timerDelta: number | "none"
    timerStartKey: string
    timerPenalty: "none" | "+2" | "DNF"
}

type TimeState = "idle" | "timing" | "ready" | "starting" | "finished"

export class Timer extends React.Component<TimerProps, TimerState>{
    constructor(props: TimerProps) {
        super(props)

        this.state = {
            timerState: "idle",
            timerStart: "none",
            timerEnd: "none",
            timerDelta: "none",
            timerStartKey: "",
            timerPenalty: "none"
        }
    }

    onKeyDown = (event: KeyboardEvent) => {
        if (this.state.timerState === "timing"){
            if (this.state.timerStart === "none") throw "impossible"

            let time = Date.now()
            let delta = time - this.state.timerStart
            console.log(delta)
            this.setState({ timerState: "finished", timerEnd: time, timerDelta: delta })
        }

        if (event.key !== " ") return

        if (this.state.timerState === "idle") {
            let startKey = Math.random().toString()
            this.setState({ timerState: "starting", timerStartKey: startKey }, () => {
                setTimeout(() => {
                    if (startKey !== this.state.timerStartKey) return

                    if (this.state.timerState === "starting") {
                        this.setState({ timerState: "ready" })
                    }
                }, 500)
            })
        }
    }
    onKeyUp = () => {
        if (this.state.timerState === "starting") {
            this.setState({ timerState: "idle" })
        }

        if (this.state.timerState === "ready") {
            let interval = setInterval(() => {
                if (this.state.timerState === "timing") {
                    if (this.state.timerStart !== "none")
                        this.setState({ timerDelta: Date.now() - this.state.timerStart })
                } else {
                    clearInterval(interval)
                }
            }, 16)
            let time = Date.now()
            this.setState({ timerState: "timing", timerStart: time })
        }

        if (this.state.timerState === "finished") {
            this.setState({ timerState: "idle" })
        }
    }

    componentDidMount() {
        window.addEventListener('keydown', this.onKeyDown)
        window.addEventListener('keyup', this.onKeyUp)
    }

    componentWillUnmount() {
        window.removeEventListener('keydown', this.onKeyDown)
        window.removeEventListener('keyup', this.onKeyUp)
    }

    getTime(time: number | "none") {
        if (time === "none") return "0.00"
        return Helpers.toReadableTime(time)
    }

    getTimerState(state: TimeState) {
        if (state === "ready" || state === "timing")
            return state
        return ""
    }

    render() {
        return <div className="timer-wrapper">
            <div className={`timer-time ${this.getTimerState(this.state.timerState)}`}>
                {this.props.solve === "none" ?
                    this.getTime(this.state.timerDelta) :
                    this.props.solve.time
                }
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