"""Provides pronoun helping functions with easy to read names."""


class Pronoun:
    """Pronoun can be called to generate pronouns."""

    def __init__(self):
        """Create Pronoun instance."""
        self.malePronouns = {"posadj": "his", "pospro": "his",
                             "obj": "him", "sub": "he",
                             "reflex": "himself"}
        self.femalePronouns = {"posadj": "her", "pospro": "hers",
                               "obj": "her", "sub": "she",
                               "reflex": "herself"}
        self.neutralPronouns = {"posadj": "their", "pospro": "theirs",
                                "obj": "them", "sub": "they",
                                "reflex": "themself"}
        self.neutralObject = {"posadj": "its", "pospro": "its",
                              "obj": "it", "sub": "it",
                              "reflex": "itself"}
        self.pronounMappings = {"m": self.malePronouns,
                                "f": self.femalePronouns,
                                "n": self.neutralPronouns,
                                "i": self.neutralObject}

    def __call__(self, gender="n", partofspeech="sub"):
        """Send back the English pronoun for a specific part of speech."""
        gender = gender.lower()
        partofspeech = partofspeech.lower()
        if gender not in self.pronounMappings:
            raise KeyError("Not a supported gender marker.")
        if partofspeech not in self.neutralObject:
            raise KeyError("Not a supported part of speech.")
        return self.pronounMappings[gender][partofspeech]

    def theirs(self, gender="n"):
        """Call for: his/hers/theirs/its."""
        return self(gender, "pospro")

    def their(self, gender="n"):
        """Call for: his/her/their/its."""
        return self(gender, "posadj")

    def them(self, gender="n"):
        """Call for: him/her/them/it."""
        return self(gender, "obj")

    def they(self, gender="n"):
        """Call for: he/she/they/it."""
        return self(gender, "sub")

    def themself(self, gender="n"):
        """Call for: him/her/their/itself."""
        return self(gender, "reflex")

    def Theirs(self, gender="n"):
        """Call for: His/Hers/Theirs/Its."""
        return self(gender, "pospro").capitalize()

    def Their(self, gender="n"):
        """Call for: His/Her/Their/Its."""
        return self(gender, "posadj").capitalize()

    def Them(self, gender="n"):
        """Call for: Him/Her/Them/It."""
        return self(gender, "obj").capitalize()

    def They(self, gender="n"):
        """Call for: He/She/They/It."""
        return self(gender, "sub").capitalize()

    def Themself(self, gender="n"):
        """Call for: Him/Her/Their/Itself."""
        return self(gender, "reflex").capitalize()

    def THEIRS(selfself, gender="n"):
        return self(gender, "pospro").upper()

    def THEIR(self, gender="n"):
        return self(gender, "posadj").upper()

    def THEM(self, gender="n"):
        return self(gender, "obj").upper()

    def THEY(self, gender="n"):
        return self(gender, "sub").upper()

    def THEMSELF(self, gender="n"):
        return self(gender, "reflex").upper()

    def THEIRS(self, gender="n"):
        return self(gender, "pospro").upper()

    def THEIR(self, gender="n"):
        return self(gender, "posadj").upper()

    def THEMSELF(self, gender="n"):
        return self(gender, "reflex").upper()
