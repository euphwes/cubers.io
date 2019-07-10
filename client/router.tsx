import * as React from 'react'
import { Router, Route } from 'react-router'
import { Header } from './header/Header';
import { BrowserRouter } from 'react-router-dom';

export class MainRouter extends React.Component<{}, {}> {
    render() {
        return <BrowserRouter>
            <Header />
            <div>Application</div>
        </BrowserRouter>
    }
}