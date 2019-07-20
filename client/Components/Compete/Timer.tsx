import * as React from 'react'

import * as Api from '../../api/api'
import * as Types from '../../api/types'
import * as Helpers from '../../api/helpers'
import { ManualEntry } from '../Helper/ManualEntry';

type TimerProps = {
    settings: Types.UserSettings
    previousSolve: Types.PreviousSolve | "none"
    currentScrambleId: { id: number } | "none"
    eventName: string
    comment: string
    postTime: (time: number, penalty: Penalty, callback: () => void) => void
    postPenalty: (penalty: Penalty) => void
    deleteTime: () => void
    updateComment: (text: string) => void
}

type TimerState = {
    timer: TimerInfo
    prompt: "delete" | "comment" | "none"
    comment: string
}

type TimeState = "idle" | "starting-inspection" | "inspecting" | "starting" | "ready" | "timing" | "finished"
type Penalty = "none" | "+2" | "DNF"
type TimerInfo = {
    state: TimeState
    start: number | "none"
    end: number | "none"
    delta: number | "none"
    startKey: string
    penalty: Penalty
    inspectionTime: number
    inspectionStart: number | "none"
    inspectionPenalty: Penalty
}

let initialTimerInfo: TimerInfo = {
    state: "idle",
    start: "none",
    end: "none",
    delta: "none",
    startKey: "",
    penalty: "none",
    inspectionTime: 15,
    inspectionStart: "none",
    inspectionPenalty: "none"
}

export class Timer extends React.Component<TimerProps, TimerState>{
    constructor(props: TimerProps) {
        super(props)

        this.state = {
            timer: initialTimerInfo,
            prompt: "none",
            comment: props.comment
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

    onKeyDown = (event: KeyboardEvent) => {
        if (this.state.prompt !== "none") return
        if (this.props.currentScrambleId === "none") return
        if (this.state.timer.state === "timing") {
            if (this.state.timer.start === "none") throw "impossible"

            let time = Date.now()
            let delta = time - this.state.timer.start
            this.setState({ timer: { ...this.state.timer, state: "finished", end: time, delta: delta } }, () => {
                this.props.postTime(delta, this.state.timer.inspectionPenalty, () => {
                    this.setState({ timer: initialTimerInfo })
                })
            })
        }

        if (event.key !== " ") return

        if (this.state.timer.state === "idle") {
            let isBlind = this.props.eventName.toLowerCase().includes("bld")
            let inspection = this.props.settings.use_inspection_time

            if (inspection && !isBlind) {
                this.setState({ timer: { ...this.state.timer, state: "starting-inspection" } })
            } else {
                this.prepareStart()
            }
        }

        if (this.state.timer.state === "inspecting") {
            this.prepareStart()
        }
    }

    prepareStart() {
        let startKey = Math.random().toString()
        this.setState({ timer: { ...this.state.timer, state: "starting", startKey: startKey } }, () => {
            setTimeout(() => {
                if (startKey !== this.state.timer.startKey) return

                if (this.state.timer.state === "starting") {
                    this.setState({ timer: { ...this.state.timer, state: "ready" } })
                }
            }, 400)
        })
    }

    onKeyUp = () => {
        if (this.state.timer.state === "finished") {
            this.setState({ timer: { ...this.state.timer, state: "idle" } })
        }

        if (this.props.currentScrambleId === "none") return

        if (this.state.timer.state === "starting-inspection") {
            this.setState({ timer: { ...this.state.timer, state: "inspecting", inspectionStart: Date.now() } }, () => {
                let interval = setInterval(() => {
                    let inspec = this.state.timer.inspectionStart as number
                    let inst = parseInt(`${(Date.now() - inspec) / 1000}`)

                    if (this.state.timer.state === "inspecting" || this.state.timer.state === "starting" || this.state.timer.state === "ready") {
                        this.setState({ timer: { ...this.state.timer, inspectionTime: 15 - inst } }, () => {
                            if (this.state.timer.inspectionTime <= 0)
                                this.setState({ timer: { ...this.state.timer, inspectionPenalty: "+2" } })
                            if (this.state.timer.inspectionTime <= -2)
                                this.setState({ timer: { ...this.state.timer, state: "idle", inspectionPenalty: "DNF" } }, () => {
                                    this.props.postTime(-10, "DNF", () => {
                                        this.setState({ timer: initialTimerInfo })
                                    })
                                })
                        })
                    } else {
                        clearInterval(interval)
                    }
                }, 16)
            })
        }

        if (this.state.timer.state === "starting") {
            let previousState: "inspecting" | "idle" = this.props.settings.use_inspection_time ? "inspecting" : "idle"
            this.setState({ timer: { ...this.state.timer, state: previousState } })
        }

        if (this.state.timer.state === "ready") {
            let interval = setInterval(() => {
                if (this.state.timer.state === "timing") {
                    if (this.state.timer.start !== "none")
                        this.setState({ timer: { ...this.state.timer, delta: Date.now() - this.state.timer.start } })
                } else {
                    clearInterval(interval)
                }
            }, 16)
            let time = Date.now()
            this.setState({ timer: { ...this.state.timer, state: "timing", start: time, delta: 0 } })
        }
    }

    getTime() {
        if (this.state.timer.state === "inspecting") {
            if (this.props.settings.hide_inspection_time) return "Inspect"
            if (this.state.timer.inspectionTime <= -2) return "DNF"
            if (this.state.timer.inspectionTime <= 0) return "+2"
            return this.state.timer.inspectionTime
        }
        if (this.state.timer.state === "starting" || this.state.timer.state === "ready") return "0.00"
        if (this.state.timer.state === "timing") {
            if (this.props.settings.hide_running_timer) return "Solve"
            return Helpers.toReadableTime(this.state.timer.delta as number)
        }
        if (this.state.timer.delta !== "none") return Helpers.toReadableTime(this.state.timer.delta)
        if (this.props.previousSolve !== "none") return this.props.previousSolve.time
        return "0.00"
    }

    getTimerState(state: TimeState) {
        if (state === "ready" || state === "timing")
            return state
        return ""
    }

    getInspectionState() {
        if (this.state.timer.inspectionTime <= -2) return "dnf"
        if (this.state.timer.state === "timing") return ""
        if (this.state.timer.inspectionTime <= 0) return "penalty"
        return ""
    }

    updateTime(penalty: Penalty) {
        this.props.postPenalty(penalty)
    }

    getPenaltyState(): Penalty {
        if (this.props.previousSolve === "none") return
        if (this.props.previousSolve.is_dnf) return "DNF"
        if (this.props.previousSolve.is_plus_2) return "+2"
    }

    renderTime() {
        let timeEntryDisabled = this.props.currentScrambleId === "none"
        if (this.props.settings.manual_time_entry_by_default)
            return <ManualEntry disabled={timeEntryDisabled} submit={(value) => this.props.postTime(value, "none", () => { })} />

        return <span className={`timer-time ${this.getTimerState(this.state.timer.state)} ${this.getInspectionState()}`}>
            {this.getTime()}
        </span>
    }

    renderPrompt() {
        if (this.props.previousSolve === "none") return
        if (this.state.prompt === "delete") {
            return <div className="prompt-background">
                <div className="timer-prompt">
                    <div className="prompt-message-bar">
                        <span className="prompt-message">Are you sure you want to delete your last solve? ({this.props.previousSolve.time})</span>
                        <button className="prompt-blank" onClick={() => this.setState({ prompt: "none" })}>×</button>
                    </div>
                    <div className="prompt-buttons">
                        <button className="prompt-button cancel" onClick={() => this.setState({ prompt: "none" })}>
                            Cancel
                        </button>
                        <button className="prompt-button" onClick={() =>
                            this.setState({ prompt: "none", timer: initialTimerInfo }, () => {
                                this.props.deleteTime()
                            })
                        }>Yes</button>
                    </div>
                </div>
            </div>
        }

        if (this.state.prompt === "comment") {
            return <div className="prompt-background">
                <div className="timer-prompt">
                    <div className="prompt-message-bar">
                        <span className="prompt-message">Comment for {this.props.eventName}</span>
                        <button className="prompt-blank" onClick={() => this.setState({ prompt: "none" })}>×</button>
                    </div>
                    <div className="prompt-textbox">
                        <textarea
                            className="prompt-textbox-input"
                            onChange={e => this.setState({ comment: e.target.value })}
                            value={this.state.comment}
                            autoFocus={true}
                        />
                    </div>
                    <div className="prompt-buttons">
                        <button className="prompt-button cancel" onClick={() => this.setState({ prompt: "none", comment: this.props.comment })}>Cancel</button>
                        <button className="prompt-button" onClick={() =>
                            this.setState({ prompt: "none" }, () => {
                                this.props.updateComment(this.state.comment)
                            })
                        }>Update Comment</button>
                    </div>
                </div>
            </div>
        }

        return <div className="prompt-background invisible"></div>
    }

    render() {
        let disabled = this.props.previousSolve === "none" || this.state.timer.state !== "idle"
        let penaltyDisabled = this.props.previousSolve === "none" || this.state.timer.state !== "idle" || this.props.previousSolve.is_inspection_dnf
        let buttonStyle = disabled ? "disabled" : "enabled"
        let penaltyButtonStyle = penaltyDisabled ? "disabled" : "enabled"

        return <div className="timer-wrapper">
            {this.renderPrompt()}
            {this.renderTime()}
            <div className="timer-buttons">
                <button className={`timer-modifier-button ${buttonStyle}`} disabled={disabled} onClick={e => {
                    this.setState({ prompt: "delete" })
                }}>
                    <i className="fas fa-undo"></i>
                </button>
                <button className={`timer-modifier-button ${penaltyButtonStyle} ${this.getPenaltyState() === "+2" ? "active" : ""}`} disabled={penaltyDisabled} onClick={e => {
                    this.updateTime("+2")
                    e.currentTarget.blur()
                }}>
                    <span>+2</span>
                </button>
                <button className={`timer-modifier-button ${penaltyButtonStyle} ${this.getPenaltyState() === "DNF" ? "active" : ""}`} disabled={penaltyDisabled} onClick={e => {
                    this.updateTime("DNF")
                    e.currentTarget.blur()
                }}>
                    <span>DNF</span>
                </button>
                <button className={`timer-modifier-button ${buttonStyle}`} disabled={disabled} onClick={e => {
                    this.setState({ prompt: "comment" })
                }}>
                    <i className="far fa-comment"></i>
                </button>
            </div>
        </div>
    }
}