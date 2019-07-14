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
            .filter(solve => !Number.isNaN(Number(solve)))
            .reverse()[0]

        return <div className="container-fluid timer-container">
            <div className="sidebar">
                <span className="sidebar-title"></span>
                <div className="sidebar-times">
                    {this.state.event.event.solves.map((solve, count) =>
                        <div key={`solve_${count}`}>{solve}</div>
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
                    solve={!latestSolve ? "none" : { time: latestSolve }}
                    postTime={() => { }}
                />
            </div>
        </div>
    }
}