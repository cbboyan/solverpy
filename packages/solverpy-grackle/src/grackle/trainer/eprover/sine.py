from ..domain.grackle import GrackleDomain


class SineDomain(GrackleDomain):
    """SinE axiom selection parameters."""

    @property
    def params(self):
        return {
            "sine": ["0", "1"],
            "sineG": ["CountFormulas", "CountTerms"],
            "sineh": ["none", "hypos"],
            "sinegf": ["1.0", "1.1", "1.2", "1.4", "1.5", "2.0", "5.0", "6.0"],
            "sineD": ["none", "1", "3", "10", "20", "40", "160"],
            "sineR": ["none", "01", "02", "03", "04"],
            "sineL": ["10", "20", "40", "60", "80", "100", "500", "20000"],
            "sineF": ["1.0", "0.8", "0.6"],
        }

    @property
    def defaults(self):
        return {
            "sine": "1",
            "sineG": "CountFormulas",
            "sineh": "hypos",
            "sinegf": "1.2",
            "sineD": "none",
            "sineR": "none",
            "sineL": "100",
            "sineF": "1.0",
        }

    @property
    def conditions(self):
        return [
            ("sineG",  "sine", ["1"]),
            ("sineh",  "sine", ["1"]),
            ("sinegf", "sine", ["1"]),
            ("sineD",  "sine", ["1"]),
            ("sineR",  "sine", ["1"]),
            ("sineL",  "sine", ["1"]),
            ("sineF",  "sine", ["1"]),
        ]
