import * as React from 'react'
import { Route, Switch } from 'react-router'
import { Header } from './Components/Header/Header';
import { BrowserRouter } from 'react-router-dom';
import { Home } from './Components/Home/Home';

export class MainRouter extends React.Component<{}, {}> {
    render() {
        return <BrowserRouter>
            <Header />

            <Switch>
                <Route exact path="/" component={() => <Home />} />

                <Route path="/compete" component={() => <div>Compete</div>} />
                <Route path="/event" component={() => <div>Event</div>} />
            </Switch>
        </BrowserRouter>
    }
}