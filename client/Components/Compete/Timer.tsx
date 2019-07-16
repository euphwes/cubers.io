import * as React from 'react'

import * as Api from '../../api/api'
import * as Types from '../../api/types'
import * as Helpers from '../../api/helpers'

type TimerProps = {
    previousSolve: { time: string } | "none"
    currentScrambleId: { id: number } | "none"
    eventName: string
    comment: string
    postTime: (time: number, penalty: Penalty) => void
    postPenalty: (penalty: Penalty) => void
    deleteTime: () => void
    updateComment: (text: string) => void
}

type TimerState = {
    timerState: TimeState
    timerStart: number | "none"
    timerEnd: number | "none"
    timerDelta: number | "none"
    timerStartKey: string
    timerPenalty: Penalty
    prompt: "delete" | "comment" | "none"
    comment: string
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
            timerPenalty: "none",
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
                            this.setState({ prompt: "none" }, () => {
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
        let disabled = this.props.previousSolve === "none"
        let buttonStyle = disabled ? "disabled" : "enabled"

        return <div className="timer-wrapper">
            {this.renderPrompt()}
            <span className={`timer-time ${this.getTimerState(this.state.timerState)}`}>
                {this.getTime()}
            </span>
            <div className="timer-buttons">
                <button className={`timer-modifier-button ${buttonStyle}`} disabled={disabled} onClick={e => {
                    this.setState({ prompt: "delete" })
                }}>
                    <i className="fas fa-undo"></i>
                </button>
                <button className={`timer-modifier-button ${buttonStyle}`} disabled={disabled} onClick={e => {
                    this.updateTime("+2")
                    e.currentTarget.blur()
                }}>
                    <span>+2</span>
                </button>
                <button className={`timer-modifier-button ${buttonStyle}`} disabled={disabled} onClick={e => {
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