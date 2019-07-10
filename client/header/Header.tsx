import * as React from 'react'

type HeaderProps = {

}

type HeaderState = {
    name: string
}

export class Header extends React.Component<HeaderProps, HeaderState> {
    constructor(props: HeaderProps) {
        super(props)

        this.state = {
            name: "cubers.io"
        }
    }

    render() {
        return <div></div>
    }
}