properties = dict(
    name='collector-server',
    sdncontroller="10.0.9.100:8080",
    peers=dict(
        # a list of available agents, i.e <addr:port>
        i2cat=["10.0.9.100:9001"],
        psnc=["10.0.9.100:9002"],
        aist=["10.0.9.100:9003"]
    ),
    monitor=[
        {
            "name": "i2cat->psnc",
            "srcaddr": "10.0.9.100",
            "srcport": 9001,
            "dstaddr": "10.0.9.100",
            "rtt": 0
        }, {
            "name": "i2cat->aist",
            "srcaddr": "10.0.9.100",
            "srcport": 9001,
            "dstaddr": "10.0.9.100",
            "rtt": 0
        }, {
            "name": "psnc->i2cat",
            "srcaddr": "10.0.9.100",
            "srcport": 9002,
            "dstaddr": "10.0.9.100",
            "rtt": 0
        }, {
            "name": "psnc->aist",
            "srcaddr": "10.0.9.100",
            "srcport": 9002,
            "dstaddr": "10.0.9.100",
            "rtt": 0
        }, {
            "name": "aist->i2cat",
            "srcaddr": "10.0.9.100",
            "srcport": 9003,
            "dstaddr": "10.0.9.100",
            "rtt": 0
        }, {
            "name": "aist->psnc",
            "srcaddr": "10.0.9.100",
            "srcport": 9003,
            "dstaddr": "10.0.9.100",
            "rtt": 0
        }
    ]
)
