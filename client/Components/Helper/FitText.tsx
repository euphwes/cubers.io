import * as React from 'react'

type FitTextProps = {
    text: string
}

type FitTextState = {
    fontSize: string
    lines: number
}

export class FitText extends React.Component<FitTextProps, FitTextState>{
    scrambleRef: React.RefObject<HTMLDivElement>

    constructor(props: FitTextProps) {
        super(props)

        this.state = {
            fontSize: "",
            lines: props.text.split("\n").length
        }

        this.scrambleRef = React.createRef()
    }

    updateFontSize = (e: UIEvent) => {
        let target = this.scrambleRef.current

        let length = this.props.text.length
        let width = target.clientWidth
        let height = target.clientHeight

        let viewsize = Math.sqrt((width * height) / length)
        let characterPerLine = width / viewsize
        viewsize = Math.sqrt((width * height) / (length + (this.state.lines - 1) * characterPerLine))

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
        return <div className="fit-text-wrapper">
            <div className="fit-text-inner" ref={this.scrambleRef} style={{ fontSize: this.state.fontSize }}>
                {this.props.text.split("\n").map((line, count) => <span key={`fit-text-${count}`}>
                    {line}
                </span>)}
            </div>
        </div>
    }
}
