import * as React from 'react'
import * as ReactDom from 'react-dom'
import { Header } from './Components/Header/Header';
import { MainRouter } from './router';

export class App extends React.Component<{}, {}> {
    render() {
        return <MainRouter />
    }
}

ReactDom.render(
    <App />,
    document.getElementById("application")
)