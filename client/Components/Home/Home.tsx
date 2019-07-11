import * as React from 'react'

import * as Api from '../../api/api'
import { CompetitionEvent } from '../../api/types'
import { Link } from 'react-router-dom';

type HomeProps = {

}

type HomeState = {
    events: CompetitionEvent[] | "loading"
}

export class Home extends React.Component<HomeProps, HomeState>{
    constructor(props: HomeProps) {
        super(props)

        this.state = {
            events: "loading"
        }
    }

    async componentDidMount() {
        let events = await Api.getCompetitionEvents()

        this.setState({ events: events })
    }

    render() {
        if (this.state.events === "loading") return null

        return <div className="container">
            <div className="ultra-hidden"></div>
            <div className="row event-cards">
                {this.state.events.map(e => this.renderCard(e))}
            </div>
        </div>
    }

    renderOverlay(status: "not_started" | "incomplete" | "complete") {
        if (status === "not_started") return null
        return <div className={`overlay ${status}-overlay`}>
            <span className="icon">
                <i className="fas fa-check"></i>
            </span>
        </div>
    }

    renderCard(event: CompetitionEvent) {
        return <Link to={event.competeLocation} key={`comp_event_${event.compId}`} className={`event-card drop-shadow ${event.status === "not_started" ? "" : event.status}`}>
            <div className="event-image-container">
                <img className="event-image" src={`./static/images/cube-${event.compId}.png`} />
                {this.renderOverlay(event.status)}
            </div>

            <div className="event-name">
                <hr />
                <div className="row">
                    <div className="col-12"><span className="event-title" />{event.name}</div>
                </div>
            </div>

            <span className="event-summary">{event.summary}</span>

            {event.bonusEvent ? <div className="bonus-event-indicator">
                <i className="fas fa-gift"></i>
            </div> : null}
        </Link>
    }
}