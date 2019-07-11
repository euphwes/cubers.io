import * as React from 'react'
import { Header } from './Components/Header/Header';
import { BrowserRouter } from 'react-router-dom';

export class MainRouter extends React.Component<{}, {}> {
    render() {
        return <BrowserRouter>
            <Header />
            <div>Application</div>
        </BrowserRouter>
    }
}