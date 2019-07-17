import * as React from 'react'

type FitTextProps = {
    text: string
}

type FitTextState = {
    fontSize: string
}

export class FitText extends React.Component<FitTextProps, FitTextState>{
    scrambleRef: React.RefObject<HTMLDivElement>

    constructor(props: FitTextProps) {
        super(props)

        this.state = {
            fontSize: ""
        }

        this.scrambleRef = React.createRef()
    }

    updateFontSize = (e: UIEvent) => {
        let target = this.scrambleRef.current

        let length = this.props.text.length
        let width = target.clientWidth
        let height = target.clientHeight

        let viewsize = Math.sqrt((width * height) / length)
        let size = Math.min(viewsize, 50);

        this.setState({ fontSize: `${size}px` })
    }

    componentDidMount() {
        window.addEventListener('resize', this.updateFontSize)
        this.updateFontSize(null)
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.updateFontSize)
    }

    render() {
        return <div className="fit-text-wrapper" ref={this.scrambleRef} style={{ fontSize: this.state.fontSize }}>
            {this.props.text}
        </div>
    }
}
