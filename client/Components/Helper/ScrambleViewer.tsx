import * as React from 'react'

import * as Types from '../../api/types'

import * as ScrambleGenerator from '../../api/helpers/scrambleGenerator/scramble_image_generator';


type ScrambleViewerProps = {
    event: Types.Event
    settings: Types.UserSettings
}

type ScrambleViewerState = {
    showBigScramble: boolean
}

export class ScrambleViewer extends React.Component<ScrambleViewerProps, ScrambleViewerState> {
    canvasRef: React.RefObject<HTMLCanvasElement>

    constructor(props: ScrambleViewerProps) {
        super(props)

        this.state = {
            showBigScramble: false
        }

        this.canvasRef = React.createRef()
    }

    componentDidMount() {
        this.canvasRef.current.width = 1500
        this.canvasRef.current.height = 300

        window.addEventListener('resize', this.handleResize)
        this.handleResize(null)
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.handleResize)
    }

    handleResize = (e: UIEvent) => {
        let event = this.props.event

        let ctx = this.canvasRef.current.getContext("2d")
        ctx.clearRect(0, 0, this.canvasRef.current.width, this.canvasRef.current.height)
        let generator = ScrambleGenerator.sig(event.currentScramble.text, event.event.name, this.props.settings)
        generator.showNormalImage()

        if (this.state.showBigScramble) {
            generator.showLargeImage()
        }
    }

    showScrambleFullscreen() {
        if (!this.state.showBigScramble) return <span className="fullscreen-scramble-preview hide"></span>

        return <span className="fullscreen-scramble-preview">
            <button className="scramble-preview-button-big" onClick={() => {
                this.setState({ showBigScramble: false })
            }}>
                <canvas
                    ref={this.canvasRef}
                    id="big_scramble_image"
                    className="scramble-preview-large"
                />
            </button>
        </span>
    }

    render() {
        let hide = this.props.settings.hide_scramble_preview

        return <div className="sidebar-scramble-preview">
            <button className={`scramble-preview-button${hide ? "-hide" : ""}`} onClick={() => {
                this.setState({ showBigScramble: true }, () => {
                    this.handleResize(null)
                })
            }}>
                <canvas
                    ref={this.canvasRef}
                    id="normal_scramble_image"
                    className={`scramble-preview ${hide ? "invisible" : ""}`}
                />
                {hide ? "Show Scramble Preview" : null}
            </button>
            {this.showScrambleFullscreen()}
        </div>
    }
}