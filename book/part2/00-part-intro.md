An agent runs inside a stack of layers, and every layer is a place to steer. This Part builds
the environment that does the steering. You will see why a structured model — not prose, not
raw code — is the sweet spot for handing an agent intent, and why enforcing a property at the
wrong level lets it slip through. From there the environment fills in: the things you can
decide up front and the ones you learn only by building, the lifecycles and runbooks that give
an agent its operating context, the metrics that let a loop sense whether it is working, and
what to do when two controls demand incompatible things. By the end you hold a working
vocabulary of constraints and sensors, and a graph that draws what lies between them.
