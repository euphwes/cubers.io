import * as React from 'react'
import { Route, Switch } from 'react-router'
import { Header } from './Components/Header/Header';
import { BrowserRouter } from 'react-router-dom';
import { Home } from './Components/Home/Home';
import { Compete } from './Components/Compete/Compete';

import * as Api from './api/api'
import * as Types from './api/types'

type RouterState = {
    settings: Types.UserSettings | "loading"
}

type RouterProps = {}

export class MainRouter extends React.Component<RouterProps, RouterState> {
    constructor(props: RouterProps) {
        super(props)

        this.state = {
            settings: "loading"
        }
    }

    componentDidMount() {
        Api.getUserSettings()
            .then(settings => this.setState({ settings: settings }))
    }

    render() {
        if (this.state.settings === "loading") return null
        
        return <BrowserRouter>
            <Header />

            <Switch>
                <Route exact path="/" component={() => <Home />} />

                <Route path="/compete/:eventType" component={({ match }: any) =>
                    <Compete eventType={Number(match.params.eventType)} />
                } />
                <Route path="/event" component={() => <div>Event</div>} />
            </Switch>
        </BrowserRouter>
    }
}