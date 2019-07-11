import * as React from 'react'
import { Link } from 'react-router-dom'
import * as Api from '../../api/api'
import * as Types from '../../api/types'

type HeaderProps = {

}

type HeaderState = {
    title: string
    recordsItems: Types.Record | "loading"
    leaderboardItems: Types.Leaderboard | "loading",
    current_user: Types.CurrentUser
}

export class Header extends React.Component<HeaderProps, HeaderState> {
    constructor(props: HeaderProps) {
        super(props)

        this.state = {
            title: "cubers.io",
            recordsItems: "loading",
            leaderboardItems: "loading",
            current_user: "none"
        }
    }

    componentDidMount() {
        Api.getHeaderInfo()
            .then(info => this.setState({
                title: info.title,
                recordsItems: info.recordsItems,
                leaderboardItems: info.leaderboardItems,
                current_user: info.current_user
            }))
    }

    renderRecordItem(item: Types.HeaderItem, loading: boolean) {
        return item.urls.map((item, id) =>
            <Link
                key={id}
                className="dropdown-item slim-nav-item"
                to={item.url}
            >{item.name}</Link>
        )
    }

    renderRecords() {
        return <>
            <Link className="nav-link dropdown-toggle py-0" role="button" data-toggle="dropdown" data-submenu to="#">Records</Link>
            <div className="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                <div className="dropdown dropright dropdown-submenu">
                    <button className="dropdown-item dropdown-toggle" type="button">
                        {this.state.recordsItems !== "loading" ? this.state.recordsItems.wca.title : "Loading..."}
                    </button>
                    <div className="dropdown-menu">
                        {this.state.recordsItems !== "loading" ?
                            this.renderRecordItem(this.state.recordsItems.wca, false) : null}
                    </div>
                </div>
                <div className="dropdown dropright dropdown-submenu">
                    <button className="dropdown-item dropdown-toggle" type="button">
                        {this.state.recordsItems !== "loading" ? this.state.recordsItems.nonWca.title : "Loading..."}
                    </button>
                    <div className="dropdown-menu">
                        {this.state.recordsItems !== "loading" ?
                            this.renderRecordItem(this.state.recordsItems.nonWca, false) : null}
                    </div>
                </div>
                <div className="dropdown-divider" />
                <div className="dropdown dropright dropdown-submenu">
                    <button className="dropdown-item dropdown-toggle" type="button">
                        {this.state.recordsItems !== "loading" ? this.state.recordsItems.sum.title : "Loading..."}
                    </button>
                    <div className="dropdown-menu">
                        {this.state.recordsItems !== "loading" ?
                            this.renderRecordItem(this.state.recordsItems.sum, false) : null}
                    </div>
                </div>
            </div>
        </>
    }

    renderLeaderboards() {
        let leaderboard = this.state.leaderboardItems
        if (leaderboard === "loading") return null

        return <>
            <Link className="nav-link dropdown-toggle py-0" role="button" data-toggle="dropdown" to="#">Leaderboards</Link>
            <div className="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                <Link className="dropdown-item" to={leaderboard.current.url}>{leaderboard.current.name}</Link>
                <Link className="dropdown-item" to={leaderboard.previous.url}>{leaderboard.previous.name}</Link>
                <div className="dropdown-divider"></div>
                <Link className="dropdown-item" to={leaderboard.all.url}>{leaderboard.all.name}</Link>
            </div>
        </>
    }

    renderUser() {
        if (this.state.current_user === "none")
            return <Link className="nav-link py-0" to="/login">Login with Reddit</Link>

        return <>
            <Link className="nav-link dropdown-toggle py-0" role="button" data-toggle="dropdown" to="#">
                {this.state.current_user.name}
            </Link>
            <div className="dropdown-menu dropdown-menu-right">
                <Link className="dropdown-item" to={this.state.current_user.profile_url}>Profile</Link>
                <div className="dropdown-divider"></div>
                <Link className="dropdown-item" to="/logout">Logout</Link>
            </div>
        </>
    }

    renderSettings() {
        if (this.state.current_user === "none") return null
        return <Link className="nav-link py-0" to={this.state.current_user.settings_url}>
            <i className="fas fa-cog"></i>
        </Link>
    }

    render() {
        return <div>
            <div className="navbar navbar-expand-md navbar-dark cubers-navbar"></div>
            <div className="navbar navbar-expand-md fixed-top navbar-dark cubers-navbar">
                <div className="container-fluid">
                    <Link to="/" className="navbar-brand py-0">{this.state.title}</Link>

                    <button className="navbar-toggler py-0" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>

                    <div id="navbarCollapse" className="collapse navbar-collapse py-0">
                        <ul className="navbar-nav ml-auto py-0">
                            <li className="nav-item dropdown">{this.renderRecords()}</li>
                            <li className="nav-item dropdown">{this.renderLeaderboards()}</li>
                            <li className="nav-item dropdown">{this.renderUser()}</li>
                            <li className="nav-item nav-settings">{this.renderSettings()}</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    }
}