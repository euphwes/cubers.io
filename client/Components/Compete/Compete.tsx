import * as React from 'react'

import * as Api from '../../api/api'
import * as Types from '../../api/types'
import { Timer } from './Timer';

type CompeteProps = {
    eventType: number
}

type CompeteState = {
    event: Types.Event | "loading"
}

export class Compete extends React.Component<CompeteProps, CompeteState>{
    constructor(props: CompeteProps) {
        super(props)

        this.state = {
            event: "loading"
        }
    }

    componentDidMount() {
        Api.getEventInfo(this.props.eventType)
            .then(event => this.setState({ event: event }))
    }

    render() {
        if (this.state.event === "loading") return null


        let latestSolve = this.state.event.event.solves
            .filter(solve => solve !== "—")
            .reverse()[0]

        return <div className="compete-container">
            <div className="sidebar">
                <div className="sidebar-title">Solves</div>
                <div className="sidebar-times">
                    {this.state.event.event.solves.map((solve, count) =>
                        <div
                            key={`solve_${count}`}
                            className="time"
                        >{solve}</div>
                    )}
                </div>
                <div className="sidebar-scramble-preview">
                    {/* Scramble Preview */}
                </div>
            </div>

            <div className="timer-container">
                <div className="scramble-wrapper">
                    {this.state.event.currentScramble.text}
                </div>
                <Timer
                    previousSolve={!latestSolve ? "none" : { time: latestSolve }}
                    currentScrambleId={this.state.event.currentScramble.id === -1 ?
                        "none" :
                        { id: this.state.event.currentScramble.id }
                    }
                    eventName={this.state.event.event.name}
                    comment={this.state.event.event.comment}
                    postTime={(time, callback) => {
                        let event = this.state.event as Types.Event
                        Api.postSolve({
                            comp_event_id: event.event.id,
                            elapsed_centiseconds: parseInt(`${time / 10}`),
                            is_dnf: false,
                            is_plus_two: false,
                            scramble_id: event.currentScramble.id
                        }).then(newEvent => this.setState({ event: newEvent }, () => callback()))
                    }}
                    postPenalty={(penalty) => {
                        let event = this.state.event as Types.Event
                        if (penalty === "+2") {
                            Api.putPlusTwo(event.event.id)
                                .then(newEvent => this.setState({ event: newEvent }))
                            return
                        }
                        if (penalty === "DNF") {
                            Api.putDnf(event.event.id)
                                .then(newEvent => this.setState({ event: newEvent }))
                            return
                        }
                    }}
                    deleteTime={() => {
                        let event = this.state.event as Types.Event
                        Api.deleteSolve(event.event.id)
                            .then(newEvent => this.setState({ event: newEvent }))
                    }}
                    updateComment={(text: string) => {
                        let event = this.state.event as Types.Event
                        Api.submitComment(event.event.id, text)
                            .then(newEvent => this.setState({ event: newEvent }))
                    }}
                />
            </div>
        </div>
    }
}