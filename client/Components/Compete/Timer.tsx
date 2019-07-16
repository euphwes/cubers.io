import * as React from 'react'

import * as Api from '../../api/api'
import * as Types from '../../api/types'
import * as Helpers from '../../api/helpers'

type TimerProps = {
    previousSolve: { time: string } | "none"
    currentScrambleId: { id: number } | "none"
    postTime: (time: number, penalty: Penalty) => void
    postPenalty: (penalty: Penalty) => void
}

type TimerState = {
    timerState: TimeState
    timerStart: number | "none"
    timerEnd: number | "none"
    timerDelta: number | "none"
    timerStartKey: string
    timerPenalty: Penalty
}

type TimeState = "idle" | "timing" | "ready" | "starting" | "finished"
type Penalty = "none" | "+2" | "DNF"

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
        if (this.props.currentScrambleId === "none") return
        if (this.state.timerState === "timing") {
            if (this.state.timerStart === "none") throw "impossible"

            let time = Date.now()
            let delta = time - this.state.timerStart
            this.setState({ timerState: "finished", timerEnd: time, timerDelta: delta }, () => {
                this.props.postTime(delta, "none")
            })
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
        if (this.props.currentScrambleId === "none") return
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

    getTime() {
        if (this.state.timerState === "starting" || this.state.timerState === "ready") return "0.00"
        if (this.state.timerState === "timing") return Helpers.toReadableTime(this.state.timerDelta as number)
        if (this.state.timerDelta !== "none") return Helpers.toReadableTime(this.state.timerDelta)
        if (this.props.previousSolve !== "none") return this.props.previousSolve.time
        return "0.00"
    }

    getTimerState(state: TimeState) {
        if (state === "ready" || state === "timing")
            return state
        return ""
    }

    updateTime(penalty: Penalty) {
        this.props.postPenalty(penalty)
    }

    render() {
        let disabled = this.props.previousSolve === "none"

        return <div className="timer-wrapper">
            <div className={`timer-time ${this.getTimerState(this.state.timerState)}`}>
                {this.getTime()}
            </div>
            <div className="timer-buttons">
                <button className="timer-modifier-button" disabled={disabled}>
                    <i className="fas fa-undo"></i>
                </button>
                <button className="timer-modifier-button" disabled={disabled} onClick={() => this.updateTime("+2")}>
                    <span>+2</span>
                </button>
                <button className="timer-modifier-button" disabled={disabled} onClick={() => this.updateTime("DNF")}>
                    <span>DNF</span>
                </button>
                <button className="timer-modifier-button" disabled={disabled}>
                    <i className="far fa-comment"></i>
                </button>
            </div>
        </div>
    }
}