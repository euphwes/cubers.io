import * as React from 'react'
import { Link } from 'react-router-dom'
import * as Api from '../api/api'
import * as Types from '../api/types'

type HeaderProps = {

}

type HeaderState = {
    title: string
    recordsItems: {
        wca: Types.HeaderItem
        nonWca: Types.HeaderItem
        sum: Types.HeaderItem
    } | "loading"
}

export class Header extends React.Component<HeaderProps, HeaderState> {
    constructor(props: HeaderProps) {
        super(props)

        this.state = {
            title: "cubers.io",
            recordsItems: "loading"
        }
    }

    componentDidMount() {
        Api.getHeaderInfo()
            .then(info => this.setState({
                title: info.title,
                recordsItems: {
                    wca: info.recordsItems.wca,
                    nonWca: info.recordsItems.nonWca,
                    sum: info.recordsItems.sum
                }
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
            <a className="nav-link dropdown-toggle py-0" role="button" data-toggle="dropdown" data-submenu href="#">Records</a>
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
        return <>
            {/* <a className="nav-link dropdown-toggle py-0" role="button" data-toggle="dropdown" href="#">Leaderboards</a>
            <div className="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                <a className="dropdown-item" href="{{ url_for('curr_leaders') }}">Current Competition</a>
                <a className="dropdown-item" href="{{ url_for('prev_leaders') }}">Last Week's Competition</a>
                <div className="dropdown-divider"></div>
                <a className="dropdown-item" href="{{ url_for('results_list') }}">All competitions</a>
            </div> */}
        </>
    }

    renderUser() {
        return <>
            {/* <a className="nav-link dropdown-toggle py-0" role="button" data-toggle="dropdown" href="#">
                {{ current_user.username }}
        </a>
            <div className="dropdown-menu dropdown-menu-right">
                <a className="dropdown-item" href="{{ url_for('profile', username=current_user.username) }}">Profile</a>
                <div className="dropdown-divider"></div>
                <a className="dropdown-item" href="{{ url_for('logout') }}">Logout</a>
            </div> */}
        </>
    }

    render() {
        return <div className="navbar navbar-expand-md navbar-dark cubers-navbar">
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

                        {/* {% if current_user.is_authenticated %} */}

                        <li className="nav-item nav-settings">
                            <a className="nav-link py-0" href="{{ url_for('edit_settings')}}">
                                <i className="fas fa-cog"></i>
                            </a>
                        </li>
                        {/* {% else %} */}
                        {/* <li className="nav-item">
                    <a className="nav-link py-0" href="{{ url_for('login') }}">Login with Reddit</a>
                </li> */}
                        {/* {% endif %} */}
                    </ul>
                </div>


            </div>
        </div>
    }
}