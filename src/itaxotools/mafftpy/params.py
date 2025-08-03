from itaxotools.common.param import Field, Group


def params():
    return Group(
        key="root",
        children=[
            Group(
                key="general",
                label="General",
                children=[
                    Field(
                        key="strategy",
                        label="Strategy",
                        doc=("Strategy"),
                        type=str,
                        list={"auto": "Auto", "fftns1": "FFT-NS-1", "ginsi": "G-INS-i"},
                        default="auto",
                    ),
                    Field(
                        key="adjustdirection",
                        label="adjustdirection",
                        doc=("adjustdirection"),
                        type=int,
                        default=0,
                    ),
                ],
            )
        ],
    )
